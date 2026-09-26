from concurrent.futures import ThreadPoolExecutor, TimeoutError
from langchain_ollama import ChatOllama
from app.core.config import get_settings

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
