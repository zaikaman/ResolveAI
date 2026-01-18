# Implementation Plan: ResolveAI Debt Freedom Coach

**Branch**: `main` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-debt-freedom-coach/spec.md`

## Summary

ResolveAI is an intelligent AI companion helping Vietnamese users escape debt through personalized plans, real-time adaptation, and behavioral coaching. The system uses a multi-agent architecture powered by GPT-5-Nano for low-latency reasoning, vision-based OCR for Vietnamese financial documents, and Opik-instrumented agents for hallucination-free financial advice. Frontend is React+Vite (TypeScript) deployed to Vercel, backend is FastAPI (Python) with async operations deployed to Render/Railway, data stored in Supabase PostgreSQL with encryption, and Vapi.ai handles creditor negotiation simulation. MVP focuses on end-to-end flow: upload/enter debts → AI analysis → optimized plan → adaptive tracking → negotiation support, with heavy Opik integration for hackathon scoring (Best Use of Opik bonus).

## Technical Context

**Language/Version**: 
- Frontend: TypeScript 5.3+ with React 18.3+, Vite 5.0+
- Backend: Python 3.11+ with FastAPI 0.109+, asyncio for concurrency

**Primary Dependencies**:
- Frontend: React, Vite, TypeScript, Recharts (visualizations), TailwindCSS (styling), react-dropzone (file uploads), zustand (state management)
- Backend: FastAPI, Pydantic v2 (validation), python-multipart (file uploads), PuLP (linear programming), LangChain 0.1+ (agent orchestration), Opik SDK (tracing), httpx (async HTTP)
- AI: OpenAI Python SDK (GPT-5-Nano API), Vapi Python SDK (voice simulation)
- Database: supabase-py (Python client), @supabase/supabase-js (TypeScript client)

**Storage**: 
- Supabase PostgreSQL 15+ for structured data (users, debts, payments, plans)
- Supabase Storage for temporary uploaded documents (bills, statements) with 24-hour auto-deletion
- Client-side encryption for sensitive fields (balances, income) using AES-256 before transmission

**Testing**: 
- Frontend: Vitest (unit), React Testing Library (component), Playwright (E2E)
- Backend: pytest (unit), pytest-asyncio (async tests), pytest-cov (coverage), hypothesis (property-based testing for financial calculations)

**Target Platform**: 
- Frontend: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+), mobile responsive (iOS Safari, Chrome Mobile)
- Backend: Linux containers (Docker) on Render/Railway, Python 3.11+ runtime
- Database: Supabase cloud (PostgreSQL 15 managed)

**Project Type**: Web application (separate frontend/backend repositories for independent deployment and scaling)

**Performance Goals**: 
- Plan generation: <3s for 20 debts (spec PERF-001)
- Payment logging: <500ms UI update (spec PERF-002)
- Document OCR: <10s for Vietnamese statements (spec PERF-003)
- Transaction categorization: <5s for 1000 transactions (spec PERF-004)
- API throughput: 100 req/s per backend instance (spec PERF-010)

**Constraints**: 
- API response: p95 <500ms (constitution + spec)
- UI interaction: p95 <200ms (constitution + spec)
- Memory: Frontend <200MB, backend <512MB (constitution)
- Database queries: <200ms p95 with proper indexes (spec PERF-007)
- Startup: Interactive UI in <2s on 4G (spec PERF-006)

**Scale/Scope**: 
- MVP target: 100-500 concurrent users during hackathon demo
- Design for 10x growth: 1000-5000 users (constitution scalability requirement)
- Data volume: ~10-50 debts per user, 1000-5000 transactions per user, 100-500 payments per user over lifetime
- Agent calls: ~5-20 LLM calls per user session (onboarding, plan generation, adaptations)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Code Quality Excellence** (Principle I):
- [x] Feature follows idiomatic patterns for chosen language/framework
  - TypeScript with strict mode, React functional components with hooks, FastAPI async/await patterns, Pydantic v2 models
- [x] Error handling strategy documented with explicit failure modes
  - Frontend: Error boundaries, toast notifications, fallback UI states
  - Backend: FastAPI exception handlers, typed errors (UserError, SystemError, ExternalError per CQ-003), Opik error tracking
  - AI: Retry logic with exponential backoff, graceful degradation (fallback to templates if LLM fails)
- [x] Public API documentation requirements identified
  - OpenAPI/Swagger auto-generated from FastAPI (per CQ-004)
  - Frontend API client generated from OpenAPI schema
  - Agent contracts documented in code (inputs/outputs, side effects)
- [x] Code review criteria specific to this feature defined
  - Financial calculations reviewed by 2 people (CQ-001 test coverage requirement)
  - Security-sensitive code (auth, encryption, PII) requires security review
  - Agent prompts reviewed for hallucination risk (Opik LLM-as-judge validation)

**User Experience Consistency** (Principle II):
- [x] UI patterns align with existing application conventions (if applicable)
  - Mobile-first design (spec UX-001), consistent component library (shadcn/ui or similar)
  - Design system with 8px grid, consistent spacing, color palette (green/progress, warm/encouragement per spec UX-007)
- [x] Accessibility requirements (WCAG 2.1 AA) documented for user-facing features
  - Semantic HTML, ARIA labels, keyboard navigation, screen reader testing (spec UX-002)
  - Color contrast ratio ≥4.5:1, focus indicators, skip links
- [x] Responsive design requirements specified for multi-device support
  - Mobile (320px+), tablet (768px+), desktop (1024px+) breakpoints (spec UX-003)
  - Touch targets ≥44x44px, swipe gestures for mobile
- [x] User feedback mechanisms (loading states, errors, success) defined
  - Loading skeletons, progress bars, spinners (spec UX-004)
  - Toast notifications (success/error/info), modal confirmations, inline validation
  - Celebratory animations with skip option (spec UX-010)
- [x] Error message strategy ensures human-readable, actionable content
  - Plain language, empathetic tone, actionable next steps (spec UX-005, UX-006)
  - Vietnamese localization for all user-facing text

**Performance by Design** (Principle III):
- [x] Response time targets specified (API: <500ms p95, UI: <200ms p95)
  - Detailed in spec PERF-001 through PERF-010
  - Monitored via Opik tracing (API latency), browser performance API (UI)
- [x] Database query patterns reviewed for N+1 issues and indexing strategy
  - Indexes on: users(id), debts(user_id, due_date), payments(user_id, date), transactions(user_id, category)
  - Batch queries (get user + debts + payments in single round-trip via Supabase RPC)
  - Connection pooling (asyncpg, 10-20 connections per backend instance)
- [x] Memory and resource budgets defined
  - Frontend: <200MB (constitution), tracked via Chrome DevTools
  - Backend: <512MB per worker (constitution), 4 workers per instance = 2GB total
  - Document uploads: <10MB per file, in-memory processing only
- [x] Performance monitoring instrumentation planned for critical paths
  - Opik tracing for all agent calls (latency, token usage, cost)
  - FastAPI middleware for API timing, Supabase slow query log
  - Frontend: Web Vitals (LCP, FID, CLS), custom metrics for plan generation time
- [x] Scalability to 10x load considered in design
  - Horizontal scaling: Backend stateless (scale to 10+ instances)
  - Database: Supabase scales automatically, read replicas if needed
  - Rate limiting: 100 req/min per user (prevents abuse)
  - Caching: Redis for session data, HTTP cache headers for static assets

**Violations**: None

## Project Structure

### Documentation (this feature)

```text
specs/1-debt-freedom-coach/
├── plan.md              # This file (technical implementation plan)
├── research.md          # Phase 0: Technology decisions and trade-offs
├── data-model.md        # Phase 1: Database schema and entity relationships
├── quickstart.md        # Phase 1: Setup and development guide
├── contracts/           # Phase 1: API contracts (OpenAPI specs)
│   ├── api.yaml         # FastAPI endpoint definitions
│   └── agents.md        # Agent input/output contracts
└── tasks.md             # Phase 2: Implementation task breakdown (NOT in this plan)
```

### Source Code (repository root)

```text
resolveai/                          # Repository root
├── frontend/                       # React + Vite frontend (deployed to Vercel)
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── common/             # Reusable UI (Button, Input, Card, etc.)
│   │   │   ├── debt/               # Debt input forms, debt list, debt card
│   │   │   ├── plan/               # Plan visualization, timeline, payment schedule
│   │   │   ├── progress/           # Progress dashboard, charts, milestones
│   │   │   ├── negotiation/        # Negotiation scripts, Vapi voice UI
│   │   │   ├── upload/             # File dropzone, OCR feedback, manual entry fallback
│   │   │   └── layout/             # App shell, nav, sidebar, mobile menu
│   │   ├── pages/                  # Route pages
│   │   │   ├── Home.tsx            # Landing/onboarding
│   │   │   ├── Dashboard.tsx       # Daily actions + progress overview
│   │   │   ├── Debts.tsx           # Debt management (add/edit/delete)
│   │   │   ├── Plan.tsx            # Full plan view with timeline
│   │   │   ├── Insights.tsx        # Spending analysis (if bank connected)
│   │   │   ├── Negotiate.tsx       # Creditor negotiation tools
│   │   │   └── Settings.tsx        # User preferences, auth, export
│   │   ├── services/               # API clients and business logic
│   │   │   ├── api.ts              # Axios/fetch wrapper, auth interceptor
│   │   │   ├── debtService.ts      # Debt CRUD operations
│   │   │   ├── planService.ts      # Plan generation, recalculation
│   │   │   ├── paymentService.ts   # Payment logging
│   │   │   ├── uploadService.ts    # Document upload, OCR status polling
│   │   │   ├── vapiService.ts      # Vapi voice simulation integration
│   │   │   └── supabaseClient.ts   # Supabase client singleton
│   │   ├── stores/                 # Zustand state management
│   │   │   ├── authStore.ts        # User session, login/logout
│   │   │   ├── debtStore.ts        # Debts state
│   │   │   ├── planStore.ts        # Active plan state
│   │   │   └── uiStore.ts          # Modals, toasts, loading states
│   │   ├── hooks/                  # Custom React hooks
│   │   │   ├── useDebts.ts         # Fetch/mutate debts
│   │   │   ├── usePlan.ts          # Fetch/recalculate plan
│   │   │   ├── useAuth.ts          # Auth state and actions
│   │   │   └── useOpik.ts          # Client-side Opik events (optional)
│   │   ├── utils/                  # Utility functions
│   │   │   ├── formatting.ts       # Currency, date, percentage formatters
│   │   │   ├── validation.ts       # Input validation schemas (Zod)
│   │   │   ├── encryption.ts       # Client-side AES encryption for PII
│   │   │   └── constants.ts        # App constants, API URLs
│   │   ├── types/                  # TypeScript type definitions
│   │   │   ├── debt.ts             # Debt, DebtType enums
│   │   │   ├── plan.ts             # RepaymentPlan, PaymentSchedule
│   │   │   ├── user.ts             # User, UserProfile
│   │   │   └── api.ts              # API request/response types
│   │   ├── App.tsx                 # Root component, routing
│   │   ├── main.tsx                # Entry point, Supabase init
│   │   └── index.css               # Global styles (TailwindCSS)
│   ├── public/                     # Static assets
│   ├── tests/                      # Frontend tests
│   │   ├── unit/                   # Component unit tests (Vitest)
│   │   ├── integration/            # Integration tests (API mocking)
│   │   └── e2e/                    # End-to-end tests (Playwright)
│   ├── package.json                # Dependencies, scripts
│   ├── tsconfig.json               # TypeScript config (strict mode)
│   ├── vite.config.ts              # Vite config, plugins
│   ├── tailwind.config.js          # TailwindCSS config
│   ├── .env.example                # Environment variables template
│   └── vercel.json                 # Vercel deployment config
│
├── backend/                        # FastAPI backend (deployed to Render/Railway)
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry, CORS, middleware
│   │   ├── config.py               # Settings (Pydantic BaseSettings), env vars
│   │   ├── dependencies.py         # FastAPI dependencies (auth, DB, Opik)
│   │   ├── models/                 # Pydantic models (request/response schemas)
│   │   │   ├── user.py             # UserCreate, UserResponse, UserProfile
│   │   │   ├── debt.py             # DebtCreate, DebtUpdate, DebtResponse
│   │   │   ├── plan.py             # PlanRequest, PlanResponse, PlanRecalculation
│   │   │   ├── payment.py          # PaymentCreate, PaymentResponse
│   │   │   ├── transaction.py      # Transaction, SpendingInsight
│   │   │   ├── negotiation.py      # NegotiationScriptRequest, VapiSession
│   │   │   └── upload.py           # UploadResponse, OCRResult
│   │   ├── routers/                # FastAPI routers (API endpoints)
│   │   │   ├── auth.py             # /auth/signup, /auth/login, /auth/logout
│   │   │   ├── debts.py            # /debts CRUD endpoints
│   │   │   ├── plans.py            # /plans/generate, /plans/recalculate, /plans/simulate
│   │   │   ├── payments.py         # /payments (log, list, stats)
│   │   │   ├── uploads.py          # /uploads (document upload, OCR trigger)
│   │   │   ├── insights.py         # /insights (spending analysis, leaks)
│   │   │   ├── negotiation.py      # /negotiation/script, /negotiation/vapi-session
│   │   │   └── health.py           # /health, /readiness (monitoring)
│   │   ├── services/               # Business logic services
│   │   │   ├── debt_service.py     # Debt CRUD, validation
│   │   │   ├── plan_service.py     # Plan generation orchestrator (calls agents)
│   │   │   ├── optimization_service.py  # PuLP linear programming for debt optimization
│   │   │   ├── payment_service.py  # Payment logging, balance updates, recalculation trigger
│   │   │   ├── ocr_service.py      # GPT-5-Nano vision API for Vietnamese document parsing
│   │   │   ├── categorization_service.py  # Transaction categorization (GPT-5-Nano)
│   │   │   ├── negotiation_service.py  # Script generation (GPT-5-Nano), Vapi integration
│   │   │   ├── supabase_service.py # Supabase client wrapper, CRUD helpers
│   │   │   └── encryption_service.py  # Server-side encryption/decryption (AES-256)
│   │   ├── agents/                 # Multi-agent system (LangChain/CrewAI patterns)
│   │   │   ├── base_agent.py       # BaseAgent class with Opik tracing decorator
│   │   │   ├── assessment_agent.py # Analyze debts, validate inputs, detect unsustainable situations
│   │   │   ├── optimization_agent.py  # Call optimization_service, select avalanche/snowball
│   │   │   ├── action_agent.py     # Generate daily actions, reminders, next steps
│   │   │   ├── habit_agent.py      # Nudge generation, milestone detection, celebration triggers
│   │   │   ├── negotiation_agent.py  # Generate negotiation scripts with GPT-5-Nano
│   │   │   └── orchestrator.py     # ReAct-style loop, agent coordination, error recovery
│   │   ├── core/                   # Core utilities
│   │   │   ├── opik_tracing.py     # Opik SDK wrappers, trace decorators, LLM-as-judge
│   │   │   ├── openai_client.py    # OpenAI client singleton (GPT-5-Nano)
│   │   │   ├── vapi_client.py      # Vapi client singleton
│   │   │   ├── errors.py           # Custom exception classes (UserError, SystemError, etc.)
│   │   │   ├── security.py         # JWT validation, password hashing (passlib)
│   │   │   └── validators.py       # Input validation helpers (balance >0, APR 0-50%, etc.)
│   │   └── db/                     # Database access layer
│   │       ├── supabase.py         # Supabase client init, connection pool
│   │       ├── models.py           # Supabase table models (dataclasses or SQLAlchemy)
│   │       ├── repositories/       # Repository pattern for data access
│   │       │   ├── user_repo.py    # User CRUD
│   │       │   ├── debt_repo.py    # Debt CRUD with encryption
│   │       │   ├── plan_repo.py    # Plan CRUD
│   │       │   ├── payment_repo.py # Payment CRUD
│   │       │   └── transaction_repo.py  # Transaction CRUD
│   │       └── migrations/         # Supabase SQL migrations (manual or via CLI)
│   │           ├── 001_init.sql    # Initial schema (users, debts, plans, payments)
│   │           ├── 002_transactions.sql  # Transactions table
│   │           └── 003_indexes.sql # Performance indexes
│   ├── tests/                      # Backend tests
│   │   ├── unit/                   # Unit tests (services, agents)
│   │   │   ├── test_optimization_service.py  # PuLP calculations, edge cases
│   │   │   ├── test_assessment_agent.py  # Unsustainable debt detection
│   │   │   └── test_encryption.py  # Encryption/decryption correctness
│   │   ├── integration/            # Integration tests (API endpoints, DB)
│   │   │   ├── test_debts_api.py   # CRUD endpoints
│   │   │   ├── test_plans_api.py   # Plan generation E2E
│   │   │   └── test_payments_api.py  # Payment logging flow
│   │   └── fixtures/               # Test fixtures (mock data, Supabase test DB)
│   ├── requirements.txt            # Python dependencies
│   ├── pyproject.toml              # Poetry/pip config, tool settings (black, ruff, mypy)
│   ├── pytest.ini                  # Pytest config (coverage, markers)
│   ├── Dockerfile                  # Docker image for deployment
│   ├── .env.example                # Environment variables template
│   └── render.yaml                 # Render deployment config (or railway.json)
│
├── docs/                           # Additional documentation
│   ├── architecture.md             # High-level architecture diagram, data flow
│   ├── opik-integration.md         # Opik setup, metrics, dashboards
│   ├── security.md                 # Security practices, encryption, compliance
│   ├── deployment.md               # Deployment steps (Vercel, Render, Supabase)
│   └── api-examples.md             # cURL examples for API endpoints
│
├── scripts/                        # Utility scripts
│   ├── setup-dev.sh                # Local dev environment setup
│   ├── seed-db.py                  # Seed test data into Supabase
│   └── run-opik-eval.py            # Run Opik LLM-as-judge evaluations
│
├── .github/                        # GitHub workflows (CI/CD)
│   └── workflows/
│       ├── frontend-ci.yml         # Frontend tests, linting, build
│       ├── backend-ci.yml          # Backend tests, linting, type checking
│       └── deploy.yml              # Deploy to Vercel + Render on merge to main
│
├── README.md                       # Project overview, setup instructions
├── LICENSE                         # License (MIT or similar)
└── .gitignore                      # Ignore node_modules, .env, __pycache__, etc.
```

**Structure Decision**: Web application with separate frontend/backend folders. This supports:
- Independent deployment (Vercel for frontend, Render for backend)
- Separate CI/CD pipelines (faster feedback)
- Clear separation of concerns (UI vs business logic)
- Team parallelization (frontend/backend can be developed concurrently)
- Independent scaling (scale backend separately from static frontend assets)

Trade-off: Slightly more complex setup than monorepo, but benefits outweigh for this architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All architecture decisions align with constitution principles.

## High-Level Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER (Vietnamese Market)                     │
│              (Mobile Browser, Desktop Browser, Tablet)               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   FRONTEND (Vercel)     │
                    │   React + Vite + TS     │
                    │   - UI Components       │
                    │   - Charts (Recharts)   │
                    │   - File Upload         │
                    │   - Client Encryption   │
                    └────────────┬────────────┘
                                 │ HTTPS (TLS 1.3)
                                 │ JWT Auth
                    ┌────────────▼────────────┐
                    │  BACKEND (Render/Railway)│
                    │   FastAPI (Python)      │
                    │   - REST API Endpoints  │
                    │   - Agent Orchestrator  │
                    │   - Business Logic      │
                    └─────┬──────┬──────┬─────┘
                          │      │      │
        ┌─────────────────┘      │      └─────────────────┐
        │                        │                        │
┌───────▼────────┐    ┌─────────▼──────────┐    ┌────────▼────────┐
│  SUPABASE      │    │  EXTERNAL SERVICES │    │   OPIK (Comet)  │
│  - PostgreSQL  │    │  ┌───────────────┐ │    │  - LLM Tracing  │
│  - Auth (JWT)  │    │  │ OpenAI API    │ │    │  - Evaluation   │
│  - Storage     │    │  │ (GPT-5-Nano)  │ │    │  - Dashboards   │
│  - Row-Level   │    │  └───────────────┘ │    │  - A/B Testing  │
│    Security    │    │  ┌───────────────┐ │    └─────────────────┘
└────────────────┘    │  │ Vapi.ai       │ │
                      │  │ (Voice Sim)   │ │
                      │  └───────────────┘ │
                      └────────────────────┘
```

### Data Flow Examples

**1. New User Onboarding Flow**
```
User → Upload Vietnamese Statement (PDF)
  → Frontend: Drag-drop component → Upload to Supabase Storage
  → Backend: /uploads endpoint triggered
    → OCR Service: GPT-5-Nano vision API (native Vietnamese support)
      → Extract: balance, APR, minimum payment, due date
      → Opik traces: prompt, response, latency, accuracy score
    → Assessment Agent: Validate extracted data, detect unsustainable debt
      → Opik LLM-as-judge: Check for hallucinations, validate math
    → Store encrypted debts in Supabase (AES-256)
  → Frontend: Display extracted data + manual correction UI
    → User confirms/corrects → Save
  → Backend: /plans/generate endpoint
    → Optimization Agent: Call PuLP for debt avalanche/snowball
      → Opik traces: algorithm choice, optimization result, total interest saved
    → Habit Agent: Generate first 7 days of actions
  → Frontend: Show plan timeline, first actions, celebration animation
```

**2. Daily Payment Logging Flow**
```
User → Open app → See "Pay $250 to Chase today"
  → User makes payment externally (bank app)
  → User logs payment in ResolveAI
    → Frontend: /payments POST with amount, debt_id, date
    → Backend: Payment Service
      → Update debt balance (with encryption)
      → Recalculate remaining plan (fast, <500ms)
      → Action Agent: Generate next actions
      → Habit Agent: Check milestone (25%? 50%? Streak?)
        → If milestone: Trigger celebration
        → Opik traces: Milestone detection logic, personalization quality
    → Frontend: Show updated balance, new debt-free date, celebration if applicable
    → Push notification scheduled for tomorrow (via Supabase Edge Functions or backend cron)
```

**3. Income Change & Real-Time Adaptation**
```
User → Update income from $4000 to $4500
  → Frontend: /plans/recalculate POST with new income
  → Backend: Optimization Agent re-runs with new constraints
    → PuLP recalculates optimal allocation
    → Action Agent: Generate options (Aggressive vs Balanced)
    → Opik traces: Adaptation quality, user preference prediction
  → Frontend: Show side-by-side comparison
    → User selects "Aggressive" → Save preference
  → Backend: Update plan, regenerate actions
  → Frontend: Show new timeline with 5 months saved
```

### Multi-Agent Architecture

**Agent Coordination (ReAct Pattern)**
```python
# Simplified orchestrator logic
async def generate_plan_with_agents(user_id: str, debts: list[Debt]):
    with opik.trace("generate_plan"):
        # 1. Assessment Agent (Thought: Analyze input)
        assessment = await assessment_agent.analyze(debts)
        if assessment.unsustainable:
            return UnsustainableResponse(...)
        
        # 2. Optimization Agent (Action: Calculate optimal plan)
        plan = await optimization_agent.optimize(
            debts=debts,
            income=assessment.available_income,
            strategy=assessment.recommended_strategy  # avalanche or snowball
        )
        
        # 3. Action Agent (Action: Generate daily steps)
        actions = await action_agent.generate_first_week(plan)
        
        # 4. Habit Agent (Thought: Identify early wins)
        nudges = await habit_agent.suggest_initial_nudges(user_id, plan)
        
        return PlanResponse(plan=plan, actions=actions, nudges=nudges)
```

**Agent Responsibilities**
- **AssessmentAgent**: Validate inputs, detect impossible scenarios (income < minimum payments), calculate available payment capacity, recommend strategy (avalanche for max savings, snowball for quick wins)
- **OptimizationAgent**: Call PuLP linear programming, minimize total interest (avalanche) or maximize psychological wins (snowball), generate payment schedule, calculate projections
- **ActionAgent**: Generate daily/weekly actions based on payment schedule, personalize language (encouraging, empathetic), create reminders
- **HabitAgent**: Detect milestones (25%, 50%, 75%, first payoff, 3-month streak), trigger celebrations, suggest nudges ("You're doing great! Keep momentum")
- **NegotiationAgent**: Generate personalized scripts using user's payment history, account age, competitive rate research, Vapi voice simulation setup

All agents wrapped with `@opik.trace()` for observability.

## Technology Research & Decisions

### Frontend Stack Decisions

**React + Vite (TypeScript)**
- **Decision**: Use React 18.3+ with Vite 5.0+ build tool, TypeScript strict mode
- **Rationale**: 
  - Vite provides fastest dev experience (HMR <50ms) and optimal production builds
  - React's ecosystem is mature, abundant Vietnamese developer talent, excellent mobile support
  - TypeScript prevents runtime errors (especially critical for financial calculations)
  - Aligns with spec PERF-006 (interactive UI in 2s) via Vite's code splitting and lazy loading
- **Alternatives Considered**:
  - Next.js: Overkill for SPA, SSR not needed (client-side state heavy)
  - Svelte: Smaller bundle but less ecosystem support, harder to find Vietnamese developers
  - Vue: Good option but React's job market larger in Vietnam

**State Management: Zustand**
- **Decision**: Zustand for global state (auth, debts, plan)
- **Rationale**: 
  - Simpler than Redux (less boilerplate), better than Context API (performance)
  - TypeScript support excellent, small bundle size (<1KB)
  - Aligns with constitution principle (minimal dependencies, idiomatic patterns)
- **Alternatives Considered**:
  - Redux Toolkit: Too heavy for MVP, unnecessary complexity
  - Jotai/Recoil: Atomic state overkill for this use case
  - TanStack Query: Good for server state but need global client state too (combine both)

**Visualization: Recharts**
- **Decision**: Recharts for debt timeline, progress charts, payment breakdowns
- **Rationale**: 
  - Declarative React API, responsive by default, accessible
  - Supports line charts (debt over time), bar charts (monthly payments), pie charts (debt by type)
  - 30KB gzipped, reasonable for MVP
- **Alternatives Considered**:
  - Chart.js: Imperative API (harder to integrate), React wrapper adds overhead
  - D3.js: Too complex for MVP, steep learning curve
  - Visx: More flexible but requires more code for basic charts

**Styling: TailwindCSS**
- **Decision**: TailwindCSS with custom config for design system
- **Rationale**: 
  - Utility-first, rapid development, excellent mobile-first defaults
  - Tree-shaking removes unused styles (small production bundle)
  - Consistent spacing/colors (8px grid, color palette per spec UX-007)
- **Alternatives Considered**:
  - CSS Modules: More code, harder to maintain consistency
  - Styled Components: Runtime overhead, unnecessary for this project
  - Vanilla CSS: Too low-level, hard to maintain design system

### Backend Stack Decisions

**FastAPI (Python 3.11+)**
- **Decision**: FastAPI with async/await, Pydantic v2 models
- **Rationale**: 
  - Best Python framework for async performance (meets spec PERF-001-010)
  - Auto-generates OpenAPI docs (meets CQ-004)
  - Pydantic v2 validation is fast (meets constitution code quality standards)
  - Python's AI ecosystem (LangChain, OpenAI SDK, Opik) is strongest
  - Vietnamese developer familiarity (Python very popular in Vietnam)
- **Alternatives Considered**:
  - Django: Too heavy, ORM overhead, slower than FastAPI async
  - Flask: No native async, less modern patterns
  - Node.js (Express/Fastify): Good but Python's AI libraries superior

**Optimization: PuLP Linear Programming**
- **Decision**: PuLP library for debt optimization calculations
- **Rationale**: 
  - Proven linear programming solver for finance (minimizes interest paid)
  - Handles constraints (minimum payments, available income) mathematically
  - Fast (<100ms for 20 debts), deterministic results
  - Aligns with spec FR-005, FR-024 (avalanche/snowball with optimal math)
- **Alternatives Considered**:
  - Custom greedy algorithm: Simpler but suboptimal (may miss 5-10% savings)
  - scipy.optimize: Lower-level, more code, PuLP abstracts well
  - External API: Latency, cost, unnecessary dependency

**Agent Orchestration: LangChain Patterns**
- **Decision**: Use LangChain Agent patterns (without full LangChain framework)
- **Rationale**: 
  - ReAct pattern fits multi-agent system (assessment → optimization → action)
  - Opik integrates natively with LangChain tracing
  - Cherry-pick patterns (don't import full LangChain, too heavy), implement custom BaseAgent
- **Alternatives Considered**:
  - CrewAI: Too opinionated, harder to customize for debt domain
  - Full LangChain: Too many dependencies (bloat), slower imports
  - Custom from scratch: Reinventing wheel, Opik integration harder

### AI/LLM Stack Decisions

**GPT-5-Nano (OpenAI API)**
- **Decision**: GPT-5-Nano as primary LLM for all agents
- **Rationale**: 
  - **Latency**: p50 ~200ms (meets spec PERF requirements)
  - **Cost**: ~10x cheaper than GPT-4 ($0.10/1M input tokens vs $1/1M), critical for hackathon budget
  - **Vision**: Native Vietnamese OCR (better than AWS Textract for Vietnamese statements, no training needed)
  - **Tool Calling**: Excellent structured output for agent function calls (Pydantic models)
  - **Quality**: Sufficient for debt advice (not creative writing), with Opik LLM-as-judge to catch hallucinations
- **Alternatives Considered**:
  - GPT-4o: Better quality but 10x cost, unnecessary latency for MVP
  - Claude 3 Haiku: Similar cost but worse Vietnamese support, less established vision API
  - Gemini Flash: Competitive but less mature tool-calling, OpenAI ecosystem stronger
  - Local models (Llama 3): Inference overhead, need GPU, harder deployment

**OCR Strategy: GPT-5-Nano Vision**
- **Decision**: Use GPT-5-Nano vision API directly for Vietnamese document parsing
- **Rationale**: 
  - Intelligent extraction (understands context, not just OCR text)
  - Handles Vietnamese banks' varied statement formats (VCB, Vietcombank, Techcombank, etc.)
  - Single API call (no separate OCR → NLP pipeline)
  - Meets spec PERF-003 (<10s) and SEC-006 (delete after parsing)
- **Alternatives Considered**:
  - Google Vision API: Pure OCR, need separate NLP to extract fields, 2x API calls
  - AWS Textract: English-optimized, worse Vietnamese accuracy, higher cost
  - Azure Form Recognizer: Requires training custom models, slow iteration

**Vapi.ai Voice Integration**
- **Decision**: Vapi.ai for creditor negotiation simulation (spec FR-016)
- **Rationale**: 
  - Out-of-box voice AI with realistic conversations (no custom voice pipeline)
  - Sandbox mode for demo (no real phone calls, meets hackathon requirements)
  - Provides feedback loop (practice → score → improve)
  - Low latency (<1s response time), good UX
- **Alternatives Considered**:
  - OpenAI Whisper + TTS: DIY approach, more code, harder to get realistic conversation flow
  - ElevenLabs: Good TTS but no conversation management (need custom logic)
  - Twilio: Real phone calls (overkill, compliance issues for hackathon)

### Observability: Opik Integration

**Opik (Comet) for LLM Tracing**
- **Decision**: Deep Opik integration throughout agent system
- **Rationale**: 
  - **Hackathon Bonus**: Best Use of Opik = $5,000 prize (strategic)
  - **LLM-as-Judge**: Validate agent outputs (detect hallucinations in financial advice), critical for trustworthiness
  - **Prompt Engineering**: A/B test prompts (e.g., empathetic vs direct tone), optimize for user engagement
  - **Cost Tracking**: Monitor token usage per user session, stay within budget
  - **Latency Analysis**: Identify slow agents, optimize critical paths
  - **Debugging**: Trace full conversation (user input → agent chain → final output) for error analysis
- **Implementation Strategy**:
  - Wrap all agent calls with `@opik.trace()` decorator
  - Log inputs, outputs, latency, token count, cost for every LLM call
  - Custom metrics: plan_quality_score (did user accept plan?), advice_accuracy (LLM-as-judge), user_satisfaction (NPS-style feedback)
  - Dashboards: Real-time agent performance, hallucination rate, cost per user, latency percentiles
- **Alternatives Considered**:
  - LangSmith: Good but less hackathon visibility, Opik has bonus prize
  - Weights & Biases: ML focus, less LLM-specific features
  - Custom logging: Reinventing wheel, no LLM-as-judge built-in

### Database & Auth: Supabase

**Supabase (PostgreSQL + Auth + Storage)**
- **Decision**: Supabase for all data needs (database, auth, file storage)
- **Rationale**: 
  - **Unified Platform**: Single service reduces complexity (vs separate DB, Auth0, S3)
  - **PostgreSQL**: Strong ACID guarantees for financial data (critical for correctness), excellent indexing
  - **Row-Level Security**: Built-in isolation (user A cannot access user B's debts), meets SEC-005
  - **Real-time Subscriptions**: Potential for live plan updates (nice-to-have, not MVP critical)
  - **Vietnamese Market**: Supabase popular in Vietnam, good docs in Vietnamese community
  - **Generous Free Tier**: 500MB DB, 1GB storage, 50K monthly active users (sufficient for hackathon)
- **Encryption Strategy**:
  - Client-side: Encrypt balances, income before sending to backend (AES-256, user-controlled key derived from password)
  - Server-side: Re-encrypt with separate key for storage (defense in depth)
  - Meets SEC-001 (encryption at rest), SEC-002 (TLS 1.3 in transit)
- **Alternatives Considered**:
  - Firebase: Good but vendor lock-in, less SQL flexibility, worse for complex queries
  - PlanetScale: MySQL (less robust for financial data), no built-in auth/storage
  - Self-hosted PostgreSQL: Infrastructure overhead, slower MVP, no free tier

### Deployment Strategy

**Frontend: Vercel**
- **Decision**: Deploy React app to Vercel
- **Rationale**: 
  - Zero-config deployment (git push → instant preview), aligns with "rapid development" priority
  - Global CDN (low latency for Vietnamese users via Singapore/Tokyo PoPs)
  - Automatic HTTPS, excellent DX
  - Generous free tier (100GB bandwidth/month, 100 deployments/day)
- **Alternatives Considered**:
  - Netlify: Similar but Vercel's Next.js heritage gives better Vite support
  - GitHub Pages: Static only, no environment variables, less features
  - AWS S3 + CloudFront: Manual setup, slower iteration

**Backend: Render (or Railway)**
- **Decision**: Deploy FastAPI to Render (primary) or Railway (backup)
- **Rationale**: 
  - Render: Free tier (750 hours/month), Dockerfile support, PostgreSQL add-on (if needed)
  - Railway: Similar but better UX, $5/month credit, faster cold starts
  - Both: Auto-deploy from GitHub, HTTPS included, environment variables easy
  - Meets spec requirements (Linux containers, Python 3.11+, 512MB memory)
- **Alternatives Considered**:
  - AWS EC2: Manual setup, overkill for MVP, higher cost
  - Google Cloud Run: Good but cold starts slower than Render/Railway
  - Heroku: More expensive, less modern DX

**Trade-Offs: Monorepo vs Separate Repos**
- **Decision**: Single monorepo (chosen structure above)
- **Rationale**: 
  - Simpler for hackathon (single clone, single PR, easier for judges)
  - Shared types (export from backend, import in frontend via codegen)
  - Unified CI/CD (test both in one workflow, deploy together)
- **Alternatives**: Separate repos cleaner for production but adds complexity for 2-week hackathon

## Phase 0: Research & Setup (Completed Above)

Research phase completed inline in "Technology Research & Decisions" section. Key decisions documented with rationale, alternatives, and trade-offs.

## Phase 1: Design & Contracts

(To be completed in separate files as part of `/speckit.plan` workflow)

**Deliverables**:
1. `data-model.md`: Database schema (Supabase tables), entity relationships, encryption strategy, indexes
2. `contracts/api.yaml`: OpenAPI specification for all FastAPI endpoints (generated from FastAPI auto-docs)
3. `contracts/agents.md`: Agent input/output contracts, ReAct loop documentation, Opik trace structure
4. `quickstart.md`: Local development setup, environment variables, running frontend/backend, seeding test data

**Agent Context Update**: After Phase 1, run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot` to add technology choices (React, FastAPI, GPT-5-Nano, Opik) to Copilot context.

## Next Steps

1. **Complete Phase 1 Design**: Generate `data-model.md`, `contracts/`, and `quickstart.md` (via `/speckit.plan` continued execution)
2. **Re-run Constitution Check**: Validate design against principles (especially security for SEC-001-008)
3. **Generate Tasks**: Run `/speckit.tasks` to break down implementation into user-story-aligned tasks
4. **Begin Implementation**: Start with P1 user story (Quick Debt Assessment), deploy MVP, iterate

## Success Metrics (Aligned with Spec)

**Hackathon Demo Readiness**:
- End-to-end flow works: Upload Vietnamese statement → Extract debts → Generate plan → Log payment → See updated timeline (covers P1-P2 user stories)
- Opik dashboard shows: 20+ traces, <5% hallucination rate (LLM-as-judge), <500ms p95 latency, clear cost tracking
- Security visible: Encrypted data in Supabase, HTTPS everywhere, auth working (JWT magic links)
- UX polished: Mobile-responsive, Vietnamese localization, celebration animations, accessible (WCAG 2.1 AA spot check)

**Performance Validation** (per spec):
- Plan generation: <3s for 10 debts (PERF-001) ✓
- Payment logging: <500ms update (PERF-002) ✓
- OCR: <10s Vietnamese statement (PERF-003) ✓
- API throughput: 100 req/s (PERF-010) - load test with Locust

**Best Use of Opik Criteria**:
- Comprehensive tracing: Every agent call logged with inputs/outputs
- LLM-as-judge: Validation for financial advice accuracy (no hallucinated interest rates, math correctness)
- Custom dashboards: Agent performance, user engagement, cost efficiency
- A/B testing: Prompt variations for negotiation scripts (empathetic vs professional tone)
- Clear ROI: "Opik helped us achieve <5% hallucination rate, ensuring trust in financial advice"
