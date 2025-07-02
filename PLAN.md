# 📈 Plan — ollama-cli-agent

This document outlines the high-level plan, milestones, and reasoning behind the architecture and choices in `ollama-cli-agent`.

## 🎯 Goals

- Fully local-first LLM agent CLI
- Ingest + retrieve content with persistent memory
- Respect user privacy: no external data leaks
- Modular & extensible for agent workflows

## 🧱 Stack Justification

| Component        | Reason                                           |
|------------------|--------------------------------------------------|
| Ollama + llama.cpp | Efficient local inference & open model support |
| Qdrant           | Fast vector search for long-term memory         |
| SerpAPI / Brave  | Web search diversity (commercial + privacy)     |
| FireCrawl        | Full-page scraping with metadata extraction     |
| Micromamba       | Lightweight Python env manager (fast, portable) |

## 🔄 Core Agent Loop

```plaintext
[input] → parse → [select tool(s)] → execute → ingest → respond
