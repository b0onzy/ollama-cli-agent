
---

### ✅ `task.md` — *What Cole uses to stay on track (daily/weekly tasks)*

```markdown
# ✅ Tasks — ollama-cli-agent

Track immediate dev goals and bugs.

## 🛠️ Core Tasks

- [x] Setup CLI REPL (ingest, ask, fetch, search, exit)
- [x] Connect Ollama to agent.py
- [x] Integrate SerpAPI / Brave tool
- [x] Add FireCrawl support
- [x] Qdrant setup + test vector storage

## 🧪 Tests & QA

- [ ] Add more tests to cover failed search/fetch
- [ ] Mock tool APIs for testability
- [ ] CLI commands unit tests

## 🧹 UX Polish

- [ ] Add `help` command for REPL
- [ ] Graceful error handling (tool fails)
- [ ] Better feedback on ingest success

## 🔌 Plugins (future)

- [ ] Git repo reader plugin
- [ ] `.md` summary plugin
- [ ] Simple RAG over local folder

## 🌐 Optional UI

- [ ] Chainlit prototype for web front-end
- [ ] WebSocket bridge for UI ↔ CLI agent
