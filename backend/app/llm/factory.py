import os
from app.config import settings
from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.lmstudio_provider import LMStudioProvider
from app.llm.openai_provider import OpenAICompatibleProvider

def get_llm_provider(override_name: str = None) -> LLMProvider:
    provider_name = (override_name or os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER)).lower()

    if provider_name == "groq":
        from app.llm.groq_provider import GroqProvider
        return GroqProvider()
    elif provider_name in ("openai", "openrouter", "deepseek"):
        return OpenAICompatibleProvider()
    elif provider_name == "ollama":
        return OllamaProvider(
            base_url=os.getenv("LLM_BASE_URL") or os.getenv("OLLAMA_BASE_URL"),
            model=os.getenv("LLM_MODEL") or os.getenv("OLLAMA_MODEL"),
        )
    elif provider_name == "lmstudio":
        return LMStudioProvider()
    else:
        # mock fallback — agent tetap hidup walau tidak ada LLM
        return MockLLMProvider()
