# 🧠 ollama‑cli‑agent

*A privacy-first, terminal-based AI assistant—with real-time web access, persistent memory, and local LLM intelligence.*

---

## 🚀 Features

- **Local LLM** via Ollama + llama.cpp (`ChatOllama`)  
- **Live Web Search**: SerpAPI, Brave Search  
- **Full-page Scraping**: FireCrawl, scraped -> ingested  
- **Long-term Memory**: Qdrant vector store for retrieval-augmented responses  
- **Terminal-first Interface**: ingest, search, fetch, ask—all from your CLI  

---

## 🛠 Installation

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ollama-cli-agent.git
cd ollama-cli-agent

# 2. Setup Micromamba environment
micromamba create -n ollama-cli-agent python=3.11 -y
micromamba activate ollama-cli-agent

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure API keys (optional)
cp .env.sample .env
# Edit .env to add:
# SERPAPI_API_KEY=...    # For Google search
# BRAVE_API_KEY=...      # For Brave search
# FIRECRAWL_API_KEY=...  # For web scraping

# 5. Install and run Ollama
# Visit https://ollama.ai to install Ollama
# Then pull a model:
ollama pull mistral:7b  # Default model
ollama pull all-minilm  # Embedding model
```

---

## ⚡ Quick Start

### Starting the Assistant

```bash
# Activate the environment
micromamba activate ollama-cli-agent

# Run the assistant
python assistant.py

# Or with custom model
python assistant.py --model llama2:7b

# Or with debug logging
python assistant.py --debug
```

### Using the Assistant

Once started, you'll see the `You>` prompt. Here are the available commands:

#### 📝 **ask** - Ask questions to the AI
```
You> ask What is Python?
You> ask Explain machine learning in simple terms
You> ask How do I create a REST API?
```

#### 💾 **ingest** - Add content to memory
```
You> ingest The capital of France is Paris
You> ingest https://example.com/article
You> ingest Python is a high-level programming language
```

#### 🔍 **search** - Search the web
```
You> search latest AI news
You> search Python tutorials for beginners
You> search OpenAI GPT-4 features
```

#### 🌐 **fetch** - Fetch and display web content
```
You> fetch https://python.org
You> fetch https://github.com/trending
```

#### 📊 **stats** - View memory statistics
```
You> stats
```

#### ❓ **help** - Show available commands
```
You> help
```

#### 👋 **exit** - Exit the assistant
```
You> exit
---

## 🧩 Project Structure

```
ollama-cli-agent/
├── assistant.py          # Entry point - CLI interface
├── src/
│   ├── agent.py         # Core agent logic
│   ├── assistant.py     # CLI command handlers
│   └── qdrant_store.py  # Vector database interface
├── web_tools/
│   ├── serpapi_tool.py  # Google search via SerpAPI
│   ├── brave_tool.py    # Brave search integration
│   └── firecrawl_tool.py # Web scraping tool
├── utils/
│   └── logging.py       # Logging configuration
├── tests/               # Unit and integration tests
├── .env.sample          # API keys template
└── requirements.txt     # Python dependencies
```

---

## 🧭 Architecture Overview

```
┌──────────────┐    ┌───────────────┐    ┌───────────────┐
│ assistant.py │ ⇄ │   agent.py    │ ⇄ │  Qdrant Memory │
└──────┬───────┘    └────┬──────────┘    └──────┬────────┘
       │ CLI             │ LLM & tools            │ Vector DB
       │ (input/output)  │ Search & fetch         │ Persistent memory
       │                 │ (SerpAPI, Brave, FireCrawl)
```

### 💾 Memory & Tools

**Memory**: 
- Uses Ollama embeddings (all-minilm model)
- Qdrant vector store for semantic search
- Persistent context across sessions

**Web Tools**:
- **SerpAPI**: Google search results
- **Brave Search**: Privacy-focused web search
- **FireCrawl**: Full-page content extraction

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Optional - for web search capabilities
SERPAPI_API_KEY=your_serpapi_key
BRAVE_API_KEY=your_brave_key
FIRECRAWL_API_KEY=your_firecrawl_key

# Qdrant settings (optional)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=ollama_cli_agent
```

### Ollama Models
The assistant uses:
- **LLM**: `mistral:7b` (default) - for text generation
- **Embeddings**: `all-minilm` - for vector embeddings

You can use any Ollama-supported model:
```bash
# List available models
ollama list

# Pull alternative models
ollama pull llama2:13b
ollama pull codellama:7b

# Use with assistant
python assistant.py --model llama2:13b
```

---

## 🧪 Testing

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_assistant -v

# Run with coverage (install coverage first)
pip install coverage
coverage run -m unittest discover tests
coverage report
```

---

## 🚨 Troubleshooting

### Common Issues

1. **"Ollama not found" error**
   - Make sure Ollama is installed and running: `ollama serve`
   - Check if models are pulled: `ollama list`

2. **"Model not found" error**
   - Pull the required models: `ollama pull mistral:7b && ollama pull all-minilm`

3. **Web search not working**
   - Check if API keys are set in `.env` file
   - Verify API keys are valid and have credits

4. **Memory/Qdrant issues**
   - For development, Qdrant runs in-memory (no setup needed)
   - For persistent storage, run: `docker run -p 6333:6333 qdrant/qdrant`

---

## 🎯 Roadmap

- [ ] 🔒 Persistent Qdrant storage configuration
- [ ] 🌐 Additional web tools (Wikipedia, arXiv)
- [ ] 📝 Export conversation history
- [ ] 🔄 Streaming responses
- [ ] 🎨 Rich terminal UI with colors
- [ ] 🔌 Plugin system for custom tools

🧹 Auto-fetch + ingest top search results

🛠 Enhanced CLI UX: help, command autocompletion

🔌 Plugin support (e.g., Git integration)

🌐 Optional web UI via Chainlit

✅ Contributing & License
Welcome contributions! Submit issues or PRs.

Licensed under MIT License.

🧠 About This Project
Built to be modular, terminal-first, private, and easy to extend—perfect for demos, portfolios, or personal productivity workflows.

