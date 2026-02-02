# Plex Refresh

A simple web UI for browsing Plex libraries and triggering metadata refreshes with one click.

## Features

- Browse all Plex library sections (Movies, TV Shows, etc.)
- Navigate through shows, seasons, and episodes
- One-click refresh at any level:
  - Entire library
  - Individual movie or show
  - Specific episode
- Clean, responsive dark theme UI
- Docker support with multi-arch images

## Quick Start

### Docker (Recommended)

```bash
docker run -d \
  -p 5000:5000 \
  -e PLEX_URL=https://your-plex-server.com:32400 \
  -e PLEX_TOKEN=your-plex-token \
  ghcr.io/yourusername/plexrefresh:latest
```

Then open http://localhost:5000 in your browser.

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PlexRefresh.git
   cd PlexRefresh
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy the example environment file and fill in your values:
   ```bash
   cp .env.example .env
   # Edit .env with your Plex URL and token
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open http://localhost:5000

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PLEX_URL` | Your Plex server URL (include port if needed) | `https://plex.example.com:32400` |
| `PLEX_TOKEN` | Your Plex authentication token | `abc123xyz...` |

## Getting Your Plex Token

1. Sign in to Plex Web App
2. Browse to any media item
3. Click the three dots menu (...) and select "Get Info"
4. Click "View XML" at the bottom
5. Look for `X-Plex-Token=` in the URL - that's your token

Alternatively, you can find it in:
- **macOS**: `~/Library/Application Support/Plex Media Server/Preferences.xml`
- **Linux**: `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml`
- **Windows**: `%LOCALAPPDATA%\Plex Media Server\Preferences.xml`

Look for the `PlexOnlineToken` attribute.

## Docker Compose

```yaml
version: '3'
services:
  plex-refresh:
    image: ghcr.io/yourusername/plexrefresh:latest
    ports:
      - "5000:5000"
    environment:
      - PLEX_URL=https://your-plex-server.com:32400
      - PLEX_TOKEN=your-plex-token
    restart: unless-stopped
```

## Building from Source

```bash
docker build -t plex-refresh .
docker run -p 5000:5000 -e PLEX_URL=... -e PLEX_TOKEN=... plex-refresh
```

## How It Works

The app uses the Plex API to:
- List library sections via `/library/sections`
- Get items in sections via `/library/sections/{id}/all`
- Get seasons/episodes via `/library/metadata/{id}/children`
- Trigger refreshes via `/library/sections/{id}/refresh?path={path}`

When you click refresh on a specific item, it passes the file path to Plex so only that item gets rescanned. When refreshing an entire library, no path is sent and Plex scans everything.

## License

MIT
