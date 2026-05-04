import asyncio
import functools
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(retries: int = 3, backoff_in_seconds: int = 1):
    """
    Decorator for retrying async functions with exponential backoff.
    Standardized as per .cursor/rules.md section 5.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        logger.error(f"Retries exhausted for {func.__name__}: {e}")
                        raise e
                    
                    sleep = (backoff_in_seconds * 2 ** x)
                    logger.warning(f"Retrying {func.__name__} in {sleep}s... (Attempt {x+1}/{retries})")
                    await asyncio.sleep(sleep)
                    x += 1
        return wrapper
    return decorator

async def safe_mode_fallback(query: str):
    """
    Fallback mechanism when RAG fails.
    Logic documented in ADR 003.
    """
    return {
        "answer": "System is in Safe Mode. Showing best-effort results from local cache.",
        "confidence": 0.1,
        "is_fallback": True
    }
