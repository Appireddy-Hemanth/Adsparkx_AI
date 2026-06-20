import json
import re
from dataclasses import dataclass
from src.config.settings import settings
from src.utils.gemini_client import RateLimitedGeminiClient
from src.personas.prompts import PERSONA_DETECTION_PROMPT
from src.utils.logger import logger

@dataclass
class PersonaResult:
    persona: str
    confidence: float
    reasoning: str

class PersonaDetector:
    TECHNICAL_KEYWORDS = [
        "api", "oauth", "jwt", "401", "403", "stack trace", "endpoint",
        "token", "config", "debug", "log", "http", "webhook", "ssl", "tls"
    ]

    FRUSTRATED_KEYWORDS = [
        "nothing works", "i've tried", "broken", "useless", "frustrated",
        "hours", "still not", "terrible", "why is this", "fed up", "!!!"
    ]

    EXECUTIVE_KEYWORDS = [
        "sla", "impact", "operations", "business", "when will", "resolution",
        "timeline", "cost", "executive", "budget", "team", "stakeholders"
    ]

    def __init__(self):
        # Initialise rate-limited gemini client using lite model for persona classification
        self.client = RateLimitedGeminiClient(
            model_name=settings.gemini_lite_model,
            api_key=settings.gemini_api_key
        )

    def _call_llm(self, prompt: str) -> str:
        """Isolated LLM call method for easy mocking in tests."""
        return self.client.generate(prompt)

    def classify(self, message: str, history: list[dict] = None) -> PersonaResult:
        if history is None:
            history = []

        # Form history string (last 3 turns)
        history_str = ""
        for turn in history[-6:]:  # last 3 full turns (user+assistant = 6 items)
            role = turn.get("role", "unknown").upper()
            content = turn.get("content", "")
            history_str += f"{role}: {content}\n"

        prompt = PERSONA_DETECTION_PROMPT.format(
            history=history_str if history_str else "No prior history.",
            user_message=message
        )

        try:
            response_text = self._call_llm(prompt)
            # Try to parse json from the response
            # Sometimes LLMs wrap JSON in markdown block ```json ... ```
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                persona = data.get("persona")
                confidence = float(data.get("confidence", 0.8))
                reasoning = data.get("reasoning", "")
                
                # Validation
                if persona in ["TECHNICAL_EXPERT", "FRUSTRATED_USER", "BUSINESS_EXECUTIVE"]:
                    return PersonaResult(persona, confidence, reasoning)
            
            logger.warning(f"Invalid persona format from LLM: {response_text}. Falling back to keyword classification.")
        except Exception as e:
            logger.error(f"Error calling LLM for persona detection: {e}. Falling back to keyword classification.")

        # Fallback to keyword-based detection
        return self.keyword_classify(message)

    def keyword_classify(self, message: str) -> PersonaResult:
        msg_lower = message.lower()
        tech_score = sum(1 for kw in self.TECHNICAL_KEYWORDS if kw in msg_lower)
        frust_score = sum(1 for kw in self.FRUSTRATED_KEYWORDS if kw in msg_lower)
        exec_score = sum(1 for kw in self.EXECUTIVE_KEYWORDS if kw in msg_lower)

        # Detect manual locks or exclamation marks
        if "!!!" in message or msg_lower.isupper():
            frust_score += 2

        scores = {
            "TECHNICAL_EXPERT": tech_score,
            "FRUSTRATED_USER": frust_score,
            "BUSINESS_EXECUTIVE": exec_score
        }

        # Find max score
        max_persona = max(scores, key=scores.get)
        max_score = scores[max_persona]

        if max_score == 0:
            # Default fallback
            return PersonaResult("FRUSTRATED_USER", 0.5, "Default classification (no keywords matched)")

        # Calculate confidence
        total = sum(scores.values())
        confidence = float(max_score / total) if total > 0 else 0.5
        # Clamp confidence to reasonable range
        confidence = max(0.5, min(0.85, confidence))
        
        reasoning = f"Keyword fallback match (scores: tech={tech_score}, frust={frust_score}, exec={exec_score})"
        return PersonaResult(max_persona, confidence, reasoning)
