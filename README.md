# API Proxy
A simple proxy that helps to bypass CORS while interacting with an external API for development purposes.

## Deploying with Docker
```bash
docker run --name api-proxy \
  --network host \
  -v ./config:/app/config:ro \
  ghcr.io/dmitryarkh/api-proxy:latest
```
