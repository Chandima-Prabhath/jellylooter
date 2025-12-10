# JellyLooter v2.4.1

## ✅ Compatibility

| Platform | Status |
|----------|--------|
| **Unraid 7.2.2** | ✅ Confirmed Working |
| **Unraid 7.2.0** | ✅ Confirmed Working |
| **Docker (Linux)** | ✅ Confirmed Working |
| **Docker (Windows)** | ✅ Confirmed Working |

## What's New

### 🐛 Bug Fixes
- **Username/password auth fixed** - Batch downloads now work correctly with user credentials
- **Poster display improved** - Better image handling for all content types (backdrops, thumbs, primary)
- **Mobile view fixed** - Hamburger menu and responsive layout work correctly
- **Translation system fixed** - All UI elements now translate properly

### ✨ New Features
- **🌍 Full UI Translation** - All modals, buttons, empty states, and messages translate to selected language
- **📊 Download History** - View completed downloads with timestamps (toggle in Activity Log panel)
- **⏱️ ETA Display** - See estimated time remaining on active downloads
- **📂 Quick Path Selection** - Jump directly to mapped folders when selecting download location
- **🔍 Filter/Search** - Find items in your current library view
- **☑️ Select All/Deselect All** - Bulk selection button for easier batch downloads
- **📑 Title Bar Download Count** - Browser tab shows active download count (e.g., "JellyLooter (3 ⬇)")
- **⚠️ Test Connection Warning** - Modal now reminds users to test before adding servers

### 🔧 Improvements
- Better error handling with detailed logging
- Fallback authentication for non-admin users (/Users/Me endpoint)
- Improved request timeout handling
- More responsive UI updates

---

## Installation

### Docker Compose (All Platforms)
```yaml
version: '3.8'
services:
  jellylooter:
    image: ghcr.io/jlightner86/jellylooter:latest
    container_name: jellylooter
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - /path/to/config:/config
      - /path/to/media:/storage
    environment:
      - TZ=America/Chicago
```

### Docker on Windows (PowerShell)
```powershell
docker run -d `
  --name jellylooter `
  --restart unless-stopped `
  -p 5000:5000 `
  -v C:\jellylooter\config:/config `
  -v C:\jellylooter\media:/storage `
  -e TZ=America/Chicago `
  ghcr.io/jlightner86/jellylooter:latest
```

### Unraid
Install from Community Apps or use the included `jellylooter.xml` template.

---

## Upgrade Notes

### From v2.3.0
- **Username/password servers:** If you have servers configured with username/password authentication that were experiencing download errors, you may need to delete and re-add them to store the user_id correctly.
- **Translations:** New language settings take effect after saving and page refresh.

---

## Known Issues
- Network shares on Windows must be mapped to a drive letter before use in Docker
- Some Jellyfin servers may return backdrop images instead of posters (images will be cropped to fit)

---

## ☕ Support

If JellyLooter saves you time, consider [supporting on Ko-fi](https://ko-fi.com/jellyloot)!

---

**Full Changelog**: https://github.com/jlightner86/jellylooter/compare/v2.3.0...v2.4.1
