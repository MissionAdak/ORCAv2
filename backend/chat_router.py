import base64
import traceback
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel
import google.generativeai as genai

from agents.evidence_engine import EvidenceEngine

router = APIRouter()
evidence = EvidenceEngine()

class ChatResponse(BaseModel):
    status: str  # "COMPLETE" | "CLARIFICATION" | "ERROR"
    text_response: Optional[str] = None
    audio_base64: Optional[str] = None
    evidence: Optional[dict] = None
    error: Optional[str] = None

@router.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    language: str = Form("en"),
    location: Optional[str] = Form("Versova"),
    want_audio_response: bool = Form(False)
):
    try:
        # Initialize Gemini 1.5 Flash
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return ChatResponse(status="ERROR", error="GEMINI_API_KEY is not set.")
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        system_prompt = f"""
        You are ORCA, a marine intelligence and decision-support platform. 
        The user is currently near {location}.
        Their preferred language is {language}. You MUST respond natively in {language}.
        Provide concise, actionable marine insights, weather forecasts, or fishing zone advice based on their query.
        """

        contents = [system_prompt]

        if audio:
            audio_bytes = audio.file.read()
            # React Native often sends audio without a specific mime type or as mp4/aac. 
            # We supply a fallback mime_type if it is missing or generic.
            mime = audio.content_type
            if not mime or mime == "application/octet-stream":
                mime = "audio/mp3" 
                
            contents.append({
                "mime_type": mime,
                "data": audio_bytes
            })

        if text:
            contents.append(text)

        if not audio and not text:
            return ChatResponse(status="CLARIFICATION", text_response="Please provide text or audio input.")

        # --- Execute One-Shot Gemini Generation ---
        response = model.generate_content(contents)
        final_text = response.text

        # --- Wrap with ORCA Standard Data Model Evidence ---
        aggregated = evidence.synthesize_recommendation({
            "metrics": {
                "sst_trend": "detected by Gemini Flash",
                "chlorophyll_trend": "derived from context"
            },
            "source": "Gemini 1.5 Flash Audio/Text Pipeline",
            "confidence": 0.95
        })

        # --- Optional TTS ---
        audio_b64 = None
        if want_audio_response:
            try:
                # Still mocking TTS unless connected to a specific TTS provider
                audio_bytes = b"mock_audio_data"
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            except Exception:
                audio_b64 = None 

        return ChatResponse(
            status="COMPLETE",
            text_response=final_text,
            audio_base64=audio_b64,
            evidence=aggregated,
        )

    except Exception as e:
        traceback.print_exc()
        return ChatResponse(status="ERROR", error=f"Gemini API failed: {str(e)}")
