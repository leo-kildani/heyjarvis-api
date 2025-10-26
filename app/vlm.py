import os
from groq import Groq
import config as c


class VLM:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        if not self.client.api_key:
            raise ValueError("GROQ_API_KEY not found in env vars")

    def get_response(self, base64_image: str, prompt: str = None):
        """
        Get VLM response from base64 encoded image.
        """
        # use custom prompt
        sys_prompt = prompt if prompt is not None else c.GROQ_VLM_SYSTEM_PROMPT

        # ensure base64 string doesn't have data URI prefix
        if base64_image.startswith("data:image"):
            image_url = base64_image
        else:
            image_url = f"data:image/jpeg;base64,{base64_image}"

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": sys_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            model=c.GROQ_VLM_MODEL,
        )

        return chat_completion.choices[0].message.content
