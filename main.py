"""
SkillBridge Android Entry Point
Bridges the Flask server to an Android WebView using Kivy + pyjnius.
"""
import os
import sys
import threading
from time import sleep

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock


def start_flask():
    """Start Flask server in a background thread."""
    try:
        from app import app
        print("Starting Flask server on 127.0.0.1:5000...")
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"Flask startup error: {e}")


class SkillBridgeMobile(App):
    def build(self):
        # Start Flask thread
        self.flask_thread = threading.Thread(target=start_flask, daemon=True)
        self.flask_thread.start()

        layout = BoxLayout(orientation='vertical')

        if platform == 'android':
            # Schedule webview open after Kivy is ready
            Clock.schedule_once(self.open_webview, 2)
        else:
            from kivy.uix.label import Label
            layout.add_widget(Label(
                text="SkillBridge Desktop Mode\nFlask running at http://127.0.0.1:5000\nOpen in your browser to test.",
                halign='center'
            ))

        return layout

    def open_webview(self, dt):
        """Open Android WebView using pyjnius to access native Java APIs."""
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            # Open the local Flask URL in the device's browser/webview
            intent = Intent(Intent.ACTION_VIEW, Uri.parse("http://127.0.0.1:5000"))
            PythonActivity.mActivity.startActivity(intent)
        except Exception as e:
            print(f"WebView error: {e}")


if __name__ == "__main__":
    SkillBridgeMobile().run()
