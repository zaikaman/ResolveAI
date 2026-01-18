# QuickStart Guide: ResolveAI Development Setup

**Feature**: ResolveAI Debt Freedom Coach  
**Created**: 2026-01-18  
**Estimated Setup Time**: 20-30 minutes

## Prerequisites

**Required Software**:
- **Node.js** 18.x+ and npm 9.x+ (for frontend)
- **Python** 3.11+ and pip (for backend)
- **Git** 2.x+
- **Code Editor**: VS Code recommended (with extensions: Python, ESLint, Prettier, Tailwind CSS IntelliSense)

**Required Accounts** (free tiers sufficient for development):
- **Supabase**: Database, auth, storage (https://supabase.com)
- **OpenAI**: GPT-5-Nano API access (https://platform.openai.com)
- **Opik**: LLM tracing and evaluation (https://www.comet.com/site/products/opik/)
- **Vapi.ai**: Voice simulation (https://vapi.ai) - optional for P5 user story
- **Vercel**: Frontend deployment (https://vercel.com) - optional, for deployment only
- **Render**: Backend deployment (https://render.com) - optional, for deployment only

---

## Quick Setup (Copy-Paste Commands)

### 1. Clone Repository

```bash
git clone https://github.com/your-username/resolveai.git
cd resolveai
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your API keys (see Environment Variables section below)

# Start development server
npm run dev
# Frontend will be available at http://localhost:5173
```

### 3. Backend Setup

```bash
cd ../backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys (see Environment Variables section below)

# Run database migrations (Supabase)
python scripts/run_migrations.py

# Start development server
uvicorn app.main:app --reload --port 8000
# Backend will be available at http://localhost:8000
```

### 4. Verify Setup

Open browser:
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Backend Health Check: http://localhost:8000/health

---

## Detailed Setup Instructions

### Frontend Setup (React + Vite)

**1. Install Dependencies**

```bash
cd frontend
npm install
```

**Dependencies Installed** (from `package.json`):
- `react@18.3`, `react-dom@18.3`: Core React
- `vite@5.0`: Build tool
- `typescript@5.3`: Type safety
- `@supabase/supabase-js@2.39`: Supabase client
- `recharts@2.10`: Charts and visualizations
- `react-dropzone@14.2`: File uploads
- `zustand@4.5`: State management
- `tailwindcss@3.4`: Styling
- `crypto-js@4.2`: Client-side encryption
- `zod@3.22`: Validation schemas
- `axios@1.6`: HTTP client

**2. Environment Variables**

Create `frontend/.env.local`:

```bash
# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key

# Backend API
VITE_API_BASE_URL=http://localhost:8000

# Optional: Opik (frontend events)
VITE_OPIK_API_KEY=your_opik_key
```

**Getting Supabase Credentials**:
1. Go to https://supabase.com/dashboard
2. Create new project (or select existing)
3. Navigate to Settings → API
4. Copy `URL` and `anon public` key

**3. Run Development Server**

```bash
npm run dev
```

**Available Scripts**:
- `npm run dev`: Start dev server (hot reload enabled)
- `npm run build`: Build production bundle
- `npm run preview`: Preview production build
- `npm run lint`: Run ESLint
- `npm run type-check`: Run TypeScript compiler

**4. Project Structure**

```
frontend/
├── src/
│   ├── components/       # React components
│   ├── pages/            # Route pages
│   ├── services/         # API clients
│   ├── stores/           # Zustand state
│   ├── utils/            # Utilities
│   ├── types/            # TypeScript types
│   ├── App.tsx           # Root component
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── package.json
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Vite config
└── tailwind.config.js    # Tailwind config
```

---

### Backend Setup (FastAPI + Python)

**1. Create Virtual Environment**

```bash
cd backend
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

**2. Install Dependencies**

```bash
pip install -r requirements.txt
```

**Dependencies Installed** (from `requirements.txt`):
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
supabase==2.3.0
openai==1.10.0
opik-python==0.2.0
vapi-python==0.1.0
pulp==2.7.0
python-multipart==0.0.6
httpx==0.26.0
cryptography==42.0.0
passlib==1.7.4
python-jose==3.3.0
pytest==7.4.3
pytest-asyncio==0.23.3
pytest-cov==4.1.0
hypothesis==6.92.0
```

**3. Environment Variables**

Create `backend/.env`:

```bash
# Application
APP_NAME=ResolveAI
APP_ENV=development
DEBUG=true

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key  # NOT anon key!
SUPABASE_JWT_SECRET=your_jwt_secret

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-5-nano

# Opik
OPIK_API_KEY=your_opik_key
OPIK_PROJECT_NAME=resolveai-agents

# Vapi (optional for P5)
VAPI_API_KEY=your_vapi_key

# Encryption
APP_ENCRYPTION_KEY=generate_32_byte_key_here  # See Encryption section below

# CORS (for local development)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Getting Service Role Key** (⚠️ Keep Secret!):
1. Supabase Dashboard → Settings → API
2. Copy `service_role` key (NOT `anon` key)
3. This key has admin access - never expose to frontend!

**Getting OpenAI API Key**:
1. https://platform.openai.com/api-keys
2. Create new secret key
3. Note: GPT-5-Nano pricing ~$0.10/1M input tokens

**Getting Opik API Key**:
1. https://www.comet.com/signup
2. Navigate to Opik section
3. Create project → Copy API key

**Generating Encryption Key**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**4. Database Setup (Supabase)**

**Option A: Run Migrations** (recommended):

```bash
python scripts/run_migrations.py
```

This will:
- Create all tables (users, debts, payments, etc.)
- Set up indexes for performance
- Enable row-level security policies
- Seed test data (optional)

**Option B: Manual SQL** (via Supabase Dashboard):

1. Supabase Dashboard → SQL Editor
2. Copy SQL from `backend/app/db/migrations/001_init.sql`
3. Execute
4. Repeat for `002_transactions.sql`, `003_indexes.sql`, `004_rls.sql`

**5. Run Development Server**

```bash
uvicorn app.main:app --reload --port 8000
```

**Available Commands**:
- `uvicorn app.main:app --reload`: Start dev server (auto-reload)
- `pytest`: Run tests
- `pytest --cov`: Run tests with coverage
- `python -m app.main`: Run without uvicorn (for debugging)

**6. Verify API**

Open browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

**Test API**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0"}
```

---

## Testing Setup

### Frontend Tests

```bash
cd frontend

# Unit tests (Vitest)
npm run test

# Coverage
npm run test:coverage

# E2E tests (Playwright)
npx playwright install  # First time only
npm run test:e2e
```

### Backend Tests

```bash
cd backend

# Unit tests
pytest tests/unit/

# Integration tests (requires Supabase test DB)
pytest tests/integration/

# All tests with coverage
pytest --cov=app --cov-report=html
# Open htmlcov/index.html for coverage report
```

**Test Database Setup**:
1. Create separate Supabase project for testing (or use local Supabase)
2. Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `backend/.env.test`
3. Run migrations: `python scripts/run_migrations.py --env test`

---

## Development Workflow

### 1. Start Both Servers

**Terminal 1** (Frontend):
```bash
cd frontend
npm run dev
```

**Terminal 2** (Backend):
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

### 2. Access Applications

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Opik Dashboard**: https://www.comet.com/your-workspace/opik

### 3. Common Development Tasks

**Add New Frontend Component**:
```bash
# Create component file
touch frontend/src/components/debt/DebtCard.tsx

# Component template:
import React from 'react';

interface DebtCardProps {
  debt: Debt;
}

export const DebtCard: React.FC<DebtCardProps> = ({ debt }) => {
  return (
    <div className="p-4 border rounded">
      <h3>{debt.creditor_name}</h3>
      <p>Balance: ${debt.current_balance}</p>
    </div>
  );
};
```

**Add New Backend Endpoint**:
```bash
# Create router file (if not exists)
touch backend/app/routers/my_feature.py

# Endpoint template:
from fastapi import APIRouter, Depends
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("/")
async def get_feature(current_user: User = Depends(get_current_user)):
    return {"message": "Hello from my feature!"}

# Register in app/main.py:
from app.routers import my_feature
app.include_router(my_feature.router)
```

**Add New Agent**:
```bash
# Create agent file
touch backend/app/agents/my_agent.py

# Agent template:
from app.agents.base_agent import BaseAgent
from opik import trace

class MyAgent(BaseAgent):
    @trace(name="my_agent_execute")
    async def execute(self, input_data: dict) -> dict:
        # Agent logic here
        return {"result": "success"}
```

**Run Database Migration**:
```bash
cd backend

# Create new migration file
touch app/db/migrations/005_my_changes.sql

# Write SQL:
-- app/db/migrations/005_my_changes.sql
ALTER TABLE debts ADD COLUMN new_field TEXT;

# Apply migration
python scripts/run_migrations.py --only 005
```

---

## Debugging Tips

### Frontend Debugging

**Chrome DevTools**:
- Network tab: Inspect API calls
- React DevTools: Inspect component state
- Performance tab: Profile rendering

**Vite HMR Not Working**:
```bash
# Clear cache and restart
rm -rf node_modules/.vite
npm run dev
```

**TypeScript Errors**:
```bash
npm run type-check
```

### Backend Debugging

**VS Code Debugger** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

**Print Debugging**:
```python
import logging
logger = logging.getLogger(__name__)

@router.get("/debug")
async def debug_endpoint():
    logger.info("Debug info here")
    return {"status": "ok"}
```

**Opik Tracing Issues**:
```bash
# Check if traces are being sent
import opik
opik.configure(api_key="your_key")
with opik.trace("test"):
    print("This should appear in Opik dashboard")
```

**Database Connection Issues**:
```bash
# Test Supabase connection
python -c "from supabase import create_client; client = create_client('url', 'key'); print(client.table('users').select('*').limit(1).execute())"
```

---

## Environment-Specific Configurations

### Development (Local)

**Frontend** (`frontend/.env.local`):
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**Backend** (`backend/.env`):
```bash
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://localhost:5173
```

### Production (Vercel + Render)

**Frontend** (Vercel Environment Variables):
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_BASE_URL=https://your-backend.onrender.com
```

**Backend** (Render Environment Variables):
```bash
APP_ENV=production
DEBUG=false
CORS_ORIGINS=https://your-app.vercel.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

---

## Common Issues & Solutions

### Issue: "Module not found" errors in frontend

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Supabase connection timeout

**Solution**:
- Check Supabase project is not paused (free tier pauses after inactivity)
- Verify URL and keys are correct
- Check firewall/network settings

### Issue: OpenAI API rate limit

**Solution**:
- Add retry logic with exponential backoff (already in code)
- Reduce concurrent requests
- Upgrade OpenAI plan if needed

### Issue: Opik traces not appearing

**Solution**:
- Verify API key is correct
- Check project name matches
- Flush traces manually: `opik.flush()`
- Check Opik service status: https://status.comet.com

### Issue: CORS errors in browser

**Solution**:
- Add frontend URL to `CORS_ORIGINS` in backend `.env`
- Restart backend server after changing CORS settings

---

## Seeding Test Data

**Seed Development Database**:

```bash
cd backend
python scripts/seed_db.py
```

**What's Seeded**:
- 2 test users (user1@test.com, user2@test.com, password: "password123")
- 5 debts per user (various balances, interest rates)
- 10 payments per user
- 1 active repayment plan per user

**Custom Seed Data**:
```python
# scripts/seed_db.py
async def seed_custom_data():
    # Add your custom test data here
    await create_user(email="custom@test.com", password="password")
    await create_debt(user_id="...", balance=10000, apr=18.5)
```

---

## Next Steps

After completing setup:

1. ✅ **Verify Health Checks**: Both frontend and backend running
2. ✅ **Create Test User**: Sign up via frontend UI
3. ✅ **Test P1 User Story**: Upload fake credit card statement (use test PDF in `docs/samples/`)
4. ✅ **Generate Plan**: Complete onboarding flow, see optimized plan
5. ✅ **Check Opik**: Verify traces appear in Opik dashboard
6. ✅ **Run Tests**: Ensure all tests pass
7. 📖 **Read Architecture Docs**: Review `docs/architecture.md`
8. 🚀 **Start Implementation**: Follow `tasks.md` (generate via `/speckit.tasks`)

---

## Additional Resources

**Documentation**:
- [Architecture Overview](../../../docs/architecture.md)
- [API Contracts](./contracts/api.md)
- [Agent Contracts](./contracts/agents.md)
- [Data Model](./data-model.md)

**External Docs**:
- Supabase: https://supabase.com/docs
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Vite: https://vitejs.dev
- Opik: https://www.comet.com/docs/opik

**Community**:
- Report issues: GitHub Issues
- Discussions: GitHub Discussions
- Vietnamese dev community: (add Discord/Slack link)

---

## Deployment Preview

### Frontend (Vercel)

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy preview
vercel

# Deploy production
vercel --prod
```

### Backend (Render)

1. Connect GitHub repo to Render
2. Create new Web Service
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env`
5. Deploy

---

## Support

**Questions?**
- Check documentation: `docs/`
- Search existing issues: GitHub Issues
- Ask in discussions: GitHub Discussions

**Found a bug?**
- Create issue with reproduction steps
- Include error logs and environment details

Happy coding! 🚀
