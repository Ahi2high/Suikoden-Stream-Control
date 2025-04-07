#!/usr/bin/env python
"""
Suikoden Display - Web Interface
Flask web server with SocketIO for real-time updates.
"""

import os
import json
import time
import logging
import threading
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('web_interface.log')
    ]
)
logger = logging.getLogger('suikoden_web')

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'suikoden_display_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize state
all_characters = []
current_party = [None] * 6
connected_clients = set()  # Track connected clients for broadcasting

# Global lock for thread safety when updating party data
import threading
party_lock = threading.Lock()

# Path configurations
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
IMAGES_DIR = BASE_DIR / 'images'
DATA_DIR = BASE_DIR / 'data'

# Ensure directories exist
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / 'img').mkdir(exist_ok=True)
(STATIC_DIR / 'css').mkdir(exist_ok=True)
(STATIC_DIR / 'js').mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Function to create an empty party structure
def create_empty_party():
    return [None] * 6

# Function to create a default party.json file
def create_default_party_file():
    try:
        empty_party = create_empty_party()
        with open(DATA_DIR / 'party.json', 'w', encoding='utf-8') as f:
            json.dump(empty_party, f, ensure_ascii=False, indent=2)
        logger.info("Created default party.json file")
        return empty_party
    except Exception as e:
        logger.error(f"Failed to create default party.json file: {e}")
        return create_empty_party()

def load_character_data():
    """Load and validate character data from JSON file"""
    sample_characters = [
        {
            "id": 1,
            "name": "Tir McDohl",
            "image_url": "/static/img/tir.png",
            "recruitment_info": "Main character, automatically recruited at the start."
        },
        {
            "id": 2,
            "name": "Gremio",
            "image_url": "/static/img/gremio.png",
            "recruitment_info": "Tir's servant. Joins at the beginning of the game."
        },
        {
            "id": 3,
            "name": "Viktor",
            "image_url": "/static/img/viktor.png",
            "recruitment_info": "Found in Lenankamp, joins after meeting him in the inn."
        }
    ]
    
    # First try loading from the processed file
    try:
        processed_file = DATA_DIR / 'characters_processed.json'
        if processed_file.exists():
            with open(processed_file, 'r', encoding='utf-8') as f:
                characters = json.load(f)
            logger.info(f"Loaded {len(characters)} characters from characters_processed.json")
            
            # Validate data structure
            if isinstance(characters, list) and all(
                isinstance(c, dict) and "id" in c and "name" in c and 
                "image_url" in c and "recruitment_info" in c for c in characters
            ):
                return characters
            else:
                logger.error("characters_processed.json has invalid data structure")
    except Exception as e:
        logger.error(f"Failed to load processed character data: {e}")
    
    # Fall back to original characters.json if processed file fails
    try:
        with open(DATA_DIR / 'characters.json', 'r', encoding='utf-8') as f:
            characters = json.load(f)
        logger.info(f"Loaded {len(characters)} characters from characters.json")
        
        # Check if we need to process this data
        if not isinstance(characters, list):
            logger.warning("Characters data is not in the expected format, creating fallback data")
            return sample_characters
            
        return characters
    except Exception as e:
        logger.error(f"Failed to load character data: {e}")
        # Use sample data if all attempts fail
        return sample_characters

# Load character data
all_characters = load_character_data()

# Try to load party data
try:
    party_file = DATA_DIR / 'party.json'
    if not party_file.exists():
        logger.info("Party file doesn't exist, creating default party.json")
        current_party = create_default_party_file()
    else:
        with open(party_file, 'r', encoding='utf-8') as f:
            current_party = json.load(f)
        logger.info(f"Loaded party data: {len([p for p in current_party if p])} members")
except Exception as e:
    logger.warning(f"Failed to load party data, using empty party: {e}")
    current_party = create_empty_party()

# Route for the main page
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {e}")
        return "Error loading page. Check logs for details.", 500

# Route for static files (fallback)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Route for character images
@app.route('/static/img/<path:filename>')
def send_image(filename):
    # Check both static/img and images directories
    if os.path.exists(os.path.join('static', 'img', filename)):
        return send_from_directory(os.path.join('static', 'img'), filename)
    elif os.path.exists(os.path.join('images', filename)):
        return send_from_directory('images', filename)
    else:
        return send_from_directory(os.path.join('static', 'img'), 'placeholder.png')

# API route to get all characters
@app.route('/api/characters', methods=['GET'])
def get_characters():
    return jsonify({"characters": all_characters})

# API route to get current party
@app.route('/api/party', methods=['GET'])
def get_party():
    return jsonify({"party": current_party})

# API route to get character details
@app.route('/api/character/<name>', methods=['GET'])
def get_character(name):
    # Improved character lookup with better error handling
    try:
        character = next((c for c in all_characters if c['name'].lower() == name.lower()), None)
        if character:
            return jsonify(character)
        return jsonify({"error": "Character not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving character data for {name}: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Socket.IO event: client connection
@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    connected_clients.add(client_id)
    emit('server_info', {'message': 'Connected to Suikoden Display server'})

# Socket.IO event: client disconnection
@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")
    if client_id in connected_clients:
        connected_clients.remove(client_id)

# Socket.IO event: request initial data
@socketio.on('request_initial_data')
def handle_initial_data():
    logger.info("Sending initial data to client")
    emit('initial_data', {
        'characters': all_characters,
        'party': current_party
    })

# Socket.IO event: select character
@socketio.on('select_character')
def handle_select_character(data):
    try:
        character_name = data.get('character_name')
        if not character_name:
            logger.warning("Character selection request missing character_name")
            emit('server_error', {'message': "Missing character name"})
            return
            
        logger.info(f"Character selected: {character_name}")
        
        # Find character in list with case-insensitive comparison
        character = next((c for c in all_characters if c['name'].lower() == character_name.lower()), None)
        
        if character:
            emit('character_selected', {
                'character': character,
                'recruitment_info': character.get('recruitment_info', 'No recruitment information available.')
            })
        else:
            logger.warning(f"Character not found: {character_name}")
            emit('server_error', {'message': f"Character {character_name} not found"})
    except Exception as e:
        logger.error(f"Error selecting character: {e}")
        emit('server_error', {'message': str(e)})

# Socket.IO event: add character to party
@socketio.on('add_to_party')
def handle_add_to_party(data):
    try:
        # Input validation
        if not isinstance(data, dict):
            emit('server_error', {'message': 'Invalid data format'})
            return
            
        character_name = data.get('character_name')
        if not character_name:
            emit('server_error', {'message': 'Missing character name'})
            return
            
        slot = data.get('slot', 0)
        if not isinstance(slot, int) or slot < 0 or slot >= 6:
            emit('server_error', {'message': 'Invalid party slot'})
            return
            
        # Find character in the available characters list
        character = next((c for c in all_characters if c['name'].lower() == character_name.lower()), None)
        
        if not character:
            emit('server_error', {'message': f"Character {character_name} not found"})
            return
            
        # Add to party
        current_party[slot] = character
        
        # Save party data and check success
        if save_party_data():
            # Create updated party information
            party_update = {
                'party': current_party,
                'updated_slot': slot,
                'action': 'add',
                'character': character
            }
            
            # Broadcast party update to all clients
            socketio.emit('party_updated', party_update)
            logger.info(f"Added {character_name} to party slot {slot}")
            emit('update_success', {'message': f"{character_name} added to party"})
        else:
            emit('server_error', {'message': 'Failed to save party data'})
    except Exception as e:
        logger.error(f"Error adding character to party: {e}")
        emit('server_error', {'message': f"Error adding character: {str(e)}"})

# Socket.IO event: remove character from party
@socketio.on('remove_from_party')
def handle_remove_from_party(data):
    try:
        # Input validation
        if not isinstance(data, dict):
            emit('server_error', {'message': 'Invalid data format'})
            return
            
        slot = data.get('slot', 0)
        
        if not isinstance(slot, int) or slot < 0 or slot >= 6:
            emit('server_error', {'message': 'Invalid party slot'})
            return
            
        if not current_party[slot]:
            emit('server_error', {'message': 'No character in that slot'})
            return
            
        character_name = current_party[slot]['name']
        current_party[slot] = None
        
        # Save party data and check success
        if save_party_data():
            # Create updated party information
            party_update = {
                'party': current_party,
                'updated_slot': slot,
                'action': 'remove',
                'character_name': character_name
            }
            
            # Broadcast party update to all clients
            socketio.emit('party_updated', party_update)
            logger.info(f"Removed {character_name} from party slot {slot}")
            emit('update_success', {'message': f"{character_name} removed from party"})
        else:
            emit('server_error', {'message': 'Failed to save party data'})
    except Exception as e:
        logger.error(f"Error removing character from party: {e}")
        emit('server_error', {'message': f"Error removing character: {str(e)}"})

# Socket.IO event: move character within party
@socketio.on('move_character')
def handle_move_character(data):
    try:
        # Input validation
        if not isinstance(data, dict):
            emit('server_error', {'message': 'Invalid data format'})
            return
            
        from_slot = data.get('from_slot')
        to_slot = data.get('to_slot')
        
        if not isinstance(from_slot, int) or not isinstance(to_slot, int):
            emit('server_error', {'message': 'Invalid slot format'})
            return

        if from_slot < 0 or from_slot >= 6 or to_slot < 0 or to_slot >= 6:
            emit('server_error', {'message': 'Invalid party slot'})
            return
            
        if not current_party[from_slot]:
            emit('server_error', {'message': 'No character in source slot'})
            return
            
        # Store character being moved
        character = current_party[from_slot]
        # Store character being replaced (if any)
        replaced = current_party[to_slot]
        
        # Make the swap
        current_party[to_slot] = character
        current_party[from_slot] = replaced
        
        # Save party data and check success
        if save_party_data():
            # Create updated party information
            party_update = {
                'party': current_party,
                'updated_slots': [from_slot, to_slot],
                'action': 'move',
                'character_name': character['name']
            }
            
            # Broadcast party update to all clients
            socketio.emit('party_updated', party_update)
            logger.info(f"Moved {character['name']} from slot {from_slot} to slot {to_slot}")
            emit('update_success', {'message': f"{character['name']} moved to slot {to_slot + 1}"})
        else:
            emit('server_error', {'message': 'Failed to save party data'})
    except Exception as e:
        logger.error(f"Error moving character in party: {e}")
        emit('server_error', {'message': f"Error moving character: {str(e)}"})

# Helper function to save party data
def save_party_data():
    try:
        # Use a lock to ensure thread safety
        with party_lock:
            with open(DATA_DIR / 'party.json', 'w', encoding='utf-8') as f:
                json.dump(current_party, f, ensure_ascii=False, indent=2)
            logger.info("Party data saved successfully")
            return True
    except Exception as e:
        logger.error(f"Error saving party data: {e}")
        return False

# Add a new Socket.IO event for external party updates
@socketio.on('external_party_update')
def handle_external_party_update(data):
    try:
        global current_party
        
        # Validate the incoming data
        if not isinstance(data, dict) or 'party' not in data:
            emit('server_error', {'message': 'Invalid party data format'})
            return
            
        # Update the party data
        new_party = data['party']
        
        # Validate party length
        if len(new_party) != 6:
            emit('server_error', {'message': 'Party must have exactly 6 slots'})
            return
            
        # Update party and save to disk
        current_party = new_party
        if save_party_data():
            # Broadcast to all clients except sender
            party_update = {
                'party': current_party,
                'source': 'external',
                'action': 'full_update'
            }
            emit('party_updated', party_update, broadcast=True, include_self=False)
            emit('update_success', {'message': 'Party updated successfully'})
            logger.info(f"Party externally updated by {request.sid}")
        else:
            emit('server_error', {'message': 'Failed to save party data'})
    except Exception as e:
        logger.error(f"Error handling external party update: {e}")
        emit('server_error', {'message': str(e)})

# Main entry point
if __name__ == '__main__':
    # First run the character data merge if needed
    characters_processed_file = DATA_DIR / 'characters_processed.json'
    if not characters_processed_file.exists():
        try:
            # Try to import and run the merge script
            import importlib.util
            import sys
            
            spec = importlib.util.spec_from_file_location("merge_character_data", 
                                                          BASE_DIR / "merge_character_data.py")
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["merge_character_data"] = module
                spec.loader.exec_module(module)
                
                # Run the merge function
                logger.info("Merging character data...")
                module.merge_character_data()
                
                # Reload character data after merging
                all_characters = load_character_data()
            else:
                logger.warning("Could not load merge_character_data module")
        except Exception as e:
            logger.error(f"Failed to merge character data: {e}")
    
    # Create a placeholder image if it doesn't exist
    placeholder_path = STATIC_DIR / 'img' / 'placeholder.png'
    if not placeholder_path.exists():
        try:
            # Create a simple blank placeholder image using any available method
            # For simplicity, we'll copy a sample image or create a minimal one
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (200, 200), color=(17, 17, 17))
            d = ImageDraw.Draw(img)
            d.text((60, 90), "No Image", fill=(233, 69, 96))
            img.save(placeholder_path)
            logger.info(f"Created placeholder image at {placeholder_path}")
        except ImportError:
            logger.warning("PIL not installed, cannot create placeholder image")
        except Exception as e:
            logger.error(f"Error creating placeholder image: {e}")
    
    # Create required templates directory and index.html if they don't exist
    templates_dir = BASE_DIR / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    index_path = templates_dir / 'index.html'
    if not index_path.exists():
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suikoden Display</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <header>
        <h1>Suikoden Display</h1>
    </header>

    <main>
        <div class="container">
            <section class="panel party-panel">
                <h2>Party Members</h2>
                <div class="party-grid">
                    <!-- Party members will be added dynamically -->
                    <div class="party-slot" data-position="0">
                        <div class="empty-text">Empty</div>
                    </div>
                    <div class="party-slot" data-position="1">
                        <div class="empty-text">Empty</div>
                    </div>
                    <div class="party-slot" data-position="2">
                        <div class="empty-text">Empty</div>
                    </div>
                    <div class="party-slot" data-position="3">
                        <div class="empty-text">Empty</div>
                    </div>
                    <div class="party-slot" data-position="4">
                        <div class="empty-text">Empty</div>
                    </div>
                    <div class="party-slot" data-position="5">
                        <div class="empty-text">Empty</div>
                    </div>
                </div>
            </section>

            <section class="panel stars-panel">
                <h2>108 Stars of Destiny</h2>
                <div class="search-container">
                    <input type="text" id="star-search" placeholder="Search characters...">
                </div>
                <div id="stars-container">
                    <!-- Star characters populated here -->
                </div>
            </section>
        </div>

        <section class="panel recruitment-panel">
            <h2>Recruitment Information</h2>
            <div id="recruitment-display">
                <div class="character-info">
                    <div class="character-image">
                        <img id="selected-character-img" src="{{ url_for('static', filename='img/placeholder.png') }}" alt="Select a character">
                    </div>
                    <div class="character-details">
                        <h3 id="selected-character-name">Select a character</h3>
                        <p id="selected-character-recruitment">Click on a character name from the 108 Stars list to view their recruitment information.</p>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <p>Suikoden Display - Web Interface</p>
    </footer>

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>""")
            logger.info(f"Created index.html template at {index_path}")
        except Exception as e:
            logger.error(f"Error creating index.html template: {e}")
    
    # Ensure party.json exists
    if not (DATA_DIR / 'party.json').exists():
        create_default_party_file()
    
    try:
        logger.info("Starting Suikoden Display web server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Error starting web server: {e}")
