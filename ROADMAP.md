# JellyLooter Roadmap

## Current Version: 2.3.0

---

## v2.4.1 - Quality of Life Update

**Development:** Local testing on Unraid before public release

### Bug Fixes
| # | Issue | Priority |
|---|-------|----------|
| 1 | Mobile view broken (displays as desktop) | Critical |
| 2 | Language support missing from UI | High |
| 3 | Library poster images wrong aspect ratio | High |

### New Features
| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| 4 | Download progress in title bar | Show "JellyLooter (3 ⬇)" in browser tab | High |
| 5 | Bulk select all on page | Checkbox to select/deselect all visible items | High |
| 6 | Search/filter within library | Filter current view by name | High |
| 7 | Download history | Log of completed downloads with timestamps | Medium |
| 8 | Estimated time remaining | Based on current speed | Medium |
| 9 | Dark/Light mode toggle in header | More visible location | Low |

---

## v2.5.0 - Performance & Security Update

### New Features
| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| 1 | Stop after current downloads | Finish active downloads but don't start new ones from queue | Medium |

### Performance Optimization

**Current Problems:**
| Issue | Likely Cause |
|-------|--------------|
| UI freezes during downloads | Blocking I/O on main thread |
| Sluggish response | Status polling too heavy |
| High CPU usage | Inefficient loops, no caching |
| Memory bloat | Holding too much in memory |

**Optimization Targets:**
| Area | Current | Optimized |
|------|---------|-----------|
| Status polling | Every 1 second, full data | Every 2-3 sec, delta updates only |
| Download workers | May block Flask thread | Fully async, separate process |
| File I/O | Synchronous | Async with threading |
| Config loading | Read from disk every request | Cache in memory, reload on change |
| Local cache | Full scan on rebuild | Incremental updates |
| Logging | Unbounded list | Ring buffer (last 500 entries) |
| Frontend | Re-render everything | Only update changed elements |

**Technical Fixes:**
1. Move downloads to separate process (multiprocessing)
2. Async Flask with gevent OR switch to FastAPI
3. Smarter status polling (delta updates)
4. Config caching with mtime check
5. Limit log buffer with deque(maxlen=500)
6. Frontend incremental DOM updates

### Security Hardening

**Current Vulnerabilities:**
| Risk | Issue | Severity |
|------|-------|----------|
| Path Traversal | `browse_local` may allow `../../etc/passwd` | Critical |
| No CSRF Protection | Forms vulnerable to cross-site attacks | High |
| Secrets in Config | API keys stored in plain text JSON | High |
| No Rate Limiting | Login brute-force possible | High |
| Session Security | Flask secret key handling | Medium |
| XSS Potential | User input in templates | Medium |
| No HTTPS Enforcement | Credentials sent in clear | Medium |

**Security Fixes:**
| Priority | Fix | Effort |
|----------|-----|--------|
| 1 | Path traversal protection | Easy |
| 2 | Rate limiting on login (5/min) | Easy |
| 3 | Input validation (URL, API key format) | Medium |
| 4 | Security headers (X-Frame-Options, CSP, etc.) | Easy |
| 5 | CSRF protection (flask-wtf) | Medium |
| 6 | Session hardening (secure cookies) | Easy |
| 7 | Encrypt stored API keys | Medium |
| 8 | HTTPS documentation | Easy |

### *arr Integration (Basic)

**Supported Apps:**
| App | Media Type |
|-----|------------|
| Sonarr | TV Shows |
| Radarr | Movies |
| Lidarr | Music |
| Readarr | Books |

**v2.5.0 Features:**
- Download to monitored folder
- API trigger after download complete
- Trigger library scan on import

**Settings UI:**
```
┌─────────────────────────────────────┐
│ *arr Integration                    │
├─────────────────────────────────────┤
│ Sonarr                              │
│ URL: [http://localhost:8989    ]    │
│ API Key: [••••••••••••••••••••]     │
│ [Test] ✓ Connected                  │
│                                     │
│ Radarr                              │
│ URL: [http://localhost:7878    ]    │
│ API Key: [••••••••••••••••••••]     │
│ [Test] ✓ Connected                  │
│                                     │
│ ☑ Notify on download complete       │
│ ☑ Trigger library scan              │
└─────────────────────────────────────┘
```

---

## v3.0.0 - Pro Features & Licensing

### Licensing System

**Tiers:**
| Tier | Price | Duration |
|------|-------|----------|
| Free | $0 | Forever |
| Trial | $0 | 14 days (user-activated) |
| Pro | $5 | Lifetime |

**Trial System:**
- User must click to activate (not automatic)
- 14 days from activation
- Floating banner reminder at bottom of page
- Reverts to Free on expiration (no data loss)
- Cannot re-activate trial (tied to config)

### Banner/Advertisement System

| Tier | Bottom Banner | Header Button |
|------|---------------|---------------|
| Free | Ko-fi support banner (permanent) | ❤️ Support button |
| Trial | "Pro Trial: X days left - Buy $5" | ❤️ Support button |
| Pro | None - clean UI | None |

### Free vs Pro Features

| Feature | Free | Pro |
|---------|------|-----|
| Remote servers | 1 | Unlimited |
| Local servers | 1 | Unlimited |
| Downloads | Manual only | Auto-sync scheduling |
| Items per page | 50 max | Unlimited |
| Theme | Default only | Custom themes + pre-built |
| Download history | ❌ | ✅ |
| Search/filter | ❌ | ✅ |
| Download scheduling | ❌ | ✅ |
| Bandwidth scheduling | ❌ | ✅ |
| Discord/Telegram notifications | ❌ | ✅ |
| Download stats dashboard | ❌ | ✅ |
| Import/Export config | ❌ | ✅ |
| Full *arr integration | ❌ | ✅ |
| Ads/Banners | Yes | None |

### Pro-Only Features (Never in Free)
- Multiple local servers
- Multiple remote servers
- Auto-sync scheduling
- Custom themes
- Notifications
- Full *arr integration

### Customization (Pro)
| Feature | Description |
|---------|-------------|
| Custom themes | Color picker for accent, background, text colors |
| Pre-built themes | Plex orange, Emby green, Netflix red, custom CSS |
| Custom logo/branding | Replace JellyLooter logo with their own |
| Dashboard layout | Rearrange panels, hide/show sections |

### Power Features (Pro)
| Feature | Description |
|---------|-------------|
| Download scheduling | Only download between specific hours (e.g., 2am-6am) |
| Bandwidth scheduling | Full speed at night, throttled during day |
| Transcode on download | Convert to different format/quality |
| Watch folders | Auto-download when new content appears on remote |

### Organization (Pro)
| Feature | Description |
|---------|-------------|
| Collections/Playlists | Group items to download together |
| Tags/Labels | Organize downloads with custom tags |
| Favorites | Star items to download later |
| Download profiles | Save different settings (4K profile, mobile profile) |

### Notifications (Pro)
| Feature | Description |
|---------|-------------|
| Discord webhook | Notify when downloads complete |
| Email notifications | Daily/weekly digest |
| Telegram bot | Push notifications |
| Apprise integration | Supports 80+ notification services |

### Analytics (Pro)
| Feature | Description |
|---------|-------------|
| Download stats | Total downloaded, by server, by month |
| Storage dashboard | Visual breakdown of disk usage |
| Speed graphs | Historical download speed chart |
| Activity calendar | Heatmap of download activity |

### Advanced (Pro)
| Feature | Description |
|---------|-------------|
| API access | REST API for automation |
| Webhook triggers | Trigger external scripts on events |
| Import/Export config | Backup and restore settings |

### Full *arr Integration (Pro)
| Feature | Description |
|---------|-------------|
| Search wanted | Show Sonarr/Radarr wanted/missing list |
| Auto-match | Link JellyLooter items to *arr entries |
| Quality profiles | Respect *arr quality settings |
| Status sync | Show import status in JellyLooter |

---

## v4.0.0 - Future Ideas

| Feature | Description |
|---------|-------------|
| Multi-user | Separate accounts with permissions |
| Mobile app | PWA or native app |
| Plex support | Add Plex as source/destination |
| Cloud storage | Download to S3, Google Drive, etc. |

---

## Technical Notes

### License Key System
- Simple key validation (no server required)
- Keys generated via email hash or random string
- Blacklist leaked keys in future updates
- Store in config.json

### Platforms for Selling
| Platform | Fee | Notes |
|----------|-----|-------|
| Ko-fi | 0% | Already set up |
| Gumroad | 10% | Built-in license keys |
| LemonSqueezy | 5-8% | Modern, good for software |

### Anti-Abuse (Light Touch)
- Config-based trial tracking (`trial_started: timestamp`)
- Hash of server URL + install path as fingerprint
- Not worth heavy DRM for $5 - honest people will pay

---

## Development Notes

- All development/testing done locally on Unraid before public release
- Ko-fi link: https://ko-fi.com/jellyloot
- No priority support offered - documentation and community only

---

*Last updated: December 2024*
