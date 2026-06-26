"""
aba_model.py
LLM backends: Groq (free API), HuggingFace Inference API (free serverless),
Google AI Studio (Gemini API), Local (on-GPU via transformers/CUDA), and Mock.

Quick start:
    backend = get_backend("groq",      model="llama3-70b")     # free API
    backend = get_backend("hf_api",    model="qwen2.5-7b")     # free serverless
    backend = get_backend("google_ai", model="gemini-2.5-flash")
    backend = get_backend("local",     model="qwen2.5-7b")     # on the GPU (cluster)
    backend = get_backend("mock")                               # no GPU/key, testing
"""
from __future__ import annotations
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


# ─────────────────────────────────────────────────────────────────────────────
# Shared types
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ModelResponse:
    text: str
    model: str
    prompt_tokens:     int   = 0
    completion_tokens: int   = 0
    latency_s:         float = 0.0
    raw: Any = None


class LLMBackend(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> ModelResponse: ...

    def batch_generate(
        self, prompts: List[str], **kwargs
    ) -> List[ModelResponse]:
        return [self.generate(p, **kwargs) for p in prompts]


# ─────────────────────────────────────────────────────────────────────────────
# Groq  — free API, fast LPU inference, access to Llama 3.1 70B
# Sign up: https://console.groq.com  → copy key to GROQ_API_KEY
# ─────────────────────────────────────────────────────────────────────────────

GROQ_MODELS = {
    # model_alias          : groq_model_id
    #   https://console.groq.com/docs/models
    "llama3-70b":          "llama-3.3-70b-versatile",   # current 70B, recommended
    "llama3-8b":           "llama-3.1-8b-instant",      # faster, smaller
    "gemma2-9b":           "gemma2-9b-it",
    "gpt-oss-120b":        "openai/gpt-oss-120b",        # strong reasoning
    "gpt-oss-20b":         "openai/gpt-oss-20b",
    "qwen":                "qwen/qwen3-32b",   # good for structured output
    # pass any full id directly if you want a specific version
}


class GroqBackend(LLMBackend):
    """
    Uses the Groq API (OpenAI-compatible).
    Install: pip install groq
    Key:     set GROQ_API_KEY=gsk_...

    Rate-limit handling:
      - On a 429 (rate_limit_exceeded), reads Groq's "try again in Xs" hint and
        sleeps exactly that long, then retries (up to max_retries times).
      - `min_interval_s` enforces a minimum gap between successive requests to
        stay under the tokens-per-minute (TPM) limit proactively.

    IMPORTANT: backoff helps with per-MINUTE limits. The per-DAY / per-hour
    (TPD/TPH) caps are hard volume ceilings — no amount of sleeping gets past
    them. If you hit TPD, switch to a smaller model or reduce --n-samples /
    --n-synthetic / --max-tokens.
    """

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        max_retries: int = 5,
        min_interval_s: float = 0.0,
        max_wait_s: float = 120.0,
    ):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("Run: pip install groq")

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Set GROQ_API_KEY environment variable. "
                "Get a free key at https://console.groq.com"
            )
        from groq import Groq
        self.client = Groq(api_key=api_key)
        self.model = GROQ_MODELS.get(model, model)
        self.max_retries = max_retries
        self.min_interval_s = min_interval_s
        self.max_wait_s = max_wait_s
        self._last_call_t = 0.0

    @staticmethod
    def _parse_retry_after(message: str, default: float = 10.0) -> float:
        """Extract the wait time from Groq's 'Please try again in 9m0s' hint."""
        import re
        # Formats seen: "try again in 9m0s", "try again in 2.5s", "in 714ms"
        m = re.search(r'try again in\s+([0-9hms\.]+)', message)
        if not m:
            return default
        token = m.group(1)
        total = 0.0
        # Parse milliseconds first and strip them, so 'ms' is not mis-read as
        # minutes+seconds.
        for value in re.findall(r'([0-9.]+)\s*ms', token):
            total += float(value) / 1000.0
        token = re.sub(r'[0-9.]+\s*ms', '', token)
        for value, unit in re.findall(r'([0-9.]+)\s*(h|m|s)', token):
            v = float(value)
            if unit == "h":   total += v * 3600
            elif unit == "m": total += v * 60
            elif unit == "s": total += v
        return total if total > 0 else default

    def _throttle(self) -> None:
        """Proactively space requests to respect the per-minute budget."""
        if self.min_interval_s <= 0:
            return
        elapsed = time.time() - self._last_call_t
        if elapsed < self.min_interval_s:
            time.sleep(self.min_interval_s - elapsed)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        from groq import RateLimitError

        attempt = 0
        while True:
            self._throttle()
            t0 = time.time()
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                self._last_call_t = time.time()
                return ModelResponse(
                    text=resp.choices[0].message.content,
                    model=self.model,
                    prompt_tokens=resp.usage.prompt_tokens,
                    completion_tokens=resp.usage.completion_tokens,
                    latency_s=time.time() - t0,
                    raw=resp,
                )
            except RateLimitError as exc:
                attempt += 1
                msg = str(exc)
                wait = self._parse_retry_after(msg)
                # If the suggested wait is huge, this is a per-day/hour cap:
                # do not block for minutes — fail fast with a clear message.
                if wait > self.max_wait_s or attempt > self.max_retries:
                    raise RuntimeError(
                        f"Groq rate limit not recoverable by waiting "
                        f"(suggested wait {wait:.0f}s, attempt {attempt}). "
                        f"This is likely a per-DAY/hour cap. Switch to a smaller "
                        f"model or lower --n-samples/--n-synthetic/--max-tokens. "
                        f"Original: {msg}"
                    )
                # Recoverable per-minute limit: sleep the suggested time + jitter
                sleep_s = wait + 1.0
                print(f"      [rate limit] waiting {sleep_s:.0f}s "
                      f"(attempt {attempt}/{self.max_retries})...")
                time.sleep(sleep_s)
                self._last_call_t = time.time()


# ─────────────────────────────────────────────────────────────────────────────
# HuggingFace Inference API  — free serverless tier, no local GPU
# Sign up: https://huggingface.co  →  Settings → Access Tokens
# ─────────────────────────────────────────────────────────────────────────────

HF_MODELS = {
    "qwen2.5-7b":   "Qwen/Qwen2.5-7B-Instruct",
    "llama3-8b":    "meta-llama/Llama-3.1-8B-Instruct",
    "mistral-7b":   "mistralai/Mistral-7B-Instruct-v0.3",
    "phi3-mini":    "microsoft/Phi-3.5-mini-instruct",
    "gemma2-9b":    "google/gemma-2-9b-it",
}


class HFInferenceBackend(LLMBackend):
    """
    Calls the HuggingFace Serverless Inference API (free tier).
    No GPU needed. Rate-limited to ~100 req/day on free accounts.

    Key: set HF_TOKEN=hf_...
    """

    def __init__(
        self,
        model: str = "Qwen/Qwen2.5-7B-Instruct",
    ):
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError("Run: pip install huggingface_hub")

        token = os.environ.get("HF_TOKEN")
        if not token:
            raise EnvironmentError(
                "Set HF_TOKEN environment variable. "
                "Get a free token at https://huggingface.co/settings/tokens"
            )
        from huggingface_hub import InferenceClient
        self.model  = HF_MODELS.get(model, model)
        self.client = InferenceClient(model=self.model, token=token)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        t0 = time.time()
        # Use chat_completion for instruct models
        resp = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=max(temperature, 0.01),  # HF requires > 0
        )
        return ModelResponse(
            text=resp.choices[0].message.content,
            model=self.model,
            prompt_tokens=resp.usage.prompt_tokens,
            completion_tokens=resp.usage.completion_tokens,
            latency_s=time.time() - t0,
            raw=resp,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Google AI Studio  —  Gemini models via google-genai SDK
# Sign up: https://aistudio.google.com  → Get API key → copy to GOOGLE_API_KEY
# Install: pip install google-genai
#
# Free-tier limits (AI Studio, 2025):
#   gemini-2.5-flash :  500 req/day  10 req/min   1 M tok/min   ← recommended
#   gemini-2.0-flash : 1500 req/day  15 req/min   1 M tok/min
#   gemini-2.5-pro   :   50 req/day   5 req/min  250 K tok/min
#
# Thinking mode (gemini-2.5-*):
#   Pass thinking=True to enable the model's built-in chain-of-thought.
#   This improves accuracy on ABA tasks (folding / assumption introduction)
#   at the cost of more output tokens. Thinking tokens are NOT counted toward
#   the response max_tokens; the final answer is still capped at max_tokens.
# ─────────────────────────────────────────────────────────────────────────────

GOOGLE_MODELS: Dict[str, str] = {
    # alias              : model id used by the API
    "gemini-2.5-flash":  "gemini-2.5-flash",        # best balance — recommended
    "gemini-3.5-flash":  "gemini-3.5-flash",        # legacy fallback
    "gemini-3.5-lite":   "gemini-3.5-flash-lite",   # legacy fallback
    # short aliases
    "flash":             "gemini-2.5-flash",
    "flash-2":           "gemini-3.0-flash",
}


class GoogleAIBackend(LLMBackend):
    """
    Google AI Studio backend using the google-genai SDK.

    Install:  pip install google-genai
    Key:      set GOOGLE_API_KEY=AIza...

    Rate limits (free tier):
      - 429 errors are retried with exponential back-off up to max_retries.
      - min_interval_s proactively spaces requests (try 6–12 s for 10 RPM models).

    Thinking mode (gemini-2.5-* only):
      Pass thinking=True at construction time.  The model emits a <think> chain
      before the final answer; only the final answer is returned as ModelResponse.text.
      Use this for the cot / guided modes where multi-step reasoning matters most.
    """

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        max_retries: int = 6,
        min_interval_s: float = 0.0,
        thinking: bool = False,
    ):
        try:
            from google import genai as _genai          # noqa: F401
        except ImportError:
            raise ImportError("Run: pip install google-genai")

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Set GOOGLE_API_KEY environment variable. "
                "Get a free key at https://aistudio.google.com/apikey"
            )

        from google import genai as _genai
        self.client = _genai.Client(api_key=api_key)
        self.model = GOOGLE_MODELS.get(model, model)
        self.max_retries = max_retries
        self.min_interval_s = min_interval_s
        self.thinking = thinking
        self._last_call_t = 0.0

    def _throttle(self) -> None:
        if self.min_interval_s <= 0:
            return
        elapsed = time.time() - self._last_call_t
        if elapsed < self.min_interval_s:
            time.sleep(self.min_interval_s - elapsed)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        from google import genai as _genai
        from google.genai import types as _types

        config_kwargs: Dict[str, Any] = {
            "temperature":      temperature,
            "max_output_tokens": max_tokens,
        }
        if self.thinking:
            config_kwargs["thinking_config"] = _types.ThinkingConfig(
                thinking_budget=8192,   # up to 8 K thinking tokens
            )

        cfg = _types.GenerateContentConfig(**config_kwargs)

        attempt = 0
        while True:
            self._throttle()
            t0 = time.time()
            try:
                resp = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=cfg,
                )
                self._last_call_t = time.time()

                # Extract text — ignore any embedded <think> blocks
                text = resp.text or ""
                usage = resp.usage_metadata
                return ModelResponse(
                    text=text,
                    model=self.model,
                    prompt_tokens=getattr(usage, "prompt_token_count", 0) or 0,
                    completion_tokens=getattr(usage, "candidates_token_count", 0) or 0,
                    latency_s=time.time() - t0,
                    raw=resp,
                )
            except Exception as exc:
                msg = str(exc)
                # 429 Resource Exhausted → retry with back-off
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    attempt += 1
                    if attempt > self.max_retries:
                        raise RuntimeError(
                            f"Google AI rate limit not recoverable after "
                            f"{attempt} retries. Check your quota at "
                            f"https://aistudio.google.com/  Original: {msg}"
                        )
                    wait = min(2 ** attempt * 5, 120)   # 10 s, 20 s, 40 s…
                    print(f"      [rate limit] waiting {wait:.0f}s "
                          f"(attempt {attempt}/{self.max_retries})...")
                    time.sleep(wait)
                    self._last_call_t = time.time()
                else:
                    raise


# ─────────────────────────────────────────────────────────────────────────────
# Local  — run an open instruct model ON THE GPU via transformers (CUDA)
# For the DISI cluster: one GPU per job (L40 48 GB, or RTX 2080 Ti 11 GB).
#
# Single-GPU fit guide:
#   L40 (48 GB)         : 7B-14B in bf16; up to ~32B with --load-4bit.
#   RTX 2080 Ti (11 GB) : 7B only with --load-4bit (nf4).
#
# IMPORTANT: the home quota is tiny (400 MB), so point the HF cache at scratch:
#   export HF_HOME=/scratch.hpc/<user>/hf_cache
# The model is downloaded once into that cache and reused on later runs.
# ─────────────────────────────────────────────────────────────────────────────

LOCAL_MODELS: Dict[str, str] = {
    # alias        : HuggingFace model id  (instruct/chat variants)
    "qwen2.5-7b":  "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5-14b": "Qwen/Qwen2.5-14B-Instruct",
    "qwen2.5-32b": "Qwen/Qwen2.5-32B-Instruct",
    "llama3-8b":   "meta-llama/Llama-3.1-8B-Instruct",
    "mistral-7b":  "mistralai/Mistral-7B-Instruct-v0.3",
    "gemma2-9b":   "google/gemma-2-9b-it",
    "phi3-mini":   "microsoft/Phi-3.5-mini-instruct",
}


class LocalHFBackend(LLMBackend):
    """
    Load a HuggingFace causal-LM locally on the GPU and generate with it.

    Install (CUDA 11.8, as on the DISI cluster):
        pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu118
        pip install --no-cache-dir transformers accelerate bitsandbytes sentencepiece

    The model and tokenizer are loaded once at construction; `generate()` then
    runs purely on the GPU (no network). Gated models (Llama, Gemma) need a HF
    token: set HF_TOKEN, or run `huggingface-cli login` once.
    """

    def __init__(
        self,
        model: str = "Qwen/Qwen2.5-7B-Instruct",
        load_4bit: bool = False,
        dtype: str = "bfloat16",
        device: str = "cuda",
    ):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise ImportError(
                "Local backend needs PyTorch + transformers. Install with:\n"
                "  pip install --no-cache-dir torch "
                "--index-url https://download.pytorch.org/whl/cu118\n"
                "  pip install --no-cache-dir transformers accelerate bitsandbytes"
            )

        self.model_id = LOCAL_MODELS.get(model, model)
        token = os.environ.get("HF_TOKEN")  # for gated repos (Llama/Gemma)

        tok = AutoTokenizer.from_pretrained(self.model_id, token=token)
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token

        load_kwargs: Dict[str, Any] = {"token": token}
        if load_4bit:
            from transformers import BitsAndBytesConfig
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            load_kwargs["device_map"] = "auto"
        else:
            load_kwargs["torch_dtype"] = getattr(torch, dtype)
            load_kwargs["device_map"] = device

        model_obj = AutoModelForCausalLM.from_pretrained(self.model_id, **load_kwargs)
        model_obj.eval()

        self._torch = torch
        self.tok = tok
        self.model = model_obj
        print(f"[local] loaded {self.model_id} "
              f"({'4-bit nf4' if load_4bit else dtype}) on {model_obj.device}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        torch = self._torch
        messages = [{"role": "user", "content": prompt}]
        try:
            input_ids = self.tok.apply_chat_template(
                messages, add_generation_prompt=True, return_tensors="pt"
            ).to(self.model.device)
        except Exception:
            input_ids = self.tok(prompt, return_tensors="pt").input_ids.to(
                self.model.device
            )

        do_sample = bool(temperature and temperature > 0)
        gen_kwargs: Dict[str, Any] = dict(
            max_new_tokens=max_tokens,
            do_sample=do_sample,
            pad_token_id=self.tok.pad_token_id,
        )
        if do_sample:
            gen_kwargs.update(temperature=temperature, top_p=0.95)

        t0 = time.time()
        with torch.no_grad():
            out = self.model.generate(input_ids, **gen_kwargs)
        completion = out[0][input_ids.shape[-1]:]
        text = self.tok.decode(completion, skip_special_tokens=True)
        return ModelResponse(
            text=text,
            model=self.model_id,
            prompt_tokens=int(input_ids.shape[-1]),
            completion_tokens=int(completion.shape[-1]),
            latency_s=time.time() - t0,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Mock  — hard-coded outputs for testing without any key or GPU
# ─────────────────────────────────────────────────────────────────────────────

class MockBackend(LLMBackend):
    RESPONSES: Dict[str, str] = {
        "nixon_diamond": """
NEW RULES:
abnormal_quaker(X) :- republican(X), alpha(X).
c_alpha(X) :- quaker(X), normal_quaker(X).
pacifist(X) :- democrat(X).

NEW ASSUMPTIONS:
alpha(X) defeated_by c_alpha(X)
""",
        "flies": """
NEW RULES:
flies(X) :- bird(X), normal_bird(X).
ab_bird(X) :- penguin(X).

NEW ASSUMPTIONS:
NONE
""",
        "tax_law": """
NEW RULES:
taxable(X) :- employed(X), normal_taxpayer(X).
taxable(X) :- self_employed(X).
exempt(X) :- employed(X), not normal_taxpayer(X).

NEW ASSUMPTIONS:
NONE
""",
        "default": "NEW RULES:\nNONE\n\nNEW ASSUMPTIONS:\nNONE",
    }

    def __init__(self, delay: float = 0.05):
        self.delay = delay

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        time.sleep(self.delay)
        # Match on distinctive predicate names that appear in each problem,
        # so the mock works even after train/test splitting (which strips the
        # problem_id but keeps the predicates).
        lower = prompt.lower()
        if "pacifist" in lower or "quaker" in lower:
            text = self.RESPONSES["nixon_diamond"]
        elif "flies" in lower or "bird" in lower:
            text = self.RESPONSES["flies"]
        elif "taxable" in lower:
            text = self.RESPONSES["tax_law"]
        else:
            text = self.RESPONSES["default"]
        return ModelResponse(text=text.strip(), model="mock", latency_s=self.delay)


# ─────────────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────────────

_BACKENDS = {
    "groq":      GroqBackend,
    "hf_api":    HFInferenceBackend,
    "google_ai": GoogleAIBackend,
    "local":     LocalHFBackend,
    "mock":      MockBackend,
}


def get_backend(
    backend: str = "mock",
    model: Optional[str] = None,
    **kwargs,
) -> LLMBackend:
    """
    Convenience factory.

    Examples:
        get_backend("groq")                              # Llama 3.3 70B, free
        get_backend("groq",      model="llama3-8b")     # faster, still free
        get_backend("hf_api",    model="qwen2.5-7b")    # HF serverless, free
        get_backend("google_ai")                         # Gemini 2.5 Flash, free
        get_backend("google_ai", model="gemini-2.5-pro") # stronger, lower quota
        get_backend("google_ai", model="flash", thinking=True)  # CoT thinking mode
        get_backend("local",     model="qwen2.5-7b")     # on the GPU (CUDA)
        get_backend("local",     model="qwen2.5-32b", load_4bit=True)  # big model, 4-bit
        get_backend("mock")                              # hard-coded, for testing
    """
    cls = _BACKENDS.get(backend)
    if cls is None:
        raise ValueError(
            f"Unknown backend '{backend}'. "
            f"Available: {list(_BACKENDS.keys())}"
        )
    if model is not None:
        return cls(model=model, **kwargs)
    return cls(**kwargs)