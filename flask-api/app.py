import os, time, urllib.parse, requests
from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev")

# Cookie settings for extension. For production, run behind HTTPS.
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
)

# CORS (restrict in prod to your extension origin)
ALLOWED_ORIGIN = os.getenv("ALLOWED_EXTENSION_ORIGIN", "http://localhost:5173")
# For development, allow multiple origins
ALLOWED_ORIGINS = [ALLOWED_ORIGIN, "http://localhost:3000", "http://localhost:8080", "http://localhost:4200"]
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True)

# ---- Config ----
CANVAS_BASE = os.getenv("CANVAS_BASE_URL", "").rstrip("/")
CID  = os.getenv("CANVAS_CLIENT_ID")
CSEC = os.getenv("CANVAS_CLIENT_SECRET")
REDIR = os.getenv("CANVAS_REDIRECT_URI")

BACKEND_URL  = os.getenv("BACKEND_URL")
BACKEND_AUTH = os.getenv("BACKEND_AUTH")  # e.g., "Bearer <key>"

# ---- Helpers: Simple token validation ----
def validate_tokens(canvas_tokens: dict, google_tokens: dict) -> bool:
    """Check if at least one valid token is provided"""
    canvas_valid = bool(canvas_tokens and canvas_tokens.get("access_token"))
    google_valid = bool(google_tokens and google_tokens.get("access_token"))
    return canvas_valid or google_valid

# ---- Routes ----
@app.get("/api/health")
def health():
    return jsonify({"ok": True})

@app.post("/api/test")
def test():
    """Test endpoint that simulates backend response without requiring Canvas authentication"""
    body = request.get_json(force=True, silent=True) or {}
    question = body.get("question", "").strip()
    context = body.get("context", {})
    
    if not question:
        return jsonify({"error": "missing_question"}), 400
    
    # Simulate backend response
    test_response = {
        "status": "success",
        "message": "Test endpoint - no authentication required",
        "user_question": question,
        "user_context": context,
        "simulated_answer": f"Test response: You asked '{question}'. This is a simulated backend response for testing purposes.",
        "timestamp": int(time.time()),
        "canvas_required": False,
        "google_drive_required": False
    }
    return jsonify(test_response)


@app.post("/api/ask-test")
def ask_test():
    """Test version of /api/ask that simulates both Canvas and Google Drive authentication for testing"""
    # 2) Read user input from extension
    body = request.get_json(force=True, silent=True) or {}
    question = body.get("question", "").strip()
    context = body.get("context", {})
    if not question:
        return jsonify({"error":"missing_question"}), 400

    # 3) Check if we're in test mode (no backend URL configured)
    if not BACKEND_URL:
        # Test mode: simulate backend response
        test_response = {
            "status": "success",
            "message": "Test mode - simulating backend response with both tokens",
            "user_question": question,
            "user_context": context,
            "tokens": {
                "canvas": {
                    "available": True,  # Simulate having Canvas token
                    "base_url": CANVAS_BASE
                },
                "google_drive": {
                    "available": True   # Simulate having Google Drive token
                }
            },
            "simulated_answer": f"Test response: You asked '{question}'. This is a simulated backend response for testing purposes with both Canvas and Google Drive tokens available.",
            "timestamp": int(time.time())
        }
        return jsonify(test_response)

    # If backend URL is configured, this would normally call the real backend
    return jsonify({"error": "Backend URL configured, use /api/ask for real backend calls"}), 400


@app.get("/auth/canvas/start")
def canvas_start():
    if not (CANVAS_BASE and CID and REDIR):
        return jsonify({"error": "missing_canvas_env"}), 500
    params = {
        "client_id": CID,
        "response_type": "code",
        "redirect_uri": REDIR,
    }
    url = f"{CANVAS_BASE}/login/oauth2/auth?{urllib.parse.urlencode(params)}"
    return redirect(url)

@app.get("/auth/canvas/callback")
def canvas_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "missing_code"}), 400

    data = {
        "grant_type": "authorization_code",
        "client_id": CID,
        "client_secret": CSEC,
        "redirect_uri": REDIR,
        "code": code
    }
    r = requests.post(f"{CANVAS_BASE}/login/oauth2/token", data=data, timeout=15)
    if not r.ok:
        return jsonify({"error":"token_exchange_failed","details": r.text}), 400

    # Canvas OAuth callback - tokens should be handled by frontend
    return "Canvas OAuth completed. Please return to your application to continue."

@app.post("/api/ask")
def ask():
    # 1) Read user input and tokens from request
    body = request.get_json(force=True, silent=True) or {}
    question = body.get("question", "").strip()
    context = body.get("context", {})
    canvas_tokens = body.get("canvas_tokens", {})
    google_tokens = body.get("google_tokens", {})
    
    if not question:
        return jsonify({"error":"missing_question"}), 400

    # 2) Validate that at least one token is provided
    if not validate_tokens(canvas_tokens, google_tokens):
        return jsonify({"error":"no_tokens_available","message":"Canvas or Google Drive authentication required"}), 401

    # 3) Check if we're in test mode (no backend URL configured)
    if not BACKEND_URL:
        # Test mode: simulate backend response
        test_response = {
            "status": "success",
            "message": "Test mode - simulating backend response",
            "user_question": question,
            "user_context": context,
            "tokens": {
                "canvas": {
                    "available": bool(canvas_tokens.get("access_token")),
                    "base_url": CANVAS_BASE if canvas_tokens.get("access_token") else None
                },
                "google_drive": {
                    "available": bool(google_tokens.get("access_token"))
                }
            },
            "simulated_answer": f"Test response: You asked '{question}'. This is a simulated backend response for testing purposes.",
            "timestamp": int(time.time())
        }
        return jsonify(test_response)

    # 4) Build payload to your team's backend with both tokens
    outbound = {
        "question": question,
        "context": context,
        "tokens": {}
    }
    
    # Add Canvas token if available
    if canvas_tokens.get("access_token"):
        outbound["tokens"]["canvas"] = {
            "access_token": canvas_tokens["access_token"],
            "base_url": CANVAS_BASE
        }
    
    # Add Google Drive token if available
    if google_tokens.get("access_token"):
        outbound["tokens"]["google_drive"] = {
            "access_token": google_tokens["access_token"]
        }

    headers = {"Content-Type": "application/json"}
    if BACKEND_AUTH:
        headers["Authorization"] = BACKEND_AUTH

    try:
        resp = requests.post(BACKEND_URL, json=outbound, headers=headers, timeout=60)
    except requests.RequestException as e:
        return jsonify({"error":"backend_unreachable","details": str(e)}), 502

    if not resp.ok:
        return jsonify({"error":"backend_error","status": resp.status_code, "body": resp.text}), 502

    # 5) Pass the backend response back to the extension
    return (resp.text, 200, {"Content-Type": "application/json"})

if __name__ == "__main__":
    # Listen on all interfaces so other computers can connect
    app.run(host='0.0.0.0', port=5001, debug=True)
