import os
import requests
import json
from dotenv import load_dotenv

load_dotenv("../.env")
API_KEY = os.getenv("DEVTO_API_KEY")

if not API_KEY:
    print("No DEVTO_API_KEY found. Skipping publish.")
    exit(1)

with open("generated_article.md", "r") as f:
    content = f.read()

# Split frontmatter
parts = content.split("---")
if len(parts) >= 3:
    body_markdown = "---".join(parts[2:]).strip()
    
    # We must include the subtitle manually in the description or just let it be in the body
    metadata = {
        "title": "Autonomous Manufacturing Defect Triager with Multi-Agent AI (Master Edition)",
        "description": "How I Automated Quality Control Routing Using LangGraph, a Structured Message Bus, and Persistent Shared State",
        "published": True,
        "tags": ["ai", "python", "machinelearning", "programming"],
        "body_markdown": body_markdown
    }
else:
    print("Invalid format")
    exit(1)

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {"article": metadata}

# Dev.to articles creation endpoint
url = "https://dev.to/api/articles"
response = requests.post(url, json=payload, headers=headers)

if response.status_code in [201, 200]:
    print("Successfully published to Dev.to!")
    print(response.json().get("url"))
else:
    print("Failed to publish", response.status_code, response.text)
    exit(1)
