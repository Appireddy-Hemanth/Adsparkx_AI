from typing import TypedDict, Literal

class BuildState(TypedDict):
    current_phase: str
    current_module: str
    test_results: dict          # {module: "pass"|"fail"|"pending"}
    review_results: dict        # {module: "LGTM"|"needs_changes"}
    error_log: list[str]
    retry_counts: dict          # {agent_name: count} — circuit breaker
    all_phases_passed: bool
    confirmation_issued: bool

MAX_RETRIES_PER_AGENT = 3

def supervisor_router(state: BuildState) -> Literal["architect", "implement", "test", "debug", "fix", "review", "improve", "END"]:
    retry_counts = state.get("retry_counts", {})
    
    # 1. Circuit breaker: if any agent exceeds MAX_RETRIES, route back to architect for redesign
    for agent, count in retry_counts.items():
        if count >= MAX_RETRIES_PER_AGENT:
            return "architect"
            
    # 2. Check if all phases passed and all reviews are LGTM
    all_passed = state.get("all_phases_passed", False)
    review_results = state.get("review_results", {})
    
    # Verify tests are not failing
    test_results = state.get("test_results", {})
    has_failing_tests = any(v == "fail" for v in test_results.values())
    
    if has_failing_tests:
        # Route to debugger/fixer if there are failing tests, never to END
        return "debug"

    # If all phases are done, and all reviews in review_results are LGTM, return END
    if all_passed and review_results and all(v == "LGTM" for v in review_results.values()):
        return "END"
        
    # Route according to current phase or module if not finished
    module = state.get("current_module", "")
    if module == "design":
        return "architect"
    elif module == "coding":
        return "implement"
    elif module == "testing":
        return "test"
    elif module == "review":
        return "review"
    
    # Default fallback
    return "improve"
