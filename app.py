import hashlib
import os
import yaml
import threading
import logging
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from waitress import serve

CONFIG_PATH = 'config/proxy.yaml'
config_map = {}
last_config_hash = None

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config():
    global config_map, last_config_hash
    try:
        with open(CONFIG_PATH, 'rb') as f:
            content = f.read()
            current_hash = hashlib.md5(content).hexdigest()
            if current_hash == last_config_hash:
                return
            last_config_hash = current_hash
            config_map = yaml.safe_load(content)
            logger.info(f'[Config Reloaded] {config_map}')
    except Exception as e:
        logger.error(f'[Config Error] Failed to load config: {e}')


class ConfigChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(CONFIG_PATH):
            load_config()


def start_watcher():
    event_handler = ConfigChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(CONFIG_PATH) or '.', recursive=False)
    observer.start()
    threading.Thread(target=observer.join, daemon=True).start()


app = Flask(__name__)
CORS(app)


@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(subpath=''):
    try:
        incoming_host = request.headers.get('Host', '').split(':')[0]
        target_base = config_map.get(incoming_host)

        if not target_base:
            return jsonify({'error': f'Host {incoming_host} is not configured'}), 400

        target_url = f"{target_base}/{subpath}"

        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
            params=request.args.to_dict(),
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        try:
            resp = jsonify(response.json())
            resp.status_code = response.status_code
        except ValueError:
            resp = app.response_class(
                response.content,
                status=response.status_code,
                headers=dict(response.headers)
            )

        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        return resp

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    load_config()
    start_watcher()
    serve(app, host='0.0.0.0', port=5050)
