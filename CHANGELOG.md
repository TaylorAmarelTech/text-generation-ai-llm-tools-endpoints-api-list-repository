# Changelog

All notable changes to this project are documented here.

## [0.4.0] - 2026-03-07

### Added
- `tools/cost_calculator.py`: Cross-provider pricing comparison with monthly cost estimates
- `tools/token_counter.py`: Token estimation without external dependencies
- `examples/curl_examples.sh`: cURL commands for 10 providers (no Python needed)
- `examples/oneliners.py`: One-liner per provider with `list` and `all` modes
- CLI commands: `python main.py costs` and `python main.py tokens`
- `CONTRIBUTING.md` with development setup and contribution guidelines
- `.gitattributes` for consistent line endings across platforms
- GitHub issue templates (New Provider, Provider Update, Bug Report)
- GitHub PR template with checklist

### Changed
- Updated provider count to 58 unique providers
- Improved `.gitignore` with comprehensive patterns (IDE, OS, logs)
- Updated `recipes/README.md` Cost Optimization recipe to use `CostCalculator`
- Updated search queries from "2025" to "2026"
- Streamlined Contributing section in README to reference `CONTRIBUTING.md`
- Architecture diagram updated to reflect 11 CLI subcommands

### Fixed
- Untracked generated data files that were committed despite gitignore rules
- `tools/__init__.py` docstring now documents all 7 tools (was missing 4)
- Removed stale `debug.log`

## [0.3.0] - 2026-03-06

### Added
- `adapters/`: Unified interface for OpenAI, Anthropic, Cohere, and Google native APIs
- `tools/rate_limiter.py`: Per-provider rate limiting with quota tracking
- `tools/conversation.py`: Chat history save/load/export (JSON, Markdown)
- `agents/data_extractor.py`: Structured data extraction agent
- `agents/summarizer.py`: Document summarization agent
- `recipes/README.md`: 10 step-by-step use case guides

### Changed
- Provider registry expanded with new free-tier and credit-based providers
- README regenerated with API adapter and utility tool documentation

## [0.2.0] - 2026-03-05

### Added
- `examples/`: 11 ready-to-run scripts (chat, streaming, RAG, vision, embeddings, agents, batch, research)
- `agents/`: LLM-powered agent framework with BaseAgent, ReActAgent, ResearchAgent, CodeAgent
- `agents/base.py`: 8 provider presets (groq, gemini, cerebras, mistral, openrouter, github, sambanova, huggingface)
- `search/`: Web search integrations (Brave, Serper, Google CSE, web scraper)
- `tools/cascade.py`: Production cascade client with health tracking and cooldowns
- `tools/compare.py`: Side-by-side provider comparison
- `tools/proxy.py`: Local OpenAI-compatible proxy server

### Changed
- README expanded with examples, agent docs, and cascade guide

## [0.1.0] - 2026-03-05

### Added
- Initial release
- `providers.py`: Provider registry with 40+ providers across 7 tiers
- `scanner.py`: Async endpoint health checker using httpx
- `report_generator.py`: Auto-generates README.md from provider data
- `main.py`: CLI with scan, report, list, discover, benchmark, models, export, compare, proxy commands
- `config.py` + `config.yaml`: YAML config with environment variable overrides
- `discovery/`: AI-powered endpoint discovery engine with 5 strategies
- `plugins/`: Plugin system (benchmark, model_list, export, pricing, notify)
- `.env.example`: Template for 50+ optional API keys
- MIT License
