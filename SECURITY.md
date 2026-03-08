# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email **security@tayloramareltech.com** (or use [GitHub's private vulnerability reporting](https://github.com/TaylorAmarelTech/text-generation-ai-llm-tools-endpoints-api-list-repository/security/advisories/new) if enabled).

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within 48 hours and work on a fix.

## Scope

This project handles API keys via environment variables and `.env` files. Security concerns include:

- **API key exposure**: Keys should never be committed. The `.env` file is gitignored and `.env.example` contains only empty placeholders.
- **Injection via provider responses**: The scanner and agents process responses from external APIs. While responses are displayed, they are not executed.
- **Dependency vulnerabilities**: We use a minimal set of well-maintained dependencies. Run `pip audit` to check for known issues.

## Best Practices for Users

- Never commit your `.env` file
- Rotate API keys if you suspect exposure
- Use environment variables or a secrets manager in production
- Review provider responses before using them in automated pipelines
