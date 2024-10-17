# DUDOXX-MMRAG API Usage Guide

This guide provides detailed instructions for using the DUDOXX-MMRAG API, with a focus on using the Swagger UI interface.

## Getting Started

### API Documentation Access

Access the interactive API documentation through Swagger UI at:
```
http://localhost:8000/docs
```

### Authentication

Before using any endpoint, you need to obtain an API key:

1. Locate the `/create_api_key` endpoint in Swagger UI
2. Click "Try it out" and then "Execute"
3. Save the returned API key
4. In Swagger UI, click the "Authorize" button (🔒) at the top
5. Enter your API key in the format: `Bearer YOUR_API_KEY`
6. Click "Authorize" to apply the key to all endpoints

## Available Endpoints

### 1. Drug Information
**Endpoint:** `GET /drug_info/{drug_name}`

Retrieves information about specific medications.

**Parameters:**
- `drug_name` (path): Name of the drug
- `include_interactions` (query, optional): Set to true to include drug interactions

**Using Swagger UI:**
1. Click on the endpoint
2. Click "Try it out"
3. Enter drug name (e.g., "aspirin")
4. Set include_interactions as needed
5. Click "Execute"

### 2. Disease Information
**Endpoint:** `GET /disease_info/{disease_name}`

Retrieves information about specific diseases.

**Parameters:**
- `disease_name` (path): Name of the disease
- `include_treatments` (query, optional): Set to true to include treatment information

### 3. Image Description
**Endpoint:** `POST /describe_image`

Analyzes and describes medical images.

**Parameters:**
- `file` (form-data): Image file (JPEG or PNG only)

**Using Swagger UI:**
1. Click "Try it out"
2. Click "Choose File" to upload an image
3. Select a JPEG or PNG image
4. Click "Execute"

### 4. Speech Generation
**Endpoint:** `POST /generate_speech`

Converts text to speech.

**Parameters:**
```json
{
  "text": "Text to convert to speech",
  "voice": "desired_voice_option"
}
```
Available voice options "alloy", "echo", "fable", "onyx", "nova", "shimmer"

**Related Endpoints:**
- `GET /speech_status/{task_id}`: Check generation status
- `GET /download_speech/{task_id}`: Download generated audio

**Workflow:**
1. Submit text using `/generate_speech`
2. Save the returned `task_id`
3. Check status using `/speech_status/{task_id}`
4. Once complete, download using `/download_speech/{task_id}`

### 5. Audio Transcription
**Endpoint:** `POST /transcribe_audio`

Transcribes audio files to text.

**Parameters:**
- `audio` (form-data): Audio file
- `target_language` (query): ISO 639-1 language code (default: "en")

**Related Endpoints:**
- `GET /task_status/{task_id}`: Check transcription status

**Workflow:**
1. Upload audio using `/transcribe_audio`
2. Save the returned `task_id`
3. Check status using `/task_status/{task_id}`

## Rate Limiting

All endpoints are rate-limited to:
- 5 requests per 60 seconds
- Exceeding this limit will return a 429 error

## Response Formats

### Success Responses

1. **Drug/Disease Info:**
```json
{
  "name": "string",
  "description": "string",
  "additional_info": {}
}
```

2. **Image Description:**
```json
{
  "description": "string"
}
```

3. **Speech Generation:**
```json
{
  "task_id": "uuid",
  "status": "processing|completed|failed",
  "progress": 0-100
}
```

4. **Transcription:**
```json
{
  "task_id": "uuid",
  "status": "processing|completed|failed",
  "text": "string"
}
```

### Error Responses

Common error status codes:
- 400: Bad Request
- 401: Invalid API key
- 404: Resource not found
- 429: Rate limit exceeded
- 500: Internal server error

## Examples Using cURL

### Drug Information
```bash
curl -X GET "http://localhost:8000/drug_info/aspirin?include_interactions=true" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

### Image Description
```bash
curl -X POST "http://localhost:8000/describe_image" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -F "file=@/path/to/image.jpg"
```

### Generate Speech
```bash
curl -X POST "http://localhost:8000/generate_speech" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world", "voice": "default"}'
```

## Best Practices

1. **API Key Management:**
   - Store API keys securely
   - Don't expose keys in client-side code
   - Rotate keys periodically

2. **Rate Limit Handling:**
   - Implement exponential backoff for retry logic
   - Monitor your API usage
   - Cache responses when appropriate

3. **File Uploads:**
   - Verify file types before uploading
   - Keep image files under reasonable size
   - Use appropriate audio formats for transcription

## Troubleshooting

1. **Authentication Issues:**
   - Verify API key format (Bearer prefix)
   - Check if key is still valid
   - Ensure key is properly authorized in Swagger UI

2. **Rate Limiting:**
   - Wait 60 seconds when limit is reached
   - Monitor response headers for rate limit info
   - Implement request queuing if needed

3. **File Upload Issues:**
   - Check file format compatibility
   - Verify file size limits
   - Ensure proper Content-Type headers

## Support

For technical support:
1. Check the Swagger documentation
2. Verify request parameters
3. Check response status codes and messages
4. Contact support with detailed error information

When reporting issues, include:
- Endpoint URL
- Request parameters
- Response status code
- Error message
- Timestamp