from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes.input_node import input_node
from src.agent.nodes.persona_node import persona_node
from src.agent.nodes.sentiment_node import sentiment_node
from src.agent.nodes.retrieval_node import retrieval_node
from src.agent.nodes.retrieval_confidence_node import retrieval_confidence_node
from src.agent.nodes.response_node import response_node
from src.agent.nodes.escalation_node import escalation_evaluation_node, human_handoff_node
from src.agent.nodes.output_node import output_formatting_node

def build_graph():
    graph = StateGraph(AgentState)

    # Add all 9 nodes in sequence
    graph.add_node("input", input_node)
    graph.add_node("persona", persona_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("retrieval_confidence", retrieval_confidence_node)
    graph.add_node("response", response_node)
    graph.add_node("escalation_evaluation", escalation_evaluation_node)
    graph.add_node("human_handoff", human_handoff_node)
    graph.add_node("output", output_formatting_node)

    # Set entry point to input node
    graph.set_entry_point("input")
    
    # Strict linear flow ensuring all stages execute without bypassing
    graph.add_edge("input", "persona")
    graph.add_edge("persona", "sentiment")
    graph.add_edge("sentiment", "retrieval")
    graph.add_edge("retrieval", "retrieval_confidence")
    graph.add_edge("retrieval_confidence", "response")
    graph.add_edge("response", "escalation_evaluation")
    graph.add_edge("escalation_evaluation", "human_handoff")
    graph.add_edge("human_handoff", "output")
    graph.add_edge("output", END)

    return graph.compile()
