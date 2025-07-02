# Changelog

All notable changes to the ollama-cli-agent project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-07-02

### Added

#### Core Agent Implementation
- **Implemented complete agent orchestration** (`src/agent.py`)
  - Integrated Ollama LLM and embeddings with Qdrant vector store
  - Added web search capabilities with automatic tool selection
  - Implemented memory-augmented question answering
  - Added comprehensive error handling and logging
  - Methods implemented:
    - `ingest()` - Add content to vector memory
    - `ask()` - Answer questions with memory retrieval
    - `search()` - Web search with SerpAPI/Brave fallback
    - `fetch()` - Retrieve and process web content
    - `get_memory_stats()` - Memory usage statistics

#### CLI Interface
- **Created interactive REPL assistant** (`src/assistant.py`)
  - Commands: `ask`, `ingest`, `search`, `fetch`, `help`, `stats`, `exit`
  - Smart URL detection for automatic fetching
  - Content preview on fetch operations
  - Command-line arguments for model selection and debug mode
  - Beautiful colored output with emojis

#### Web Tools Integration
- **Implemented SerpAPI tool** (`web_tools/serpapi_tool.py`)
  - Google search integration with structured results
  - Error handling for missing API keys
  
- **Implemented Brave Search tool** (`web_tools/brave_tool.py`)
  - Privacy-focused search alternative
  - Consistent result formatting with SerpAPI
  
- **Implemented FireCrawl tool** (`web_tools/firecrawl_tool.py`)
  - Full-page web scraping with markdown support
  - Metadata extraction (title, description, etc.)
  - Fallback to basic requests for missing API key

#### Testing & Utilities
- **Created integration test suite** (`test_integration.py`)
  - Tests all major components end-to-end
  - Clear success/failure indicators
  
- **Added centralized logging** (`utils/logging.py`)
  - Configurable log levels and formatting
  - Singleton pattern to avoid duplicate handlers

### Changed

- **Updated to use `langchain-ollama` package**
  - Migrated from deprecated `langchain_community` imports
  - Now using `OllamaLLM` and `OllamaEmbeddings` from `langchain_ollama`
  
- **Improved dependency management**
  - Cleaned up `requirements.txt` with proper versions
  - Removed duplicate entries and conflicts
  - Organized dependencies by category

### Fixed

- **Resolved QdrantStore integration issues**
  - Fixed incorrect `embedding_function` parameter
  - Updated agent to properly pass embeddings to QdrantStore
  - Set in-memory mode as default for development
  
- **Fixed model compatibility**
  - Changed default from unavailable `llama3.2` to `mistral`
  - Updated all references across the codebase
  
- **Fixed import errors**
  - Added missing `langchain-community` dependency
  - Resolved module not found errors

## [Unreleased] - 2025-01-02

### Added

#### Vector Store Implementation
- **Implemented `src/qdrant_store.py`** - Complete Qdrant vector store integration
  - `QdrantStore` class with full CRUD operations for vector storage
  - Support for both persistent (Docker) and in-memory modes
  - Automatic fallback to in-memory mode if Qdrant server is unavailable
  - Methods implemented:
    - `add_documents()` - Store texts with embeddings and metadata
    - `search()` - Semantic search with optional filtering
    - `delete_collection()` - Clean up vector storage
    - `get_collection_info()` - Monitor collection statistics
  - Configurable vector dimensions (default: 384 for all-MiniLM-L6-v2)
  - Batch processing for efficient document uploads

#### Setup and Configuration
- **Created `setup_qdrant.sh`** - Automated Qdrant setup script
  - Detects Docker availability
  - Provides instructions for both Docker and in-memory setups
  - Creates persistent storage directory for Docker deployment
  - Includes helpful commands for managing Qdrant container

- **Created `.env` file** from `.env.sample`
  - Configured API keys for SerpAPI, Brave, and FireCrawl
  - Ready for immediate use with web tools

#### Development Environment
- **Set up Micromamba environment** `ollama-cli-agent`
  - Python 3.11 as specified in project requirements
  - All dependencies successfully installed
  - Environment ready for development

#### Testing
- **Created `test_qdrant.py`** - Comprehensive test script for Qdrant functionality
  - Tests document ingestion with dummy embeddings
  - Verifies search functionality
  - Validates collection management
  - Provides clear feedback on setup status

#### Web Tools Implementation
- **Implemented `web_tools/serpapi_tool.py`** - SerpAPI integration for web search
  - Full Google search functionality with configurable result count
  - Error handling and fallback mechanisms
  - Returns structured results with title, link, and snippet

- **Implemented `web_tools/brave_tool.py`** - Brave Search API integration
  - Privacy-focused web search alternative
  - Compatible API with SerpAPI for easy switching
  - Supports the same result format for consistency

- **Implemented `web_tools/firecrawl_tool.py`** - FireCrawl web scraping
  - Full-page content extraction with markdown support
  - Automatic metadata extraction (title, description)
  - Clean content extraction focusing on main content only

#### Core Agent Implementation
- **Implemented `src/agent.py`** - Main agent orchestration
  - Ollama LLM integration for text generation
  - Ollama embeddings for semantic search
  - Tool management with automatic initialization based on API keys
  - Memory-augmented question answering with RAG
  - Automatic content ingestion from fetched URLs
  - Web search with automatic tool selection
  - Comprehensive error handling and logging

#### CLI Interface Implementation  
- **Implemented `src/assistant.py`** - Interactive CLI REPL
  - Commands: `ask`, `ingest`, `search`, `fetch`, `help`, `stats`, `exit`
  - Beautiful terminal UI with emojis and clear formatting
  - Smart URL detection for automatic fetching
  - Content preview for fetched pages
  - Memory statistics display
  - Command-line arguments for model selection and debug mode

- **Created `assistant.py`** - Root-level entry point
  - Simple wrapper for easy execution
  - Made executable for direct running

#### Utilities and Infrastructure
- **Implemented `utils/logging.py`** - Centralized logging configuration
  - Configurable log levels and formatting
  - Console output with timestamps
  - Singleton pattern to avoid duplicate handlers

- **Created `test_integration.py`** - Integration testing script
  - Tests all major components: agent init, ingestion, memory, Q&A, search
  - Clear success/failure indicators
  - Helpful error messages for debugging

### Changed

#### Dependencies
- **Updated `requirements.txt`**
  - Fixed `serpapi` version from `>=0.2.0` to `==0.1.5` (latest available version)
  - Added `numpy>=1.24.0` for embedding operations
  - Added `langchain-community>=0.0.10` for community integrations
  - Cleaned up duplicate entries and version conflicts
  - Reorganized dependencies by category for better clarity
  - All dependencies now compatible with Python 3.11

#### Project Structure
- **Created root-level `assistant.py`** entry point
  - Simple wrapper for `src.assistant.main()`
  - Made executable for easy CLI access
  - Allows running with `./assistant.py` or `python assistant.py`

- **Added `utils/__init__.py`**
  - Proper module initialization for utils package
  - Exports logger and setup_logger for easy imports

### Fixed

- **Resolved dependency conflicts** preventing installation
  - SerpAPI version was requesting non-existent 0.2.0
  - Now using stable, available version 0.1.5

- **Fixed langchain deprecation warnings**
  - Migrated from `langchain_community` to `langchain_ollama` for Ollama integration
  - Updated imports to use `OllamaLLM` and `OllamaEmbeddings` from `langchain_ollama`
  - Resolved compatibility issues with latest langchain versions

- **Fixed QdrantStore integration issues**
  - Removed incorrect `embedding_function` parameter from QdrantStore initialization
  - Updated agent to properly handle embeddings when adding documents
  - Set QdrantStore to use in-memory mode by default for development

- **Fixed model availability issues**
  - Changed default model from `llama3.2` to `mistral` (commonly available)
  - Updated all references in agent.py, assistant.py, and test files
  - Added automatic model pulling for `all-minilm` embedding model

### Technical Details

#### Qdrant Configuration
- Default collection name: `ollama_agent_memory`
- Default vector size: 384 dimensions
- Distance metric: Cosine similarity
- Default host: localhost:6333
- Supports both persistent and in-memory storage

#### File Structure Changes
```
ollama-cli-agent/
├── .env                    # NEW: Environment variables (from .env.sample)
├── CHANGELOG.md            # NEW: This file
├── setup_qdrant.sh         # NEW: Qdrant setup automation
├── test_qdrant.py          # NEW: Qdrant functionality tests
├── requirements.txt        # MODIFIED: Fixed dependencies
└── src/
    └── qdrant_store.py     # NEW: Complete vector store implementation
```

### Development Notes

1. **Memory Mode vs Persistent Mode**
   - Development can use in-memory mode (no Docker required)
   - Production should use Docker for data persistence
   - Automatic fallback ensures development isn't blocked

2. **Next Integration Steps**
   - Connect QdrantStore to the agent's embedding model
   - Implement document ingestion in the `ingest` command
   - Add retrieval-augmented generation to the `ask` command
   - Create proper unit tests with mocked dependencies

3. **API Keys Status**
   - All required API keys are configured in `.env`
   - Ready for web search and scraping functionality

### Commands for Future Reference

```bash
# Activate environment
micromamba activate ollama-cli-agent

# Run Qdrant with Docker (for persistence)
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Test Qdrant setup
python test_qdrant.py

# Install/update dependencies
pip install -r requirements.txt
```

---

*Session conducted by: Cascade AI Assistant*  
*Date: 2025-01-02*  
*Time: 15:09 - 15:22 EST*
