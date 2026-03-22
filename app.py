from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AI Meal Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class MealPlanRequest(BaseModel):
    user_id: str
    goal: str = "lose_weight"
    diet_type: str = "regular"
    daily_calories: int = 1800

class LogMealRequest(BaseModel):
    user_id: str
    meal_name: str
    calories: int
    protein: int = 0
    carbs: int = 0
    fat: int = 0

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/signup")
async def signup(data: SignupRequest):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        if response.user:
            supabase.table("users").insert({
                "id": str(response.user.id),
                "email": data.email,
                "full_name": data.full_name,
                "plan": "free"
            }).execute()
            return {"message": "Account created!", "user_id": str(response.user.id)}
        raise HTTPException(status_code=400, detail="Signup failed")
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
            "user_id": str(response.user.id),
            "access_token": response.session.access_token
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/meal-plan/generate")
async def generate_meal_plan(data: MealPlanRequest):
    try:
        plans = supabase.table("meal_plan_templates")            .select("*")            .eq("diet_type", data.diet_type)            .eq("goal", data.goal)            .limit(7).execute()
        if plans.data:
            return {"meal_plan": plans.data, "source": "database"}
        return {"meal_plan": get_default_plan(data.diet_type, data.daily_calories), "source": "default"}
    except Exception as e:
        return {"meal_plan": get_default_plan(data.diet_type, data.daily_calories), "source": "default"}

def get_default_plan(diet_type: str, calories: int):
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    meals = {
        "regular": {"b":"Oatmeal","l":"Chicken salad","d":"Salmon+veggies","s":"Greek yogurt"},
        "keto":    {"b":"Bacon+eggs","l":"Tuna avocado","d":"Steak","s":"Cheese+nuts"},
        "vegan":   {"b":"Smoothie bowl","l":"Lentil soup","d":"Tofu stir fry","s":"Fruit+nuts"}
    }
    m = meals.get(diet_type, meals["regular"])
    return [{"day":d,"breakfast":m["b"],"lunch":m["l"],"dinner":m["d"],"snack":m["s"],"calories":calories} for d in days]

@app.get("/meal-plan/{user_id}")
async def get_meal_plan(user_id: str):
    try:
        result = supabase.table("meal_plans")            .select("*").eq("user_id", user_id)            .order("created_at", desc=True).limit(1).execute()
        return result.data[0] if result.data else {"message": "No plan found"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/log-meal")
async def log_meal(data: LogMealRequest):
    try:
        supabase.table("nutrition_logs").insert({
            "user_id": data.user_id,
            "meal_name": data.meal_name,
            "calories": data.calories,
            "protein": data.protein,
            "carbs": data.carbs,
            "fat": data.fat
        }).execute()
        return {"message": "Meal logged!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/grocery-list/{user_id}")
async def grocery_list(user_id: str):
    items = [
        {"item": "Chicken breast", "amount": "2 lbs", "category": "Protein"},
        {"item": "Salmon", "amount": "1 lb", "category": "Protein"},
        {"item": "Greek yogurt", "amount": "32 oz", "category": "Dairy"},
        {"item": "Spinach", "amount": "5 oz", "category": "Vegetables"},
        {"item": "Broccoli", "amount": "1 head", "category": "Vegetables"},
        {"item": "Brown rice", "amount": "2 lbs", "category": "Carbs"},
        {"item": "Almonds", "amount": "1 lb", "category": "Snacks"},
        {"item": "Avocados", "amount": "4 pcs", "category": "Fats"},
    ]
    return {"grocery_list": items}

@app.post("/webhook")
async def webhook(data: dict):
    event = data.get("meta", {}).get("event_name", "")
    if event == "subscription_created":
        print(f"New subscription!")
    return {"received": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
