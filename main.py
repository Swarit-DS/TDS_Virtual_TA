from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
from scraper import scrape_discourse
import os
import json

app = FastAPI()

class QuestionInput(BaseModel):
    question: str
    image: Optional[str] = None

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/")
async def ask(input: QuestionInput):
    question = input.question
    links = scrape_discourse()
    context = "\n\n".join(links)

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
        assistant_reply = response.choices[0].message.content
        return json.loads(assistant_reply)

    except Exception as e:
        return {
            "answer": "Something went wrong. Please try again later.",
            "links": [{"url": l, "text": "Related discussion"} for l in links[:2]]
        }

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
      <head>
        <title>TDS Virtual TA API</title>
      </head>
      <body>
        <h2>TDS Virtual TA API is Running ✅</h2>
        <p>This API accepts a <code>POST</code> request at <code>/api/</code> with a JSON body.</p>

        <h3>Example curl command:</h3>
        <pre>
curl -X POST https://tds-virtual-ta-byqp.onrender.com/api/ \\
  -H "Content-Type: application/json" \\
  -d '{"question": "Should I use gpt-3.5-turbo-0125 or gpt-4o-mini?"}'
        </pre>

        <h3>Example JSON body:</h3>
        <pre>
{
  "question": "Should I use gpt-3.5-turbo-0125 or gpt-4o-mini?"
}
        </pre>

        <p>Supported method: <strong>POST</strong> only on <code>/api/</code></p>
      </body>
    </html>
    """
