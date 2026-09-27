from concurrent.futures import ThreadPoolExecutor, TimeoutError
from langchain_ollama import ChatOllama
from app.core.config import get_settings
from langchain_google_genai import ChatGoogleGenerativeAI

class BoundedChatOllama(ChatOllama):
    """
    A wrapper around ChatOllama that enforces a strict execution timeout on synchronous calls.
    Prevents the agent from blocking indefinitely during LangGraph execution.
    """
    def invoke(self, *args, **kwargs):
        settings = get_settings()
        timeout = settings.OLLAMA_TIMEOUT_SECONDS
        
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(super().invoke, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            raise TimeoutError(f"LLM execution exceeded {timeout} seconds configured timeout")
        finally:
            executor.shutdown(wait=False)

def get_llm(temperature: float = 0):
    """
    Factory function to get the configured LLM provider.
    """
    settings = get_settings()
    provider = settings.AI_PROVIDER.lower()
    
    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY must be configured when AI_PROVIDER is 'gemini'")
            
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=temperature,
            api_key=settings.GEMINI_API_KEY,
        )
    
    elif provider == "ollama":
        return BoundedChatOllama(model="qwen3:4b", temperature=temperature)
    
    else:
        raise ValueError(f"Invalid AI_PROVIDER: '{provider}'. Supported providers are 'ollama' and 'gemini'.")
