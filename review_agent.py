# review_agent.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PlanInput(BaseModel):
    plan: str
    
class ReviewResponse(BaseModel):
    analysis: str
    recommendations: List[str]

@app.post("/review", response_model=ReviewResponse)
async def review_plan(plan_input: PlanInput):
    # OpenAI агент анализирует план путешествия
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """Ты опытный путешественник-эксперт. 
             Проанализируй план поездки и предоставь:
             1. Общий анализ плана
             2. Список конкретных рекомендаций по улучшению"""},
            {"role": "user", "content": plan_input.plan}
        ]
    )
    
    content = response.choices[0].message.content
    
    # Разделяем ответ на анализ и рекомендации
    parts = content.split("\n\n")
    analysis = parts[0]
    recommendations = [r.strip("- ") for r in parts[1].split("\n") if r.strip()]
    
    return ReviewResponse(
        analysis=analysis,
        recommendations=recommendations
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
