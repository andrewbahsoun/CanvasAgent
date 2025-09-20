# Flask Canvas Connector API

**by Landon Kauer**

Minimal Flask gateway that:
- Handles Canvas OAuth2 (start + callback)
- Supports both Canvas and Google Drive tokens
- Exposes `/api/ask` to accept questions from Chrome extension and forwards
  them to your team's backend **including both access tokens** (server→server).

## Quickstart

1) Create and fill `.env` from `.env.example`.
2) Create conda environment & install deps:
   ```bash
   conda create -n hackathon python=3.9
   conda activate hackathon
   pip install -r requirements.txt
   ```
3) Run:
   ```bash
   python app.py
   ```
4) From your Chrome extension:
   - POST to `http://localhost:5001/api/ask` with tokens and question

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/test` - Simple test (no auth required)
- `POST /api/ask-test` - Test with simulated tokens
- `POST /api/ask` - **Main endpoint** (requires tokens in request body)
- `GET /auth/canvas/start` - Start Canvas OAuth flow
- `GET /auth/canvas/callback` - Canvas OAuth callback

## Request Format

```json
{
  "question": "What are my assignments?",
  "context": {"course": "CS101"},
  "canvas_tokens": {
    "access_token": "canvas_token_123",
    "refresh_token": "canvas_refresh_123",
    "expires_in": 3600
  },
  "google_tokens": {
    "access_token": "google_token_456",
    "refresh_token": "google_refresh_456", 
    "expires_in": 3600
  }
}
```

## Important ENV Vars

- `ALLOWED_EXTENSION_ORIGIN`: set to your extension's origin in prod
- `CANVAS_*`: your Canvas developer key + base URL + redirect URI
- `BACKEND_URL` and `BACKEND_AUTH`: where to forward the question and tokens

## Security Notes

- Tokens are never stored on the server (frontend manages them)
- Use HTTPS in production
- Lock CORS to your exact extension origin in production
