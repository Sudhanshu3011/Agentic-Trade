import os
import time
import requests
import threading
from typing import Any, List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
from langchain_openrouter import ChatOpenRouter
from langchain_core.runnables import Runnable
from core.logging import get_logger

logger = get_logger(__name__)

# ── Available OpenRouter Model Pool ──────────────────────────────────────────
DEFAULT_FREE_MODELS: List[str] = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "inclusionai/ling-3.0-flash-fin:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "google/gemma-4-31b-it:free",
    "dots-studio/dots-3-note-preview:free",
    "nvidia/nemotron-3.5-lightning:free",
]


class ModelHealthTracker:
    """
    Tracks and caches OpenRouter model availability with a fast probe check.
    """

    _cache: Dict[str, Tuple[bool, float]] = {}  # model -> (is_available, timestamp)
    _lock = threading.Lock()
    TTL_SECONDS = 60  # Cache availability status for 60s

    @classmethod
    def check_availability(cls, model_name: str, api_key: str | None) -> bool:
        now = time.time()
        with cls._lock:
            if model_name in cls._cache:
                is_avail, ts = cls._cache[model_name]
                if now - ts < cls.TTL_SECONDS:
                    return is_avail

        # Perform fast light HTTP probe check
        is_avail = True
        try:
            headers = {"Content-Type": "application/json"}
            if api_key and api_key.strip():
                headers["Authorization"] = f"Bearer {api_key.strip()}"

            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                },
                timeout=2.0,
            )
            # HTTP 200 (OK) or 401 (Auth check) means the model endpoint is online
            if resp.status_code in (200, 401):
                is_avail = True
            elif resp.status_code in (404, 429, 502, 503):
                logger.warning(
                    f"[LoadBalancer] Model probe returned HTTP {resp.status_code} | model='{model_name}'"
                )
                is_avail = False
            else:
                is_avail = True
        except Exception as exc:
            logger.warning(
                f"[LoadBalancer] Model probe failed | model='{model_name}' | error={exc}"
            )
            is_avail = False

        with cls._lock:
            cls._cache[model_name] = (is_avail, now)

        return is_avail

    @classmethod
    def check_availability_batch(cls, models: List[str], api_key: str | None) -> Dict[str, bool]:
        """Check availability of a list of models concurrently using thread pool."""
        results: Dict[str, bool] = {}
        with ThreadPoolExecutor(max_workers=min(len(models), 8)) as executor:
            futures = {executor.submit(cls.check_availability, m, api_key): m for m in models}
            for future in futures:
                model = futures[future]
                try:
                    results[model] = future.result()
                except Exception:
                    results[model] = True
        return results

    @classmethod
    def mark_degraded(cls, model_name: str) -> None:
        """Mark a model as temporarily degraded when a request fails."""
        with cls._lock:
            cls._cache[model_name] = (False, time.time())
            logger.warning(f"[LoadBalancer] Marked model degraded | model='{model_name}'")


class OpenRouterLoadBalancer:
    """
    Load balances and manages fallbacks across OpenRouter model pool.
    - Round-robin primary model rotation for equal load distribution.
    - Concurrent pre-call probe checking to prioritize healthy models.
    - Automatic dynamic fallbacks via LangChain RunnableWithFallbacks.
    """

    _lock = threading.Lock()
    _counter = 0

    def __init__(
        self,
        api_key: str | None = None,
        base_models: List[str] | None = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.kwargs = kwargs

        raw_pool = list(base_models or DEFAULT_FREE_MODELS)
        env_model = os.getenv("OPEN_ROUTER_MODEL")
        if env_model:
            raw_pool.insert(0, env_model)

        # Deduplicate pool while preserving order
        self.model_pool = list(dict.fromkeys(raw_pool))

    def _get_ordered_models(self) -> List[str]:
        with OpenRouterLoadBalancer._lock:
            idx = OpenRouterLoadBalancer._counter
            OpenRouterLoadBalancer._counter += 1

        n = len(self.model_pool)
        if n == 0:
            return DEFAULT_FREE_MODELS

        start_idx = idx % n
        rotated = self.model_pool[start_idx:] + self.model_pool[:start_idx]

        # Check availability of models concurrently
        availability = ModelHealthTracker.check_availability_batch(rotated, self.api_key)

        healthy = [m for m in rotated if availability.get(m, True)]
        degraded = [m for m in rotated if not availability.get(m, True)]

        # Combine: healthy models first, degraded models at the end as last-resort fallbacks
        ordered = healthy + degraded if healthy else rotated
        logger.info(
            f"[LoadBalancer] Round-robin call #{idx} | primary='{ordered[0]}' | pool_size={len(ordered)} | healthy={len(healthy)}"
        )
        return ordered

    def get_runnable(self, structured_schema: Any = None) -> Runnable:
        ordered_models = self._get_ordered_models()

        runnables = []
        for model_name in ordered_models:
            llm_kwargs = dict(self.kwargs)
            llm_kwargs["model"] = model_name
            if self.api_key:
                llm_kwargs["openrouter_api_key"] = self.api_key

            llm_inst = ChatOpenRouter(**llm_kwargs)

            if structured_schema is not None:
                runnables.append(llm_inst.with_structured_output(structured_schema))
            else:
                runnables.append(llm_inst)

        primary = runnables[0]
        fallbacks = runnables[1:]

        return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))

    def with_structured_output(self, schema: Any, **kwargs) -> Runnable:
        return self.get_runnable(structured_schema=schema)

    def invoke(self, input_val: Any, config: Any = None, **kwargs) -> Any:
        return self.get_runnable().invoke(input_val, config=config, **kwargs)

    def stream(self, input_val: Any, config: Any = None, **kwargs) -> Any:
        return self.get_runnable().stream(input_val, config=config, **kwargs)

