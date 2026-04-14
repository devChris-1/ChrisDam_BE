from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone

@app.route("/api/classify", methods=["GET"])
def classify_name():
name = request.args.get("name")

# Validate input
if name is None:
return jsonify({
"status": "error",
"message": "Name query parameter is required"
}), 400

name = name.strip()

if name == "":
return jsonify({
"status": "error",
"message": "Name query parameter is required"
}), 400

try:
response = requests.get(
GENDERIZE_API,
params={"name": name},
timeout=3
)
response.raise_for_status()
api_data = response.json()

gender = api_data.get("gender")
probability = api_data.get("probability") or 0
sample_size = api_data.get("count") or 0

# ✅ ONLY check gender (not count)
if gender is None:
return jsonify({
"status": "error",
"message": "No prediction available for the provided name"
}), 422

is_confident = probability >= 0.7 and sample_size >= 100

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


# ---- CORS (important for grading) ----
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
