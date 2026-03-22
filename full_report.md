### Deployment Files and Setup Guides

#### 1. requirements.txt — All Python packages needed
```plaintext
Flask==2.2.2
gunicorn==20.1.0
psycopg2-binary==2.9.3
SQLAlchemy==1.4.31
```

#### 2. vercel.json — Vercel deployment config
```json
{
  "version": 2,
  "builds": [
    {
      "src": "./app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    { 
      "src": "/(.*)",
      "dest": "http://localhost:8000" 
    },
    { 
      "src": "/api/(.*)", 
      "dest": "./app.py" 
    }  
  ]
}
```

#### 3. Dockerfile — For Railway backend deployment
```dockerfile
# Use the official lightweight Python image.
FROM python:3.9-slim

# Set environment variables.
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Install dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application source code.
COPY . .

# Expose the port the app runs on
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

#### 4. database_schema.sql — Supabase tables:
```sql
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
```

#### README.md — Complete setup guide:
```markdown
# SmartMealPlan

## Overview
This project provides a comprehensive solution for an AI Meal Planner SaaS application. The app includes a user-friendly landing page, interactive dashboard, and backend API endpoints.

### How to Run Locally
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smartmealplan.git
   cd smartmealplan
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend server locally**
   ```bash
   python app.py
   ```

4. **Access the application**
   Open your browser and go to `http://localhost:5000`.

### How to Deploy

1. **Create a Vercel account** (if you don't have one) and log in.

2. **Deploy to Vercel**:
    - Go to https://vercel.com/new
    - Select the Git repository for this project.
    - Click `Import Project` and follow the prompts.
  
3. **Setup Railway backend deployment**:
   - Create a Docker image of your application (Dockerfile provided).
   - Push it to Docker Hub or any other container registry.

4. **Set up Supabase database**:
   - Visit https://app.supabase.io
   - Create a new project.
   - Run `database_schema.sql` script in the Supabase console to create tables.

5. **Environment Variables**
    - Set environment variables for your backend, frontend, and Vercel project.
    ```json
    {
      "FLASK_APP": "app.py",
      "DATABASE_URL": "<Your_Supabase_Database_URL>",
      // Other necessary keys or secrets
    }
    ```

### Additional Notes

- This is a simplified setup guide. For production environments, consider using CI/CD pipelines and proper secret management.
```

#### How to Deploy the Application (Guide)

1. **Create a Vercel account** (if you don't have one) and log in.

2. **Deploy Backend API with Vercel**
   - Go to https://vercel.com/new
   - Choose `Upload Code` > `Python`
   - Select this GitHub repository.
   - Follow the setup instructions provided by Vercel.
   
3. **Setup Railway for Backend Deployment**
   - Sign up and create a new project on Railway.
   - Use the Dockerfile in your local project to build a container image.
   - Push it to Railway and configure the environment variables.

4. **Set Up Supabase Database**
   - Go to https://app.supabase.io
   - Create a new project.
   - Navigate to `Database` and run `database_schema.sql`.

5. **Environment Variables Setup for Vercel & Flask Application**
    - In your `.env` file, include keys like:
      ```plaintext
      FLASK_ENV=production
      DATABASE_URL=https://your_supabase_url.supabase.co
      ```

6. **Run and Test Locally (Optional)**
   - For local testing without deployment: `pip install -r requirements.txt && python app.py`.
   
### Summary

This setup guide covers the essential steps to deploy a Python Flask application with Vercel for frontend, Railway for backend, Supabase database integration, and environment variable management. Ensure proper secrets handling and CI/CD pipelines are set up in production environments for security and efficiency.

---

The provided files and guides should help you fully configure your AI Meal Planner SaaS project from a local development setup to deployment on cloud services.