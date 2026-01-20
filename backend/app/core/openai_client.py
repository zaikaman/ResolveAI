"""
OpenAI client singleton for GPT-5-Nano API calls
"""
from typing import cast, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from app.config import settings


class OpenAIClient:
    """Singleton wrapper for OpenAI async client"""
    
    _instance: AsyncOpenAI | None = None
    
    @classmethod
    def get_client(cls) -> AsyncOpenAI:
        """Get or create OpenAI client instance"""
        if cls._instance is None:
            client_kwargs = {"api_key": settings.OPENAI_API_KEY}
            if settings.OPENAI_BASE_URL:
                client_kwargs["base_url"] = settings.OPENAI_BASE_URL
            cls._instance = AsyncOpenAI(**client_kwargs)
        return cls._instance
    
    @classmethod
    async def chat_completion(
        cls,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        """Execute a chat completion and return response text"""
        client = cls.get_client()
        
        # Cast messages to the expected type
        typed_messages = cast(list[ChatCompletionMessageParam], messages)
        
        # Build API parameters, only include max_tokens if it's not None
        api_params = {
            "model": model or settings.OPENAI_MODEL,
            "messages": typed_messages,
        }
        
        response = await client.chat.completions.create(**api_params)
        
        return response.choices[0].message.content or ""
    
    @classmethod
    async def vision_completion(
        cls,
        image_url: str,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Execute vision API call for OCR"""
        client = cls.get_client()
        
        response = await client.chat.completions.create(
            model=model or settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
        )
        
        return response.choices[0].message.content or ""


# Convenience function
async def get_openai_client() -> AsyncOpenAI:
    """Get OpenAI client instance"""
    return OpenAIClient.get_client()


# Export singleton instance for direct usage
openai_client = OpenAIClient()
