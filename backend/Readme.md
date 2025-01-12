# LinkedIn Post Generator Backend Service

A robust, AI-powered backend service for generating engaging LinkedIn posts. This service combines OpenAI's GPT and Google's Gemini models with advanced content optimization techniques to create highly effective professional social media content.

## 🚀 Key Features

- **Advanced AI Integration**
  - Dual model support (OpenAI GPT-4 and Google Gemini)
  - Smart model fallback mechanism
  - Context-aware content generation
  - Tone and style preservation

- **Professional Content Optimization**
  - LinkedIn-specific formatting
  - Hashtag optimization
  - Engagement metrics analysis
  - Character count optimization

- **Enterprise-Ready Infrastructure**
  - Rate limiting and request throttling
  - Comprehensive error handling
  - Request validation
  - Response caching
  - Detailed logging system

- **Security & Compliance**
  - API key authentication
  - Request sanitization
  - CORS configuration
  - Input validation
  - Rate limiting per API key

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- 2GB RAM minimum
- 1GB free disk space

### Required API Keys
- OpenAI API key (GPT-4 access required)
- Google Cloud API key (Gemini API access)
- (Optional) LinkedIn API credentials for direct posting

## 🛠 Installation

1. Clone the repository:
```bash
git clone https://github.com/Rishabh250/Linkedin-Post-Content-Generator.git
cd linkedin-post-generator/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
```

## 🚀 Running the Service

### Development Mode
```bash
python app.py --debug
```

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📡 API Endpoints

### Generate Post Content
`POST /api/v1/generate-post`

Generate optimized LinkedIn post content based on provided parameters.

#### Request Body
```json
{
  "topic": "string",
  "tone": "string",
  "target_audience": "string",
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| topic | string | Yes | Main topic or subject of the post |
| tone | string | Yes | Desired tone (professional, casual, enthusiastic, authoritative) |
| target_audience | string | Yes | Target audience category |

#### Response
```json
{
  "status": "success",
  "message": "string"
}
```

### Error Responses

```json
{
  "status": "error",
  "message": "string"
}
```

## ⚙️ Configuration

### Available Environment Variables

```plaintext
# Core Settings
PORT=5000
HOST=0.0.0.0
DEBUG=False
ENVIRONMENT=production

# API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_TOKENS_PER_REQUEST=2000

# Security
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
API_KEY_REQUIRED=True
```

## 🔒 Security Considerations

1. **API Security**
   - Use API key authentication
   - Implement request signing
   - Set up rate limiting
   - Configure CORS properly

2. **Data Protection**
   - Sanitize input data
   - Validate request parameters
   - Implement request size limits
   - Use HTTPS in production

3. **Error Handling**
   - Never expose internal errors
   - Log security events
   - Implement retry mechanisms
   - Handle timeout scenarios

## 🔍 Monitoring and Logging

## 📈 Performance Optimization

1. **Caching Strategy**
   - Response caching
   - Model response caching
   - Cache invalidation rules
   - Distributed caching support

2. **Request Processing**
   - Async request handling
   - Request batching
   - Connection pooling
   - Task queuing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.