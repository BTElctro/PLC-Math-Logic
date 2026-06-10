[app]
title = PLC Logic Studio
package.name = plclogicstudio
package.domain = org.plcstudio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0.0
version.regex = __version__\s*=\s*['\"](.*)['\"]
version.filename = %(source.dir)s/main.py
requirements = python3,kivy==2.3.1,kivymd==1.0.2,Pillow,reportlab

orientation = landscape
osx.prefer_screen = auto
fullscreen = 0

presplash.color = #1E1E1E
icon = 

# Permission
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 34
android.ndk = 25b
android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1,com.google.android.material:material:1.9.0

# Log level (0, 1, 2, 3)
android.logcat_filters = *:S python:D

# Window size (for desktop testing)
window.size = (1200, 800)

# Enable touch emulation
touch = 1
