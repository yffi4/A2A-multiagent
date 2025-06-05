import requests
import json
from typing import Dict, Any

def call_review_agent(plan: str) -> Dict[str, Any]:
    """Вызов агента проверки плана (Pydantic)"""
    response = requests.post(
        "http://localhost:8000/review",
        json={"plan": plan}
    )
    return response.json()

def call_optimization_agent(plan: str, budget: float, days: int) -> Dict[str, Any]:
    """Вызов агента оптимизации (LangChain)"""
    response = requests.post(
        "http://localhost:8001/optimize",
        json={
            "plan": plan,
            "budget": budget,
            "days": days
        }
    )
    return response.json()

def main():
    # Пример плана путешествия
    initial_plan = """
    План поездки в Париж:
    1. Прилет в аэропорт Шарль-де-Голль
    2. Посещение Эйфелевой башни
    3. Поход в Лувр
    4. Прогулка по Елисейским полям
    5. Посещение Нотр-Дам
    6. Круиз по Сене
    7. Отъезд домой
    """
    
    # Шаг 1: Получаем анализ плана
    print("=== Шаг 1: Анализ плана ===")
    review_result = call_review_agent(initial_plan)
    print("\nАнализ:")
    print(review_result.get("analysis", "Анализ недоступен"))
    print("\nРекомендации:")
    for rec in review_result.get("recommendations", []):
        print(f"- {rec}")
    
    # Шаг 2: Оптимизируем план
    print("\n=== Шаг 2: Оптимизация плана ===")
    optimization_result = call_optimization_agent(
        initial_plan,
        budget=1000.0,
        days=3
    )
    
    print("\nОптимизированный план:")
    print(optimization_result.get("optimized_plan", "План недоступен"))
    print(f"\nПредполагаемая стоимость: ${optimization_result.get('estimated_cost', 'Н/Д')}")
    print("\nПлан по дням:")
    for day in optimization_result.get("daily_breakdown", []):
        print(f"- {day}")

if __name__ == "__main__":
    main() 