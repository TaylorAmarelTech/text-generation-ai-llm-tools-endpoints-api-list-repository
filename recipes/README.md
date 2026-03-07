# Recipes: Real-World Use Cases

Step-by-step guides for common tasks using free LLM endpoints.

## Quick Reference

| Recipe | Use Case | Providers | Difficulty |
|:-------|:---------|:----------|:-----------|
| [Chatbot](#chatbot) | Build a conversational chatbot | Any | Beginner |
| [RAG System](#rag-system) | Answer questions from your documents | Any | Intermediate |
| [Content Pipeline](#content-pipeline) | Generate, review, and refine content | Multiple | Intermediate |
| [Data Extraction](#data-extraction) | Pull structured data from unstructured text | Groq, Gemini | Beginner |
| [Code Assistant](#code-assistant) | Generate, review, and debug code | Any | Beginner |
| [Research Agent](#research-agent) | Search the web and synthesize answers | Any + Search API | Intermediate |
| [Multi-Provider Failover](#multi-provider-failover) | Never go down with cascade fallback | Multiple | Intermediate |
| [Batch Processing](#batch-processing) | Process hundreds of prompts efficiently | Any | Intermediate |
| [Cost Optimization](#cost-optimization) | Minimize costs with smart routing | Multiple | Advanced |
| [Monitoring Dashboard](#monitoring-dashboard) | Track usage, latency, and errors | All | Advanced |

---

## Chatbot

Build a conversational chatbot with memory in under 20 lines:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)
messages = [{"role": "system", "content": "You are a helpful assistant."}]

while True:
    user_input = input("You: ")
    if user_input.lower() in ("quit", "exit"):
        break
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=messages, max_tokens=1024
    )
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    print(f"Bot: {reply}\n")
```

**Tips:**
- Use `examples/interactive_chat.py` for a ready-made version with `/clear` and `/system` commands
- Add `tools/conversation.py` to save/load chat histories
- Switch providers by changing `base_url` and `api_key`

---

## RAG System

Retrieval-Augmented Generation: answer questions using your own documents.

```python
# 1. Index your documents (using the built-in TF-IDF store)
from examples.rag_pipeline import SimpleVectorStore

store = SimpleVectorStore()
store.add_documents([
    "Your document text here...",
    "Another document...",
])

# 2. Retrieve relevant context
results = store.search("your question", top_k=3)
context = "\n\n".join(doc for doc, score in results)

# 3. Generate answer with context
from openai import OpenAI
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key="...")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{
        "role": "user",
        "content": f"Answer based on this context:\n{context}\n\nQuestion: your question"
    }],
    temperature=0.3,
)
```

**For production:**
- Replace `SimpleVectorStore` with a real vector DB (Chroma, Pinecone, Qdrant)
- Use `examples/embeddings.py` providers for real embeddings
- See `examples/rag_pipeline.py` for a complete runnable demo

---

## Content Pipeline

Generate, review, and refine content using multiple models:

```python
from agents import CodeAgent, BaseAgent

# Step 1: Generate draft with a fast model
writer = BaseAgent("groq")
writer.config.system_prompt = "You are a technical blog writer."
draft = writer.chat("Write a blog post about Python async programming")

# Step 2: Review with a different model for diverse feedback
reviewer = BaseAgent("gemini")
reviewer.config.system_prompt = "You are an editor. Review for clarity and accuracy."
feedback = reviewer.chat(f"Review this draft:\n\n{draft}")

# Step 3: Refine based on feedback
writer.chat(f"Revise the draft based on this feedback:\n\n{feedback}")
```

---

## Data Extraction

Extract structured data from unstructured text:

```python
from agents import DataExtractorAgent

agent = DataExtractorAgent("groq")

# Extract entities
text = "Apple CEO Tim Cook announced the iPhone 16 at $799 in Cupertino on Sept 9, 2024."
entities = agent.extract_entities(text)
# {"people": ["Tim Cook"], "organizations": ["Apple"], "locations": ["Cupertino"], ...}

# Extract with custom schema
data = agent.extract(text, {
    "company": "string",
    "product": "string",
    "price": "number",
    "date": "string",
})

# Extract tabular data from prose
table = agent.extract_table(report_text, columns=["quarter", "revenue", "growth"])
```

---

## Code Assistant

Generate, review, and debug code:

```python
from agents import CodeAgent

agent = CodeAgent("groq", language="python")

# Generate code
code = agent.generate("a function that finds all prime numbers up to N using Sieve of Eratosthenes")

# Review existing code
feedback = agent.review("""
def sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i] < arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
""")

# Debug with error message
fix = agent.debug(
    "def divide(a, b): return a / b",
    "ZeroDivisionError: division by zero"
)

# Explain code
explanation = agent.explain("lambda f: (lambda x: x(x))(lambda x: f(lambda *a: x(x)(*a)))")
```

---

## Research Agent

Search the web and synthesize comprehensive answers:

```python
from agents import ResearchAgent
from search import get_available_search

# Requires BRAVE_API_KEY, SERPER_API_KEY, or GOOGLE_API_KEY
search = get_available_search()
agent = ResearchAgent("groq", search_provider=search)

answer = agent.chat("What are the pros and cons of Rust vs Go for backend development?")
# Agent will search, read pages, and synthesize an answer with citations
```

See `examples/research_demo.py` for a complete runnable demo.

---

## Multi-Provider Failover

Never go down -- cascade through providers automatically:

```python
from tools.cascade import CascadeClient

client = CascadeClient()  # Uses all providers from .env

# Simple call (auto-failover)
response = client.chat("Explain quantum computing")

# Streaming (auto-failover)
for chunk in client.chat_stream("Write a haiku"):
    print(chunk, end="", flush=True)
```

Or use the adapter pattern for non-OpenAI providers:

```python
from adapters import get_adapter, ChatMessage

# Same interface, different backends
for provider_type in ["openai", "anthropic", "cohere", "google"]:
    adapter = get_adapter(provider_type, model="...")
    response = adapter.simple_chat("Hello!")
```

---

## Batch Processing

Process hundreds of prompts efficiently with concurrency control:

```python
import asyncio
import httpx

async def batch_complete(prompts, base_url, api_key, model, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def single(prompt):
        async with semaphore:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                    timeout=30,
                )
                return resp.json()["choices"][0]["message"]["content"]

    return await asyncio.gather(*[single(p) for p in prompts])
```

See `examples/batch_async.py` for a complete example with error handling and stats.

---

## Cost Optimization

Minimize costs by routing to the cheapest provider that fits:

```python
from tools.cost_calculator import CostCalculator
from tools.rate_limiter import RateLimiter

calc = CostCalculator()
limiter = RateLimiter()

# Find the cheapest provider for your workload
print(calc.summary(input_tokens=1000, output_tokens=500))

# Estimate monthly spend before committing
from tools.cost_calculator import estimate_monthly_cost
monthly = estimate_monthly_cost("deepseek", requests_per_day=100)
print(f"Estimated monthly cost: ${monthly['monthly_cost']:.2f}")

# Smart routing: try free providers first, fall back to cheapest paid
FREE_PROVIDERS = ["groq", "cerebras", "mistral", "gemini", "openrouter"]

def smart_route(prompt):
    for provider in FREE_PROVIDERS:
        if limiter.can_request(provider):
            # Make request...
            limiter.record_request(provider, tokens=100)
            return response
    # All free providers rate limited -- use cheapest paid
    fallback = calc.cheapest_paid(input_tokens=500, output_tokens=200)
    print(f"Falling back to {fallback['provider']} (${fallback['cost']:.6f}/req)")
    # Make request to fallback...
```

**Tip:** Use `python main.py costs` to see a full pricing comparison table from the CLI.

---

## Monitoring Dashboard

Track usage across all providers:

```python
from tools.rate_limiter import RateLimiter

limiter = RateLimiter()

# After each request, record stats
limiter.record_request("groq", tokens=150, latency_ms=230)
limiter.record_request("gemini", tokens=200, latency_ms=450)

# View summary
print(limiter.summary())
# Provider Usage Summary:
# ============================================================
#   gemini          |     1 reqs |      200 tokens | avg 450ms | remaining: 14 RPM, 249 RPD
#   groq            |     1 reqs |      150 tokens | avg 230ms | remaining: 29 RPM, 999 RPD

# Check remaining quota
print(limiter.remaining("groq"))  # {"rpm": 29, "rpd": 999}

# Export conversation histories
from tools.conversation import ConversationManager
manager = ConversationManager()
conv = manager.new("Debug Session", provider="groq", model="llama-3.3-70b")
conv.add_message("user", "Fix this bug...")
manager.save(conv)
manager.save(conv, format="md")  # Also save as readable Markdown
```
