# Genderize Integration API

This is a single-endpoint API built with FastAPI that integrates with the external [Genderize API](https://genderize.io/) to determine the likely gender of a given name. It's part of the HNG 14 assigned task stage 0.

## Features
- It provides predicting analytics based on name parameter along with a customized confidence scale (`is_confident`).
- Error handling matches stringent application requirements (missing parameters, upstream failures, bad requests).
- Full CORS support to allow any frontend applications to access the service and the thanos bot to read properly
- Ultra fast execution based on FastAPI asynchronous routes.So multiple GET requests can be sent overtime

## Endpoints

### `GET /api/classify`
Classifies a name into `gender`, computes `probability` and `sample_size`, and resolves whether the API result is logically confident.

**Query Parameter:**
- `name` (required): The name you want to classify (e.g. `?name=john`).

**Success Response (200 OK)**
```json
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 1234,
    "is_confident": true,
    "processed_at": "2026-04-01T12:00:00Z"
  }
}
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server locally:**
   ```bash
   uvicorn main:app --reload
   ```
   The local server starts at `http://127.0.0.1:8000`.

## Testing

You can visit `http://127.0.0.1:8000/api/classify?name=john` or make a GET request using a tool like `curl` I already made use of Swagger UI from FastAPI: 
```bash
curl "http://127.0.0.1:8000/api/classify?name=peter"
```
