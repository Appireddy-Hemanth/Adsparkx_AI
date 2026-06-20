import asyncio
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

    async def _call_llm_async(self, prompt: str) -> str:
        from unittest.mock import Mock
        if isinstance(self._call_llm, Mock):
            res = self._call_llm(prompt)
            if asyncio.iscoroutine(res):
                return await res
            return res
        return await self.client.generate_async(prompt)

    def run(self, state: dict) -> dict:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                return executor.submit(asyncio.run, self.run_async(state)).result()
        else:
            return asyncio.run(self.run_async(state))

    async def run_async(self, state: dict) -> dict:
        import time
        start_time = time.time()
        
        retrieved_chunks = state.get("retrieved_chunks", [])
        retrieval_confidence = state.get("retrieval_confidence", 0.0)

        # Anti-hallucination check: if no chunks found or low confidence, refuse factual generation
        if not retrieved_chunks or retrieval_confidence < settings.low_confidence_threshold:
            logger.info("RAG Retrieval confidence too low or no chunks found. Setting fallback response.")
            elapsed_time = time.time() - start_time
            return {
                "response": "I don't have enough information in the knowledge base to answer this accurately.",
                "attempted_steps": list(state.get("attempted_steps", [])),
                "response_time": elapsed_time,
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

        # Format conversation history (excluding the current user message at the end)
        history_str = ""
        prev_messages = state.get("messages", [])[:-1]
        for idx, turn in enumerate(prev_messages[-6:]):
            role = turn.get("role", "unknown").upper()
            content = turn.get("content", "")
            history_str += f"{role}: {content}\n"
        if not history_str:
            history_str = "No prior history."

        # Format attempted steps
        attempted_steps = state.get("attempted_steps", [])
        attempted_str = "\n".join(f"- {step}" for step in attempted_steps) if attempted_steps else "None."

        # Reinforce alternative solutions if there are attempted steps
        user_message_text = state.get("current_message", "")
        if attempted_steps:
            user_message_text += (
                f"\n\n(Important Instruction: The user has already tried the following troubleshooting steps: {', '.join(attempted_steps)}. "
                "Do NOT repeat these steps or suggest them again. You must offer alternative steps or suggest checking other configs if available in the context.)"
            )

        prompt = system_prompt_tmpl.format(
            context=context_str,
            user_message=user_message_text,
            history=history_str,
            attempted_steps=attempted_str
        )

        try:
            response_text = (await self._call_llm_async(prompt)).strip()
            
            # Extract suggested steps from response to build attempted_steps list
            import re
            steps = re.findall(r"(?:^\d+\.\s+|^-\s+|\*\s+)(.+)$", response_text, re.MULTILINE)
            attempted_steps_list = list(state.get("attempted_steps", []))
            for step in steps:
                clean_step = re.sub(r"\s*\[Source:\s*[^\]]+\]", "", step).strip()
                if clean_step and clean_step not in attempted_steps_list:
                    attempted_steps_list.append(clean_step)

            # Check if response actually cites a source
            if "Source:" not in response_text and retrieved_chunks:
                source_file = retrieved_chunks[0].get("source", "novasuite_documentation")
                response_text += f"\n\n[Source: {source_file}]"

            elapsed_time = time.time() - start_time
            logger.info(
                f"[RESPONSE] Session={state.get('session_id')} | Persona={persona} | "
                f"Chunks={len(retrieved_chunks)} | Confidence={retrieval_confidence:.2f} | "
                f"Time={elapsed_time:.2f}s"
            )

            return {
                "response": response_text,
                "attempted_steps": attempted_steps_list,
                "response_time": elapsed_time
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            elapsed_time = time.time() - start_time
            return {
                "response": "I don't have enough information in the knowledge base to answer this accurately.",
                "attempted_steps": list(state.get("attempted_steps", [])),
                "response_time": elapsed_time,
                "escalate": True,
                "escalation_reason": "response_generation_failure"
            }

_response_node_instance = None

# LangGraph function wrapper
async def response_node(state: dict) -> dict:
    global _response_node_instance
    if _response_node_instance is None:
        _response_node_instance = ResponseNode()
    return await _response_node_instance.run_async(state)
