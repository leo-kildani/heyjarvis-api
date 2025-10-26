import config as c
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


class LLMSynthesis:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        if not self.client.api_key:
            raise ValueError("GROQ_API_KEY not found in env vars")

    def synthesize(
        self, transcription_analysis: str, surrounding_analysis: list[str]
    ) -> str:
        """
        Synthesize transcription analysis and surrounding visual analyses into a conversational response.

        Args:
            transcription_analysis: JSON string containing the transcription analysis result
            surrounding_analysis: List of JSON strings containing VLM analysis results

        Returns:
            A conversational response synthesizing the audio and visual context
        """
        # Construct the user message with all analysis data
        surrounding_context = "\n".join(
            [
                f"Frame {i+1}: {analysis}"
                for i, analysis in enumerate(surrounding_analysis)
            ]
        )

        user_message = f"""Transcription Analysis:
{transcription_analysis}

Surrounding Visual Analysis:
{surrounding_context}"""

        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": c.GROQ_SYNTHESIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            model=c.GROQ_LLM_SYNTHESIS_MODEL,
        )

        return chat_completion.choices[0].message.content
