import os
from dotenv import load_dotenv

load_dotenv()


def configure_tracing():
    """
    Enable LangSmith tracing by setting the required env vars.
    Call this once at app startup before running any LangChain/LangGraph code.
    """
    api_key = os.getenv("LANGCHAIN_API_KEY")
    project = os.getenv("LANGCHAIN_PROJECT", "research-agent")
    tracing = os.getenv("LANGCHAIN_TRACING_V2", "true")

    if not api_key:
        print("⚠️  LANGCHAIN_API_KEY not set — LangSmith tracing disabled.")
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = tracing
    os.environ["LANGCHAIN_PROJECT"] = project
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv(
        "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
    )
    print(f"✅ LangSmith tracing enabled → project: '{project}'")
    return True
