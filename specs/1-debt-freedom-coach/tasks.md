# Tasks: ResolveAI Debt Freedom Coach

**Input**: Design documents from `/specs/1-debt-freedom-coach/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/ (API + agents), quickstart.md

**Tests**: Tests are OPTIONAL - not included in this task list per project requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5, US6)
- All task descriptions include exact file paths

---

## Phase 1: Setup & Infrastructure

**Purpose**: Project initialization, configuration, and shared infrastructure

- [ ] T001 Create frontend project structure with Vite+React+TypeScript at frontend/
- [ ] T002 Create backend project structure with FastAPI+Python at backend/
- [ ] T003 Configure frontend dependencies in frontend/package.json (React 18.3+, Vite 5.0+, TypeScript 5.3+, TailwindCSS, Recharts, Zustand, @supabase/supabase-js, react-dropzone, crypto-js, zod, axios)
- [ ] T004 Configure backend dependencies in backend/requirements.txt (fastapi, uvicorn, pydantic, supabase, openai, opik-python, vapi-python, pulp, cryptography, passlib, python-jose, pytest)
- [ ] T005 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [ ] T006 [P] Configure TailwindCSS with design system in frontend/tailwind.config.js (8px grid, color palette: green/progress, warm/encouragement)
- [ ] T007 [P] Configure Python code quality tools in backend/pyproject.toml (black, ruff, mypy)
- [ ] T008 [P] Create environment variable templates frontend/.env.example and backend/.env.example
- [ ] T009 Setup Supabase project and copy connection details to .env files
- [ ] T010 Initialize Opik project in Comet workspace and configure API keys
- [ ] T011 Create Supabase database schema migrations in backend/app/db/migrations/001_init.sql (users, debts, repayment_plans, payments, actions, transactions, insights, milestones, reminders, negotiation_scripts tables)
- [ ] T012 Create database indexes migration in backend/app/db/migrations/002_indexes.sql (20+ indexes per data-model.md for <200ms query performance)
- [ ] T013 Create row-level security policies migration in backend/app/db/migrations/003_rls.sql (user data isolation)
- [ ] T014 Run database migrations against Supabase project using python scripts/run_migrations.py
- [ ] T015 [P] Configure CORS settings in backend/app/main.py for frontend origin
- [ ] T016 [P] Create FastAPI app entry point with middleware in backend/app/main.py
- [ ] T017 [P] Create Pydantic settings configuration in backend/app/config.py for environment variables
- [ ] T018 [P] Setup Opik tracing initialization in backend/app/core/opik_tracing.py with LLM-as-judge configuration
- [ ] T019 [P] Create OpenAI client singleton in backend/app/core/openai_client.py (GPT-5-Nano configuration)
- [ ] T020 [P] Create Vapi client singleton in backend/app/core/vapi_client.py
- [ ] T021 [P] Setup Supabase client in frontend/src/services/supabaseClient.ts
- [ ] T022 [P] Create encryption utility in frontend/src/utils/encryption.ts (client-side AES-256-GCM)
- [ ] T023 [P] Create encryption service in backend/app/services/encryption_service.py (server-side AES-256)

---

## Phase 2: Foundational Layer (Blocking Prerequisites)

**Purpose**: Core authentication, base models, and shared services required by all user stories

- [ ] T024 Create authentication router in backend/app/routers/auth.py (POST /auth/signup, POST /auth/login)
- [ ] T025 Create user Pydantic models in backend/app/models/user.py (UserCreate, UserResponse, UserProfile)
- [ ] T026 Create user repository in backend/app/db/repositories/user_repo.py (CRUD with encryption)
- [ ] T027 Create JWT validation and security utilities in backend/app/core/security.py (password hashing, token generation)
- [ ] T028 Create FastAPI auth dependency in backend/app/dependencies.py (get_current_user)
- [ ] T029 Create Supabase service wrapper in backend/app/services/supabase_service.py (connection pool, CRUD helpers)
- [ ] T030 [P] Create auth store in frontend/src/stores/authStore.ts (Zustand state for user session)
- [ ] T031 [P] Create auth API service in frontend/src/services/api.ts (Axios wrapper with auth interceptor)
- [ ] T032 [P] Create auth hook in frontend/src/hooks/useAuth.ts (signup, login, logout)
- [ ] T033 [P] Create common UI components in frontend/src/components/common/ (Button, Input, Card, Modal, Toast)
- [ ] T034 [P] Create layout components in frontend/src/components/layout/ (AppShell, Nav, Sidebar, MobileMenu)
- [ ] T035 [P] Create TypeScript types in frontend/src/types/ (debt.ts, plan.ts, user.ts, api.ts)
- [ ] T036 [P] Create validation schemas in frontend/src/utils/validation.ts (Zod schemas for forms)
- [ ] T037 [P] Create formatting utilities in frontend/src/utils/formatting.ts (currency, date, percentage formatters)
- [ ] T038 [P] Create constants file in frontend/src/utils/constants.ts (API URLs, debt types, repayment strategies)
- [ ] T039 Create BaseAgent class in backend/app/agents/base_agent.py with Opik tracing decorator
- [ ] T040 Create custom error classes in backend/app/core/errors.py (UserError, SystemError, ExternalError)
- [ ] T041 Create input validators in backend/app/core/validators.py (balance >0, APR 0-50%, etc.)
- [ ] T042 Create health check router in backend/app/routers/health.py (GET /health, GET /readiness)
- [ ] T043 Create Home/Landing page in frontend/src/pages/Home.tsx (signup/login forms)
- [ ] T044 Create App root component with routing in frontend/src/App.tsx (React Router v6 setup)

---

## Phase 3: User Story 1 - Quick Debt Assessment & Initial Plan (P1) 🎯 MVP

**Story Goal**: Users can input debts (manual or OCR), provide income/expenses, and receive an optimized repayment plan within 5 minutes showing payment schedule, interest savings, and debt-free date.

**Independent Test Criteria**: 
- User creates account → adds 3-5 debts with different rates/balances → receives working plan with timeline
- Plan shows debt-free date, total interest, monthly breakdown
- Delivers standalone value

### Backend - Data Layer

- [ ] T045 [P] [US1] Create debt Pydantic models in backend/app/models/debt.py (DebtCreate, DebtUpdate, DebtResponse, DebtType enum)
- [ ] T046 [P] [US1] Create plan Pydantic models in backend/app/models/plan.py (PlanRequest, PlanResponse, PlanRecalculation, PaymentSchedule)
- [ ] T047 [P] [US1] Create upload Pydantic models in backend/app/models/upload.py (UploadResponse, OCRResult)
- [ ] T048 [US1] Create debt repository in backend/app/db/repositories/debt_repo.py (CRUD with field encryption for balances/rates)
- [ ] T049 [US1] Create repayment plan repository in backend/app/db/repositories/plan_repo.py (create, update, get active plan)

### Backend - Business Logic

- [ ] T050 [US1] Create AssessmentAgent in backend/app/agents/assessment_agent.py (analyze debts, validate sustainability, calculate available income, recommend strategy)
- [ ] T051 [US1] Create OptimizationAgent in backend/app/agents/optimization_agent.py (call PuLP for debt optimization, support avalanche/snowball strategies)
- [ ] T052 [US1] Create debt optimization service in backend/app/services/optimization_service.py (PuLP linear programming for avalanche/snowball, minimize total interest)
- [ ] T053 [US1] Create debt service in backend/app/services/debt_service.py (CRUD operations, validation, calculate minimum payments)
- [ ] T054 [US1] Create plan service in backend/app/services/plan_service.py (orchestrate agents, generate plan, calculate projections)
- [ ] T055 [US1] Create OCR service in backend/app/services/ocr_service.py (GPT-5-Nano vision API for Vietnamese statement parsing)
- [ ] T056 [US1] Create agent orchestrator in backend/app/agents/orchestrator.py (ReAct pattern coordination, error recovery)

### Backend - API Layer

- [ ] T057 [US1] Create debts router in backend/app/routers/debts.py (GET /debts, POST /debts, PATCH /debts/{id}, DELETE /debts/{id})
- [ ] T058 [US1] Create plans router in backend/app/routers/plans.py (POST /plans/generate, POST /plans/recalculate, POST /plans/simulate)
- [ ] T059 [US1] Create uploads router in backend/app/routers/uploads.py (POST /uploads/document, GET /uploads/{id}/status)

### Frontend - State & Services

- [ ] T060 [P] [US1] Create debt store in frontend/src/stores/debtStore.ts (Zustand state for debts list)
- [ ] T061 [P] [US1] Create plan store in frontend/src/stores/planStore.ts (Zustand state for active repayment plan)
- [ ] T062 [US1] Create debt API service in frontend/src/services/debtService.ts (CRUD operations with encryption)
- [ ] T063 [US1] Create plan API service in frontend/src/services/planService.ts (generate, recalculate, simulate)
- [ ] T064 [US1] Create upload API service in frontend/src/services/uploadService.ts (document upload, OCR polling)

### Frontend - UI Components

- [ ] T065 [P] [US1] Create DebtCard component in frontend/src/components/debt/DebtCard.tsx (display single debt with balance, rate, creditor)
- [ ] T066 [P] [US1] Create DebtForm component in frontend/src/components/debt/DebtForm.tsx (manual debt entry with validation)
- [ ] T067 [P] [US1] Create DebtList component in frontend/src/components/debt/DebtList.tsx (list all debts with actions)
- [ ] T068 [P] [US1] Create FileDropzone component in frontend/src/components/upload/FileDropzone.tsx (react-dropzone wrapper, file validation)
- [ ] T069 [P] [US1] Create OCRFeedback component in frontend/src/components/upload/OCRFeedback.tsx (loading state, progress, extracted data preview)
- [ ] T070 [P] [US1] Create PlanTimeline component in frontend/src/components/plan/PlanTimeline.tsx (Recharts line chart showing debt reduction over time)
- [ ] T071 [P] [US1] Create PaymentSchedule component in frontend/src/components/plan/PaymentSchedule.tsx (table showing monthly payment breakdown per debt)
- [ ] T072 [P] [US1] Create PlanSummary component in frontend/src/components/plan/PlanSummary.tsx (debt-free date, total interest, interest saved)

### Frontend - Pages & Integration

- [ ] T073 [US1] Create Debts page in frontend/src/pages/Debts.tsx (manage debts: add manual, upload OCR, edit, delete)
- [ ] T074 [US1] Create Plan page in frontend/src/pages/Plan.tsx (full plan view with timeline, schedule, summary)
- [ ] T075 [US1] Create hooks in frontend/src/hooks/useDebts.ts (fetch debts, add debt, update debt, delete debt)
- [ ] T076 [US1] Create hooks in frontend/src/hooks/usePlan.ts (generate plan, recalculate plan, simulate scenarios)
- [ ] T077 [US1] Integrate onboarding flow in frontend/src/pages/Home.tsx (income/expenses input → add debts → generate plan)
- [ ] T078 [US1] Test end-to-end flow: signup → add 3 debts → generate plan → verify timeline shows debt-free date <3s

---

## Phase 4: User Story 2 - Daily Action & Progress Tracking (P2)

**Story Goal**: Users see daily recommended actions, log payments instantly, and view updated progress with visual feedback (debt melting away, percentage complete, milestones).

**Independent Test Criteria**:
- With existing debts/plan → user views daily actions → logs payment → sees updated progress
- Works independently of other features

### Backend - Data Layer

- [ ] T079 [P] [US2] Create payment Pydantic models in backend/app/models/payment.py (PaymentCreate, PaymentResponse, PaymentStats)
- [ ] T080 [US2] Create payment repository in backend/app/db/repositories/payment_repo.py (log payment, get recent payments, calculate stats)

### Backend - Business Logic

- [ ] T081 [US2] Create ActionAgent in backend/app/agents/action_agent.py (generate daily actions based on payment schedule, personalize messages)
- [ ] T082 [US2] Create HabitAgent in backend/app/agents/habit_agent.py (detect milestones, generate celebrations, suggest nudges)
- [ ] T083 [US2] Create payment service in backend/app/services/payment_service.py (log payment, update debt balance, trigger plan recalculation, calculate interest saved)

### Backend - API Layer

- [ ] T084 [US2] Create payments router in backend/app/routers/payments.py (POST /payments, GET /payments, GET /payments/stats)
- [ ] T085 [US2] Create actions endpoint in backend/app/routers/plans.py (GET /plans/actions/daily)

### Frontend - State & Services

- [ ] T086 [US2] Create payment API service in frontend/src/services/paymentService.ts (log payment, get payment history)

### Frontend - UI Components

- [ ] T087 [P] [US2] Create DailyActions component in frontend/src/components/progress/DailyActions.tsx (prioritized action list with "Pay $X" buttons)
- [ ] T088 [P] [US2] Create PaymentLogger component in frontend/src/components/progress/PaymentLogger.tsx (quick payment entry modal with amount, date)
- [ ] T089 [P] [US2] Create ProgressDashboard component in frontend/src/components/progress/ProgressDashboard.tsx (metrics: total debt reduced, % complete, days to milestone)
- [ ] T090 [P] [US2] Create ProgressChart component in frontend/src/components/progress/ProgressChart.tsx (Recharts bar chart showing debt reduction over time)
- [ ] T091 [P] [US2] Create MilestoneCard component in frontend/src/components/progress/MilestoneCard.tsx (celebration animation, badge, progress message)

### Frontend - Pages & Integration

- [ ] T092 [US2] Create Dashboard page in frontend/src/pages/Dashboard.tsx (daily actions + progress overview)
- [ ] T093 [US2] Test payment logging flow: log $200 payment → verify debt balance updates <500ms → see updated projections → check milestone detection

---

## Phase 5: User Story 3 - Income Changes & Plan Adaptation (P3)

**Story Goal**: Users can update income/expenses mid-plan, system recalculates instantly showing new timeline and presents options (aggressive vs balanced).

**Independent Test Criteria**:
- User modifies income → system regenerates plan with new projections
- Shows side-by-side comparison of options
- Adaptive intelligence works independently

### Backend - Business Logic

- [ ] T094 [US3] Enhance plan service in backend/app/services/plan_service.py with recalculation logic (compare old vs new plan, generate options: aggressive vs balanced)
- [ ] T095 [US3] Add "what-if" simulation to optimization service in backend/app/services/optimization_service.py (test scenarios without saving)

### Backend - API Layer

- [ ] T096 [US3] Add scenario simulation endpoint in backend/app/routers/plans.py (POST /plans/simulate with income changes, extra payments, rate reductions)

### Frontend - UI Components

- [ ] T097 [P] [US3] Create PlanComparison component in frontend/src/components/plan/PlanComparison.tsx (side-by-side comparison of old vs new plan)
- [ ] T098 [P] [US3] Create ScenarioSimulator component in frontend/src/components/plan/ScenarioSimulator.tsx (sliders for income, extra payments, rate changes with live preview)
- [ ] T099 [P] [US3] Create AdaptationOptions component in frontend/src/components/plan/AdaptationOptions.tsx (aggressive vs balanced strategy cards with impact)

### Frontend - Pages & Integration

- [ ] T100 [US3] Add income/expense editor to Settings page in frontend/src/pages/Settings.tsx (trigger recalculation on save)
- [ ] T101 [US3] Test adaptation flow: increase income $500 → see recalculated plan <2s → compare aggressive vs balanced → select option → save

---

## Phase 6: User Story 4 - Smart Spending Insights & Leak Detection (P4)

**Story Goal**: Users connect bank account or upload CSV, system categorizes transactions, identifies spending leaks (subscriptions, excessive dining), quantifies impact on debt timeline.

**Independent Test Criteria**:
- User uploads transaction CSV → receives categorized analysis → sees top leak categories → impact on debt-free date
- Delivers value independently

### Backend - Data Layer

- [ ] T102 [P] [US4] Create transaction Pydantic models in backend/app/models/transaction.py (Transaction, SpendingInsight, CategoryBreakdown)
- [ ] T103 [US4] Create transaction repository in backend/app/db/repositories/transaction_repo.py (bulk insert, categorization queries)

### Backend - Business Logic

- [ ] T104 [US4] Create categorization service in backend/app/services/categorization_service.py (GPT-5-Nano transaction categorization with caching)
- [ ] T105 [US4] Create spending analysis logic in backend/app/services/categorization_service.py (detect leaks: duplicate subscriptions, excessive spending, suggest savings)

### Backend - API Layer

- [ ] T106 [US4] Create insights router in backend/app/routers/insights.py (POST /insights/upload-csv, GET /insights/spending, GET /insights/leaks)

### Frontend - State & Services

- [ ] T107 [US4] Create insights API service in frontend/src/services/insightsService.ts (upload CSV, get spending analysis)

### Frontend - UI Components

- [ ] T108 [P] [US4] Create TransactionUpload component in frontend/src/components/insights/TransactionUpload.tsx (CSV dropzone with format validation)
- [ ] T109 [P] [US4] Create CategoryChart component in frontend/src/components/insights/CategoryChart.tsx (Recharts pie chart showing spending by category)
- [ ] T110 [P] [US4] Create LeaksList component in frontend/src/components/insights/LeaksList.tsx (identified leaks with suggestions and impact)
- [ ] T111 [P] [US4] Create SavingsImpact component in frontend/src/components/insights/SavingsImpact.tsx (show "eliminate leaks = X months faster")

### Frontend - Pages & Integration

- [ ] T112 [US4] Create Insights page in frontend/src/pages/Insights.tsx (upload transactions, view analysis, apply savings to plan)
- [ ] T113 [US4] Test insights flow: upload 1000-transaction CSV → see categorization <5s → identify $150/month in leaks → apply to plan → see accelerated timeline

---

## Phase 7: User Story 5 - Creditor Negotiation Support (P5)

**Story Goal**: Users select high-interest debt, receive personalized negotiation script based on payment history/account age, practice with AI voice simulation (Vapi), update rate after success.

**Independent Test Criteria**:
- User selects debt → receives negotiation script → practices with voice AI → updates rate in app
- Delivers value independently

### Backend - Data Layer

- [ ] T114 [P] [US5] Create negotiation Pydantic models in backend/app/models/negotiation.py (NegotiationScriptRequest, NegotiationScript, VapiSession)

### Backend - Business Logic

- [ ] T115 [US5] Create NegotiationAgent in backend/app/agents/negotiation_agent.py (generate personalized scripts using GPT-5-Nano, call Vapi for voice simulation)
- [ ] T116 [US5] Create negotiation service in backend/app/services/negotiation_service.py (script generation with user history context, Vapi session management)

### Backend - API Layer

- [ ] T117 [US5] Create negotiation router in backend/app/routers/negotiation.py (POST /negotiation/script, POST /negotiation/vapi-session, PATCH /negotiation/rate-update)

### Frontend - State & Services

- [ ] T118 [US5] Create Vapi integration service in frontend/src/services/vapiService.ts (start/stop voice session, handle events)

### Frontend - UI Components

- [ ] T119 [P] [US5] Create NegotiationScript component in frontend/src/components/negotiation/NegotiationScript.tsx (display script with talking points, copy button)
- [ ] T120 [P] [US5] Create VapiVoiceUI component in frontend/src/components/negotiation/VapiVoiceUI.tsx (voice waveform, mute/unmute, hang up controls)
- [ ] T121 [P] [US5] Create RateUpdateForm component in frontend/src/components/negotiation/RateUpdateForm.tsx (update interest rate after successful negotiation)

### Frontend - Pages & Integration

- [ ] T122 [US5] Create Negotiate page in frontend/src/pages/Negotiate.tsx (select debt, view script, practice with Vapi, update rate)
- [ ] T123 [US5] Test negotiation flow: select 23% APR debt → generate script → start Vapi practice session → complete practice → update rate to 16% → see recalculated savings

---

## Phase 8: User Story 6 - Milestone Celebrations & Habit Reinforcement (P6)

**Story Goal**: Users receive celebrations when paying off debts or reaching milestones (25%, 50%, 75%), see achievement badges, get motivational messages for consistency streaks.

**Independent Test Criteria**:
- User completes debt payoff → celebration animation triggers → badge awarded → plan updates automatically
- Enhances motivation independently

### Backend - Data Layer

- [ ] T124 [P] [US6] Create milestone models in backend/app/models/milestone.py (Milestone, Achievement, Badge)

### Backend - Business Logic

- [ ] T125 [US6] Enhance HabitAgent in backend/app/agents/habit_agent.py with celebration triggers (detect debt payoff, percentage milestones, consistency streaks)

### Backend - API Layer

- [ ] T126 [US6] Add milestones endpoint in backend/app/routers/plans.py (GET /plans/milestones, POST /plans/milestones/celebrate)

### Frontend - UI Components

- [ ] T127 [P] [US6] Create CelebrationModal component in frontend/src/components/progress/CelebrationModal.tsx (confetti animation, badge display, interest saved summary)
- [ ] T128 [P] [US6] Create AchievementBadge component in frontend/src/components/progress/AchievementBadge.tsx (badge icons with unlock states)
- [ ] T129 [P] [US6] Create StreakDisplay component in frontend/src/components/progress/StreakDisplay.tsx (consistency streak counter with fire icon)

### Frontend - Pages & Integration

- [ ] T130 [US6] Add milestone detection to payment logging in frontend/src/services/paymentService.ts (trigger celebration on milestone)
- [ ] T131 [US6] Add achievements section to Dashboard in frontend/src/pages/Dashboard.tsx (show earned badges, current streaks)
- [ ] T132 [US6] Test celebration flow: pay off first debt → see confetti animation → receive "First Victory" badge → verify payment redirects to next debt

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, error handling, accessibility, deployment preparation

### Performance & Optimization

- [ ] T133 [P] Implement code splitting in frontend/src/App.tsx (React.lazy for route-based splitting)
- [ ] T134 [P] Add request caching to frontend/src/services/api.ts (HTTP cache headers, stale-while-revalidate)
- [ ] T135 [P] Optimize Recharts bundle size in frontend (tree-shake unused chart types)
- [ ] T136 [P] Add connection pooling to backend/app/db/supabase.py (asyncpg 10-20 connections)
- [ ] T137 [P] Implement rate limiting middleware in backend/app/main.py (100 req/min per user)
- [ ] T138 [P] Add database query batching in backend/app/services/supabase_service.py (reduce round-trips)
- [ ] T139 [P] Setup Opik performance dashboards (API latency, LLM token usage, agent execution time)

### Error Handling & Resilience

- [ ] T140 [P] Create error boundary in frontend/src/components/common/ErrorBoundary.tsx (catch React errors, fallback UI)
- [ ] T141 [P] Add retry logic with exponential backoff in backend/app/core/openai_client.py (handle rate limits)
- [ ] T142 [P] Implement graceful degradation in backend/app/agents/orchestrator.py (fallback to templates if LLM fails)
- [ ] T143 [P] Add global error handler in frontend/src/App.tsx (network errors, auth failures)
- [ ] T144 [P] Create toast notification system in frontend/src/stores/uiStore.ts (success, error, info messages)

### Accessibility & UX

- [ ] T145 [P] Add ARIA labels to all interactive elements in frontend/src/components/
- [ ] T146 [P] Implement keyboard navigation for all forms in frontend (Tab order, Enter submit, Escape cancel)
- [ ] T147 [P] Test color contrast ratios (WCAG 2.1 AA ≥4.5:1) in frontend/src/index.css
- [ ] T148 [P] Add screen reader announcements for dynamic content updates (payment logged, plan recalculated)
- [ ] T149 [P] Create loading skeletons for all data-loading states in frontend/src/components/common/Skeleton.tsx

### Security & Compliance

- [ ] T150 [P] Implement certificate pinning for production in frontend/src/services/api.ts
- [ ] T151 [P] Add audit logging for sensitive operations in backend/app/services/payment_service.py (payment logging, rate updates)
- [ ] T152 [P] Create data export endpoint in backend/app/routers/users.py (GDPR compliance: GET /users/me/export)
- [ ] T153 [P] Create data deletion endpoint in backend/app/routers/users.py (GDPR compliance: DELETE /users/me)
- [ ] T154 [P] Setup document auto-deletion job in backend (delete uploaded statements after 24 hours)

### Deployment & DevOps

- [ ] T155 Create Dockerfile for backend in backend/Dockerfile (Python 3.11 slim image)
- [ ] T156 Create Vercel deployment config in frontend/vercel.json (SPA fallback, env vars)
- [ ] T157 Create Render deployment config in backend/render.yaml (build command, start command, env vars)
- [ ] T158 [P] Setup environment-specific configs (development, staging, production) in backend/app/config.py
- [ ] T159 [P] Create database seeding script in backend/scripts/seed_db.py (test users, sample debts, transactions)
- [ ] T160 [P] Create Opik evaluation script in backend/scripts/run_opik_eval.py (LLM-as-judge for agent outputs)

### Documentation & Developer Experience

- [ ] T161 [P] Generate OpenAPI documentation in backend/app/main.py (auto-generated at /docs endpoint)
- [ ] T162 [P] Create API usage examples in docs/api-examples.md (cURL commands for common flows)
- [ ] T163 [P] Create architecture diagram in docs/architecture.md (system components, data flow)
- [ ] T164 [P] Create Opik integration guide in docs/opik-integration.md (setup, metrics, dashboards)
- [ ] T165 [P] Update README.md with project overview, setup instructions, tech stack

---

## Implementation Strategy

### MVP Scope (Recommended)

**Target**: User Story 1 only (Quick Debt Assessment & Initial Plan)
- Tasks T001-T044 (Setup + Foundational)
- Tasks T045-T078 (User Story 1)
- Total: ~78 tasks
- **Value**: Users can input debts and receive optimized repayment plan (core value proposition)
- **Demo**: Complete end-to-end flow for hackathon demo

### Incremental Delivery

After MVP (US1), add features incrementally:
1. **US2 (Daily Actions)**: ~15 tasks - Add T079-T093
2. **US3 (Adaptation)**: ~8 tasks - Add T094-T101
3. **US4 (Insights)**: ~12 tasks - Add T102-T113
4. **US5 (Negotiation)**: ~9 tasks - Add T114-T123
5. **US6 (Celebrations)**: ~9 tasks - Add T124-T132
6. **Polish**: ~33 tasks - Add T133-T165

### Parallel Execution Opportunities

**Within User Story 1** (after T044 complete):
- **Parallel Group A** (Backend Data): T045, T046, T047 (Pydantic models)
- **Parallel Group B** (Backend Repos): T048, T049 (after data models)
- **Parallel Group C** (Backend Agents): T050, T051 (after base agent T039)
- **Parallel Group D** (Backend Services): T052, T053, T054, T055 (after repos + agents)
- **Parallel Group E** (Backend Routers): T057, T058, T059 (after services)
- **Parallel Group F** (Frontend Stores): T060, T061 (independent)
- **Parallel Group G** (Frontend Services): T062, T063, T064 (after stores)
- **Parallel Group H** (Frontend Components): T065-T072 (8 components in parallel after types T035)
- **Parallel Group I** (Frontend Pages): T073, T074 (after components)

**Within User Story 2**:
- **Parallel Group J**: T079, T080 (models + repo)
- **Parallel Group K**: T081, T082, T083 (agents + service after T080)
- **Parallel Group L**: T087-T091 (5 components in parallel)

**Polish Phase** (nearly all tasks can run in parallel):
- Performance: T133-T139 (7 tasks)
- Error Handling: T140-T144 (5 tasks)
- Accessibility: T145-T149 (5 tasks)
- Security: T150-T154 (5 tasks)
- Docs: T161-T165 (5 tasks)

---

## Dependencies Graph

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational)
                     ↓
                  Phase 3 (US1: Quick Assessment) ← MVP Target
                     ↓
                  Phase 4 (US2: Daily Actions)
                     ↓
    ┌────────────────┴────────────────┐
    ↓                                 ↓
Phase 5 (US3: Adaptation)    Phase 6 (US4: Insights)
    ↓                                 ↓
    └────────────────┬────────────────┘
                     ↓
    ┌────────────────┴────────────────┐
    ↓                                 ↓
Phase 7 (US5: Negotiation)   Phase 8 (US6: Celebrations)
    ↓                                 ↓
    └────────────────┬────────────────┘
                     ↓
              Phase 9 (Polish)
```

### Blocking Relationships

**MUST Complete Before Starting User Stories**:
- Phase 1 (Setup): T001-T023 → Foundational infrastructure
- Phase 2 (Foundational): T024-T044 → Auth, base models, shared services

**User Story Dependencies**:
- **US2** depends on US1: Needs debts, plans, payments (T045-T078)
- **US3** depends on US1: Needs plan service (T054)
- **US4** independent: Can implement anytime after Foundational (T024-T044)
- **US5** depends on US1: Needs debts (T048-T049)
- **US6** depends on US2: Needs payment logging (T079-T093)

**Recommended Order**: US1 → US2 → (US3, US4, US5 in parallel) → US6 → Polish

---

## Validation Checklist

### Format Compliance
- ✅ All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description`
- ✅ Task IDs sequential: T001-T165 (165 total tasks)
- ✅ [P] marker present for parallelizable tasks (75+ tasks marked)
- ✅ [Story] labels present for user story tasks (US1-US6)
- ✅ File paths included in all task descriptions

### Completeness
- ✅ Setup phase covers all infrastructure (Supabase, Opik, dependencies)
- ✅ Foundational phase covers auth, base models, shared utilities
- ✅ Each user story has complete implementation tasks (models → services → API → UI)
- ✅ All 10 database entities mapped to tasks
- ✅ All 25+ API endpoints mapped to tasks
- ✅ All 5 agents mapped to tasks
- ✅ Polish phase covers performance, security, accessibility, deployment

### Organization
- ✅ Tasks grouped by user story for independent implementation
- ✅ Clear phase boundaries (Setup → Foundational → US1-US6 → Polish)
- ✅ Dependencies documented in graph
- ✅ Parallel execution opportunities identified
- ✅ MVP scope defined (US1 = 78 tasks)

---

## Summary

**Total Tasks**: 165
**MVP Tasks** (US1): 78 (47% of total)
**User Story Breakdown**:
- Setup: 23 tasks
- Foundational: 21 tasks
- US1 (Quick Assessment): 34 tasks
- US2 (Daily Actions): 15 tasks
- US3 (Adaptation): 8 tasks
- US4 (Insights): 12 tasks
- US5 (Negotiation): 9 tasks
- US6 (Celebrations): 9 tasks
- Polish: 33 tasks

**Parallel Opportunities**: 75+ tasks marked [P] (45% can run in parallel within their phase)

**MVP Scope**: User Story 1 delivers core value (input debts → receive plan) - immediately executable for hackathon demo.

**Next Action**: Begin implementation with Phase 1 (Setup) tasks T001-T023.
