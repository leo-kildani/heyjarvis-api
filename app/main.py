from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv
from .vlm import VLM
from .transcriptionanalysis import TranscriptionAnalysis
from .llmsynthesis import LLMSynthesis
import uvicorn


load_dotenv()

app = FastAPI(
    title="Jarvis External Models API",
    description="API for VLM and Transcription Analysis using Groq models",
    version="1.0.0",
)

security = HTTPBearer()
AUTH_TOKEN = os.environ.get("API_AUTH_TOKEN")

# Initialize service instances
vlm_service = VLM()
transcription_service = TranscriptionAnalysis()
synthesis_service = LLMSynthesis()


# Pydantic models for request/response validation
class VLMRequest(BaseModel):
    base64_image: str = Field(
        ..., description="Base64 encoded image string (with or without data URI prefix)"
    )
    prompt: Optional[str] = Field(
        None, description="Custom prompt to override the default system prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "base64_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                "prompt": "Describe what you see in this image",
            }
        }


class VLMResponse(BaseModel):
    response: str = Field(..., description="VLM analysis response")

    class Config:
        json_schema_extra = {
            "example": {
                "response": '{"hazard": "none", "people": "2 ahead 1.5 m", "actions": ["walking forward"], "objects": ["counter front 3 m"], "path": "clear left 4 m", "notes": "daylight", "confidence": 0.93}'
            }
        }


class TranscriptionAnalysisRequest(BaseModel):
    transcript: str = Field(..., description="The text transcript to analyze")
    prompt: Optional[str] = Field(
        None, description="Custom prompt to override the default system prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "Let's schedule a meeting for next Tuesday to discuss the project timeline and deliverables.",
                "prompt": None,
            }
        }


class TranscriptionAnalysisResponse(BaseModel):
    analysis: str = Field(..., description="Analysis result of the transcript")

    class Config:
        json_schema_extra = {
            "example": {
                "analysis": '{"context": "Team discussion about project delivery timeline", "keywords": ["project", "deadline", "update", "client"], "domain": "business", "actions": ["send progress report", "confirm next meeting"], "tone": "collaborative", "confidence": 0.94}'
            }
        }


class SynthesisRequest(BaseModel):
    transcription_analysis: str = Field(
        ..., description="JSON string containing the transcription analysis result"
    )
    surrounding_analysis: list[str] = Field(
        ..., description="List of JSON strings containing VLM analysis results"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "transcription_analysis": '{"context": "User asking about nearby objects", "keywords": ["where", "counter"], "domain": "casual", "actions": ["locate object"], "tone": "inquisitive", "confidence": 0.91}',
                "surrounding_analysis": [
                    '{"hazard": "none", "people": "2 ahead 1.5 m", "actions": ["walking forward"], "objects": ["counter front 3 m"], "path": "clear left 4 m", "notes": "daylight", "confidence": 0.93}'
                ],
            }
        }


class SynthesisResponse(BaseModel):
    response: str = Field(
        ..., description="Conversational response synthesizing audio and visual context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "The counter you're asking about is directly in front of you, about 3 meters away. There are a couple of people ahead walking forward, about 1.5 meters from you. The path to your left is clear if you need to move around them."
            }
        }


# Authentication dependency
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the bearer token for authentication"""
    if AUTH_TOKEN and credentials.credentials != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Jarvis External Models API",
        "endpoints": {
            "vlm": "/api/vlm",
            "transcription_analysis": "/api/transcription-analysis",
            "synthesis": "/api/synthesize",
        },
    }


@app.post(
    "/api/vlm",
    response_model=VLMResponse,
    tags=["VLM"],
    summary="Analyze image using Vision Language Model",
    description="Processes a base64-encoded image and returns scene analysis in JSON format",
)
async def analyze_image(request: VLMRequest, token: str = Depends(verify_token)):
    """
    Analyze an image using the VLM (Vision Language Model).

    - **base64_image**: Base64 encoded image (with or without data URI prefix)
    - **prompt**: Optional custom prompt to override default system prompt

    Returns a JSON-formatted scene analysis including hazards, people, actions, objects, and path information.
    """
    try:
        response = vlm_service.get_response(
            base64_image=request.base64_image, prompt=request.prompt
        )
        return VLMResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}",
        )


@app.post(
    "/api/transcription-analysis",
    response_model=TranscriptionAnalysisResponse,
    tags=["Transcription Analysis"],
    summary="Analyze transcript text",
    description="Analyzes a text transcript and returns context, keywords, domain, actions, and tone",
)
async def analyze_transcript(
    request: TranscriptionAnalysisRequest, token: str = Depends(verify_token)
):
    """
    Analyze a text transcript using the Transcription Analysis service.

    - **transcript**: The text transcript to analyze
    - **prompt**: Optional custom prompt to override default system prompt

    Returns a JSON-formatted analysis including context, keywords, domain, actions, tone, and confidence.
    """
    try:
        analysis = transcription_service.analyze_transcript(
            transcript=request.transcript, prompt=request.prompt
        )
        return TranscriptionAnalysisResponse(analysis=analysis)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing transcript: {str(e)}",
        )


@app.post(
    "/api/synthesize",
    response_model=SynthesisResponse,
    tags=["Synthesis"],
    summary="Synthesize transcription and visual analyses",
    description="Combines transcription analysis and visual scene analyses into a conversational response",
)
async def synthesize(request: SynthesisRequest, token: str = Depends(verify_token)):
    """
    Synthesize transcription analysis and visual scene analyses into a conversational response.

    - **transcription_analysis**: JSON string containing the transcription analysis result
    - **surrounding_analysis**: List of JSON strings containing VLM analysis results from multiple frames

    Returns a natural, conversational response that combines the audio context with the visual scene information,
    suitable for speaking to the user.
    """
    try:
        response = synthesis_service.synthesize(
            transcription_analysis=request.transcription_analysis,
            surrounding_analysis=request.surrounding_analysis,
        )
        return SynthesisResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error synthesizing response: {str(e)}",
        )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
