from flask import Flask, request, jsonify, make_response
import requests
from datetime import datetime, timezone

app = Flask(__name__)

GENDERIZE_URL = "https://api.genderize.io"


def error_response(message, status_code):
    response = jsonify({
        "status": "error",
        "message": message
    })
    response.status_code = status_code
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route("/api/classify", methods=["GET"])
def classify_name():
    name = request.args.get("name")

    # ✅ REQUIRED: validation (restore this)
    if name is None or name.strip() == "":
        return error_response("Missing or empty name parameter", 400)

    try:
        # ✅ Correct API call
        res = requests.get(GENDERIZE_URL, params={"name": name}, timeout=2)

        if res.status_code != 200:
            return error_response("Upstream service error", 502)

        data = res.json()

        gender = data.get("gender")
        probability = data.get("probability")
        count = data.get("count")

        # ✅ Edge case: return error for nonsense names
        if gender is None or count == 0:
            return error_response(
                "No prediction available for the provided name", 422
            )

        sample_size = count

        # ✅ Correct confidence logic
        is_confident = probability is not None and probability >= 0.75

        processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        response_body = {
            "status": "success",
            "data": {
                "name": name.lower(),
                "gender": gender,
                "probability": probability,
                "sample_size": sample_size,
                "is_confident": is_confident,
                "processed_at": processed_at
            }
        }

        response = make_response(jsonify(response_body), 200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except requests.exceptions.RequestException:
        return error_response("Failed to connect to upstream service", 502)
    except Exception:
        return error_response("Internal server error", 500)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
