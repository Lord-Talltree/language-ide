# L-ide Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose installed
- 4GB RAM minimum
- 2GB free disk space

### 1. Clone Repository
```bash
git clone https://github.com/Lord-Talltree/language-ide.git
cd language-ide/prototype
```

### 2. Start Services
```bash
docker compose up -d
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop Services
```bash
docker compose down
```

---

## Data Persistence

### SQLite Database Location
The SQLite database is stored in a Docker volume:
- **Volume name**: `lide-data`
- **Container path**: `/app/data/lide.db`

### Backup Database
```bash
# Create backup
docker compose exec backend cat /app/data/lide.db > lide-backup.db

# Restore backup
docker compose cp lide-backup.db backend:/app/data/lide.db
```

### View Database
```bash
# Access SQLite CLI
docker compose exec backend sqlite3 /app/data/lide.db
```

---

## Production Deployment

### Environment Variables

Create a `.env` file:
```env
# Database
DATABASE_PATH=/app/data/lide.db

# CORS (add your production domain)
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000

# Optional: Port configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Production Docker Compose
```bash
# Use production config
docker compose -f docker-compose.prod.yml up -d
```

### SSL/HTTPS Setup
For production, use a reverse proxy (nginx or Caddy):

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://localhost:8000/v0/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

---

## Troubleshooting

### Database Locked Error
```bash
# Check if database is in use
docker compose exec backend lsof /app/data/lide.db

# Restart backend
docker compose restart backend
```

### Reset Database
```bash
# WARNING: This deletes all data
docker compose down -v
docker compose up -d
```

### View Logs
```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

### Check Health
```bash
curl http://localhost:8000/v0/health
```

---

## Development Workflow

### Hot Reload
Backend and frontend support hot reload in development mode:
```bash
# Backend automatically reloads on code changes (--reload flag)
# Frontend uses Vite HMR
```

### Run Tests
```bash
# Backend tests
docker compose exec backend pytest

# With coverage
docker compose exec backend pytest --cov=app
```

### Access Backend Shell
```bash
docker compose exec backend python3
```

---

## Monitoring

### Container Stats
```bash
docker compose stats
```

### Database Size
```bash
docker compose exec backend du -h /app/data/lide.db
```

### Session Count
```bash
curl http://localhost:8000/v0/sessions | jq 'length'
```

---

## Updating

### Pull Latest Code
```bash
git pull origin main
docker compose build --no-cache
docker compose up -d
```

### Database Migration
If schema changes (future):
```bash
docker compose exec backend python3 -m app.migrations.migrate
```

---

## Security

### Recommended Practices
1. **Change default ports** in production
2. **Use environment variables** for secrets
3. **Enable SSL/TLS** with reverse proxy
4. **Regular backups** of lide-data volume
5. **Limit CORS origins** to your domain only

### Docker Security
```bash
# Run as non-root user (already configured in Dockerfile)
# Scan for vulnerabilities
docker scout cves language-ide_backend
```

---

## Support

- **GitHub Issues**: https://github.com/Lord-Talltree/language-ide/issues
- **Docs**: https://lord-talltree.github.io/language-ide/
