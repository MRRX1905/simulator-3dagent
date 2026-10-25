"""
Groq LLM Provider — gratis, ultra-cepat, tanpa beban GPU lokal.
Daftar API key gratis di https://console.groq.com/keys
"""
import os
from typing import List, Dict, Optional
from app.llm.base import LLMProvider

class GroqProvider(LLMProvider):
    """
    Provider Groq menggunakan SDK resmi groq-python.
    Model default: llama-3.3-70b-versatile (gratis, sangat cepat).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY tidak ditemukan. "
                "Set LLM_API_KEY di C:\\AI_CITY\\backend\\.env. "
                "Dapatkan key gratis di https://console.groq.com/keys"
            )

        from groq import AsyncGroq
        self._client = AsyncGroq(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, temperature, max_tokens)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choices = response.choices
        if choices:
            return choices[0].message.content or ""
        return ""
