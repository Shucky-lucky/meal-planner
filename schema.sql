CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE CHECK (POSITION('@' IN email) > 1),
    plan VARCHAR(50),
    goal VARCHAR(50),
    diet_type VARCHAR(50)
);

CREATE TABLE meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    week_start DATE,
    plan_data JSONB
);

CREATE TABLE nutrition_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    meals JSONB,
    calories INTEGER CHECK (calories >= 0)
);

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plan VARCHAR(50),
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled'))
);