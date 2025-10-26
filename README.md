# HeyJarvis API

API endpoints for passing transcription and frame data to VLM and LLM for Surrounding Awareness and User Profile Classification.

## Features

- **VLM (Vision Language Model)**: Analyze first-person view images for hazards, people, actions, and spatial awareness
- **Transcription Analysis**: Analyze spoken transcripts for context, keywords, domain classification, and action extraction
- **LLM Synthesis**: Combine transcription and visual analyses into natural, conversational responses
- **FastAPI Framework**: Modern, fast, and well-documented API
- **Bearer Token Authentication**: Secure your endpoints with API tokens
- **Pydantic Validation**: Strong request/response validation

## Prerequisites

- Python 3.8+
- Groq API Key ([Get one here](https://console.groq.com/))

## Installation

1. Clone the repository:

```bash
git clone https://github.com/leo-kildani/heyjarvis-api.git
cd heyjarvis-api
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
GROQ_API_KEY=your_groq_api_key_here
API_AUTH_TOKEN=your_secret_token_here  # Optional
```

## Running the API

### Development Mode (with auto-reload)

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```bash
GET /health
```

**Response:**

```json
{
  "status": "online",
  "service": "Jarvis External Models API",
  "endpoints": {
    "vlm": "/api/vlm",
    "transcription_analysis": "/api/transcription-analysis",
    "synthesis": "/api/synthesize"
  }
}
```

### VLM - Image Analysis

```bash
POST /api/vlm
```

**Request Body:**

```json
{
  "base64_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "prompt": "Optional custom prompt"
}
```

**Response:**

```json
{
  "response": "{\"hazard\": \"none\", \"people\": \"2 ahead 1.5 m\", \"actions\": [\"walking forward\"], ...}"
}
```

**Example with curl:**

```bash
curl -X POST "http://localhost:8000/api/vlm" \
  -H "Authorization: Bearer your_secret_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "base64_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }'
```

### Transcription Analysis

```bash
POST /api/transcription-analysis
```

**Request Body:**

```json
{
  "transcript": "Let's schedule a meeting for next Tuesday to discuss the project timeline.",
  "prompt": "Optional custom prompt"
}
```

**Response:**

```json
{
  "analysis": "{\"context\": \"Team discussion about project delivery timeline\", \"keywords\": [...], ...}"
}
```

**Example with curl:**

```bash
curl -X POST "http://localhost:8000/api/transcription-analysis" \
  -H "Authorization: Bearer your_secret_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Let'\''s schedule a meeting for next Tuesday to discuss the project timeline and deliverables."
  }'
```

### Synthesis - Combine Audio and Visual Context

```bash
POST /api/synthesize
```

**Request Body:**

```json
{
  "transcription_analysis": "{\"context\": \"User asking about nearby objects\", \"keywords\": [\"where\", \"counter\"], \"domain\": \"casual\", \"actions\": [\"locate object\"], \"tone\": \"inquisitive\", \"confidence\": 0.91}",
  "surrounding_analysis": [
    "{\"hazard\": \"none\", \"people\": \"2 ahead 1.5 m\", \"actions\": [\"walking forward\"], \"objects\": [\"counter front 3 m\"], \"path\": \"clear left 4 m\", \"notes\": \"daylight\", \"confidence\": 0.93}",
    "{\"hazard\": \"none\", \"people\": \"2 ahead 1.2 m\", \"actions\": [\"walking forward\"], \"objects\": [\"counter front 2.5 m\"], \"path\": \"clear left 4 m\", \"notes\": \"daylight\", \"confidence\": 0.94}"
  ]
}
```

**Response:**

```json
{
  "response": "The counter you're asking about is directly in front of you, about 3 meters away. There are a couple of people ahead walking forward, about 1.5 meters from you. The path to your left is clear if you need to move around them."
}
```

**Example with curl:**

```bash
curl -X POST "http://localhost:8000/api/synthesize" \
  -H "Authorization: Bearer your_secret_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "transcription_analysis": "{\"context\": \"User asking about nearby objects\", \"keywords\": [\"where\", \"counter\"], \"domain\": \"casual\", \"actions\": [\"locate object\"], \"tone\": \"inquisitive\", \"confidence\": 0.91}",
    "surrounding_analysis": [
      "{\"hazard\": \"none\", \"people\": \"2 ahead 1.5 m\", \"actions\": [\"walking forward\"], \"objects\": [\"counter front 3 m\"], \"path\": \"clear left 4 m\", \"notes\": \"daylight\", \"confidence\": 0.93}"
    ]
  }'
```

## Authentication

If `API_AUTH_TOKEN` is set in your `.env` file, all requests must include the Bearer token in the Authorization header:

```bash
Authorization: Bearer your_secret_token_here
```

If `API_AUTH_TOKEN` is not set, authentication is disabled (useful for local development).

## Project Structure

```
heyjarvis-api/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── vlm.py                      # Vision Language Model service
│   ├── transcriptionanalysis.py   # Transcription analysis service
│   └── llmsynthesis.py             # LLM synthesis service
├── config.py                       # Configuration and prompts
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── Dockerfile                      # Docker configuration
├── gunicorn_conf.py               # Gunicorn configuration
└── README.md                       # This file
```

## Models Used

- **VLM**: `meta-llama/llama-4-scout-17b-16e-instruct` - Specialized for visual scene understanding
- **Transcription Analysis**: `openai/gpt-oss-120b` - Large language model for text analysis
- **Synthesis**: `openai/gpt-oss-20b` - Conversational response generation combining audio and visual context

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `401`: Unauthorized (invalid/missing token)
- `500`: Internal Server Error

## Development

To modify the system prompts or model configurations, edit `config.py`.

## License

See LICENSE file for details.

## Support

For issues or questions, please open an issue on GitHub.
