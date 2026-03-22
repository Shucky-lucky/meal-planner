
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    plan TEXT DEFAULT 'free',
    goal TEXT,
    diet_type TEXT,
    daily_calories INTEGER DEFAULT 1800,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meal_plan_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diet_type TEXT NOT NULL,
    goal TEXT NOT NULL,
    day_number INTEGER,
    breakfast JSONB,
    lunch JSONB,
    dinner JSONB,
    snack JSONB,
    total_calories INTEGER
);

CREATE TABLE IF NOT EXISTS nutrition_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    meal_name TEXT,
    calories INTEGER,
    protein INTEGER DEFAULT 0,
    carbs INTEGER DEFAULT 0,
    fat INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    plan TEXT,
    status TEXT DEFAULT 'active',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meal_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    plan_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
