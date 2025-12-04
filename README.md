# 🍇 JellyLooter v2.3.0

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/friendlymedia)

Sync media content from remote Jellyfin/Emby servers to your local storage.

![JellyLooter Screenshot](https://raw.githubusercontent.com/jlightner86/jellylooter/main/icon.png)

## ✨ Features

- 📁 **Browse Remote Libraries** - Navigate and preview content from multiple Jellyfin/Emby servers
- 🔄 **Automatic Sync** - Schedule automatic downloads based on library mappings
- ✓ **Duplicate Detection** - Scans your local library to avoid re-downloading content
- ⏸️ **Download Control** - Pause, resume, and cancel downloads
- 🚀 **Speed Limiting** - Optional bandwidth throttling (updates in real-time)
- 👥 **Dynamic Workers** - Adjust concurrent downloads without restart
- 🔐 **Optional Authentication** - Secure login (disabled by default)
- 📱 **Mobile Friendly** - Responsive design works on phones and tablets
- 🌍 **Multi-Language** - English, Spanish, German
- 🎨 **Clean UI** - Jellyfin-inspired dark theme with Grid/List view toggle

## 🆕 What's New in v2.3.0

- **Authentication is now optional** - No more secret key errors! Auth is disabled by default.
- **Mobile-friendly design** - Works great on phones and tablets
- **Grid/List view toggle** - Choose how you browse your library
- **Pagination** - Configurable items per page (25/50/100)
- **Download queue ordering** - Library order, complete shows first, round-robin, alphabetical, or random
- **Multi-language support** - English, Spanish, German
- **Fixed tooltip z-index** - Refresh button tooltip no longer hidden
- **Confirmed working on Unraid 7.2.0**

## 🐳 Docker Installation

### Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  jellylooter:
    build: .
    container_name: jellylooter
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./config:/config
      - /path/to/your/media:/storage  # Change this!
    environment:
      - TZ=America/Chicago
```

### Docker CLI

```bash
docker build -t jellylooter .
docker run -d \
  --name jellylooter \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /path/to/config:/config \
  -v /path/to/media:/storage \
  -e TZ=America/Chicago \
  jellylooter
```

### Unraid

1. Go to **Docker → Add Container**
2. Configure:
   - **Repository:** `jellylooter`
   - **Port:** `5000` → `5000`
   - **Path:** `/config` → `/mnt/user/appdata/jellylooter`
   - **Path:** `/storage` → `/mnt/user` (or your media location)
3. Click **Apply**

## 🚀 Quick Start

1. Access the web UI at `http://YOUR_IP:5000`
2. Add a remote Jellyfin/Emby server in Settings
3. Browse and download!

## ⚙️ Configuration

### Adding a Remote Server
1. Go to **Settings** tab
2. Click **Add Server**
3. Enter server URL and API key (or username/password)
4. Test connection and save

### Duplicate Detection
1. Configure your local Jellyfin/Emby server in Settings
2. Click **Rebuild Cache** to scan your library
3. Items you already have will be marked with ✓

### Download Order Options
- **Library Order** - Match remote server order
- **Complete Shows First** - Download all episodes of one show before moving to next
- **Season Round Robin** - First season of each show, then second seasons, etc.
- **Episode Round Robin** - First episode of each show, then second episodes, etc.
- **Alphabetical** - Sort by title
- **Random** - Shuffle order

### Speed Limiting
- Set in **Settings → Downloads → Speed Limit**
- Value is in KB/s (0 = unlimited)
- Changes apply to active downloads within 10 seconds

## 🔧 Troubleshooting

### "No space left on device" Error
Check your Docker volume mapping:
```bash
docker inspect jellylooter | grep -A10 "Mounts"
docker exec jellylooter df -h /storage
docker exec jellylooter touch /storage/test && docker exec jellylooter rm /storage/test
```

### View Logs
```bash
docker logs -f jellylooter
```

## ☕ Support the Project

If JellyLooter is useful to you, consider buying me a coffee!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/friendlymedia)

## 📜 License

MIT License

---

JellyLooter v2.3.0 • Made with ❤️ by [FriendlyMedia](https://buymeacoffee.com/friendlymedia)
