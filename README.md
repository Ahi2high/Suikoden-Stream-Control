Suikoden I Stream Control
Suikoden I Stream Control is a Tkinter-based desktop application designed to assist streamers in tracking and managing key aspects of Suikoden I gameplay. This application provides an intuitive interface with multiple tabs to monitor party members, the 108 Stars of Destiny, and recruitment progress.

Features
Dynamic Background Resizing – The application adjusts seamlessly to window size.

Party Management – View and organize your party members.

108 Stars of Destiny Tracking – Keep track of all recruitable characters.

Recruitment Progress – Monitor which characters have been recruited and their conditions.

Custom Themes & Styles – Dark UI with Suikoden-inspired aesthetics.

Real-time WebSocket Support – Communicate with external applications or scripts.

Technologies Used
Python (Tkinter for UI)

PIL (Pillow) for image handling

JSON for storing character and recruitment data

WebSocket (for real-time server communication)

Installation & Setup
Prerequisites
Ensure you have Python installed on your system. You can download it from Python's official website.

Steps
Clone the repository:

sh
Copy
Edit
git clone https://github.com/yourusername/suikoden-stream-control.git
cd suikoden-stream-control
Install dependencies:

sh
Copy
Edit
pip install -r requirements.txt
Running the Application
There are two ways to run the application:

Standalone Mode (Main GUI)
Run the application as a standalone GUI program:

sh
Copy
Edit
python main.py
This launches the graphical interface, allowing you to interact with the party tracker, 108 Stars of Destiny, and recruitment progress.

WebSocket Mode (Streamer View)
If you want to enable WebSocket functionality for external integrations, run:

sh
Copy
Edit
python web_interface.py
This will start a WebSocket server on 127.0.0.1:5000, allowing communication with other applications or scripts in real time. Note: The main.py GUI does not need to be running at the same time as web_interface.py. This allows you to access the application from a separate web interface or streamer's view.

Important Note
As of now, the web_interface.py operates as a standalone server-side application, so main.py is not required to run concurrently. In future updates, the integration between the two will be fixed for a more streamlined experience.

GUI Colors Update
The application's user interface has received some updates to its color scheme for better contrast and readability. This update includes:

Background Color – Darker shades for improved visual appeal.

Accent Color – Red accents for better navigation.

Text Color – Lighter shades for text, ensuring legibility against the dark background.

If you'd like to customize the colors further, refer to the styles section in the main.py script for color variables.

Usage
The application will launch with a user-friendly interface.

Use the tabs to navigate through different sections:

Party Tab: View and manage your party members.

108 Stars Tab: Track the progress of character recruitment.

Recruitment Tab: Monitor recruit conditions and statuses.

The background will dynamically adjust based on window size for better visualization.

Future Enhancements
Integration with Twitch API for live updates.

Additional tracking for items, runes, and battles.

Further integration of main.py and web_interface.py for a unified experience.

Customizable themes and settings.

Contributing
Contributions are welcome! If you find bugs or have suggestions for improvements, feel free to open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For any inquiries or suggestions, reach out via GitHub Issues.

🚀 Enhance your Suikoden I streaming experience with organization! real-time tracking (being workded on)
