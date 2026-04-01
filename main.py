"""
SkillBridge Android Entry Point
Bridges the Flask server to an Android WebView using Kivy.
"""
import os
import sys
import threading
from time import sleep

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

# Start Flask in a background thread
def start_flask():
    print("Starting Flask server...")
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)

class SkillBridgeMobile(App):
    def build(self):
        # Start Flask thread
        self.flask_thread = threading.Thread(target=start_flask)
        self.flask_thread.daemon = True
        self.flask_thread.start()
        
        # Give Flask a second to start
        sleep(1.5)
        
        # Create a layout to hold the WebView
        layout = BoxLayout(orientation='vertical')
        
        if platform == 'android':
            from android.webview import WebView
            # Initialize Android WebView pointing to local Flask
            self.webview = WebView("http://127.0.0.1:5000")
        else:
            # Fallback for desktop testing (showing a label instead of a full browser)
            from kivy.uix.label import Label
            return Label(text="SkillBridge: Server running on localhost:5000\n(WebView only active on Android)")
            
        return layout

if __name__ == "__main__":
    SkillBridgeMobile().run()
