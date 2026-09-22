import logging
from datetime import datetime, timezone
from typing import Dict, Any

# Configure basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvidenceEngine:
    """
    Synthesizer class that takes deterministic GIS/Marine outputs and formats them 
    into explainable, evidence-backed recommendations.
    """
    def __init__(self):
        pass

    def synthesize_recommendation(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw data dictionary and formats an explainable recommendation.
        Gracefully handles missing or malformed data to prevent crashes.
        """
        try:
            # CRASH PREVENTION: Validate input
            if not raw_data or not isinstance(raw_data, dict):
                raise ValueError("Input data must be a non-empty dictionary.")

            # Extract parameters safely
            metrics = raw_data.get("metrics", {})
            sst_trend = metrics.get("sst_trend", "unknown")
            chlorophyll_trend = metrics.get("chlorophyll_trend", "unknown")
            
            source = raw_data.get("source", "unknown_source")
            confidence = float(raw_data.get("confidence", 0.0))

            # SCIENTIFIC WORDING: Use correlation language, never causation.
            explanation = (
                f"We observed an SST trend of {sst_trend} and a chlorophyll trend of {chlorophyll_trend}. "
                "These are possible contributing factors to the observed fishing productivity levels. "
                "Note: Changing sea surface temperatures are highly correlated with fish movement, "
                "but other environmental variables may also be involved."
            )

            return self._format_output(explanation, source, confidence)

        except Exception as e:
            # CRASH PREVENTION: Catch everything and return safe default
            logger.warning(f"Failed to synthesize recommendation: {e}. Returning safe default.")
            return self._format_output(
                explanation="Data is currently insufficient to accurately determine contributing factors. Proceed with caution.",
                source="orca_fallback_system",
                confidence=0.0
            )

    def _format_output(self, explanation: str, source: str, confidence: float) -> Dict[str, Any]:
        """
        Appends mandatory metadata (source, timestamp, confidence) to every AI 
        recommendation per the ORCA PRD.
        """
        return {
            "recommendation": explanation,
            "metadata": {
                "source": source,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "confidence": confidence
            }
        }
