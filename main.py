import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI, RateLimitError
from json import JSONDecodeError
from scraper import scrape_discourse

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionInput(BaseModel):
    question: str
    image: Optional[str] = None

@app.post("/api/")
async def ask(input: QuestionInput):
    question = input.question
    links = scrape_discourse()
    context = "\n\n".join(links[:5])

    prompt = f"""
You are a teaching assistant helping students in the TDS course.

Use the question and relevant links below to generate a helpful and direct answer.

Question: {question}

Links:
{context}

Answer in JSON format:
{{
  "answer": "<answer_here>",
  "links": [
    {{"url": "<link1>", "text": "<summary1>"}},
    {{"url": "<link2>", "text": "<summary2>"}}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        return json.loads(content)

    except RateLimitError:
        return {
            "answer": "OpenAI quota exceeded. Please try again later.",
            "links": []
        }
    except JSONDecodeError:
        return {
            "answer": "Could not parse LLM response properly.",
            "links": [{"url": link, "text": "Related discussion"} for link in links[:2]]
        }

@app.api_route("/", methods=["GET", "HEAD", "OPTIONS"])
def root(request: Request):
    return {"message": "TDS Virtual TA API is running"}
