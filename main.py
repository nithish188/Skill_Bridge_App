"""
SkillBridge Android App
A lightweight Kivy WebView that opens the SkillBridge web app.

HOW IT WORKS:
- On Android, it opens the SkillBridge URL in the native browser via Intent.
- The Flask backend runs on your PC/server — configure SERVER_URL below.

DEPLOYMENT OPTIONS:
1. Local Network: Run 'python app.py' on your PC, set SERVER_URL to your PC's IP
   e.g. SERVER_URL = "http://192.168.1.100:5000"
2. Cloud Deployment: Deploy Flask to Render/Railway, set SERVER_URL to that URL
   e.g. SERVER_URL = "https://skillbridge.onrender.com"
"""

# =====================================================================
# CONFIGURE YOUR SERVER URL HERE
# If running on local network: use your PC's IP (e.g. 192.168.1.5:5000)
# If deployed to cloud: use your deployment URL
SERVER_URL = "http://192.168.1.100:5000"
# =====================================================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.clock import Clock
from kivy.core.window import Window


class SkillBridgeApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.04, 0.06, 1)  # Dark background #0a0a0f
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        title = Label(
            text="[b]SkillBridge[/b]",
            markup=True,
            font_size='32sp',
            color=(0.39, 0.40, 0.95, 1),  # #6366f1
            size_hint=(1, 0.3)
        )

        subtitle = Label(
            text="AI-Powered Adaptive Learning Engine",
            font_size='16sp',
            color=(0.7, 0.7, 0.8, 1),
            size_hint=(1, 0.15)
        )

        self.status_label = Label(
            text=f"Connecting to:\n{SERVER_URL}",
            font_size='13sp',
            color=(0.5, 0.5, 0.6, 1),
            size_hint=(1, 0.2),
            halign='center'
        )

        open_btn = Button(
            text="Open SkillBridge →",
            font_size='18sp',
            size_hint=(1, 0.15),
            background_color=(0.39, 0.40, 0.95, 1),
            color=(1, 1, 1, 1)
        )
        open_btn.bind(on_press=self.open_app)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(self.status_label)
        layout.add_widget(open_btn)

        # Auto-open on Android after 1 second
        if platform == 'android':
            Clock.schedule_once(self.open_app, 1)

        return layout

    def open_app(self, *args):
        """Open the SkillBridge URL using the native Android browser."""
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(SERVER_URL))
                PythonActivity.mActivity.startActivity(intent)
                self.status_label.text = "Opening SkillBridge..."
            except Exception as e:
                self.status_label.text = f"Error: {e}"
        else:
            import webbrowser
            webbrowser.open(SERVER_URL)
            self.status_label.text = "Opening in desktop browser..."


if __name__ == "__main__":
    SkillBridgeApp().run()
