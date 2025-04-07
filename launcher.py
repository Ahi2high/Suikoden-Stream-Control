#!/usr/bin/env python
"""
Suikoden Display Launcher
------------------------
Launches both the web interface and GUI components of the Suikoden Display application.
"""

import os
import sys
import time
import signal
import logging
import threading
import subprocess
import webbrowser
from pathlib import Path
import multiprocessing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('launcher.log')
    ]
)
logger = logging.getLogger('suikoden_launcher')

# Path configurations
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Global flags
web_process = None
gui_process = None
is_running = True

def setup_environment():
    """Prepare the environment for running the application."""
    try:
        # Create necessary directories if they don't exist
        for dir_path in ['data', 'static/css', 'static/js', 'static/img', 'templates']:
            (BASE_DIR / dir_path).mkdir(exist_ok=True, parents=True)
            
        # Check for required files
        if not (DATA_DIR / 'party.json').exists():
            logger.info("Creating default party.json file")
            create_default_party_file()
            
        # Check for dependencies
        missing_deps = check_dependencies()
        if missing_deps:
            logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
            logger.info("Please install missing dependencies using pip:")
            logger.info(f"pip install {' '.join(missing_deps)}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        return False

def create_default_party_file():
    """Create a default empty party file if it doesn't exist."""
    try:
        empty_party = [None] * 6
        with open(DATA_DIR / 'party.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(empty_party, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to create default party.json file: {e}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []
    required = ['flask', 'flask_socketio']
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def start_web_interface():
    """Start the web interface server on localhost only."""
    try:
        import web_interface
        from web_interface import app, socketio
        
        # Override host to localhost only
        logger.info("Starting web interface on http://127.0.0.1:5000")
        socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Error starting web interface: {e}")

def start_gui():
    """Start the GUI application."""
    try:
        # Check if main.py exists
        gui_path = BASE_DIR / 'main.py'
        
        if gui_path.exists():
            logger.info("Starting Suikoden GUI application")
            # Import and run the GUI module
            sys.path.insert(0, str(BASE_DIR))
            try:
                import main
                if hasattr(main, 'main'):
                    main.main()
                else:
                    logger.warning("No main() function found in main.py, attempting to run module directly")
                    exec(open(gui_path).read())
            except Exception as e:
                logger.error(f"Error running GUI from module: {e}")
                # Fallback to subprocess
                run_gui_process()
        else:
            logger.warning("main.py not found, checking for alternative GUI files")
            # Look for other potential GUI files
            gui_files = list(BASE_DIR.glob('*main*.py'))
            if gui_files:
                logger.info(f"Found potential GUI file: {gui_files[0].py}")
                run_gui_process(gui_files[0])
            else:
                logger.error("No GUI file found. Please create a GUI file or specify the path.")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error starting GUI application: {e}")
        return False

def run_gui_process(gui_file=None):
    """Run the GUI as a subprocess."""
    global gui_process
    
    if gui_file is None:
        gui_file = BASE_DIR / 'main.py'
    
    try:
        # Start the GUI as a subprocess
        cmd = [sys.executable, str(gui_file)]
        gui_process = subprocess.Popen(cmd)
        return True
    except Exception as e:
        logger.error(f"Error running GUI subprocess: {e}")
        return False

def run_web_process():
    """Run the web interface as a subprocess."""
    global web_process
    
    try:
        # Start the web interface as a subprocess
        cmd = [sys.executable, str(BASE_DIR / 'web_interface.py'), '--local-only']
        web_process = subprocess.Popen(cmd)
        return True
    except Exception as e:
        logger.error(f"Error running web interface subprocess: {e}")
        return False

def open_browser():
    """Open the web browser to the application URL."""
    time.sleep(2)  # Give the web server a moment to start
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")

def cleanup():
    """Clean up resources and terminate processes."""
    global web_process, gui_process, is_running
    
    logger.info("Shutting down Suikoden Display...")
    is_running = False
    
    # Terminate web process if running
    if web_process:
        logger.info("Terminating web interface")
        try:
            web_process.terminate()
            web_process.wait(timeout=5)
        except Exception as e:
            logger.error(f"Error terminating web process: {e}")
            try:
                web_process.kill()
            except:
                pass
    
    # Terminate GUI process if running
    if gui_process:
        logger.info("Terminating GUI application")
        try:
            gui_process.terminate()
            gui_process.wait(timeout=5)
        except Exception as e:
            logger.error(f"Error terminating GUI process: {e}")
            try:
                gui_process.kill()
            except:
                pass
    
    logger.info("Shutdown complete")

def signal_handler(sig, frame):
    """Handle termination signals."""
    logger.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

def main():
    """Main entry point for the launcher."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Suikoden Display Launcher")
    
    # Setup environment
    if not setup_environment():
        logger.error("Failed to set up environment. Exiting.")
        return 1
    
    try:
        # Use multiprocessing to run components
        web_process = multiprocessing.Process(target=start_web_interface)
        web_process.daemon = True
        web_process.start()
        
        # Open browser after a short delay
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start GUI (this will block until GUI closes)
        start_gui()
        
        # If GUI exits, wait briefly for user to close browser too
        time.sleep(2)
        
        # If we get here, the GUI has closed, so clean up
        cleanup()
        
        return 0
    except KeyboardInterrupt:
        logger.info("User interrupted the program")
        cleanup()
        return 0
    except Exception as e:
        logger.error(f"Unexpected error in launcher: {e}")
        cleanup()
        return 1
    finally:
        # Ensure processes are terminated
        if web_process and web_process.is_alive():
            web_process.terminate()
        if 'gui_process' in locals() and gui_process and gui_process.poll() is None:
            gui_process.terminate()

if __name__ == "__main__":
    sys.exit(main())

