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
```

## Install Cloudflared (Optional)

Linux (amd64):
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

macOS:
```bash
brew install cloudflared
```
**Windows: Download from:** https://github.com/cloudflare/cloudflared/releases

## Usage
Basic Usage
```base
python3 gps.py
```
---

## The tool will:

1. Start a Flask server on port 8080
2. Launch a Cloudflared tunnel (if available)
3. Display the phishing URL and dashboard URL

    Then access:
      - http://localhost:8080 - Phishing page
      - http://localhost:8080/results - Dashboard

## Sending the Link
Once the tunnel is active, send the generated URL to the target. When they visit:

1. Immediately: WebRTC IP, browser fingerprint, canvas fingerprint, WebGL info, network data, and battery status are silently collected
2. On Allow: GPS coordinates (if permission granted) are captured, then redirected to Google Maps
3. On Deny: Redirected to Google Maps without GPS

## Dashboard
Access /results to view all captured data:

- Log files with timestamps and IP addresses
- GPS coordinates with direct Google Maps links
- Device fingerprints and canvas hashes
- Network intelligence reports

---

  ## Data Collected
  
   Data Point	| File |	Collection Method |
  |-----------|------|--------------------|
   Victim IP + User-Agent	| victims.log	| HTTP request headers |
   GPS Coordinates	| gps_data.log, gps_links.txt	| Geolocation API (on allow) |
   WebRTC IP	| webrtc_leaks.log	| STUN request via RTCPeerConnection |
   Battery Status	| device_fingerprints.log	| Battery API |
   Browser Fingerprint	| fingerprints.log	| Navigator + Screen APIs |
   Canvas Hash	| canvas_fingerprints.log	| Canvas 2D rendering |
   WebGL/GPU	| gpu_info.log	| WebGL API |
   Network Info	| network_info.log	| Network Information API |
   Extended Network	| network_detector.log | External APIs + WebRTC heuristic |

---

  ## Log File Structure
  ```
  All logs are appended with timestamps and structured for easy parsing:
  ========================================================
  GPS COORDINATES CAPTURED - 2026-06-08 14:30:22
  ========================================================
  Victim IP: 192.168.1.100
  Latitude: 40.712776
  Longitude: -74.005974
  Accuracy: 12m
  Google Maps: https://maps.google.com/?q=40.712776,-74.005974
  ========================================================
  ```
---

# ⚠️ Legal Disclaimer
This tool is intended ONLY for authorized security testing and educational purposes. Usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program.

| Always obtain written permission before testing on any system you do not own.

## Operational Security
- All data is stored locally on the server
- No data is sent to third parties (except victim's browser contacting Google Maps for the redirect)
- External APIs (ipify.org, ipapi.co) are used for public IP and ISP identification
- Cloudflared provides TLS encryption for the phishing page
- Run on a VPS or disposable infrastructure for assessments

## Limitations
WebRTC leaks may not work in all browsers (Chrome/Chromium-based work best)
GPS requires user to click "Allow" and may fail on desktop devices without GPS hardware
Extended network detection depends on external APIs (ipify.org, ipapi.co) which may rate-limit or be blocked
Canvas fingerprinting is blocked by some privacy extensions and browsers (Tor Browser, Brave with shields up)
Screen/webcam capture has been removed from this version; see v1 for that functionality

## License
This project is for educational and authorized security testing purposes only.

## Acknowledgments
- Google Maps for the UI inspiration (used under fair use for security research demonstration)
- Cloudflare for the tunnel service
- ipify.org and ipapi.co for IP geolocation APIs
