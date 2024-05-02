# API Proxy
A simple proxy that helps to bypass CORS while interacting with an external API for development purposes.

## Deploying with Docker
```bash
docker run --name api-proxy \
  -e API_HOST=<external host> \
  -p 5000:5000 \
  ghcr.io/dmitryarkh/api-proxy:main
```