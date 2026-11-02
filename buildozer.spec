[app]
title = Ttoken Escritorio
package.name = ttokenescritorio
package.domain = br.com.grupofb
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp4
version = 0.1.0
requirements = python3,kivy,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,POST_NOTIFICATIONS,READ_MEDIA_VIDEO,READ_EXTERNAL_STORAGE
android.api = 35
android.minapi = 23
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.release_artifact = apk
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
