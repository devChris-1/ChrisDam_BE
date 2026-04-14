from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})

GENDERIZE_API = "https://api.genderize.io"


@app.route("/api/classify", methods=["GET"])
def classify_name():
    name = request.args.get("name")

    # 🔴 400: Missing or empty name
    if name is None or name.strip() == "":
        return jsonify({
            "status": "error",
            "message": "Name query parameter is required"
        }), 400

    # 🔴 422: Invalid type (should be string)
    if not isinstance(name, str):
        return jsonify({
            "status": "error",
            "message": "Name must be a string"
        }), 422

    try:
        # Call external API (with timeout for performance)
        response = requests.get(
            GENDERIZE_API,
            params={"name": name},
            timeout=3
        )
        response.raise_for_status()
        api_data = response.json()

        gender = api_data.get("gender")
        probability = api_data.get("probability", 0)
        count = api_data.get("count", 0)

        # 🔴 Genderize edge case
        if gender is None or count == 0:
            return jsonify({
                "status": "error",
                "message": "No prediction available for the provided name"
            }), 422

        # Rename count → sample_size
        sample_size = count

        # Compute is_confident
        is_confident = (
            probability >= 0.7 and sample_size >= 100
        )

        # Generate processed_at (UTC ISO 8601)
        processed_at = datetime.now(timezone.utc)\
            .isoformat()\
            .replace("+00:00", "Z")

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

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=5000)
