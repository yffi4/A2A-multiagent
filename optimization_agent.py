from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
import json

app = FastAPI()

class OptimizationInput(BaseModel):
    plan: str
    budget: float
    days: int

class OptimizedPlan(BaseModel):
    optimized_plan: str
    estimated_cost: float
    daily_breakdown: List[str]

# Настраиваем LangChain с Groq
llm = ChatGroq(
    temperature=0.7,
    model_name="gemma2-9b-it",  # Используем Mixtral модель
    api_key=os.getenv("GROQ_API_KEY")  # Исправлено с groq_api_key на api_key
)

# Создаем шаблон промпта
template = """Ты опытный турагент-оптимизатор. 
Оптимизируй следующий план путешествия с учетом бюджета {budget}$ и длительности {days} дней.

План:
{plan}

Создай ответ строго в следующем формате JSON (все поля обязательны):
{{
    "optimized_plan": "детальное описание оптимизированного плана",
    "estimated_cost": 1000.0,
    "daily_breakdown": [
        "День 1: детальное описание",
        "День 2: детальное описание",
        "День 3: детальное описание"
    ]
}}

Убедись, что:
1. estimated_cost - это число (не строка)
2. daily_breakdown содержит ровно {days} дней
3. все значения представлены в правильном формате
4. ответ должен быть только в формате JSON, без дополнительного текста
"""

prompt = ChatPromptTemplate.from_template(template)

@app.post("/optimize")
async def optimize_plan(input_data: OptimizationInput):
    try:
        # Форматируем промпт
        messages = prompt.format_messages(
            budget=input_data.budget,
            days=input_data.days,
            plan=input_data.plan
        )
        
        # Получаем ответ от модели
        response = llm.invoke(messages)
        
        try:
            # Извлекаем JSON из ответа
            content = response.content
            # Удаляем все, что не является JSON
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
            else:
                raise ValueError("No JSON found in response")

            # Парсим JSON ответ
            result = json.loads(json_str)
            
            # Проверяем наличие всех необходимых полей
            if not all(key in result for key in ["optimized_plan", "estimated_cost", "daily_breakdown"]):
                raise ValueError("Missing required fields in response")
            
            # Проверяем типы данных
            if not isinstance(result["estimated_cost"], (int, float)):
                result["estimated_cost"] = float(result["estimated_cost"])
            
            # Проверяем количество дней
            if len(result["daily_breakdown"]) != input_data.days:
                result["daily_breakdown"] = result["daily_breakdown"][:input_data.days] if len(result["daily_breakdown"]) > input_data.days else \
                    result["daily_breakdown"] + [f"День {i+1}: Требуется планирование" for i in range(len(result["daily_breakdown"]), input_data.days)]
            
            # Создаем и валидируем объект OptimizedPlan
            optimized_plan = OptimizedPlan(
                optimized_plan=result["optimized_plan"],
                estimated_cost=result["estimated_cost"],
                daily_breakdown=result["daily_breakdown"]
            )
            
            return optimized_plan
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing response: {str(e)}")
            print(f"Raw response: {response.content}")
            # Если не удалось распарсить JSON или данные некорректны
            return OptimizedPlan(
                optimized_plan="План не удалось оптимизировать",
                estimated_cost=float(input_data.budget),
                daily_breakdown=[f"День {i+1}: Требуется перепланировка" for i in range(input_data.days)]
            )
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 