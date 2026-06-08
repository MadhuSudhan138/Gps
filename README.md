# Google Maps Location Tracker (GMLT)

A penetration testing tool for capturing geolocation data, device fingerprints, and network intelligence through a social engineering attack vector. This tool demonstrates how a convincing Google Maps permission prompt can be used to collect sensitive target information during authorized security assessments.

---

## About

**Google Maps Location Tracker (GMLT)** is an ethical hacking tool designed for authorized penetration testers and security researchers. It simulates a realistic Google Maps location permission prompt to capture:

-  **GPS Coordinates** - Precise latitude/longitude with accuracy metrics
-  **WebRTC IP Leak** - Real IP addresses leaked through WebRTC STUN requests
-  **Device Fingerprinting** - Screen resolution, platform, languages, timezone, storage capabilities
-  **Canvas Fingerprinting** - Browser-specific rendering hashes for unique device identification
-  **WebGL/GPU Information** - Graphics vendor and renderer details
-  **Network Intelligence** - Connection type, effective bandwidth, RTT, downlink speed
-  **Extended Network Detection** - ISP identification, VPN/proxy detection, Tor detection, public IP enumeration
-  **Battery Status** - Level and charging state

All data is logged to structured files for analysis during security assessments.

---

## Features

| Feature | Description |
|---------|-------------|
| **Realistic UI** | Convincing Google Maps permission dialog with embedded Google Maps background |
| **Silent Collection** | WebRTC, fingerprinting, canvas, WebGL, network data collected without user interaction |
| **GPS Capture** | High-accuracy GPS coordinates with Google Maps link generation |
| **Network Detector** | ISP identification, VPN/proxy detection, connection quality metrics |
| **Auto-redirect** | After data collection, user is redirected to real Google Maps |
| **Cloudflared Tunnel** | Automatic public URL generation via Cloudflared |
| **Dashboard** | Web-based results viewer at `/results` |

---

## Installation

### Prerequisites

- Python 3.7+
- Cloudflared (for public tunnel) - optional, can use locally

### Install Dependencies

```bash
pip install flask
