# Canvas Connector (Flask Starter)

Minimal Flask gateway that:
- Handles Canvas OAuth2 (start + callback)
- Stores tokens server-side (session for hackathon)
- Exposes `/api/ask` to accept a question from your Chrome extension and forwards
  it to your team's backend **including the Canvas access token** (server→server).

## Quickstart
1) Create and fill `.env` from `.env.example`.
2) Create venv & install deps:
   ```bash
   python -m venv .venv
   source ./.venv/bin/activate   # Windows: .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3) Run:
   ```bash
   python app.py
   ```
4) From your Chrome extension popup:
   - Open `http://localhost:5001/auth/canvas/start` to connect Canvas
   - POST to `http://localhost:5001/api/ask` with `{"question": "..."}`

## Important ENV Vars
- `ALLOWED_EXTENSION_ORIGIN`: set to your extension's origin in prod, e.g.
  `chrome-extension://<YOUR_EXT_ID>`; for local web UIs you can use `http://localhost:5173`.
- `CANVAS_*`: your Canvas developer key + base URL + redirect URI.
- `BACKEND_URL` and `BACKEND_AUTH`: where to forward the question and token.

## Security Notes
- Do **not** return Canvas tokens to the extension.
- Use HTTPS in production and keep `SameSite=None; Secure` cookie settings.
- Lock CORS to your exact extension origin in production.
