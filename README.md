# 🍇 JellyLooter v2.4.1

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-yellow?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/jellyloot)

Sync media content from remote Jellyfin/Emby servers to your local storage.

![JellyLooter Screenshot](https://raw.githubusercontent.com/jlightner86/jellylooter/main/icon.png)

## ✅ Compatibility

| Platform | Status |
|----------|--------|
| **Unraid 7.2.2** | ✅ Confirmed Working |
| **Unraid 7.2.0** | ✅ Confirmed Working |
| **Docker (Linux)** | ✅ Confirmed Working |
| **Docker (Windows)** | ✅ Confirmed Working |
| **Docker (macOS)** | ✅ Should Work |

## ✨ Features

- 📁 **Browse Remote Libraries** - Navigate and preview content from multiple Jellyfin/Emby servers
- 🔄 **Automatic Sync** - Schedule automatic downloads based on library mappings
- ✓ **Duplicate Detection** - Scans your local library to avoid re-downloading content
- ⏸️ **Download Control** - Pause, resume, and cancel downloads
- 🚀 **Speed Limiting** - Optional bandwidth throttling (updates in real-time)
- 👥 **Dynamic Workers** - Adjust concurrent downloads without restart
- 🔐 **Optional Authentication** - Secure login (disabled by default)
- 📱 **Mobile Friendly** - Responsive design works on phones and tablets
- 🌍 **Multi-Language** - English, Spanish, German (fully translated UI)
- 🎨 **Clean UI** - Jellyfin-inspired dark/light theme with Grid/List view toggle
- 📊 **Download History** - Track completed downloads with timestamps
- ⏱️ **ETA Display** - See estimated time remaining on active downloads

## 🆕 What's New in v2.4.1

- **Full UI Translation** - All modals, buttons, and messages now translate properly
- **Download History** - View completed downloads with timestamps
- **ETA on Downloads** - See estimated time remaining
- **Quick Path Selection** - Jump to mapped folders when downloading
- **Filter/Search** - Find items in your current view
- **Select All/Deselect All** - Bulk selection made easy
- **Title Bar Download Count** - See active downloads in browser tab
- **Fixed username/password auth** - Batch downloads now work with user credentials
- **Improved poster display** - Better image handling for all content types

## 🐳 Docker Installation

### Docker Compose (Recommended)

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
      - ./config:/config
      - /path/to/your/media:/storage  # Change this!
    environment:
      - TZ=America/Chicago
```

### Docker CLI (Linux/macOS)

```bash
docker run -d \
  --name jellylooter \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /path/to/config:/config \
  -v /path/to/media:/storage \
  -e TZ=America/Chicago \
  ghcr.io/jlightner86/jellylooter:latest
```

### 🪟 Docker on Windows

#### Option 1: Docker Desktop with WSL2 (Recommended)

1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. Enable WSL2 backend in Docker Desktop settings
3. Open PowerShell or Command Prompt and run:

```powershell
# Create directories for config and media
mkdir C:\jellylooter\config
mkdir C:\jellylooter\media

# Run the container
docker run -d `
  --name jellylooter `
  --restart unless-stopped `
  -p 5000:5000 `
  -v C:\jellylooter\config:/config `
  -v C:\jellylooter\media:/storage `
  -e TZ=America/Chicago `
  ghcr.io/jlightner86/jellylooter:latest
```

#### Option 2: Docker Compose on Windows

Create a `docker-compose.yml` file:

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
      - C:\jellylooter\config:/config
      - C:\jellylooter\media:/storage
      # Or use a different drive:
      # - D:\Media:/storage
    environment:
      - TZ=America/Chicago
```

Then run:
```powershell
docker-compose up -d
```

#### Windows Path Examples

| Windows Path | Docker Mount |
|--------------|--------------|
| `C:\Users\You\Media` | `-v C:\Users\You\Media:/storage` |
| `D:\Movies` | `-v D:\Movies:/storage` |
| `\\NAS\Media` | Use mapped drive letter instead |

> **Note:** For network shares (NAS), map them to a drive letter first (e.g., `Z:\`) then use that in Docker.

### 🐧 Unraid Installation

1. Go to **Docker → Add Container**
2. Configure:
   - **Repository:** `ghcr.io/jlightner86/jellylooter:latest`
   - **Port:** `5000` → `5000`
   - **Path:** `/config` → `/mnt/user/appdata/jellylooter`
   - **Path:** `/storage` → `/mnt/user` (or your media location)
3. Click **Apply**

Or install from Community Apps using the included `jellylooter.xml` template.

**✅ Confirmed working on Unraid 7.2.0 and 7.2.2**

## 🚀 Quick Start

1. Access the web UI at `http://YOUR_IP:5000`
2. Go to **Settings** and add a remote Jellyfin/Emby server
3. **Test the connection** before adding
4. Browse libraries and download!

## ⚙️ Configuration

### Adding a Remote Server
1. Go to **Settings** tab
2. Click **Add Remote Server**
3. Enter server URL and API key (or username/password)
4. **Test connection first** (important!)
5. Click **Add Server**

> **Important:** If using username/password authentication, always test the connection before adding. Servers must be re-added if you change auth methods.

### Duplicate Detection
1. Configure your local Jellyfin/Emby server in Settings
2. Click **Rebuild Cache** to scan your library
3. Items you already have will be marked with ✓

### Library Mappings (Auto-Sync)
1. Go to **Sync** tab
2. Click **Add Mapping**
3. Select a remote server and library
4. Choose a local destination folder
5. Enable **Auto-Sync** to download new content automatically

### Download Order Options
- **Library Order** - Match remote server order
- **Complete Shows First** - Download all episodes of one show before moving to next
- **Season Round Robin** - First season of each show, then second seasons, etc.
- **Episode Round Robin** - First episode of each show, then second episodes, etc.
- **Alphabetical** - Sort by title
- **Random** - Shuffle order

### Speed Limiting
- Set in **Settings → Advanced → Speed Limit**
- Value is in KB/s (0 = unlimited)
- Changes apply to active downloads within 10 seconds

### Changing Language
- Go to **Settings → Appearance → Language**
- Select English, Spanish, or German
- Click **Save** - page will refresh with new language

## 🔧 Troubleshooting

### "Expecting value" Error on Downloads
This usually means authentication failed. Try:
1. Delete the server from Settings
2. Re-add with correct credentials
3. **Test connection** before adding

### "No space left on device" Error
Check your Docker volume mapping:
```bash
docker inspect jellylooter | grep -A10 "Mounts"
docker exec jellylooter df -h /storage
```

### View Logs
```bash
docker logs -f jellylooter
```

### Windows: "path not found" Error
- Use forward slashes or escaped backslashes in paths
- Ensure Docker Desktop has access to the drive (Settings → Resources → File Sharing)

## ☕ Support the Project

If JellyLooter is useful to you, consider supporting on Ko-fi!

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-yellow?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/jellyloot)

## 📜 License

MIT License

---

JellyLooter v2.4.1 • Made with ❤️ by [FriendlyMedia](https://ko-fi.com/jellyloot)
