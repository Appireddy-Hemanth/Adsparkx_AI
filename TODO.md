# TODO.md — Live Build Tracker

## PHASE 0 — Design & Setup
- [x] P0.1 Run `npx getdesign@latest add spotify` → DESIGN.md in root
- [x] P0.2 Create project structure (all dirs and __init__.py files)
- [x] P0.3 Create .env.example with all required keys
- [x] P0.4 Create requirements.txt with pinned versions
- [x] P0.5 Create pyproject.toml
- [x] P0.6 Create src/config/settings.py (pydantic-settings)
- [x] P0.7 Create src/utils/logger.py (structured timestamps)
- [x] P0.8 Create src/utils/gemini_client.py (rate-limited wrapper)
             GATE: `python -c "from src.utils.gemini_client import RateLimitedGeminiClient; print('OK')"`

## PHASE 1 — Knowledge Base
- [x] P1.1 Write novasuite_sla_policy.pdf (PDF — required)
- [x] P1.2 Write password_reset_guide.txt
- [x] P1.3 Write api_authentication_errors.txt
- [x] P1.4 Write billing_faq.txt
- [x] P1.5 Write account_lock_troubleshooting.txt
- [x] P1.6 Write getting_started.md
- [x] P1.7 Write integration_guide.md
- [x] P1.8 Write troubleshooting_connectivity.md
- [x] P1.9 Write data_export_guide.md
- [x] P1.10 Write mfa_setup_guide.md
- [x] P1.11 Write rate_limiting_policy.md
- [x] P1.12 Write webhook_configuration.md
- [x] P1.13 Write subscription_management.md
- [x] P1.14 Write api_reference_overview.md
- [x] P1.15 Write incident_response_playbook.md
             GATE: All 15 files exist, each ≥ 300 words

## PHASE 2 — RAG Pipeline
- [x] P2.1 src/rag/embeddings.py (Gemini text-embedding-004 wrapper)
- [x] P2.2 src/rag/ingestion.py (load → chunk → embed → store)
- [x] P2.3 src/rag/retriever.py (query → rerank → confidence score)
- [x] P2.4 scripts/ingest_kb.py (runner)
- [x] P2.5 scripts/reset_db.py (wipe + reingest)
             GATE: pytest tests/unit/test_rag_retrieval.py -v → 0 failures

## PHASE 3 — Persona Detection
- [x] P3.1 src/personas/prompts.py (3 system prompts)
- [x] P3.2 src/personas/detector.py (LLM + keyword fallback)
             GATE: pytest tests/unit/test_persona_detection.py -v → 0 failures

## PHASE 4 — Sentiment Analysis
- [x] P4.1 src/sentiment/analyzer.py (VADER + trend tracking)
             GATE: pytest tests/unit/test_sentiment_analyzer.py -v → 0 failures

## PHASE 5 — Escalation System
- [x] P5.1 src/escalation/triggers.py (all 6 trigger conditions)
- [x] P5.2 src/escalation/handoff.py (HandoffSummary builder)
             GATE: pytest tests/unit/test_escalation_triggers.py tests/unit/test_handoff_summary.py -v → 0 failures

## PHASE 6 — LangGraph Agent Core
- [x] P6.1 src/agent/state.py (AgentState TypedDict)
- [x] P6.2 src/agent/nodes/input_node.py
- [x] P6.3 src/agent/nodes/persona_node.py
- [x] P6.4 src/agent/nodes/retrieval_node.py
- [x] P6.5 src/agent/nodes/escalation_node.py
- [x] P6.6 src/agent/nodes/response_node.py
- [x] P6.7 src/agent/nodes/output_node.py
- [x] P6.8 src/agent/graph.py (StateGraph compile)
             GATE: pytest tests/unit/test_response_generation.py -v → 0 failures
             GATE: `python -c "from src.agent.graph import build_graph; build_graph(); print('Graph OK')`

## PHASE 7 — Multi-Agent Orchestration Layer
- [x] P7.1 src/orchestration/supervisor.py (LangGraph supervisor)
- [x] P7.2 src/orchestration/agents/architect_agent.py
- [x] P7.3 src/orchestration/agents/implementation_agent.py
- [x] P7.4 src/orchestration/agents/tester_agent.py
- [x] P7.5 src/orchestration/agents/debugger_agent.py
- [x] P7.6 src/orchestration/agents/bug_fixer_agent.py
- [x] P7.7 src/orchestration/agents/reviewer_agent.py
- [x] P7.8 src/orchestration/agents/improvements_agent.py
             GATE: pytest tests/unit/test_multi_agent_orchestration.py -v → 0 failures

## PHASE 8 — CLI Interface
- [x] P8.1 ui/cli.py (Click REPL with persona badges + source display)
             GATE: Manual smoke test — 3 different personas respond correctly

## PHASE 9 — Streamlit UI (DESIGN.md Spotify Theme)
- [x] P9.1 ui/streamlit_app.py — main chat panel
- [x] P9.2 ui/components/sidebar.py — metrics sidebar
- [x] P9.3 ui/components/persona_badge.py — colored persona indicator
- [x] P9.4 ui/components/source_expander.py — retrieved chunks display
- [x] P9.5 ui/components/escalation_modal.py — handoff JSON panel
- [x] P9.6 ui/components/rate_limit_banner.py — Gemini quota display
- [x] P9.7 Apply DESIGN.md: #121212 bg, #1DB954 accent, Inter/Circular font
             GATE: `streamlit run ui/streamlit_app.py` — no console errors
             GATE: All 3 personas visually distinguishable with correct badge colors
             GATE: DESIGN.md Spotify palette visible (dark bg, green accent)

## PHASE 10 — Integration Tests
- [x] P10.1 tests/integration/test_full_pipeline.py
- [x] P10.2 tests/integration/test_multi_turn_memory.py
- [x] P10.3 tests/integration/test_rate_limit_guard.py
             GATE: pytest tests/ -v --tb=short → 0 failures, 0 errors

## PHASE 11 — Final Review & Confirmation
- [x] P11.1 Code Reviewer Agent: full codebase scan
- [x] P11.2 Improvements Agent: logging, UX polish, error messages
- [x] P11.3 Remove all hardcoded secrets (grep -r "api_key" src/)
- [x] P11.4 Verify .gitignore covers: .env, chroma_db/, __pycache__/
- [x] P11.5 Final pytest run: ALL 35+ tests pass
             ✅ SUPERVISOR ISSUES CONFIRMED STATUS ONLY HERE
