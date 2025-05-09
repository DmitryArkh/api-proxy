import hashlib
import os
import yaml
import logging
import sys
import time
import signal
import subprocess

NGINX_CONFIG_PATH = "/etc/nginx/conf.d/default.conf"
CONFIG_PATH = "/app/routes.yaml"
config_map = {}
last_config_hash = None

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def generate_nginx_config(mapping):
    conf = ""
    for server_name, target_url in mapping.items():
        conf += f"""
server {{
    listen 5050;
    server_name {server_name};

    location / {{
        proxy_pass {target_url};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'Origin, Content-Type, Accept, Authorization' always;

        if ($request_method = OPTIONS) {{
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Length' 0;
            add_header 'Content-Type' 'text/plain; charset=UTF-8';
            return 204;
        }}
    }}
}}
"""
    return conf


def update_nginx_config(config_text):
    try:
        with open(NGINX_CONFIG_PATH, "w") as f:
            f.write(config_text)
        subprocess.run(["nginx", "-s", "reload"], check=True)
        logger.info("Nginx config reloaded.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reload nginx: {e}")


def load_config():
    global config_map, last_config_hash
    try:
        if not os.path.exists(CONFIG_PATH):
            logger.warning(f"Config file not found: {CONFIG_PATH}")
            return

        with open(CONFIG_PATH, 'rb') as f:
            content = f.read()
            current_hash = hashlib.md5(content).hexdigest()
            if current_hash == last_config_hash:
                return
            last_config_hash = current_hash
            config_map = yaml.safe_load(content)
            if not isinstance(config_map, dict):
                logger.error("Invalid YAML structure: expected a mapping")
                return
            config_text = generate_nginx_config(config_map)
            update_nginx_config(config_text)
            logger.info(f"Config updated: {config_map}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")


def stop_gracefully(signum, frame):
    logger.info("Gracefully stopping the process...")
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop_gracefully)
    signal.signal(signal.SIGTERM, stop_gracefully)
    load_config()

    try:
        while True:
            load_config()
            time.sleep(2)
    except KeyboardInterrupt:
        stop_gracefully(None, None)
