from langchain_ollama import ChatOllama
from pydantic import BaseModel

class BoundedChatOllama(ChatOllama):
    def invoke(self, *args, **kwargs):
        print("INVOKED invoke")
        return super().invoke(*args, **kwargs)
    
    def _generate(self, *args, **kwargs):
        print("INVOKED _generate")
        return super()._generate(*args, **kwargs)

    def _stream(self, *args, **kwargs):
        print("INVOKED _stream")
        return super()._stream(*args, **kwargs)

class Schema(BaseModel):
    test: str

llm = BoundedChatOllama(model="qwen3:4b")
chain = llm.with_structured_output(Schema)
try:
    chain.invoke("hello")
except Exception as e:
    print(f"Exception: {e}")
