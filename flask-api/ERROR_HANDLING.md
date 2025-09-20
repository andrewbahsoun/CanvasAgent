# Flask API Error Handling Guide

## What Happens When Fields Are Missing

### 1. **Missing `question` field**
**Request:**
```json
{
  "context": {"course": "CS101"},
  "canvas_tokens": {"access_token": "token123"}
}
```

**Response:**
```json
HTTP 400 Bad Request
{
  "error": "missing_question"
}
```

### 2. **Empty `question` field**
**Request:**
```json
{
  "question": "",
  "context": {"course": "CS101"},
  "canvas_tokens": {"access_token": "token123"}
}
```

**Response:**
```json
HTTP 400 Bad Request
{
  "error": "missing_question"
}
```

### 3. **Missing both `canvas_tokens` and `google_tokens`**
**Request:**
```json
{
  "question": "What are my assignments?",
  "context": {"course": "CS101"}
}
```

**Response:**
```json
HTTP 401 Unauthorized
{
  "error": "no_tokens_available",
  "message": "Canvas or Google Drive authentication required"
}
```

### 4. **Empty token objects**
**Request:**
```json
{
  "question": "What are my assignments?",
  "context": {"course": "CS101"},
  "canvas_tokens": {},
  "google_tokens": {}
}
```

**Response:**
```json
HTTP 401 Unauthorized
{
  "error": "no_tokens_available",
  "message": "Canvas or Google Drive authentication required"
}
```

### 5. **Missing `access_token` in tokens**
**Request:**
```json
{
  "question": "What are my assignments?",
  "context": {"course": "CS101"},
  "canvas_tokens": {
    "refresh_token": "refresh123",
    "expires_in": 3600
  },
  "google_tokens": {
    "refresh_token": "refresh456",
    "expires_in": 3600
  }
}
```

**Response:**
```json
HTTP 401 Unauthorized
{
  "error": "no_tokens_available",
  "message": "Canvas or Google Drive authentication required"
}
```

### 6. **Missing `context` field (OK)**
**Request:**
```json
{
  "question": "What are my assignments?",
  "canvas_tokens": {"access_token": "token123"}
}
```

**Response:**
```json
HTTP 200 OK
{
  "status": "success",
  "message": "Test mode - simulating backend response",
  "user_question": "What are my assignments?",
  "user_context": {},
  "tokens": {
    "canvas": {
      "available": true,
      "base_url": "https://your-canvas-instance.instructure.com"
    },
    "google_drive": {
      "available": false
    }
  },
  "simulated_answer": "Test response: You asked 'What are my assignments?'. This is a simulated backend response for testing purposes.",
  "timestamp": 1758329845
}
```

## Validation Rules

### Required Fields:
- ✅ **`question`** - Must be present and non-empty string
- ✅ **At least one valid token** - Either `canvas_tokens.access_token` OR `google_tokens.access_token`

### Optional Fields:
- ⚪ **`context`** - Defaults to `{}` if missing
- ⚪ **`canvas_tokens`** - Defaults to `{}` if missing
- ⚪ **`google_tokens`** - Defaults to `{}` if missing

### Token Validation:
- **Canvas token**: Must have `access_token` field
- **Google token**: Must have `access_token` field
- **At least one** of the above must be valid

## Error Response Format

All errors follow this format:
```json
{
  "error": "error_code",
  "message": "Human readable description"  // Optional
}
```

## HTTP Status Codes

- **400 Bad Request**: Missing required field (`question`)
- **401 Unauthorized**: No valid tokens provided
- **200 OK**: Success (with test response or backend response)

## Testing Missing Fields

Use these test cases to verify error handling:

```bash
# Test 1: Missing question
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"context": {"course": "CS101"}}'

# Test 2: Empty question
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "", "canvas_tokens": {"access_token": "token123"}}'

# Test 3: No tokens
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are my assignments?"}'

# Test 4: Invalid tokens (no access_token)
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are my assignments?", "canvas_tokens": {"refresh_token": "refresh123"}}'
```
