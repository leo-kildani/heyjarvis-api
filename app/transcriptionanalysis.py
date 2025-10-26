import config as c
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


class TranscriptionAnalysis:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        if not self.client.api_key:
            raise ValueError("GROQ_API_KEY not found in env vars")

    def analyze_transcript(self, transcript: str, prompt: str = None):
        sys_prompt = (
            prompt
            if prompt is not None
            else c.GROQ_TRANSCRIPTION_ANALYSIS_SYSTEM_PROMPT
        )
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": transcript},
            ],
            model=c.GROQ_TRANSCRIPTION_ANALYSIS_MODEL,
        )
        return chat_completion.choices[0].message.content
