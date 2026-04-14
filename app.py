from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone

app = Flask(__name__)

GENDERIZE_API = "https://api.genderize.io"

def error_response(message, status_code):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code


@app.route('/api/classify', methods=['GET'])
def classify_name():
    name = request.args.get('name')

    # ---- Validation ----
    if name is None or name.strip() == "":
        return error_response("Missing or empty name parameter", 400)

    if not isinstance(name, str):
        return error_response("Name must be a string", 422)

    try:
        # ---- External API Call ----
        response = requests.get(GENDERIZE_API, params={"name": name}, timeout=2)

        if response.status_code != 200:
            return error_response("Upstream service error", 502)

        data = response.json()

    except requests.exceptions.RequestException:
        return error_response("Failed to reach upstream service", 502)

    # ---- Edge Case Handling ----
    if data.get("gender") is None or data.get("count", 0) == 0:
        return error_response("No prediction available for the provided name", 422)

    # ---- Processing ----
    gender = data.get("gender")
    probability = data.get("probability", 0)
    sample_size = data.get("count", 0)

    is_confident = probability >= 0.7 and sample_size >= 100

    processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    result = {
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

    return jsonify(result), 200


# ---- CORS (important for grading) ----
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
