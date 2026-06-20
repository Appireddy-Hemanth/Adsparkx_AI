import pytest
import os
from src.config.settings import settings

@pytest.fixture(autouse=True)
def setup_test_env():
    # Reset singletons to prevent test cross-contamination/mock bypassing
    try:
        import src.rag.retriever as retriever
        retriever._chroma_client = None
        retriever._chroma_collection = None
    except ImportError:
        pass

    try:
        import src.agent.nodes.response_node as resp_node
        resp_node._response_node_instance = None
    except ImportError:
        pass

    try:
        import src.agent.nodes.escalation_node as esc_node
        esc_node._escalation_checker_instance = None
        esc_node._handoff_builder_instance = None
    except ImportError:
        pass
