[app]
# (str) Title of your application
title = SkillBridge

# (str) Package name
package.name = skillbridge

# (str) Package domain (needed for android/ios packaging)
package.domain = org.6ixmindslabs

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,ttf,json,css,js,html

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,flask,pdfplumber,python-docx,werkzeug

# (str) Custom source folders for requirements
# (list) Garden requirements
# (str) Presplash of the application
#icon.filename = %(source.dir)s/static/img/icon.png
icon.filename = %(source.dir)s/static/img/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
#android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is to use start.py
android.entrypoint = android_main.py

# (list) List of Java files to add to the android project (for WebView bridge)
#android.add_src =

# (list) Java libraries to add
#android.add_libs_external = 

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1
