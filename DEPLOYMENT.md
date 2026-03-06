# 🚀 AutoML Platform Deployment Guide

## Quick Deploy Options

### 1. Local Development (Recommended for testing)
```bash
# Clone and run
git clone https://github.com/yourusername/automl-platform.git
cd automl-platform
./start.sh  # Linux/Mac
# or
start.bat   # Windows
```

### 2. Docker Deployment (Recommended for production)
```bash
# Build and run with Docker
docker build -t automl-platform .
docker run -p 8000:8000 automl-platform
```

### 3. Cloud Deployment

#### Heroku
```bash
# Install Heroku CLI then:
heroku create your-automl-app
git push heroku main
heroku open
```

#### Railway
```bash
# Connect GitHub repo to Railway
# Auto-deploys on push
```

#### DigitalOcean App Platform
```yaml
# Create app.yaml:
name: automl-platform
services:
- name: web
  source_dir: /
  github:
    repo: yourusername/automl-platform
    branch: main
  run_command: uvicorn project.api_server:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8000
```

#### AWS EC2
```bash
# On EC2 instance:
sudo yum update -y
sudo yum install python3 pip -y
git clone https://github.com/yourusername/automl-platform.git
cd automl-platform
pip3 install -r requirements.txt
nohup uvicorn project.api_server:app --host 0.0.0.0 --port 8000 &
```

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy automl-platform \
  --source . \
  --port 8000 \
  --allow-unauthenticated
```

### 4. Production Setup

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  automl:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/project/datasets
      - ./models:/app/project/models
    environment:
      - AUTOML_HOST=0.0.0.0
      - AUTOML_PORT=8000
    restart: always
```

#### Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/automl
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Systemd Service (Linux)
```ini
# /etc/systemd/system/automl.service
[Unit]
Description=AutoML Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/automl-platform
Environment=PATH=/opt/automl-platform/venv/bin
ExecStart=/opt/automl-platform/venv/bin/uvicorn project.api_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Environment Variables

```bash
# Production configuration
export AUTOML_HOST=0.0.0.0
export AUTOML_PORT=8000
export AUTOML_WORKERS=4
export AUTOML_MODELS_DIR=/data/models
export AUTOML_DATASETS_DIR=/data/datasets
export AUTOML_LOGS_DIR=/data/logs
```

## Security (Production)

```python
# Add to api_server.py for production
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)

# CORS configuration  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Monitoring

```bash
# Health check endpoint
curl http://localhost:8000/health

# Metrics endpoint (add to your monitoring)
curl http://localhost:8000/platform-summary
```

## Scaling

```bash
# Multiple workers
uvicorn project.api_server:app --host 0.0.0.0 --port 8000 --workers 4

# Load balancer setup
# Use nginx, HAProxy, or cloud load balancer
```

---

**Choose the deployment method that fits your needs!**