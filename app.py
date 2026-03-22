from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
import os
import json
import random

load_dotenv()

app = FastAPI(title="AI Meal Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ============================================
# MODELS
# ============================================
class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class MealPlanRequest(BaseModel):
    user_id: str
    goal: str
    diet_type: str
    daily_calories: int = 1800

class LogMealRequest(BaseModel):
    user_id: str
    meal_name: str
    calories: int
    protein: int = 0
    carbs: int = 0
    fat: int = 0

# ============================================
# ROUTES
# ============================================

@app.get("/health")
async def health():
    return {"status": "ok", "message": "AI Meal Planner API running"}

@app.post("/signup")
async def signup(data: SignupRequest):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        if response.user:
            supabase.table("users").insert({
                "id": response.user.id,
                "email": data.email,
                "full_name": data.full_name,
                "plan": "free"
            }).execute()
        return {"message": "Account created!", "user_id": response.user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
async def login(data: LoginRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "message": "Login successful",
            "user_id": response.user.id,
            "access_token": response.session.access_token
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/meal-plan/generate")
async def generate_meal_plan(data: MealPlanRequest):
    # Get pre-generated plans from database
    try:
        plans = supabase.table("meal_plan_templates")            .select("*")            .eq("diet_type", data.diet_type)            .eq("goal", data.goal)            .limit(7)            .execute()

        if plans.data:
            return {"meal_plan": plans.data, "source": "database"}

        # Fallback meal plan
        meal_plan = generate_default_plan(data.diet_type, data.goal, data.daily_calories)
        return {"meal_plan": meal_plan, "source": "generated"}
    except Exception as e:
        meal_plan = generate_default_plan(data.diet_type, data.goal, data.daily_calories)
        return {"meal_plan": meal_plan, "source": "generated"}

def generate_default_plan(diet_type: str, goal: str, calories: int):
    meals = {
        "regular": {
            "breakfasts": ["Oatmeal with berries", "Eggs and toast", "Greek yogurt parfait"],
            "lunches": ["Grilled chicken salad", "Turkey sandwich", "Quinoa bowl"],
            "dinners": ["Salmon with vegetables", "Chicken stir fry", "Pasta with chicken"],
            "snacks": ["Apple with almonds", "Greek yogurt", "Mixed nuts"]
        },
        "keto": {
            "breakfasts": ["Bacon and eggs", "Bulletproof coffee", "Cheese omelette"],
            "lunches": ["Tuna avocado salad", "Chicken lettuce wraps", "Salmon bowl"],
            "dinners": ["Beef and broccoli", "Grilled salmon", "Chicken thighs"],
            "snacks": ["Cheese and nuts", "Avocado", "Pork rinds"]
        },
        "vegan": {
            "breakfasts": ["Smoothie bowl", "Avocado toast", "Oatmeal with fruit"],
            "lunches": ["Lentil soup", "Buddha bowl", "Chickpea wrap"],
            "dinners": ["Tofu stir fry", "Black bean tacos", "Lentil curry"],
            "snacks": ["Fruit and nuts", "Hummus with veggies", "Energy balls"]
        }
    }

    diet_meals = meals.get(diet_type, meals["regular"])
    plan = []

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(days):
        plan.append({
            "day": day,
            "breakfast": {"name": diet_meals["breakfasts"][i % len(diet_meals["breakfasts"])], "calories": int(calories * 0.25)},
            "lunch": {"name": diet_meals["lunches"][i % len(diet_meals["lunches"])], "calories": int(calories * 0.35)},
            "dinner": {"name": diet_meals["dinners"][i % len(diet_meals["dinners"])], "calories": int(calories * 0.30)},
            "snack": {"name": diet_meals["snacks"][i % len(diet_meals["snacks"])], "calories": int(calories * 0.10)},
            "total_calories": calories
        })

    return plan

@app.get("/meal-plan/{user_id}")
async def get_meal_plan(user_id: str):
    try:
        result = supabase.table("meal_plans")            .select("*")            .eq("user_id", user_id)            .order("created_at", desc=True)            .limit(1)            .execute()
        if result.data:
            return result.data[0]
        return {"message": "No meal plan found"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/log-meal")
async def log_meal(data: LogMealRequest):
    try:
        result = supabase.table("nutrition_logs").insert({
            "user_id": data.user_id,
            "meal_name": data.meal_name,
            "calories": data.calories,
            "protein": data.protein,
            "carbs": data.carbs,
            "fat": data.fat
        }).execute()
        return {"message": "Meal logged!", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/nutrition/{user_id}")
async def get_nutrition(user_id: str):
    try:
        result = supabase.table("nutrition_logs")            .select("*")            .eq("user_id", user_id)            .execute()
        total_calories = sum(log["calories"] for log in result.data)
        return {
            "logs": result.data,
            "total_calories": total_calories,
            "total_meals": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/grocery-list/{user_id}")
async def get_grocery_list(user_id: str):
    grocery_items = [
        {"item": "Chicken breast", "amount": "2 lbs", "category": "Protein"},
        {"item": "Salmon fillets", "amount": "1 lb", "category": "Protein"},
        {"item": "Greek yogurt", "amount": "32 oz", "category": "Dairy"},
        {"item": "Eggs", "amount": "1 dozen", "category": "Protein"},
        {"item": "Spinach", "amount": "5 oz bag", "category": "Vegetables"},
        {"item": "Broccoli", "amount": "1 head", "category": "Vegetables"},
        {"item": "Sweet potatoes", "amount": "3 lbs", "category": "Carbs"},
        {"item": "Brown rice", "amount": "2 lbs", "category": "Carbs"},
        {"item": "Olive oil", "amount": "1 bottle", "category": "Fats"},
        {"item": "Almonds", "amount": "1 lb", "category": "Snacks"},
        {"item": "Berries mix", "amount": "2 cups", "category": "Fruit"},
        {"item": "Avocados", "amount": "4 pieces", "category": "Fats"},
    ]
    return {"grocery_list": grocery_items, "total_items": len(grocery_items)}

@app.post("/webhook")
async def webhook(data: dict):
    # Lemon Squeezy webhook
    event = data.get("meta", {}).get("event_name", "")
    if event == "subscription_created":
        user_email = data.get("data", {}).get("attributes", {}).get("user_email")
        print(f"New subscription: {user_email}")
    return {"received": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
