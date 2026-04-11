from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone

app = Flask(__name__)

GENDERIZE_API = "https://api.genderize.io"

# GET /api/classify?name={name}
@app.route("/api/classify", methods= ["GET"])
def classify_name():
    name = request.args.get("name")

    # Validate query parameter
    if not name:
        return jsonify({
            "status": "error",
            "message": "Name query parameter is required"
        }), 400

    try:
        # Call external API
        response = requests.get(GENDERIZE_API, params={"name": name})
        response.raise_for_status()
        data = response.json()

        # Extract fields
        gender = data.get("gender")
        probability = data.get("probability", 0)
        count = data.get("count", 0)

        # Rename count → sample_size
        sample_size = count

        # Compute is_confident
        is_confident = (
            probability is not None and
            sample_size is not None and
            probability >= 0.7 and
            sample_size >= 100
        )

        # Generate processed_at (UTC ISO 8601)
        processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Return structured response
        return jsonify({
            "status": "success",
            "data": {
                "name": name,
                "gender": gender,
                "probability": probability,
                "sample_size": sample_size,
                "is_confident": is_confident,
                "processed_at": processed_at
            }
        }), 200

    except requests.exceptions.RequestException:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch data from external API"
        }), 502


if __name__ == "__main__":
    app.run(debug=True)