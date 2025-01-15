import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

app = Flask(__name__)
CORS(app, resources={
    r"/generate-post": {
        "origins": ["http://localhost:3000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def setup_logging() -> None:
    """Configure logging settings"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=f'linkedin_post_generator_{datetime.now().strftime("%Y%m%d")}.log'
    )

def load_environment() -> None:
    """Load and validate environment variables"""
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError("Please set GOOGLE_API_KEY in your environment variables")
    
class ReformatTool:
    """Tool for reformatting text"""
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(temperature=0.7, model="gemini-1.5-flash-002", google_api_key=os.getenv("GOOGLE_API_KEY"))

    def reformat(self, text: str) -> str:
        """Reformat text"""
        return self.llm.run(text)

@dataclass
class WebSearchTool:
    """Tool for performing web searches"""
    name: str = "web_search"
    description: str = "Search the web for the latest information related to a topic."

    def _run(self, query: str) -> str:
        """Run web search query with error handling."""
        try:
            response = requests.get(
                f"https://api.duckduckgo.com/?q={query}&format=json",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("AbstractText") or self._fallback_search(query)
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logging.error("Web search error: %s", str(e))
            return self._fallback_search(query)

    def _arun(self, query: str) -> None:
        """Async run not implemented."""
        raise NotImplementedError("This tool does not support async.")

    def _fallback_search(self, query: str) -> str:
        """Fallback method when primary search fails."""
        try:
            return "Unable to fetch latest information. Using cached data instead."
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logging.error("Fallback search error: %s", str(e))
            return "Search functionality temporarily unavailable."

    def search(self, query: str) -> str:
        """Public interface for web search."""
        return self._run(query)

class VectorDB:
    """Vector database management"""
    def __init__(self, embeddings: HuggingFaceEmbeddings):
        self.embeddings = embeddings
        self.db = None

    def initialize(self, texts_file: Optional[Path] = None) -> None:
        """Initialize vector database with texts"""
        texts = self._load_texts(texts_file) if texts_file else self._get_default_texts()
        try:
            self.db = FAISS.from_texts(texts, embedding=self.embeddings)
            logging.info("Vector database initialized successfully")
        except Exception as e:
            logging.error("Vector database initialization error: %s", str(e))
            raise

    def _load_texts(self, file_path: Path) -> List[str]:
        """Load texts from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_default_texts(self) -> List[str]:
        """Return default marketing texts"""
        return [
            "AI helps in personalized marketing campaigns and customer segmentation.",
            "Latest trends in AI for digital marketing and social media optimization.",
            "Data-driven marketing strategies using machine learning algorithms.",
            "Content optimization using natural language processing.",
            "Marketing automation and customer journey mapping with AI."
        ]

class PostGenerator:
    """Core post generation functionality"""
    def __init__(self, llm: ChatGoogleGenerativeAI, vector_db: VectorDB):
        self.llm = llm
        self.vector_db = vector_db
        self.prompt = self._create_prompt_template()

    def generate(self, topic: str, tone: str, audience: str, latest_info: str) -> str:
        """Generate post content"""
        vector_results = self.vector_db.db.similarity_search(topic, k=3)
        context = " ".join([doc.page_content for doc in vector_results])

        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        post_content = chain.run({
            "topic": topic,
            "tone": tone,
            "audience": audience,
            "latest_info": latest_info,
            "context": context
        })

        return post_content.strip()

    def _create_prompt_template(self) -> PromptTemplate:
        """Create the prompt template for post generation"""

        template = """
            Create a professional LinkedIn post following these guidelines:
            Topic: {topic}
            Tone: {tone}
            Target Audience: {audience}
            
            Latest Information to include:
            {latest_info}
            
            Additional Context:
            {context}
            
            Content Structure:
            • Opening:
              - Start with attention-grabbing hook using emojis and question/statistic
              - Set up context and establish thought leadership
              - Create urgency around the topic
            
            • Body:
              - Include 3-4 data-backed statistics/insights with source citations
              - Structure in clear 2-3 sentence paragraphs with bullet points
              - Use industry-specific terminology matched to audience expertise level
              - Add strategic emojis to highlight key points (2-3 per paragraph)
              - Include real-world examples and case studies
              - Address common pain points and solutions
              - Incorporate trending industry keywords
            
            • Closing:
              - End with compelling call-to-action
              - Include 2 discussion questions to drive engagement
              - Add 5-6 strategic hashtags (mix of trending/niche/branded)
              - Provide 3 key takeaways or actionable tips
              - Include invitation to connect/follow for more insights
            
            Formatting Guidelines:
            • Length: 1000-2000 characters optimized for LinkedIn algorithm
            • Use strategic line breaks and spacing for readability
            • Match tone precisely to audience expectations
            • Technical depth calibrated to audience expertise
            • Include numbered lists and bullet points for scalability
            • Use bold text for key phrases and statistics
            • Add relevant mentions and tags where appropriate
            
            Engagement Optimization:
            • Front-load key insights in first 2-3 lines
            • Include controversy or unique perspective to drive comments
            • Ask questions throughout to encourage interaction
            • Use power words and emotional triggers
            • Add relevant external links in first comment
            • Time post for optimal engagement window
            
            Summary:
            Create a data-driven, highly engaging post that establishes authority while driving meaningful discussion and audience growth through strategic formatting and psychology-based engagement tactics.
            """

        return PromptTemplate(
            template=template,
            input_variables=["topic", "tone", "audience", "latest_info", "context"]
        )

class LinkedInPostGenerator:
    """Main application class"""
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.llm = ChatGoogleGenerativeAI(temperature=0.7, model="gemini-1.5-flash-002", google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.vector_db = VectorDB(self.embeddings)
        self.vector_db.initialize()
        self.post_generator = PostGenerator(self.llm, self.vector_db)
        self.agent = self._setup_agent()

    def _setup_agent(self) -> None:
        """Set up LangChain agent"""
        self.web_search_tool = WebSearchTool()

        tools = [
            Tool(
                name="Web Search",
                func=self.web_search_tool.search,
                description="Search for latest information about topics"
            ),
        ]

        return initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

    def _get_latest_info(self, topic: str) -> str:
        """Get latest information about topic"""
        try:
            return self.agent.run(f"Find recent updates or insights on {topic}")
        except (ValueError, TypeError, KeyError) as e:
            logging.warning("Agent execution error: %s", str(e))
            return f"Based on industry trends and analysis, here are key insights about {topic}..."

    def generate_post(self, topic: str, tone: str, audience: str) -> str:
        """Generate LinkedIn post with error handling"""
        try:
            latest_info = self._get_latest_info(topic)
            return self.post_generator.generate(topic, tone, audience, latest_info)
        except (ValueError, TypeError, KeyError) as e:
            logging.error("Post generation error: %s", str(e))
            raise

@app.route('/generate-post', methods=['POST', 'OPTIONS'])
def generate_post():
    """API endpoint to generate LinkedIn post"""
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        return response

    try:
        data = request.get_json()

        topic = data.get('topic')
        tone = data.get('tone') 
        audience = data.get('audience')

        if not topic or not tone or not audience:
            raise ValueError("Topic, tone, and audience are required")

        generator = LinkedInPostGenerator()
        post = generator.generate_post(topic, tone, audience)

        response = jsonify({
            'status': 'success',
            'post': post
        })
        return response

    except (ValueError, TypeError, KeyError) as e:
        logging.error("API error: %s", str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == "__main__":
    setup_logging()
    load_environment()
    app.run(debug=True, port=8000, host='0.0.0.0')