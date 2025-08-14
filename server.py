import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import logging

app = Flask(__name__)
# Configure CORS for local testing (update with Railway URL later)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:8000"]}})

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# File path for JSON storage
DATA_FILE = 'data.json'

# Initialize JSON file if it doesn't exist or is empty/invalid
def initialize_json_file():
    default_data = {'users': []}
    try:
        if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
            logger.debug("Creating new data.json with default data")
            with open(DATA_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
            return default_data
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError in data.json: {e}")
        with open(DATA_FILE, 'w') as f:
            json.dump(default_data, f, indent=4)
        return default_data
    except Exception as e:
        logger.error(f"Error reading data.json: {e}")
        return default_data

# Helper function to write JSON file
def write_json(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logger.debug("Successfully wrote to data.json")
    except Exception as e:
        logger.error(f"Error writing to data.json: {e}")

# Endpoint to save user name and generate ID
@app.route('/save_name', methods=['POST'])
def save_name():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        user_id = str(uuid.uuid4())
        json_data = initialize_json_file()
        json_data['users'].append({
            'user_id': user_id,
            'name': name,
            'conversations': [],
            'feedback': []
        })
        write_json(json_data)
        logger.debug(f"Saved user: {name}, ID: {user_id}")
        return jsonify({'user_id': user_id, 'name': name}), 201
    except Exception as e:
        logger.error(f"Error in save_name: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Endpoint to save conversation
@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        conversation = data.get('conversation')
        if not user_id or not conversation:
            return jsonify({'error': 'User ID and conversation are required'}), 400
        
        json_data = initialize_json_file()
        for user in json_data['users']:
            if user['user_id'] == user_id:
                user['conversations'].append(conversation)
                write_json(json_data)
                logger.debug(f"Saved conversation for user ID: {user_id}")
                return jsonify({'success': True, 'user_id': user_id}), 201
        return jsonify({'error': 'User ID not found'}), 404
    except Exception as e:
        logger.error(f"Error in save_conversation: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Endpoint to save feedback
@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        feedback_text = data.get('feedback_text')
        if not user_id or not feedback_text:
            return jsonify({'error': 'User ID and feedback text are required'}), 400
        
        json_data = initialize_json_file()
        for user in json_data['users']:
            if user['user_id'] == user_id:
                user['feedback'].append(feedback_text)
                write_json(json_data)
                logger.debug(f"Saved feedback for user ID: {user_id}")
                return jsonify({'success': True, 'user_id': user_id}), 201
        return jsonify({'error': 'User ID not found'}), 404
    except Exception as e:
        logger.error(f"Error in save_feedback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Endpoint for admin to fetch all data
@app.route('/fetch_all', methods=['GET'])
def fetch_all():
    try:
        json_data = initialize_json_file()
        logger.debug("Fetched all data")
        return jsonify(json_data), 200
    except Exception as e:
        logger.error(f"Error in fetch_all: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Test endpoint to verify server
@app.route('/', methods=['GET'])
def test_server():
    logger.debug("Accessed test endpoint")
    return jsonify({'message': 'Server is running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)