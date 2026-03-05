"""
Comprehensive registry of LLM text-generation API providers.

Each provider entry contains:
  - tier: classification (free, generous_free, free_credits, freemium, payg, router, local)
  - endpoint: base URL (OpenAI-compatible where possible)
  - env_key: environment variable name for the API key
  - auth_style: how auth works ("bearer", "x-api-key", "query", "none")
  - free_limits: human-readable description of free quota
  - models: list of notable/best models
  - openai_compatible: whether you can use the OpenAI SDK
  - signup_url: where to get an API key
  - test_model: model ID to use when probing the endpoint
  - notes: any extra context
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Tier(str, Enum):
    FREE = "free"
    GENEROUS_FREE = "generous_free"
    FREE_CREDITS = "free_credits"
    FREEMIUM = "freemium"
    PAYG = "payg"
    ROUTER = "router"
    LOCAL = "local"

    @property
    def label(self) -> str:
        return {
            "free": "Truly Free (no credit card, ongoing)",
            "generous_free": "Generous Free Tier (notable limitations)",
            "free_credits": "Free Credits on Signup (one-time, may expire)",
            "freemium": "Freemium (credit card required)",
            "payg": "Pay-per-use (no free tier, very cheap)",
            "router": "Routers / Aggregators",
            "local": "Local / Self-hosted (unlimited, free forever)",
        }[self.value]


@dataclass
class Provider:
    name: str
    tier: Tier
    endpoint: str
    env_key: str | None = None
    auth_style: str = "bearer"
    free_limits: str = ""
    models: list[str] = field(default_factory=list)
    openai_compatible: bool = True
    signup_url: str = ""
    test_model: str = ""
    notes: str = ""
    # Populated at scan time
    status: str = "unknown"
    latency_ms: float | None = None
    error_detail: str = ""


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

PROVIDERS: list[Provider] = [
    # ======== TIER 1: TRULY FREE ========
    Provider(
        name="Google Gemini",
        tier=Tier.FREE,
        endpoint="https://generativelanguage.googleapis.com/v1beta/openai/",
        env_key="GEMINI_API_KEY",
        free_limits="250 RPD Flash, 100 RPD Pro",
        models=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        signup_url="https://aistudio.google.com",
        test_model="gemini-2.0-flash",
        notes="Free tier is very generous. Supports OpenAI SDK via compatibility layer.",
    ),
    Provider(
        name="Groq",
        tier=Tier.FREE,
        endpoint="https://api.groq.com/openai/v1",
        env_key="GROQ_API_KEY",
        free_limits="~1K RPD 70B, 14K RPD 8B",
        models=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b", "meta-llama/llama-4-scout-17b-16e-instruct"],
        signup_url="https://console.groq.com",
        test_model="llama-3.3-70b-versatile",
        notes="Fastest inference. Custom LPU hardware.",
    ),
    Provider(
        name="Mistral",
        tier=Tier.FREE,
        endpoint="https://api.mistral.ai/v1",
        env_key="MISTRAL_API_KEY",
        free_limits="1B tokens/mo per model",
        models=["mistral-large-latest", "mistral-small-latest", "open-mistral-nemo"],
        signup_url="https://console.mistral.ai",
        test_model="mistral-small-latest",
        notes="French AI lab. Excellent multilingual support.",
    ),
    Provider(
        name="Cerebras",
        tier=Tier.FREE,
        endpoint="https://api.cerebras.ai/v1",
        env_key="CEREBRAS_API_KEY",
        free_limits="1M tokens/day, 8K context",
        models=["llama-3.3-70b", "llama-3.1-8b", "qwen-3-32b"],
        signup_url="https://cloud.cerebras.ai",
        test_model="llama-3.3-70b",
        notes="Wafer-scale inference. Extremely fast.",
    ),
    Provider(
        name="OpenRouter",
        tier=Tier.FREE,
        endpoint="https://openrouter.ai/api/v1",
        env_key="OPENROUTER_API_KEY",
        free_limits="25+ free models, 50 RPD each",
        models=["deepseek/deepseek-r1:free", "meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen3-235b-a22b:free"],
        signup_url="https://openrouter.ai",
        test_model="deepseek/deepseek-r1:free",
        notes="Aggregator with 25+ permanently free model variants.",
    ),
    Provider(
        name="Cloudflare Workers AI",
        tier=Tier.FREE,
        endpoint="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
        env_key="CLOUDFLARE_API_TOKEN",
        auth_style="bearer",
        free_limits="10K neurons/day",
        models=["@cf/meta/llama-3.3-70b-instruct-fp8-fast", "@cf/qwen/qwen2.5-coder-32b-instruct"],
        signup_url="https://dash.cloudflare.com",
        test_model="@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        notes="Requires CLOUDFLARE_ACCOUNT_ID env var too. Edge inference.",
    ),
    Provider(
        name="GitHub Models",
        tier=Tier.FREE,
        endpoint="https://models.inference.ai.azure.com",
        env_key="GITHUB_TOKEN",
        free_limits="50-150 RPD, 8K token limit",
        models=["gpt-4o", "Meta-Llama-3.1-70B-Instruct", "Mistral-large-2411"],
        signup_url="https://github.com/marketplace/models",
        test_model="gpt-4o",
        notes="Uses your GitHub PAT. Great for prototyping.",
    ),
    Provider(
        name="Zhipu (GLM)",
        tier=Tier.FREE,
        endpoint="https://open.bigmodel.cn/api/paas/v4",
        env_key="ZHIPU_API_KEY",
        free_limits="GLM-4-Flash unlimited, no quota",
        models=["glm-4-flash", "glm-4-plus"],
        signup_url="https://open.bigmodel.cn",
        test_model="glm-4-flash",
        notes="Chinese AI lab. GLM-4-Flash is completely free with no rate limits.",
    ),
    Provider(
        name="OVHcloud AI Endpoints",
        tier=Tier.FREE,
        endpoint="https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
        env_key="OVHCLOUD_API_KEY",
        auth_style="bearer",
        free_limits="2 RPM anon, 400 RPM with auth",
        models=["Meta-Llama-3_1-70B-Instruct", "Qwen2.5-72B-Instruct"],
        signup_url="https://ovhcloud.com",
        test_model="Meta-Llama-3_1-70B-Instruct",
        notes="European cloud. Can work without auth at reduced rate.",
    ),
    Provider(
        name="HuggingFace Inference",
        tier=Tier.FREE,
        endpoint="https://router.huggingface.co/v1",
        env_key="HUGGINGFACE_API_KEY",
        free_limits="~300 req/hr",
        models=["Qwen/Qwen2.5-72B-Instruct", "meta-llama/Llama-3.3-70B-Instruct"],
        signup_url="https://huggingface.co",
        test_model="Qwen/Qwen2.5-72B-Instruct",
        notes="Also offers free Inference Endpoints (serverless). Huge model catalog.",
    ),
    Provider(
        name="Cohere",
        tier=Tier.FREE,
        endpoint="https://api.cohere.com/v2",
        env_key="COHERE_API_KEY",
        free_limits="1,000 calls/month forever",
        models=["command-r-plus", "command-r", "command-light"],
        signup_url="https://dashboard.cohere.com",
        test_model="command-r",
        notes="Great for RAG/search. Aya models for 23 languages.",
    ),
    Provider(
        name="NVIDIA NIM",
        tier=Tier.FREE,
        endpoint="https://integrate.api.nvidia.com/v1",
        env_key="NVIDIA_API_KEY",
        free_limits="1K-5K credits, 40 RPM",
        models=["meta/llama-3.3-70b-instruct", "deepseek-ai/deepseek-r1"],
        signup_url="https://build.nvidia.com",
        test_model="meta/llama-3.3-70b-instruct",
        notes="NVIDIA's inference microservices. Generous free credits.",
    ),
    Provider(
        name="Glhf.chat",
        tier=Tier.FREE,
        endpoint="https://glhf.chat/api/openai/v1",
        env_key="GLHF_API_KEY",
        free_limits="Free tier, 30 RPM",
        models=["hf:meta-llama/Llama-3.3-70B-Instruct", "hf:Qwen/Qwen2.5-72B-Instruct"],
        signup_url="https://glhf.chat",
        test_model="hf:meta-llama/Llama-3.3-70B-Instruct",
        notes="Run any HuggingFace model via vLLM. Prefix model IDs with 'hf:'.",
    ),
    Provider(
        name="Chutes.ai",
        tier=Tier.FREE,
        endpoint="https://api.chutes.ai/v1",
        env_key="CHUTES_API_KEY",
        free_limits="~200 RPD",
        models=["deepseek-ai/DeepSeek-R1", "meta-llama/Llama-3.3-70B-Instruct"],
        signup_url="https://chutes.ai",
        test_model="meta-llama/Llama-3.3-70B-Instruct",
        notes="Decentralized GPU network. Free tier available.",
    ),
    Provider(
        name="Venice.ai",
        tier=Tier.FREE,
        endpoint="https://api.venice.ai/api/v1",
        env_key="VENICE_API_KEY",
        free_limits="10 prompts/day free",
        models=["llama-3.3-70b", "qwen-2.5-72b"],
        signup_url="https://venice.ai",
        test_model="llama-3.3-70b",
        notes="Privacy-focused. Uncensored models. May need credits for API.",
    ),

    # ======== TIER 2: GENEROUS FREE TIER ========
    Provider(
        name="Fireworks AI",
        tier=Tier.GENEROUS_FREE,
        endpoint="https://api.fireworks.ai/inference/v1",
        env_key="FIREWORKS_API_KEY",
        free_limits="10 RPM, $1 trial credits",
        models=["accounts/fireworks/models/llama-v3p3-70b-instruct", "accounts/fireworks/models/deepseek-v3"],
        signup_url="https://fireworks.ai",
        test_model="accounts/fireworks/models/llama-v3p3-70b-instruct",
        notes="Very fast. Supports function calling on open models.",
    ),
    Provider(
        name="AIMLAPI",
        tier=Tier.GENEROUS_FREE,
        endpoint="https://api.aimlapi.com/v1",
        env_key="AIMLAPI_API_KEY",
        free_limits="10 req/hr, 50K credits",
        models=["gpt-4o", "claude-3-5-sonnet", "meta-llama/Llama-3.3-70B-Instruct-Turbo"],
        signup_url="https://aimlapi.com",
        test_model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        notes="Aggregator with 300+ models including GPT, Claude, open-source.",
    ),
    Provider(
        name="Inference.net",
        tier=Tier.GENEROUS_FREE,
        endpoint="https://api.inference.net/v1",
        env_key="INFERENCE_NET_API_KEY",
        free_limits="$1 + $25 (survey)",
        models=["deepseek-ai/DeepSeek-R1", "meta-llama/Llama-3.1-70B-Instruct"],
        signup_url="https://inference.net",
        test_model="meta-llama/Llama-3.1-70B-Instruct",
        notes="Decentralized inference. Complete survey for extra credits.",
    ),
    Provider(
        name="NLP Cloud",
        tier=Tier.GENEROUS_FREE,
        endpoint="https://api.nlpcloud.io/v1",
        env_key="NLPCLOUD_API_KEY",
        auth_style="bearer",
        free_limits="3 RPM ongoing, $15 credits",
        models=["finetuned-llama-3-70b", "chatdolphin"],
        openai_compatible=False,
        signup_url="https://nlpcloud.com",
        test_model="finetuned-llama-3-70b",
        notes="Also has NER, summarization, translation. Custom API format.",
    ),
    Provider(
        name="Coze (ByteDance)",
        tier=Tier.GENEROUS_FREE,
        endpoint="https://api.coze.com/v1",
        env_key="COZE_API_KEY",
        free_limits="Free tier (bot-based)",
        models=["Via bots: GPT-4o, Gemini, Claude"],
        signup_url="https://coze.com",
        test_model="",
        notes="Build bots that call underlying LLMs. ByteDance platform.",
    ),

    # ======== TIER 3: FREE CREDITS ON SIGNUP ========
    Provider(
        name="xAI / Grok",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.x.ai/v1",
        env_key="XAI_API_KEY",
        free_limits="$25 + $150/mo (data sharing)",
        models=["grok-3", "grok-3-mini", "grok-2"],
        signup_url="https://console.x.ai",
        test_model="grok-3-mini",
        notes="$150/mo free if you allow data sharing. 2M context window on Grok 3.",
    ),
    Provider(
        name="DeepSeek",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.deepseek.com/v1",
        env_key="DEEPSEEK_API_KEY",
        free_limits="5M tokens (30 days)",
        models=["deepseek-chat", "deepseek-reasoner"],
        signup_url="https://platform.deepseek.com",
        test_model="deepseek-chat",
        notes="Cheapest frontier model. $0.014/M for cache hits. V3 is 685B MoE.",
    ),
    Provider(
        name="DeepInfra",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.deepinfra.com/v1/openai",
        env_key="DEEPINFRA_API_KEY",
        free_limits="$5 credits",
        models=["meta-llama/Llama-3.3-70B-Instruct", "deepseek-ai/DeepSeek-R1"],
        signup_url="https://deepinfra.com",
        test_model="meta-llama/Llama-3.3-70B-Instruct",
        notes="100+ models. Very competitive pricing after credits.",
    ),
    Provider(
        name="SambaNova",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.sambanova.ai/v1",
        env_key="SAMBANOVA_API_KEY",
        free_limits="$5 credits + free tier (3 months)",
        models=["Meta-Llama-3.1-405B-Instruct", "Meta-Llama-3.3-70B-Instruct"],
        signup_url="https://cloud.sambanova.ai",
        test_model="Meta-Llama-3.3-70B-Instruct",
        notes="Custom RDU hardware. Fast inference on large models.",
    ),
    Provider(
        name="Together AI",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.together.xyz/v1",
        env_key="TOGETHER_API_KEY",
        free_limits="$5 credits",
        models=["meta-llama/Llama-3.3-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-R1"],
        signup_url="https://together.ai",
        test_model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        notes="200+ models. Great fine-tuning support.",
    ),
    Provider(
        name="AI21 Labs",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.ai21.com/studio/v1",
        env_key="AI21_API_KEY",
        free_limits="$10 credits (3 months)",
        models=["jamba-1.5-large", "jamba-1.5-mini"],
        signup_url="https://studio.ai21.com",
        test_model="jamba-1.5-mini",
        notes="SSM-Transformer hybrid (Jamba). 256K context.",
    ),
    Provider(
        name="Upstage",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.upstage.ai/v1/solar",
        env_key="UPSTAGE_API_KEY",
        free_limits="$10 credits (3 months)",
        models=["solar-pro"],
        signup_url="https://console.upstage.ai",
        test_model="solar-pro",
        notes="Korean AI lab. Solar Pro 3 is a 102B MoE model.",
    ),
    Provider(
        name="Scaleway",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.scaleway.ai/v1",
        env_key="SCALEWAY_API_KEY",
        free_limits="1M tokens (one-time)",
        models=["llama-3.3-70b-instruct", "deepseek-r1"],
        signup_url="https://console.scaleway.com",
        test_model="llama-3.3-70b-instruct",
        notes="European cloud provider. GDPR-compliant.",
    ),
    Provider(
        name="Alibaba DashScope",
        tier=Tier.FREE_CREDITS,
        endpoint="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        env_key="DASHSCOPE_API_KEY",
        free_limits="1M tokens/model",
        models=["qwen-max", "qwen-plus", "qwen-turbo"],
        signup_url="https://alibabacloud.com",
        test_model="qwen-turbo",
        notes="Alibaba Cloud's AI platform. Qwen model family.",
    ),
    Provider(
        name="Nebius AI Studio",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.studio.nebius.ai/v1",
        env_key="NEBIUS_API_KEY",
        free_limits="$1 credits",
        models=["meta-llama/Llama-3.1-70B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"],
        signup_url="https://studio.nebius.ai",
        test_model="meta-llama/Llama-3.1-70B-Instruct",
        notes="Yandex spin-off. European GPU cloud.",
    ),
    Provider(
        name="Kluster.ai",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.kluster.ai/v1",
        env_key="KLUSTER_API_KEY",
        free_limits="$5 credits",
        models=["Meta-Llama-3.1-405B-Instruct", "Qwen2.5-72B-Instruct"],
        signup_url="https://kluster.ai",
        test_model="Qwen2.5-72B-Instruct",
        notes="Batch inference specialist. Good for high-throughput.",
    ),
    Provider(
        name="Friendli",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.friendli.ai/v1",
        env_key="FRIENDLI_API_KEY",
        free_limits="$10 credits",
        models=["meta-llama-3.3-70b-instruct", "mixtral-8x7b-instruct-v0-1"],
        signup_url="https://friendli.ai",
        test_model="meta-llama-3.3-70b-instruct",
        notes="Korean inference startup. Fast and cost-effective.",
    ),
    Provider(
        name="Hyperbolic",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.hyperbolic.xyz/v1",
        env_key="HYPERBOLIC_API_KEY",
        free_limits="$1-$50 credits",
        models=["deepseek-ai/DeepSeek-V3", "meta-llama/Llama-3.3-70B-Instruct"],
        signup_url="https://app.hyperbolic.xyz",
        test_model="meta-llama/Llama-3.3-70B-Instruct",
        notes="Decentralized compute. Variable free credits.",
    ),
    Provider(
        name="Novita AI",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.novita.ai/v3/openai",
        env_key="NOVITA_API_KEY",
        free_limits="$0.50 credits (1 year)",
        models=["meta-llama/llama-3.3-70b-instruct"],
        signup_url="https://novita.ai",
        test_model="meta-llama/llama-3.3-70b-instruct",
        notes="Also has image generation and training.",
    ),
    Provider(
        name="SiliconCloud (SiliconFlow)",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.siliconflow.cn/v1",
        env_key="SILICONFLOW_API_KEY",
        free_limits="Small credits on signup",
        models=["deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-72B-Instruct"],
        signup_url="https://siliconflow.com",
        test_model="Qwen/Qwen2.5-72B-Instruct",
        notes="Chinese inference platform. Competitive pricing.",
    ),
    Provider(
        name="Eden AI",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.edenai.co/v2",
        env_key="EDENAI_API_KEY",
        free_limits="$10 credits",
        models=["Multi-provider aggregator"],
        openai_compatible=False,
        signup_url="https://edenai.co",
        test_model="",
        notes="Aggregates OpenAI, Google, Anthropic, etc. under one API.",
    ),
    Provider(
        name="Lepton AI",
        tier=Tier.FREE_CREDITS,
        endpoint="https://api.lepton.ai/v1",
        env_key="LEPTON_API_KEY",
        free_limits="Trial credits",
        models=["llama-3.3-70b"],
        signup_url="https://lepton.ai",
        test_model="llama-3.3-70b",
        notes="Fast serverless inference.",
    ),

    # ======== TIER 4: FREEMIUM (credit card required) ========
    Provider(
        name="OpenAI",
        tier=Tier.FREEMIUM,
        endpoint="https://api.openai.com/v1",
        env_key="OPENAI_API_KEY",
        free_limits="$5 credits (3 months)",
        models=["gpt-4o", "gpt-4o-mini", "o3-mini"],
        signup_url="https://platform.openai.com",
        test_model="gpt-4o-mini",
        notes="Industry standard. Credit card required for API access.",
    ),
    Provider(
        name="Anthropic",
        tier=Tier.FREEMIUM,
        endpoint="https://api.anthropic.com/v1",
        env_key="ANTHROPIC_API_KEY",
        auth_style="x-api-key",
        free_limits="$5-10 credits",
        models=["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
        openai_compatible=False,
        signup_url="https://console.anthropic.com",
        test_model="claude-haiku-4-5-20251001",
        notes="Not OpenAI-compatible. Uses Messages API + x-api-key header.",
    ),
    Provider(
        name="Perplexity",
        tier=Tier.FREEMIUM,
        endpoint="https://api.perplexity.ai",
        env_key="PERPLEXITY_API_KEY",
        free_limits="$5/mo (with Pro subscription)",
        models=["sonar", "sonar-pro", "sonar-reasoning"],
        signup_url="https://docs.perplexity.ai",
        test_model="sonar",
        notes="Search-grounded LLM. Answers include citations.",
    ),

    # ======== TIER 5: PAY-PER-USE ========
    Provider(
        name="Moonshot / Kimi",
        tier=Tier.PAYG,
        endpoint="https://api.moonshot.cn/v1",
        env_key="MOONSHOT_API_KEY",
        free_limits="None (very cheap: $0.10/M cache hit)",
        models=["moonshot-v1-128k", "kimi-k2.5"],
        signup_url="https://platform.moonshot.ai",
        test_model="moonshot-v1-128k",
        notes="Chinese AI. 256K context. Extremely cheap with caching.",
    ),
    Provider(
        name="MiniMax",
        tier=Tier.PAYG,
        endpoint="https://api.minimax.chat/v1",
        env_key="MINIMAX_API_KEY",
        free_limits="None (8% of Claude Sonnet pricing)",
        models=["abab6.5s-chat", "abab5.5-chat"],
        signup_url="https://platform.minimax.io",
        test_model="abab5.5-chat",
        notes="Chinese AI. Very cost-effective.",
    ),

    # ======== ROUTERS / AGGREGATORS ========
    Provider(
        name="OpenRouter",
        tier=Tier.ROUTER,
        endpoint="https://openrouter.ai/api/v1",
        env_key="OPENROUTER_API_KEY",
        free_limits="25+ free models",
        models=["Unified access to 100+ models"],
        signup_url="https://openrouter.ai",
        test_model="deepseek/deepseek-r1:free",
        notes="Best aggregator. Free models available. Unified API.",
    ),
    Provider(
        name="Requesty",
        tier=Tier.ROUTER,
        endpoint="https://router.requesty.ai/v1",
        env_key="REQUESTY_API_KEY",
        free_limits="Free credits",
        models=["Routes to 500+ models"],
        signup_url="https://requesty.ai",
        test_model="",
        notes="Auto-failover between providers.",
    ),
    Provider(
        name="Portkey",
        tier=Tier.ROUTER,
        endpoint="https://api.portkey.ai/v1",
        env_key="PORTKEY_API_KEY",
        free_limits="Free tier",
        models=["Gateway to any provider"],
        signup_url="https://portkey.ai",
        test_model="",
        notes="AI gateway with observability, guardrails, caching.",
    ),
    Provider(
        name="Unify.ai",
        tier=Tier.ROUTER,
        endpoint="https://api.unify.ai/v0",
        env_key="UNIFY_API_KEY",
        free_limits="Free tier",
        models=["ML-based optimal routing"],
        signup_url="https://unify.ai",
        test_model="",
        notes="ML-based model routing. Picks optimal provider per query.",
    ),
    Provider(
        name="LiteLLM (self-hosted)",
        tier=Tier.ROUTER,
        endpoint="http://localhost:4000/v1",
        env_key=None,
        auth_style="none",
        free_limits="Free (open source)",
        models=["Proxy to 100+ providers"],
        signup_url="https://github.com/BerriAI/litellm",
        test_model="",
        notes="Open-source proxy. Unified format for all providers.",
    ),

    # ======== LOCAL / SELF-HOSTED ========
    Provider(
        name="Ollama",
        tier=Tier.LOCAL,
        endpoint="http://localhost:11434/v1",
        env_key=None,
        auth_style="none",
        free_limits="Unlimited (local)",
        models=["llama3.3", "qwen2.5", "deepseek-r1", "phi4", "gemma2"],
        signup_url="https://ollama.com",
        test_model="llama3.3",
        notes="Easiest local setup. 50+ models. OpenAI-compatible.",
    ),
    Provider(
        name="LM Studio",
        tier=Tier.LOCAL,
        endpoint="http://localhost:1234/v1",
        env_key=None,
        auth_style="none",
        free_limits="Unlimited (local)",
        models=["Any GGUF model from HuggingFace"],
        signup_url="https://lmstudio.ai",
        test_model="",
        notes="Best GUI for local models. Drag-and-drop GGUF loading.",
    ),
    Provider(
        name="llama.cpp",
        tier=Tier.LOCAL,
        endpoint="http://localhost:8080/v1",
        env_key=None,
        auth_style="none",
        free_limits="Unlimited (local)",
        models=["Any GGUF model"],
        signup_url="https://github.com/ggerganov/llama.cpp",
        test_model="",
        notes="Foundation for most local inference tools.",
    ),
    Provider(
        name="Jan.ai",
        tier=Tier.LOCAL,
        endpoint="http://localhost:1337/v1",
        env_key=None,
        auth_style="none",
        free_limits="Unlimited (local)",
        models=["Any supported model"],
        signup_url="https://jan.ai",
        test_model="",
        notes="100% offline desktop app.",
    ),
]


def get_providers_by_tier(tier: Tier) -> list[Provider]:
    """Return all providers matching a given tier."""
    return [p for p in PROVIDERS if p.tier == tier]


def get_unique_providers() -> list[Provider]:
    """Return providers deduplicated by name (prefers earlier in list)."""
    seen: set[str] = set()
    result: list[Provider] = []
    for p in PROVIDERS:
        if p.name not in seen:
            seen.add(p.name)
            result.append(p)
    return result
