# WaniKani MCP Server

A production-ready MCP (Model Context Protocol) server that connects AI assistants like Claude Code to WaniKani learning data. Get real-time progress updates, identify problem items, and manage your Japanese learning workflow through natural conversation.

## ✨ Quick Start

### For Users with Claude Code

1. **Set up the MCP server connection:**
   ```bash
   cd wanikani-mcp
   claude mcp add-json wanikani '{"command": "uv", "args": ["run", "python", "-m", "wanikani_mcp.server"], "env": {}, "cwd": "/path/to/wanikani-mcp"}'
   ```
2. **Verify connection:** Run `claude mcp list` - wanikani should show as "connected"
3. **Register your WaniKani account:**
   ```
   Register me with WaniKani API token: your-wanikani-token
   ```
4. **Start learning:**
   ```
   How many lessons and reviews do I have?
   What are my worst leeches that need practice?
   ```

### For Developers

```bash
git clone https://github.com/jackedney/wanikani-mcp.git
cd wanikani-mcp
uv install
cp .env.example .env  # Configure your database
uv run alembic upgrade head
task dev
```

## 🎯 What This Does

**Real Learning Integration**: Your AI assistant can now see your actual WaniKani progress and help with personalized study strategies.

### Architecture Overview

![Architecture Diagram](images/architecture.png)

**Core Features:**
- **Live Status**: Current level, lesson count, review count, next review time
- **Leech Detection**: Identifies consistently difficult items for focused practice  
- **Background Sync**: Keeps data fresh automatically (every 30 minutes)
- **Multi-User**: Secure per-user authentication with MCP API keys

**Example Conversations:**
```
You: "How am I doing with my Japanese studies?"
Claude: "You're Level 8 with 30 lessons and 206 reviews available. Your next reviews are at 11:00 PM."

You: "What should I focus on?"
Claude: "You have 15 leeches - items you consistently get wrong. Let's practice these kanji: 体, 茶, 牛..."
```

## 🔧 MCP Tools & Resources

### Tools (Actions)
- **`register_user`**: Connect your WaniKani account securely
- **`get_status`**: Current level, lessons, reviews, next review time
- **`get_leeches`**: Items that need extra practice (wrong >3 times)
- **`sync_data`**: Manual data refresh from WaniKani

### Resources (Data Access)
- **`user_progress`**: Detailed statistics and learning metrics
- **`review_forecast`**: Timeline of upcoming review sessions
- **`item_database`**: Searchable collection of your WaniKani items

## 🚀 Deployment Options

### Render (Recommended)

1. **Fork this repository**
2. **Connect to Render:**
   - Create new Web Service from your fork
   - Environment: `DATABASE_URL` (PostgreSQL connection string)
   - Build: `uv install` 
   - Start: `uv run python -m wanikani_mcp.http_server`
3. **Run migrations:** `uv run alembic upgrade head`

### Local Development

```bash
# Install dependencies
uv install

# Set up database
cp .env.example .env
# Edit .env with your PostgreSQL URL
uv run alembic upgrade head

# Run in stdio mode (for Claude Code)
task dev

# Run in HTTP mode (for web access)  
task dev-http
```

### Container (Podman/Docker)

```bash
# Build
podman build -t wanikani-mcp .

# Run
podman run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  wanikani-mcp
```

## 🔐 Security & Authentication

**Two-Tier Security:**
1. **WaniKani API Token**: Your personal WaniKani API key (from wanikani.com/settings/personal_access_tokens)
2. **MCP API Key**: Generated server key for Claude Code authentication

**Registration Flow:**
1. Get your WaniKani API token from https://www.wanikani.com/settings/personal_access_tokens
2. Use `register_user` tool with your WaniKani token
3. Receive MCP API key for all future requests
4. MCP API key authenticates you for `get_status`, `get_leeches`, `sync_data`

**Privacy:** Each user's data is completely isolated. MCP API keys are securely generated and hashed.

## ⚙️ Configuration

**Environment Variables** (copy `.env.example` to `.env`):
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
WANIKANI_API_BASE_URL=https://api.wanikani.com/v2
SYNC_INTERVAL_MINUTES=30
MAX_CONCURRENT_SYNCS=3
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
```

**MCP Server Configuration** (for Claude Code):

**Method 1: JSON Configuration (Recommended)**
```bash
cd /path/to/wanikani-mcp
claude mcp add-json wanikani '{"command": "uv", "args": ["run", "python", "-m", "wanikani_mcp.server"], "env": {}, "cwd": "/path/to/wanikani-mcp"}'
```

**Method 2: Manual Configuration**
```json
{
  "mcpServers": {
    "wanikani": {
      "command": "uv",
      "args": ["run", "python", "-m", "wanikani_mcp.server"],
      "cwd": "/path/to/wanikani-mcp",
      "env": {}
    }
  }
}
```

**Important**: 
- Must specify `cwd` (working directory) for the server to find dependencies
- Server uses file logging to avoid interfering with stdio MCP communication
- Run `uv install` first to ensure dependencies are available

## 🧑‍💻 Development

**Code Quality:**
```bash
uv run ruff check .      # Linting
uv run ruff format .     # Formatting  
uvx ty check .           # Type checking
uv run pytest           # Testing
```

**Database Management:**
```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Reset database (development only)
uv run python -c "from wanikani_mcp.database import reset_database; reset_database()"
```

**Tech Stack:**
- **Framework**: FastAPI + Python MCP SDK
- **Database**: PostgreSQL + SQLModel ORM  
- **Background Jobs**: APScheduler
- **Package Manager**: uv
- **Containerization**: Podman
- **Deployment**: Render

## 🤝 Production Checklist

Before deploying:
- [ ] PostgreSQL database configured
- [ ] Environment variables set
- [ ] Database migrations applied
- [ ] Rate limiting configured
- [ ] Monitoring/logging enabled
- [ ] SSL/TLS certificates in place
- [ ] Backup strategy implemented

## 📈 Monitoring

**Health Check Endpoint**: `GET /health`
**Metrics**: Built-in logging for sync operations, API calls, and errors
**Database**: Monitor connection pool, query performance, storage usage

---

## 📄 License

See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **WaniKani**: For providing the excellent Japanese learning platform and API
- **Anthropic**: For the MCP specification and Claude Code integration
- **Python MCP SDK**: For the foundational MCP implementation
