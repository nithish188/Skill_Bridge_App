[app]
# (str) Title of your application
title = SkillBridge

# (str) Package name
package.name = skillbridge

# (str) Package domain (needed for android/ios packaging)
package.domain = org.sixmindslabs

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Keep it minimal - only Kivy and pyjnius for the WebView bridge
requirements = python3,kivy,pyjnius

# (str) App icon
icon.filename = %(source.dir)s/static/img/icon.png

# (str) Supported orientation
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Android API to use
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage
android.private_storage = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
warn_on_root = 1
