# Flask API Testing Templates

**For Chrome Extension Testing**

## Base URL
```
http://localhost:5001
```

## 1. Health Check (GET)
```bash
GET http://localhost:5001/api/health
```

## 2. Simple Test (POST) - No Auth Required
```bash
POST http://localhost:5001/api/test
Content-Type: application/json

{
  "question": "What are my assignments?",
  "context": {
    "course": "CS101",
    "user_id": "12345"
  }
}
```

## 3. Test with Simulated Tokens (POST)
```bash
POST http://localhost:5001/api/ask-test
Content-Type: application/json

{
  "question": "Show me my grades for CS101",
  "context": {
    "course": "CS101",
    "semester": "Fall 2024"
  }
}
```

## 4. Main Ask Endpoint (POST) - With Real Tokens
```bash
POST http://localhost:5001/api/ask
Content-Type: application/json

{
  "question": "What are my upcoming assignments?",
  "context": {
    "course": "CS101",
    "user_id": "12345",
    "semester": "Fall 2024"
  },
  "canvas_tokens": {
    "access_token": "your_canvas_access_token_here",
    "refresh_token": "your_canvas_refresh_token_here",
    "expires_in": 3600,
    "token_type": "Bearer"
  },
  "google_tokens": {
    "access_token": "your_google_access_token_here",
    "refresh_token": "your_google_refresh_token_here",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
}
```

## 5. Canvas OAuth Start (GET)
```bash
GET http://localhost:5001/auth/canvas/start
```

## 6. Canvas OAuth Callback (GET)
```bash
GET http://localhost:5001/auth/canvas/callback?code=your_oauth_code_here
```

## Expected Responses

### Success Response (Test Mode):
```json
{
  "status": "success",
  "message": "Test mode - simulating backend response",
  "user_question": "What are my assignments?",
  "user_context": {
    "course": "CS101"
  },
  "tokens": {
    "canvas": {
      "available": true,
      "base_url": "https://your-canvas-instance.instructure.com"
    },
    "google_drive": {
      "available": true
    }
  },
  "simulated_answer": "Test response: You asked 'What are my assignments?'. This is a simulated backend response for testing purposes.",
  "timestamp": 1758329845
}
```

### Error Response (No Tokens):
```json
{
  "error": "no_tokens_available",
  "message": "Canvas or Google Drive authentication required"
}
```

### Error Response (Missing Question):
```json
{
  "error": "missing_question"
}
```

## Testing with Postman

1. **Import Collection**: Create a new collection in Postman
2. **Set Base URL**: `http://localhost:5001`
3. **Add Headers**: `Content-Type: application/json`
4. **Test Each Endpoint**: Use the templates above

## Testing with Chrome Extension

```javascript
// Example fetch request from Chrome extension
const response = await fetch('http://localhost:5001/api/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: "What are my assignments?",
    context: {
      course: "CS101",
      user_id: "12345"
    },
    canvas_tokens: {
      access_token: "your_canvas_token",
      refresh_token: "your_canvas_refresh_token",
      expires_in: 3600
    },
    google_tokens: {
      access_token: "your_google_token",
      refresh_token: "your_google_refresh_token", 
      expires_in: 3600
    }
  })
});

const data = await response.json();
console.log(data);
```

## Notes

- **Test Mode**: If `BACKEND_URL` is not set, all `/api/ask` requests return simulated responses
- **CORS**: Currently allows multiple localhost origins for development
- **Tokens**: At least one valid token (Canvas OR Google Drive) is required for `/api/ask`
- **Port**: Flask runs on port 5001 by default
