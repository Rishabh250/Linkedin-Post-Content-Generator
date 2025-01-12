# LinkedIn Post Generator Backend Service

This is the backend service for the LinkedIn Post Generator application - an AI-powered tool that helps generate engaging LinkedIn posts. The service provides RESTful API endpoints that leverage OpenAI and Google's Generative AI to create customized content.

## Features

- AI-powered post generation with customizable tone and target audience
- Error handling and logging
- CORS support for frontend integration
- Multiple AI model support (OpenAI GPT and Google Gemini)

## Prerequisites

- Python 3.8+
- pip package manager
- OpenAI API key
- Google Cloud API key (for Gemini model)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the backend directory and add your API keys:
     ```plaintext
     OPENAI_API_KEY=your_openai_api_key
     GOOGLE_API_KEY=your_google_api_key
     ```

## Running the Backend

Start the Flask server: