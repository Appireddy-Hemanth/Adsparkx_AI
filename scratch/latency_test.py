import os
import sys
import time
import asyncio
import uuid
import statistics

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.graph import build_graph

# 10 Test Cases representing different categories
TEST_CASES = [
    # Technical Questions
    {
        "query": "How do I configure OAuth webhook authentication?",
        "category": "Technical"
    },
    {
        "query": "Why does my API key return a 401 Unauthorized error?",
        "category": "Technical"
    },
    {
        "query": "Can you check the webhook logs for my application?",
        "category": "Technical"
    },
    # Frustrated Users
    {
        "query": "I've tried everything and nothing works! This is terrible!!!",
        "category": "Frustrated"
    },
    {
        "query": "I need a refund immediately! This product is completely useless!",
        "category": "Frustrated"
    },
    # Business Executives
    {
        "query": "What is the impact of this API downtime on our SLA?",
        "category": "Executive"
    },
    {
        "query": "When will the service disruption be resolved? Stakeholders are asking.",
        "category": "Executive"
    },
    # Password resetting / common checks
    {
        "query": "How do I reset my password?",
        "category": "Standard Support"
    },
    # Out of Scope / Fallbacks
    {
        "query": "Can you tell me a joke?",
        "category": "Out of Scope"
    },
    {
        "query": "What is the capital of France?",
        "category": "Out of Scope"
    }
]

async def run_latency_test():
    print("=" * 60)
    print("NovaSuite AI Support Agent — Asynchronous Latency Benchmark")
    print("=" * 60)
    
    # Build the graph
    graph = build_graph()
    
    latencies = []
    success_count = 0
    
    for idx, tc in enumerate(TEST_CASES):
        query = tc["query"]
        cat = tc["category"]
        print(f"\n[{idx+1}/10] Testing Category: {cat}")
        print(f"Query: '{query}'")
        
        # Initialise state
        state = {
            "session_id": str(uuid.uuid4())[:8],
            "messages": [],
            "current_message": query,
            "persona": "",
            "persona_confidence": 0.0,
            "retrieved_chunks": [],
            "retrieval_confidence": 0.0,
            "response": "",
            "escalate": False,
            "escalation_reason": "",
            "handoff_summary": None,
            "turn_count": 0,
            "resolution_attempts": 0,
            "sentiment_scores": [],
            "attempted_steps": [],
            "gemini_daily_calls": 0,
            "rate_limit_warning": False
        }
        
        start_time = time.perf_counter()
        try:
            # Run graph asynchronously!
            result_state = await graph.ainvoke(state)
            latency = time.perf_counter() - start_time
            latencies.append(latency)
            success_count += 1
            
            persona = result_state.get("persona", "UNKNOWN")
            retrieval_conf = result_state.get("retrieval_confidence", 0.0)
            escalate = result_state.get("escalate", False)
            response = result_state.get("response", "")
            
            print(f"  Latency: {latency:.4f}s")
            print(f"  Persona: {persona} (conf={result_state.get('persona_confidence', 0.0):.2f})")
            print(f"  Retrieval Confidence: {retrieval_conf:.2f}")
            print(f"  Escalated: {escalate} (reason: {result_state.get('escalation_reason', 'none')})")
            print(f"  Response Preview: {response.replace('\n', ' ')[:80]}...")
        except Exception as e:
            latency = time.perf_counter() - start_time
            print(f"  [ERROR] Execution failed after {latency:.4f}s: {e}")
            latencies.append(latency)
            
        # Small delay between runs to avoid hitting tight rate limits on consecutive calls
        await asyncio.sleep(1.0)
        
    print("\n" + "=" * 60)
    print("Benchmark Results Summary")
    print("=" * 60)
    print(f"Successful runs: {success_count}/{len(TEST_CASES)}")
    if latencies:
        print(f"Min Latency:  {min(latencies):.4f}s")
        print(f"Max Latency:  {max(latencies):.4f}s")
        print(f"Avg Latency:  {statistics.mean(latencies):.4f}s")
        if len(latencies) > 1:
            print(f"Std Dev:      {statistics.stdev(latencies):.4f}s")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_latency_test())
