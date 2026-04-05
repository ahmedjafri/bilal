# Bilal

A low-dependency azan clock that is optimized for playing the azan reliably every time. Bilal calculates prayer times for your location and plays the azan audio at each salat time. It includes a web dashboard for viewing prayer times and configuring settings.

## Requirements

- **Python** 3.10+
- **Poetry** for dependency and virtualenv management
- **Node.js / npm** for running project scripts (optional, convenience wrapper around poetry commands)

### Audio playback

Bilal uses the system audio player to play `.wav` files:

- **Linux** -- `aplay` (part of `alsa-utils`)
  ```
  # Debian / Ubuntu / Raspberry Pi OS
  sudo apt install alsa-utils
  ```
- **macOS** -- `afplay` (included with macOS, no install needed)

### Network discovery (optional)

Bilal registers itself on the local network via mDNS (Zeroconf) so other devices can find it. This works out of the box on macOS. On Linux, make sure Avahi is available:

```
sudo apt install avahi-daemon
```

## Getting started

### Install dependencies

```
poetry install
```

Or via npm:

```
npm install
```

### Run

```
poetry run bilal
```

Or via npm:

```
npm start
```

The web dashboard will be available at **http://localhost:8080**.

### Configuration

On first run, Bilal creates a `config.json` in the working directory with defaults:

| Setting              | Default         | Description                          |
| -------------------- | --------------- | ------------------------------------ |
| `latitude`           | `47.606209`     | Your latitude (decimal degrees)      |
| `longitude`          | `-122.332069`   | Your longitude (decimal degrees)     |
| `calculation_method` | `MWL`           | Prayer time calculation method       |
| `quiet_times_start`  | `9`             | Quiet hours start (hour, 24h format) |
| `quiet_times_end`    | `18`            | Quiet hours end (hour, 24h format)   |

You can edit `config.json` directly or use the Settings page in the web dashboard.

**Supported calculation methods:** MWL, ISNA, Egypt, Makkah, Karachi, Tehran, Jafari

### Quiet hours

During quiet hours (weekdays only), Bilal skips audio playback. Set `quiet_times_start` and `quiet_times_end` to the hour range you want silenced. For example, start=9 and end=18 means azans between 9:00 AM and 5:59 PM won't play audio.

## Development

### Run tests

```
npm test
```

### Lint and format

```
npm run lint
npm run format
```

### Build

Build a Python wheel:

```
npm run build:wheel
```

Build the Docker image:

```
npm run build:docker
```

### Docker

```
npm run build:docker
npm run docker:run
```

On Linux, `--device /dev/snd` is passed so the container can access the host sound card. You may also need to pass `--privileged` or map specific ALSA devices depending on your setup.

### All npm scripts

| Script           | Description                     |
| ---------------- | ------------------------------- |
| `npm install`    | `poetry install`                |
| `npm start`      | Run bilal                       |
| `npm run dev`    | Run bilal (same as start)       |
| `npm test`       | Run pytest                      |
| `npm run lint`   | Lint with ruff                  |
| `npm run format` | Format with ruff                |
| `npm run build:wheel`  | Build Python wheel        |
| `npm run build:docker` | Build Docker image        |
| `npm run docker:run`   | Run Docker container      |
| `npm run clean`  | Remove build artifacts          |

## License

MIT
