import pytest
from src.orchestration.supervisor import supervisor_router, BuildState

class TestMultiAgentOrchestration:

    def test_circuit_breaker_fires_at_max_retries(self):
        """If an agent hits MAX_RETRIES, supervisor routes to architect."""
        state = BuildState(
            current_phase="P2", current_module="rag_retrieval",
            test_results={"rag_retrieval": "fail"},
            review_results={},
            error_log=["TypeError on line 42"],
            retry_counts={"debugger": 3},   # At max
            all_phases_passed=False,
            confirmation_issued=False
        )
        next_agent = supervisor_router(state)
        assert next_agent == "architect"

    def test_confirmation_not_issued_with_failing_tests(self):
        """Supervisor NEVER routes to END if any tests are failing."""
        state = BuildState(
            current_phase="P10", current_module="integration",
            test_results={"integration": "fail"},
            review_results={"rag": "LGTM"},
            error_log=[],
            retry_counts={},
            all_phases_passed=False,
            confirmation_issued=False
        )
        next_agent = supervisor_router(state)
        assert next_agent != "END"

    def test_confirmation_issued_when_all_gates_pass(self):
        """Supervisor routes to END only when all phases pass and all reviews LGTM."""
        state = BuildState(
            current_phase="P11", current_module="final_review",
            test_results={k: "pass" for k in ["rag", "persona", "escalation", "response", "integration"]},
            review_results={k: "LGTM" for k in ["rag", "persona", "escalation", "response"]},
            error_log=[],
            retry_counts={},
            all_phases_passed=True,
            confirmation_issued=False
        )
        next_agent = supervisor_router(state)
        assert next_agent == "END"

    def test_agent_badges_in_output(self):
        """Every agent output must start with its role badge."""
        from src.orchestration.agents.tester_agent import TesterAgent
        agent = TesterAgent()
        output = agent.run({"module": "test_module", "test_code": ""})
        assert output.startswith("[🧪 TESTER]")
