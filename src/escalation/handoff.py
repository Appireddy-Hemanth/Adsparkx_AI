import uuid
from datetime import datetime, timezone
from src.config.settings import settings
from src.utils.gemini_client import RateLimitedGeminiClient
from src.utils.logger import logger

class HandoffBuilder:
    def __init__(self):
        # Initialize rate-limited gemini client using lite model for quick summarization
        self.client = RateLimitedGeminiClient(
            model_name=settings.gemini_lite_model,
            api_key=settings.gemini_api_key
        )

    def _call_llm(self, prompt: str) -> str:
        """Isolated LLM call for testing."""
        return self.client.generate(prompt)

    def build(
        self,
        persona: str,
        persona_confidence: float,
        messages: list[dict],
        retrieved_chunks: list[dict] = None,
        attempted_steps: list[str] = None,
        sentiment_scores: list[float] = None,
        escalation_reason: str = "Unspecified",
        session_id: str = None
    ) -> dict:
        if retrieved_chunks is None:
            retrieved_chunks = []
        if attempted_steps is None:
            attempted_steps = []
        if sentiment_scores is None:
            sentiment_scores = [0.0]
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Determine unique documents used
        documents_used = list(set(
            chunk.get("source") for chunk in retrieved_chunks if chunk.get("source")
        ))

        # Format conversation history for summary prompt
        history_str = ""
        for idx, msg in enumerate(messages):
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            history_str += f"Turn {idx+1} - {role}: {content}\n"

        # 1. Generate Issue Summary via LLM
        issue_summary = ""
        if history_str:
            summary_prompt = f"""
            You are a technical support lead at NovaSuite. Summarize the following customer support incident in 2-3 sentences.
            Focus on the core technical problem, what the user has tried, and why they are blocked.

            Conversation History:
            {history_str}

            Summary (2-3 sentences, direct, no preamble):
            """
            try:
                issue_summary = self._call_llm(summary_prompt).strip()
            except Exception as e:
                logger.error(f"Error generating issue summary with LLM: {e}")
                issue_summary = f"User is experiencing issues. Last message: '{messages[-1]['content']}' if messages else 'No messages'."
        else:
            issue_summary = "No conversation history provided for escalation."

        # 2. Generate Recommended Next Steps via LLM
        recommended_next_steps = []
        if history_str:
            steps_prompt = f"""
            You are a technical support lead at NovaSuite. Based on the conversation history below, suggest 3 bullet points of next troubleshooting steps for the human engineer.
            Format the response as 3 separate lines starting with a bullet (-) or list.

            Conversation History:
            {history_str}

            Troubleshooting steps for human engineer (exactly 3 bullet points, direct, no preamble):
            """
            try:
                steps_response = self._call_llm(steps_prompt).strip()
                # Parse steps
                for line in steps_response.split("\n"):
                    cleaned = line.strip().lstrip("-").strip().lstrip("*").strip()
                    if cleaned:
                        recommended_next_steps.append(cleaned)
            except Exception as e:
                logger.error(f"Error generating next steps with LLM: {e}")
                recommended_next_steps = ["Verify user account details", "Check server logs for session ID", "Contact user via security email"]
        else:
            recommended_next_steps = ["Contact client for details", "Review workspace settings"]

        # Ensure we have exactly 3 steps or at least some steps
        if not recommended_next_steps:
            recommended_next_steps = ["Review user activity logs", "Verify credentials", "Inspect system status page"]

        # 3. Determine Priority (P1, P2, or P3)
        priority = "P3"
        latest_sentiment = sentiment_scores[-1] if sentiment_scores else 0.0
        
        # P1 rules: Very negative sentiment (e.g. < -0.6) or urgent legal keyword
        if latest_sentiment <= -0.60:
            priority = "P1"
        # P2 rules: Frustrated user or moderately negative sentiment (e.g. < -0.3)
        elif persona == "FRUSTRATED_USER" or latest_sentiment <= -0.30:
            priority = "P2"
        else:
            priority = "P3"

        return {
            "persona": persona,
            "persona_confidence": float(persona_confidence),
            "issue_summary": issue_summary,
            "conversation_history": messages,
            "documents_used": documents_used,
            "retrieved_chunks": retrieved_chunks,
            "attempted_steps": attempted_steps,
            "sentiment_trajectory": sentiment_scores,
            "escalation_reason": escalation_reason,
            "recommended_next_steps": recommended_next_steps,
            "session_id": session_id,
            "escalated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "priority": priority
        }
