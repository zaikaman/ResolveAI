# ResolveAI - Debt Freedom Coach

AI-powered debt management and repayment planning system helping Vietnamese users escape debt through personalized plans, real-time adaptation, and behavioral coaching.

## 🎯 Features

- **Quick Debt Assessment**: Upload documents (OCR) or manual entry → AI-optimized repayment plan in <3s
- **Daily Action Tracking**: Personalized daily actions and instant payment logging with progress visualization
- **Adaptive Planning**: Real-time plan recalculation when income/expenses change
- **Smart Spending Insights**: Transaction categorization and spending leak detection
- **Creditor Negotiation Support**: AI-generated scripts and voice simulation practice
- **Milestone Celebrations**: Gamification with badges and achievement tracking

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **Framework**: Vite 5.0+ with React 18.3+ and TypeScript 5.3+
- **Styling**: TailwindCSS with custom design system (8px grid, progress/encouragement colors)
- **State Management**: Zustand
- **Visualizations**: Recharts
- **Authentication**: Supabase Auth
- **Deployment**: Vercel

### Backend (Python + FastAPI)
- **Framework**: FastAPI 0.109+ with Python 3.11+
- **Database**: Supabase PostgreSQL 15+ with RLS
- **AI/LLM**: OpenAI GPT-4o-mini for agents and OCR
- **Optimization**: PuLP for debt repayment optimization
- **Voice AI**: Vapi.ai for negotiation practice
- **Observability**: Opik (Comet ML) for LLM tracing
- **Deployment**: Render/Railway

### Key Technologies
- **Encryption**: Dual-layer (client AES-256 + server Fernet)
- **Multi-Agent System**: Assessment, Optimization, Action, Habit, Negotiation agents
- **Real-time Updates**: Supabase realtime subscriptions

## 📁 Project Structure

```
ResolveAI/
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Route pages
│   │   ├── services/        # API clients
│   │   ├── stores/          # Zustand state
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utilities (encryption, formatting)
│   │   └── types/           # TypeScript types
│   └── package.json
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── routers/         # API endpoints
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Business logic
│   │   ├── agents/          # AI agents
│   │   ├── db/              # Database layer
│   │   │   ├── repositories/# Data access
│   │   │   └── migrations/  # SQL migrations
│   │   └── core/            # Core utilities
│   ├── scripts/             # Utility scripts
│   ├── tests/               # Pytest tests
│   └── requirements.txt
│
└── specs/                    # Design documents
    └── 1-debt-freedom-coach/
        ├── spec.md          # Feature specification
        ├── plan.md          # Technical implementation plan
        ├── data-model.md    # Database schema
        ├── tasks.md         # Task breakdown
        └── contracts/       # API contracts
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.11+
- Supabase account
- OpenAI API key
- Comet ML account (for Opik)

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your Supabase credentials
npm run dev
```

Runs at `http://localhost:5173`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys and Supabase credentials
uvicorn app.main:app --reload
```

Runs at `http://localhost:8000`

### Database Setup

1. Create a Supabase project at https://supabase.com
2. Copy the project URL and service role key to `backend/.env`
3. Run migrations:

```bash
cd backend
python scripts/run_migrations.py
```

This will create all tables, indexes, and RLS policies.

## 🔐 Security

- **Dual-layer encryption**: Client-side AES-256 + server-side Fernet for sensitive financial data
- **Row-level security**: Supabase RLS policies enforce user data isolation
- **JWT authentication**: Secure token-based auth with Supabase
- **HTTPS only**: All production traffic encrypted in transit
- **Document auto-deletion**: Uploaded statements deleted after 24 hours

## 📊 Performance Targets

- Plan generation: <3s for 20 debts
- Payment logging: <500ms UI update
- Document OCR: <10s for Vietnamese statements
- Transaction categorization: <5s for 1000 transactions
- API response: p95 <500ms
- UI interaction: p95 <200ms

## 🧪 Testing

### Frontend
```bash
cd frontend
npm test              # Vitest unit tests
npm run test:e2e      # Playwright E2E tests
```

### Backend
```bash
cd backend
pytest                # All tests
pytest --cov         # With coverage report
```

## 📝 Development Workflow

### Phase 1: Setup & Infrastructure ✅
- [x] Project structure and dependencies
- [x] Database schema and migrations
- [x] Core configuration files

### Phase 2: Foundational Layer (Next)
- [ ] Authentication system
- [ ] Base models and repositories
- [ ] Shared utilities and components

### Phase 3: User Story 1 - MVP
- [ ] Debt input (manual + OCR)
- [ ] AI-optimized repayment plan
- [ ] Timeline visualization

## 🤝 Contributing

1. Tasks are organized by user story in `specs/1-debt-freedom-coach/tasks.md`
2. Each task includes exact file paths and dependencies
3. Run tests before committing
4. Follow code quality standards (TypeScript strict mode, Python Black/Ruff)

## 📄 License

MIT

## 🔗 Links

- [Technical Plan](specs/1-debt-freedom-coach/plan.md)
- [Data Model](specs/1-debt-freedom-coach/data-model.md)
- [Tasks](specs/1-debt-freedom-coach/tasks.md)
- [API Documentation](http://localhost:8000/docs) (when running backend)
