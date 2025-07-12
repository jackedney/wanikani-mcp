# Deployment Guide

## Render Deployment

### Prerequisites
1. GitHub repository with the code
2. Render account
3. PostgreSQL database

### Steps

1. **Create PostgreSQL Database on Render**
   - Go to Render Dashboard
   - Create new PostgreSQL database
   - Note the connection string

2. **Deploy the Application**
   - Connect your GitHub repository to Render
   - Use the provided `render.yaml` configuration
   - Set environment variables:
     - `DATABASE_URL`: Your PostgreSQL connection string
     - Other variables are pre-configured

3. **Run Database Migrations**
   ```bash
   # After deployment, run migrations via Render shell
   python -m alembic upgrade head
   ```

### Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection string
- `WANIKANI_API_BASE_URL`: https://api.wanikani.com/v2

Optional (with defaults):
- `DEBUG`: false
- `LOG_LEVEL`: INFO
- `SYNC_INTERVAL_MINUTES`: 30
- `MAX_CONCURRENT_SYNCS`: 3
- `WANIKANI_RATE_LIMIT`: 60

### Health Check

The application exposes a health check endpoint at `/health` for monitoring.

### Monitoring

- Use Render's built-in logging and metrics
- Application logs include sync status and error information
- Consider adding Sentry for error tracking (set `SENTRY_DSN`)

## Local Development with Podman

```bash
# Build the container
podman build -t wanikani-mcp .

# Run with environment file
podman run -p 8000:8000 --env-file .env wanikani-mcp

# Or run HTTP mode
podman run -p 8000:8000 -e DATABASE_URL="sqlite:///./wanikani_mcp.db" wanikani-mcp
```

## MCP Integration

Once deployed, users can connect via:
- HTTP mode: Use the deployed URL
- Stdio mode: Run locally with `task dev`