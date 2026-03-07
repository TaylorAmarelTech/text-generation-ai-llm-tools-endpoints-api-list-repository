# Contributing

Thanks for your interest in contributing! This project aims to be the most comprehensive directory of free and affordable LLM API endpoints.

## How to Contribute

### Adding a New Provider

1. **Edit `providers.py`** -- add a `Provider(...)` entry in the appropriate tier section
2. **Test it:** `python main.py scan --provider YourProvider`
3. **Regenerate the README:** `python main.py report`
4. **Submit a PR** with the provider name, endpoint URL, free tier details, and a link to their docs

### Updating Provider Info

Free tier limits change frequently. If you notice outdated info:

1. Update the relevant entry in `providers.py`
2. Run `python main.py report` to regenerate the README
3. Submit a PR describing what changed

### Reporting Issues

- **Provider down or limits changed?** [Open an issue](https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository/issues) with the provider name and what you observed
- **New provider suggestion?** Include the endpoint URL, free tier details, and a link to their pricing page

### Code Contributions

- Keep changes focused -- one feature or fix per PR
- Follow existing code style (no linter enforced, just be consistent)
- Test your changes: `python main.py scan` and `python main.py report`
- New tools go in `tools/`, new examples in `examples/`, new agents in `agents/`

### Writing Examples

Good examples are:
- Self-contained (copy-paste and run)
- Use `python-dotenv` for API keys
- Include a `--provider` flag where it makes sense
- Have a clear docstring explaining what the example does

## Development Setup

```bash
git clone https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository.git
cd text-generation-ai-llm-tools-endpoints-api-list-repository
pip install -r requirements.txt
cp .env.example .env
# Fill in at least one API key in .env
python main.py list          # Verify setup
python main.py scan --tier free  # Test free providers
```

## Project Structure

- `providers.py` -- Provider registry (the core data)
- `scanner.py` -- Async endpoint health checker
- `report_generator.py` -- README generator
- `main.py` -- CLI entry point
- `tools/` -- Standalone utilities (cascade, proxy, cost calculator, etc.)
- `examples/` -- Ready-to-run example scripts
- `agents/` -- LLM-powered agent framework
- `adapters/` -- API format adapters (OpenAI, Anthropic, Cohere, Google)
- `search/` -- Web search integrations for agents
- `discovery/` -- AI-powered provider discovery engine
- `plugins/` -- Extensible plugin system
- `recipes/` -- Step-by-step guides for common use cases
