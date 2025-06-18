# TDS Virtual TA

A FastAPI-based virtual assistant that answers student queries related to the Tools in Data Science (TDS) course using OpenAI GPT.

## Features
- Answers questions using context scraped from:
  - TDS Course Portal
  - IITM Discourse Forum
- Accepts optional base64 image input (e.g., screenshots)
- Returns answers with reference links
- Deployable on Render

## API Endpoint
```http
POST /api/
