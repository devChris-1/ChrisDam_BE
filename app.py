from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone

app = Flask(__name__)

GENDERIZE_URL = "https://api.genderize.io"


# Utility: standardized error response
def error_response(message, status_code):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code


# Add CORS header to all responses
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route("/api/classify", methods=["GET"])
def classify_name():
    name = request.args.get("name")

    # --- Validation ---
    if name is None or name.strip() == "":
        return error_response("Missing or empty name parameter", 400)

    if not isinstance(name, str):
        return error_response("Name must be a string", 422)

    try:
        # --- Call external API ---
        response = requests.get(GENDERIZE_URL, params={"name": name}, timeout=3)

        if response.status_code != 200:
            return error_response("Upstream API error", 502)

        data = response.json()

        gender = data.get("gender")
        probability = data.get("probability")
        count = data.get("count")

        # --- Edge Case Handling ---
        if gender is None or count == 0:
            return error_response(
                "No prediction available for the provided name", 422
            )

        # --- Processing Rules ---
        sample_size = count
        is_confident = (
            probability is not None and
            sample_size is not None and
            probability >= 0.7 and
            sample_size >= 100
        )

        processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # --- Success Response ---
        return jsonify({
            "status": "success",
            "data": {
                "name": name.lower(),
                "gender": gender,
                "probability": probability,
                "sample_size": sample_size,
                "is_confident": is_confident,
                "processed_at": processed_at
            }
        }), 200

    except requests.exceptions.Timeout:
        return error_response("External API timeout", 504)

    except requests.exceptions.RequestException:
        return error_response("Failed to connect to external API", 502)

    except Exception:
        return error_response("Internal server error", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
