# PLC Logic Studio - Android

## Build APK (GitHub Actions)

1. ارفع هذا المجلد إلى GitHub
2. اذهب إلى **Actions** ← **Build PLC Studio APK** ← **Run workflow**
3. انتظر 15-30 دقيقة (البناء الأول)
4. حمّل الـ APK من **Artifacts**

## Build Locally (Linux/WSL)

```bash
pip install buildozer
buildozer android debug
```
