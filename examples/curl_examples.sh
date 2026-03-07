#!/usr/bin/env bash
# ============================================================
# cURL Examples for Free LLM API Endpoints
# ============================================================
# Each provider uses the OpenAI-compatible /chat/completions format.
# Replace YOUR_*_KEY with your actual API key.
#
# Usage:
#   export GROQ_API_KEY="your-key-here"
#   bash examples/curl_examples.sh groq
#   bash examples/curl_examples.sh all    # Test all providers
# ============================================================

set -euo pipefail

PROMPT="${2:-Explain quantum computing in one sentence.}"

# --- Provider definitions ---

call_groq() {
  echo "=== Groq (llama-3.3-70b-versatile) ==="
  curl -s https://api.groq.com/openai/v1/chat/completions \
    -H "Authorization: Bearer ${GROQ_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"llama-3.3-70b-versatile\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_gemini() {
  echo "=== Google Gemini (gemini-2.0-flash) ==="
  curl -s "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
    -H "Authorization: Bearer ${GEMINI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"gemini-2.0-flash\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_cerebras() {
  echo "=== Cerebras (llama-3.3-70b) ==="
  curl -s https://api.cerebras.ai/v1/chat/completions \
    -H "Authorization: Bearer ${CEREBRAS_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"llama-3.3-70b\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_mistral() {
  echo "=== Mistral (mistral-small-latest) ==="
  curl -s https://api.mistral.ai/v1/chat/completions \
    -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"mistral-small-latest\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_openrouter() {
  echo "=== OpenRouter (deepseek-r1:free) ==="
  curl -s https://openrouter.ai/api/v1/chat/completions \
    -H "Authorization: Bearer ${OPENROUTER_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"deepseek/deepseek-r1:free\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_github() {
  echo "=== GitHub Models (gpt-4o) ==="
  curl -s https://models.inference.ai.azure.com/chat/completions \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"gpt-4o\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_huggingface() {
  echo "=== HuggingFace (Qwen2.5-72B) ==="
  curl -s https://router.huggingface.co/v1/chat/completions \
    -H "Authorization: Bearer ${HUGGINGFACE_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"Qwen/Qwen2.5-72B-Instruct\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_sambanova() {
  echo "=== SambaNova (Llama-3.3-70B) ==="
  curl -s https://api.sambanova.ai/v1/chat/completions \
    -H "Authorization: Bearer ${SAMBANOVA_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"Meta-Llama-3.3-70B-Instruct\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_deepseek() {
  echo "=== DeepSeek (deepseek-chat) ==="
  curl -s https://api.deepseek.com/v1/chat/completions \
    -H "Authorization: Bearer ${DEEPSEEK_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"deepseek-chat\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

call_xai() {
  echo "=== xAI / Grok (grok-3-mini) ==="
  curl -s https://api.x.ai/v1/chat/completions \
    -H "Authorization: Bearer ${XAI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"grok-3-mini\",
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
      \"max_tokens\": 200
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(failed)"
  echo
}

# --- Main ---

case "${1:-help}" in
  groq)       call_groq ;;
  gemini)     call_gemini ;;
  cerebras)   call_cerebras ;;
  mistral)    call_mistral ;;
  openrouter) call_openrouter ;;
  github)     call_github ;;
  huggingface) call_huggingface ;;
  sambanova)  call_sambanova ;;
  deepseek)   call_deepseek ;;
  xai)        call_xai ;;
  all)
    for provider in groq gemini cerebras mistral openrouter github huggingface sambanova deepseek xai; do
      call_$provider 2>/dev/null || true
    done
    ;;
  *)
    echo "Usage: bash examples/curl_examples.sh <provider|all> [prompt]"
    echo ""
    echo "Providers: groq, gemini, cerebras, mistral, openrouter, github,"
    echo "           huggingface, sambanova, deepseek, xai"
    echo ""
    echo "Example:"
    echo "  export GROQ_API_KEY='your-key'"
    echo "  bash examples/curl_examples.sh groq 'What is AI?'"
    ;;
esac
