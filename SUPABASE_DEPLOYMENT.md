# 🗄️ Supabase Deployment Guide - Co-Living Proforma AI

Complete guide for deploying Co-Living Proforma AI with Supabase integration.

---

## 📋 Table of Contents

1. [Supabase Setup](#supabase-setup)
2. [Database Schema](#database-schema)
3. [Environment Configuration](#environment-configuration)
4. [API Deployment](#api-deployment)
5. [Frontend Integration](#frontend-integration)
6. [Testing](#testing)
7. [Monitoring](#monitoring)

---

## 🚀 Supabase Setup

### Step 1: Access Your Supabase Project

Project URL: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo

### Step 2: Create Database Tables

1. Navigate to **SQL Editor**: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new

2. Copy the SQL from `supabase_schema.sql` file

3. Click **Run** to execute

4. Verify tables created in **Table Editor**

### Step 3: Verify Tables Created

You should see these 5 tables:
- ✅ `coliving_properties` - Property records
- ✅ `coliving_analyses` - Analysis results
- ✅ `coliving_reports` - Generated reports
- ✅ `coliving_conversations` - Chatbot history
- ✅ `coliving_scenarios` - Scenario comparisons

---

## 🗄️ Database Schema

### Table Structure

```sql
-- 5 Core Tables
1. coliving_properties    → Property data & assumptions
2. coliving_analyses      → Financial analysis results
3. coliving_reports       → Excel/PDF/Dashboard outputs
4. coliving_conversations → Chatbot message history
5. coliving_scenarios     → Scenario comparisons

-- Relationships
properties ←─┐
             ├─→ analyses ──→ reports
             └─→ conversations
             └─→ scenarios
```

### Key Features

**JSONB Storage:**
- Flexible schema for assumptions, projections, analysis results
- Efficient querying with GIN indexes
- Future-proof for new metrics

**Row Level Security (RLS):**
- Service role: Full access
- Authenticated users: Read access
- Public: No access

**Automatic Timestamps:**
- `created_at` - Record creation
- `updated_at` - Last modification (properties only)

---

## ⚙️ Environment Configuration

### Step 1: Copy Environment Template

```bash
cp .env.example .env
```

### Step 2: Configure Variables

Edit `.env` file:

```bash
# Get from Supabase Dashboard → Settings → API
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Finding Supabase Keys:**
1. Go to: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/settings/api
2. Copy **URL** → `SUPABASE_URL`
3. Copy **service_role** key → `SUPABASE_SERVICE_KEY`
4. Copy **anon public** key → `SUPABASE_ANON_KEY`

### Step 3: Verify Configuration

```bash
python3 -c "
from coliving_supabase import CoLivingSupabaseClient
client = CoLivingSupabaseClient()
print('✅ Supabase connection successful!')
"
```

---

## 🌐 API Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export SUPABASE_SERVICE_KEY="your-key"

# Run FastAPI server
uvicorn coliving_api:app --reload --port 8000
```

**Access API:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Analytics: http://localhost:8000/api/analytics

### Production Deployment (Cloudflare Workers / Railway / Render)

**Option 1: Cloudflare Workers (Recommended)**

```bash
# Install Wrangler
npm install -g wrangler

# Configure wrangler.toml
cat > wrangler.toml << EOF
name = "coliving-proforma-api"
main = "coliving_api.py"
compatibility_date = "2024-01-01"

[vars]
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"

[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id"
EOF

# Deploy
wrangler deploy
```

**Option 2: Railway**

```bash
# Create railway.json
cat > railway.json << EOF
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn coliving_api:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
EOF

# Deploy to Railway
railway up
```

**Option 3: Render**

1. Connect GitHub repository
2. Create new **Web Service**
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn coliving_api:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

---

## 🎨 Frontend Integration

### Update React Chatbot

Replace the mock API call in `coliving_chatbot_ui.jsx`:

```javascript
// Replace this mock function:
const analyzeCoLivingProperty = async (query, file) => {
  await new Promise(resolve => setTimeout(resolve, 2000));
  return generateMockResponse(query);
};

// With actual API call:
const analyzeCoLivingProperty = async (query, file) => {
  const response = await fetch('https://your-api-url.com/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      user_id: 'user_123',  // Replace with actual user ID
      session_id: sessionId
    })
  });
  
  if (!response.ok) {
    throw new Error('Analysis failed');
  }
  
  return response.json();
};
```

### Deploy Frontend to Cloudflare Pages

```bash
# Build React app
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy build/ --project-name=coliving-proforma-ui

# Configure environment variables in Cloudflare dashboard
# REACT_APP_API_URL=https://your-api-url.com
```

---

## 🧪 Testing

### Test Supabase Integration

```bash
# Test database connection
python3 coliving_supabase.py

# Expected output:
# ✅ Supabase client initialized: https://mocerqjnksmhcjzxrewo.supabase.co
# ✅ Property created: abc-123-def
# ✅ Analysis saved: xyz-456-uvw
# 📊 Platform Analytics: {...}
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Analyze property
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze 20-unit property at $900/bedroom",
    "user_id": "test_user"
  }'

# Get analytics
curl http://localhost:8000/api/analytics
```

### Integration Tests

```python
# test_integration.py
import pytest
from coliving_api import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_analyze_endpoint():
    response = client.post("/api/analyze", json={
        "query": "Analyze 20 units at $900/bedroom",
        "user_id": "test_user"
    })
    assert response.status_code == 200
    assert "property_id" in response.json()
    assert "analysis_id" in response.json()

def test_get_analytics():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    assert "total_properties" in response.json()["analytics"]
```

Run tests:
```bash
pytest test_integration.py -v
```

---

## 📊 Monitoring

### Supabase Dashboard

Monitor database activity:
1. **Table Editor**: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/editor
2. **Database Metrics**: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/database/metrics

### API Monitoring

```python
# Add logging to coliving_api.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# View logs
tail -f app.log
```

### Analytics Queries

```python
from coliving_supabase import CoLivingSupabaseClient

supabase = CoLivingSupabaseClient()

# Get platform analytics
analytics = supabase.get_analytics_summary()
print(f"Total Properties: {analytics['total_properties']}")
print(f"Total Analyses: {analytics['total_analyses']}")
print(f"Avg Cap Rate: {analytics['avg_cap_rate']}%")
print(f"Investment Decisions: {analytics['investment_decisions']}")
```

### Performance Monitoring

```sql
-- Run in Supabase SQL Editor

-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'coliving_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Recent analyses by investment decision
SELECT 
  investment_decision,
  COUNT(*) as count,
  AVG(cap_rate) as avg_cap_rate,
  AVG(dscr) as avg_dscr
FROM coliving_analyses
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY investment_decision;
```

---

## 🔒 Security Checklist

- ✅ **RLS Enabled**: Row Level Security on all tables
- ✅ **Service Role**: Only backend uses service_role key
- ✅ **Anon Key**: Frontend uses anon key (read-only)
- ✅ **Environment Variables**: Never commit `.env` file
- ✅ **CORS**: Configure allowed origins for production
- ✅ **API Rate Limiting**: Implement in production
- ✅ **Input Validation**: Pydantic models validate all inputs

---

## 📝 Troubleshooting

### Issue: "Could not connect to Supabase"

**Solution:**
1. Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `.env`
2. Check network connectivity
3. Verify Supabase project is active

### Issue: "Table does not exist"

**Solution:**
1. Run `supabase_schema.sql` in SQL Editor
2. Verify tables in Table Editor
3. Check for SQL execution errors

### Issue: "RLS policy error"

**Solution:**
1. Ensure using `service_role` key in backend
2. Verify RLS policies created correctly
3. Check user authentication if using `anon` key

---

## 🎉 Deployment Complete!

Your Co-Living Proforma AI is now fully integrated with Supabase:

✅ **Database**: 5 tables with relationships
✅ **API**: FastAPI backend with Supabase client
✅ **Reports**: Excel, PDF, Dashboard stored in database
✅ **Conversations**: Full chatbot history persisted
✅ **Analytics**: Real-time platform metrics

**Next Steps:**
1. Test all API endpoints
2. Deploy frontend to Cloudflare Pages
3. Configure production environment variables
4. Set up monitoring and alerts
5. Enable backups in Supabase dashboard

**Resources:**
- API Docs: http://your-api-url.com/docs
- Supabase Dashboard: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo
- GitHub Repo: https://github.com/breverdbidder/coliving-proforma-ai

---

**Support:**
For issues or questions, create an issue in the GitHub repository or consult the Supabase documentation.
