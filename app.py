from flask import Flask, render_template, redirect, jsonify, request
from requests import RequestException
import requests

app = Flask(__name__)


striim_api_url = ("http://localhost:5001/api/v1")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/striim/status', methods=['GET'])
def check_status():
    response = requests.get(f'{striim_api_url}/server/status')

    return jsonify(response.json())

@app.route('/striim/restart', methods=['POST'])
def restart_server():
    response = requests.post(f'{striim_api_url}/server/restart')

    try:
        return jsonify(response.json())
    except requests.RequestException as e:
            return jsonify({"error": str(e)}), 500

@app.route('/striim/stop', methods=['POST'])
def stop_server():
    response = requests.post(f'{striim_api_url}/server/stop')
    try:
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/striim/start', methods=['POST'])
def start_server():
    response = requests.post(f'{striim_api_url}/server/start')

    try:
        return jsonify(response.json())
    except requests.RequestException as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)