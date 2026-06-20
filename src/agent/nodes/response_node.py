from src.config.settings import settings
from src.utils.gemini_client import RateLimitedGeminiClient
from src.personas.prompts import (
    TECHNICAL_EXPERT_SYSTEM_PROMPT,
    FRUSTRATED_USER_SYSTEM_PROMPT,
    BUSINESS_EXECUTIVE_SYSTEM_PROMPT
)
from src.utils.logger import logger

class ResponseNode:
    def __init__(self):
        # Initialise Gemini flash model client for high-quality response generation
        self.client = RateLimitedGeminiClient(
            model_name=settings.gemini_flash_model,
            api_key=settings.gemini_api_key
        )

    def _call_llm(self, prompt: str) -> str:
        """Isolated LLM call for testing."""
        return self.client.generate(prompt)

    def run(self, state: dict) -> dict:
        retrieved_chunks = state.get("retrieved_chunks", [])
        retrieval_confidence = state.get("retrieval_confidence", 0.0)

        # Anti-hallucination check: if no chunks found or low confidence, escalate
        if not retrieved_chunks or retrieval_confidence < settings.low_confidence_threshold:
            logger.info("RAG Retrieval confidence too low or no chunks found. Escalating to human agent.")
            return {
                "escalate": True,
                "escalation_reason": "no_relevant_kb_content"
            }

        persona = state.get("persona", "FRUSTRATED_USER")
        
        # Load system prompt based on persona
        if persona == "TECHNICAL_EXPERT":
            system_prompt_tmpl = TECHNICAL_EXPERT_SYSTEM_PROMPT
        elif persona == "BUSINESS_EXECUTIVE":
            system_prompt_tmpl = BUSINESS_EXECUTIVE_SYSTEM_PROMPT
        else:
            system_prompt_tmpl = FRUSTRATED_USER_SYSTEM_PROMPT

        # Compile retrieved chunks context
        context_str = ""
        for idx, chunk in enumerate(retrieved_chunks):
            context_str += f"[{idx+1}] Source: {chunk.get('source', 'unknown')} | Section: {chunk.get('section', 'General')}\n{chunk.get('text', '')}\n\n"

        prompt = system_prompt_tmpl.format(
            context=context_str,
            user_message=state.get("current_message", "")
        )

        try:
            response_text = self._call_llm(prompt).strip()
            
            # Extract suggested steps from response to build attempted_steps list
            # We look for numbered list patterns or bullet points
            import re
            steps = re.findall(r"(?:^\d+\.\s+|^-\s+|\*\s+)(.+)$", response_text, re.MULTILINE)
            attempted_steps = list(state.get("attempted_steps", []))
            for step in steps:
                # Strip potential source citations from the step text
                clean_step = re.sub(r"\s*\[Source:\s*[^\]]+\]", "", step).strip()
                if clean_step and clean_step not in attempted_steps:
                    attempted_steps.append(clean_step)

            # Check if response actually cites a source
            # If prompt required citation and model didn't include it, we append a default citation
            if "Source:" not in response_text and retrieved_chunks:
                source_file = retrieved_chunks[0].get("source", "novasuite_documentation")
                response_text += f"\n\n[Source: {source_file}]"

            return {
                "response": response_text,
                "attempted_steps": attempted_steps,
                "escalate": False
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "escalate": True,
                "escalation_reason": "response_generation_failure"
            }

# LangGraph function wrapper
def response_node(state: dict) -> dict:
    return ResponseNode().run(state)
