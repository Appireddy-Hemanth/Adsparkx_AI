from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes.input_node import input_node
from src.agent.nodes.persona_node import persona_node
from src.agent.nodes.retrieval_node import retrieval_node
from src.agent.nodes.escalation_node import escalation_check_node, escalation_node
from src.agent.nodes.response_node import response_node
from src.agent.nodes.output_node import output_node

def build_graph():
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("input", input_node)
    graph.add_node("persona", persona_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("escalation_check", escalation_check_node)
    graph.add_node("response", response_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("output", output_node)

    # Set entry point
    graph.set_entry_point("input")
    
    # Simple linear flow to escalation check
    graph.add_edge("input", "persona")
    graph.add_edge("persona", "retrieval")
    graph.add_edge("retrieval", "escalation_check")
    
    # Conditional edge routing based on 'escalate' flag
    graph.add_conditional_edges(
        "escalation_check",
        lambda s: "escalation" if s["escalate"] else "response",
        {
            "response": "response",
            "escalation": "escalation"
        }
    )
    
    # Connect terminal nodes to output node
    graph.add_edge("response", "output")
    graph.add_edge("escalation", "output")
    
    # Output node ends the graph execution
    graph.add_edge("output", END)

    return graph.compile()
