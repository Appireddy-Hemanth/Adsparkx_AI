import json
import re
import asyncio
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
        "api", "oauth", "logs", "webhooks", "jwt", "configurations",
        "token", "config", "debug", "log", "http", "webhook", "ssl", "tls", "401", "403"
    ]

    FRUSTRATED_KEYWORDS = [
        "nothing works", "terrible", "fed up", "still broken", "hours", "urgent",
        "broken", "useless", "frustrated", "why is this", "!!!", "password reset", "login failure"
    ]

    EXECUTIVE_KEYWORDS = [
        "impact", "sla", "stakeholders", "timeline", "operations", "contract",
        "business", "resolution", "cost", "executive", "team"
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

    async def _call_llm_async(self, prompt: str) -> str:
        from unittest.mock import Mock
        if isinstance(self._call_llm, Mock):
            res = self._call_llm(prompt)
            if asyncio.iscoroutine(res):
                return await res
            return res
        return await self.client.generate_async(prompt)

    def classify(self, message: str, history: list[dict] = None) -> PersonaResult:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                return executor.submit(asyncio.run, self.classify_async(message, history)).result()
        else:
            return asyncio.run(self.classify_async(message, history))

    async def classify_async(self, message: str, history: list[dict] = None) -> PersonaResult:
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

        llm_result = None
        try:
            response_text = await self._call_llm_async(prompt)
            # Try to parse json from the response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                persona = data.get("persona")
                confidence = float(data.get("confidence", 0.8))
                reasoning = data.get("reasoning", "")
                
                # Validation
                if persona in ["TECHNICAL_EXPERT", "FRUSTRATED_USER", "BUSINESS_EXECUTIVE"]:
                    llm_result = PersonaResult(persona, confidence, reasoning)
            if not llm_result:
                logger.warning(f"Invalid persona format from LLM: {response_text}.")
        except Exception as e:
            logger.error(f"Error calling LLM for persona detection: {e}.")

        # 2. Secondary Layer: Rule-Based Classification
        rule_result = self.keyword_classify(message)

        # 3. Final Layer: Confidence-Based Arbitration
        # If LLM succeeded and has high confidence (>= 0.70), we prefer it
        if llm_result and llm_result.confidence >= 0.70:
            logger.info(f"[PERSONA] Primary LLM Classification accepted: {llm_result.persona} (conf={llm_result.confidence:.2f})")
            return llm_result

        # If LLM has low confidence or failed, but rule-based found keywords, arbitrate
        if rule_result.confidence > 0.50 or "Weighted keyword fallback (scores:" in rule_result.reasoning:
            # Check if keyword classification is more specific
            # A rule score > 0 yields a keyword fallback match reasoning
            if not rule_result.reasoning.startswith("Default classification"):
                logger.info(f"[PERSONA] Secondary Rule-Based Classification accepted: {rule_result.persona} (reason={rule_result.reasoning})")
                return rule_result

        # Fallback Arbitration: If LLM succeeded at all, use it; otherwise, use rule-based fallback (which defaults to FRUSTRATED_USER)
        if llm_result:
            logger.info(f"[PERSONA] Falling back to low-confidence LLM: {llm_result.persona} (conf={llm_result.confidence:.2f})")
            return llm_result

        logger.info(f"[PERSONA] Falling back to default: {rule_result.persona}")
        return rule_result

    def keyword_classify(self, message: str) -> PersonaResult:
        msg_lower = message.lower()
        
        # Weighted scoring: technical and executive terms carry higher weight
        tech_score = sum(2 for kw in self.TECHNICAL_KEYWORDS if kw in msg_lower)
        frust_score = sum(1 for kw in self.FRUSTRATED_KEYWORDS if kw in msg_lower)
        exec_score = sum(2 for kw in self.EXECUTIVE_KEYWORDS if kw in msg_lower)

        # Detect extra emphasis for frustration
        if "!!!" in message or (message.isupper() and len(message) > 4):
            frust_score += 2

        scores = {
            "TECHNICAL_EXPERT": tech_score,
            "FRUSTRATED_USER": frust_score,
            "BUSINESS_EXECUTIVE": exec_score
        }

        max_persona = max(scores, key=scores.get)
        max_score = scores[max_persona]

        if max_score == 0:
            # Default fallback (never UNKNOWN)
            return PersonaResult("FRUSTRATED_USER", 0.5, "Default classification (no keywords matched)")

        total = sum(scores.values())
        confidence = float(max_score / total) if total > 0 else 0.5
        confidence = max(0.5, min(0.95, confidence))
        
        reasoning = f"Weighted keyword fallback (scores: tech={tech_score}, frust={frust_score}, exec={exec_score})"
        return PersonaResult(max_persona, confidence, reasoning)
