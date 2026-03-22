# AI Meal Planner SaaS

Your personal AI nutritionist targeting the USA market.

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment variables
Copy .env.example to .env and fill in your keys:
```
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
LEMONSQUEEZY_API_KEY=your_key
```

### 3. Run locally
```bash
uvicorn app:app --reload
```

Open http://localhost:8000

## Deploy

### Frontend (Vercel)
1. Push to GitHub
2. Connect to Vercel
3. Deploy automatically

### Backend (Railway)
1. Connect GitHub repo to Railway
2. Add environment variables
3. Deploy automatically

## Pricing
- Free: 3-day meal plan
- Pro: $14.99/month — full access
- Family: $24.99/month — up to 5 members
