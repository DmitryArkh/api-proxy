import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

load_dotenv()
API_HOST = os.environ.get('API_HOST')
assert API_HOST, 'Envvar API_HOST is required'

app = Flask(__name__)
CORS(app)


@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(subpath=''):
    try:
        target_url_with_path = f'{API_HOST}/{subpath}'
        response = requests.request(
            method=request.method,
            url=target_url_with_path,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
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
    app.run(host='0.0.0.0', port=5000)
