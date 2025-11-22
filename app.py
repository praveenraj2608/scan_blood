from flask import Flask, render_template_string, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb+srv://praveensah2608_db_user:XEDQI2M5OWk4I3EE@cluster0.lilts6y.mongodb.net/lifelink_grid?retryWrites=true&w=majority')
mongo = PyMongo(app)

# Collections
blood_units = mongo.db.blood_units
hospitals = mongo.db.hospitals
donors = mongo.db.donors
scan_logs = mongo.db.scan_logs
activities = mongo.db.activities

# Mobile-Optimized Dark Theme HTML with Enhanced Features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0a0e27">
    <title>Blood Bank Mobile Scanner</title>
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(239, 68, 68, 0.15) 0px, transparent 50%);
            min-height: 100vh;
            padding: 15px;
            color: #e2e8f0;
            overflow-x: hidden;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 20px;
            padding: 20px 0;
        }

        .header h1 {
            font-size: 1.8rem;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #667eea 0%, #ef4444 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stats-bar {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 15px;
            padding: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        }

        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
            display: block;
            margin-bottom: 4px;
        }

        .stat-label {
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .scanner-wrapper {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }

        #reader {
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 15px;
            border: 2px solid rgba(99, 102, 241, 0.4);
            background: #000;
        }

        #reader video {
            width: 100% !important;
            height: auto !important;
            border-radius: 15px;
        }

        .controls {
            text-align: center;
            margin-top: 15px;
            display: grid;
            gap: 10px;
        }

        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            width: 100%;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }

        .btn-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }

        .btn-warning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }

        .btn:active {
            transform: scale(0.98);
        }

        .result-card {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            display: none;
            animation: slideUp 0.4s ease-out;
        }

        .result-card.show {
            display: block;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .blood-info {
            display: grid;
            gap: 12px;
            margin-top: 15px;
        }

        .info-item {
            background: rgba(30, 41, 59, 0.7);
            padding: 12px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }

        .info-label {
            font-size: 11px;
            text-transform: uppercase;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .info-value {
            font-size: 16px;
            font-weight: 700;
            color: #e2e8f0;
        }

        .blood-type-big {
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            border-radius: 12px;
            font-size: 28px;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
        }

        .status-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
        }

        .status-available {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }

        .status-used {
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            color: white;
        }

        .status-expired {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }

        .alert {
            padding: 12px;
            border-radius: 8px;
            margin: 12px 0;
            font-size: 14px;
        }

        .alert-warning {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fbbf24;
        }

        .alert-danger {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }

        .alert-success {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #6ee7b7;
        }

        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            background: rgba(15, 23, 42, 0.6);
            padding: 6px;
            border-radius: 12px;
        }

        .tab {
            flex: 1;
            padding: 10px;
            background: transparent;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            color: #94a3b8;
            font-size: 14px;
        }

        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .history-item {
            background: rgba(30, 41, 59, 0.7);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 12px;
            border-left: 4px solid #667eea;
        }

        .history-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .history-time {
            font-size: 12px;
            color: #94a3b8;
        }

        .loading {
            text-align: center;
            padding: 30px;
        }

        .spinner {
            border: 3px solid rgba(99, 102, 241, 0.2);
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .vibrate-on-scan {
            animation: vibrate 0.3s;
        }

        @keyframes vibrate {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }

        .torch-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(0, 0, 0, 0.6);
            border: none;
            border-radius: 50%;
            width: 45px;
            height: 45px;
            font-size: 20px;
            cursor: pointer;
            z-index: 10;
            display: none;
        }

        .offline-indicator {
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: #ef4444;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            display: none;
            z-index: 1000;
        }

        @media (max-width: 480px) {
            .header h1 {
                font-size: 1.5rem;
            }
            
            .stats-bar {
                grid-template-columns: repeat(3, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="offline-indicator" id="offlineIndicator">
        📡 Offline - Some features unavailable
    </div>

    <div class="container">
        <div class="header">
            <h1>🩸 Blood Scanner</h1>
            <p style="color: #94a3b8; font-size: 0.95rem;">Mobile QR Code Scanner</p>
        </div>

        <div class="stats-bar">
            <div class="stat-card">
                <span class="stat-value" id="totalScans">0</span>
                <span class="stat-label">Scans Today</span>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="availableUnits">0</span>
                <span class="stat-label">Available</span>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="expiringUnits">0</span>
                <span class="stat-label">Expiring</span>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('scanner')">📱 Scanner</button>
            <button class="tab" onclick="switchTab('history')">📋 History</button>
            <button class="tab" onclick="switchTab('search')">🔍 Search</button>
        </div>

        <div id="scanner-tab" class="tab-content active">
            <div class="scanner-wrapper">
                <div style="position: relative;">
                    <button class="torch-btn" id="torchBtn" onclick="toggleTorch()">💡</button>
                    <div id="reader"></div>
                </div>
                <div class="controls">
                    <button id="startBtn" class="btn btn-primary" onclick="startScanner()">🎥 Start Camera</button>
                    <button id="stopBtn" class="btn btn-danger" style="display: none;" onclick="stopScanner()">⏹️ Stop Camera</button>
                </div>
                <div id="scanMessage" class="alert" style="display: none;"></div>
            </div>

            <div class="result-card" id="resultCard">
                <h2 style="text-align: center; margin-bottom: 20px;">📋 Blood Unit Details</h2>
                <div class="blood-info" id="bloodInfo"></div>
                <div class="controls">
                    <button class="btn btn-success" onclick="markAsUsed()">✓ Mark as Used</button>
                    <button class="btn btn-warning" onclick="viewFullDetails()">📄 Full Details</button>
                    <button class="btn btn-primary" onclick="scanAnother()">🔄 Scan Another</button>
                </div>
            </div>
        </div>

        <div id="history-tab" class="tab-content">
            <div class="scanner-wrapper">
                <h2 style="margin-bottom: 15px;">Recent Scans</h2>
                <div id="historyList" class="loading">
                    <div class="spinner"></div>
                    <p style="color: #94a3b8;">Loading...</p>
                </div>
            </div>
        </div>

        <div id="search-tab" class="tab-content">
            <div class="scanner-wrapper">
                <h2 style="margin-bottom: 15px;">Search Blood Unit</h2>
                <input type="text" id="searchInput" placeholder="Enter Blood ID..." 
                    style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.3); background: rgba(30, 41, 59, 0.7); color: white; font-size: 16px; margin-bottom: 15px;">
                <button class="btn btn-primary" onclick="searchBlood()">🔍 Search</button>
                <div id="searchResults"></div>
            </div>
        </div>
    </div>

    <script>
        let scanner = null;
        let isScanning = false;
        let currentBloodId = null;
        let torchEnabled = false;

        // Check online/offline status
        window.addEventListener('online', () => {
            document.getElementById('offlineIndicator').style.display = 'none';
        });

        window.addEventListener('offline', () => {
            document.getElementById('offlineIndicator').style.display = 'block';
        });

        // Load stats
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('totalScans').textContent = data.total_scans || 0;
                document.getElementById('availableUnits').textContent = data.available_units || 0;
                document.getElementById('expiringUnits').textContent = data.expiring_units || 0;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }

        function showMessage(message, type = 'success') {
            const msgEl = document.getElementById('scanMessage');
            msgEl.textContent = message;
            msgEl.className = `alert alert-${type}`;
            msgEl.style.display = 'block';
            setTimeout(() => msgEl.style.display = 'none', 4000);
        }

        function vibrateDevice() {
            if ('vibrate' in navigator) {
                navigator.vibrate([100, 50, 100]);
            }
        }

        function playBeep() {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // First note - higher pitch
            const osc1 = audioContext.createOscillator();
            const gain1 = audioContext.createGain();
            osc1.connect(gain1);
            gain1.connect(audioContext.destination);
            osc1.frequency.value = 800; // Higher pitch
            osc1.type = 'sine';
            gain1.gain.setValueAtTime(0.3, audioContext.currentTime);
            gain1.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
            osc1.start(audioContext.currentTime);
            osc1.stop(audioContext.currentTime + 0.15);
            
            // Second note - even higher (cute chirp)
            setTimeout(() => {
                const osc2 = audioContext.createOscillator();
                const gain2 = audioContext.createGain();
                osc2.connect(gain2);
                gain2.connect(audioContext.destination);
                osc2.frequency.value = 1000; // Even higher
                osc2.type = 'sine';
                gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
                gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
                osc2.start(audioContext.currentTime);
                osc2.stop(audioContext.currentTime + 0.15);
            }, 100);
            
            // Third note - highest (success!)
            setTimeout(() => {
                const osc3 = audioContext.createOscillator();
                const gain3 = audioContext.createGain();
                osc3.connect(gain3);
                gain3.connect(audioContext.destination);
                osc3.frequency.value = 1200; // Highest!
                osc3.type = 'sine';
                gain3.gain.setValueAtTime(0.25, audioContext.currentTime);
                gain3.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
                osc3.start(audioContext.currentTime);
                osc3.stop(audioContext.currentTime + 0.2);
            }, 200);
        }

        function formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        }

        function calculateDaysUntilExpiry(expiryDate) {
            const now = new Date();
            const expiry = new Date(expiryDate);
            const days = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
            return days;
        }

        function displayBloodInfo(blood) {
            currentBloodId = blood.blood_id;
            document.getElementById('resultCard').classList.add('show');
            
            const daysUntilExpiry = calculateDaysUntilExpiry(blood.expiry_date);
            const statusClass = `status-${blood.status}`;
            
            let alertHTML = '';
            if (daysUntilExpiry < 0) {
                alertHTML = '<div class="alert alert-danger">⚠️ EXPIRED - This blood cannot be used</div>';
            } else if (daysUntilExpiry < 7) {
                alertHTML = `<div class="alert alert-warning">⚠️ Expires in ${daysUntilExpiry} days - Use soon!</div>`;
            } else {
                alertHTML = '<div class="alert alert-success">✓ Good condition</div>';
            }
            
            document.getElementById('bloodInfo').innerHTML = `
                ${alertHTML}
                <div style="text-align: center; margin: 20px 0;">
                    <span class="blood-type-big">${blood.blood_type}</span>
                </div>
                <div class="info-item">
                    <div class="info-label">Blood ID</div>
                    <div class="info-value">${blood.blood_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="info-value">
                        <span class="status-badge ${statusClass}">${blood.status}</span>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">Units Available</div>
                    <div class="info-value">${blood.units} unit(s)</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Hospital</div>
                    <div class="info-value">${blood.hospital || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Donor ID</div>
                    <div class="info-value">${blood.donor_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Collected</div>
                    <div class="info-value">${formatDate(blood.collected_date)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Expires</div>
                    <div class="info-value">${formatDate(blood.expiry_date)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Days Remaining</div>
                    <div class="info-value">${daysUntilExpiry} days</div>
                </div>
            `;
        }

        async function onScanSuccess(decodedText) {
            if (isScanning) return;
            isScanning = true;
            
            stopScanner();
            vibrateDevice();
            playBeep();
            
            showMessage('QR Code detected! Verifying...', 'success');
            
            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ qr_data: decodedText })
                });
                
                const data = await response.json();
                if (data.success) {
                    displayBloodInfo(data.blood);
                    loadStats();
                } else {
                    showMessage(data.error || 'Blood unit not found', 'danger');
                    isScanning = false;
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'danger');
                isScanning = false;
            }
        }

        function startScanner() {
            scanner = new Html5Qrcode("reader");
            
            scanner.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: { width: 250, height: 250 } },
                onScanSuccess,
                () => {} // Ignore errors
            ).then(() => {
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'block';
                document.getElementById('resultCard').classList.remove('show');
                isScanning = false;
            }).catch(err => {
                showMessage('Camera access denied', 'danger');
            });
        }

        function stopScanner() {
            if (scanner) {
                scanner.stop().then(() => {
                    document.getElementById('startBtn').style.display = 'block';
                    document.getElementById('stopBtn').style.display = 'none';
                });
            }
        }

        function scanAnother() {
            document.getElementById('resultCard').classList.remove('show');
            isScanning = false;
            currentBloodId = null;
            startScanner();
        }

        async function markAsUsed() {
            if (!currentBloodId) return;
            
            if (!confirm('Mark this blood unit as USED?')) return;
            
            try {
                const response = await fetch(`/api/blood/mark-used/${currentBloodId}`, {
                    method: 'POST'
                });
                const data = await response.json();
                if (data.success) {
                    showMessage('✓ Marked as USED successfully!', 'success');
                    displayBloodInfo(data.blood);
                    loadStats();
                }
            } catch (error) {
                showMessage('Failed to update status', 'danger');
            }
        }

        function viewFullDetails() {
            if (!currentBloodId) return;
            window.open(`/blood-details/${currentBloodId}`, '_blank');
        }

        async function loadHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '<div class="loading"><div class="spinner"></div><p style="color:#94a3b8;">Loading...</p></div>';
            
            try {
                const response = await fetch('/api/scan-history');
                const data = await response.json();
                
                if (data.length === 0) {
                    list.innerHTML = '<p style="text-align:center;color:#94a3b8;padding:30px;">No scan history yet</p>';
                    return;
                }
                
                list.innerHTML = '';
                data.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.onclick = () => {
                        switchTab('scanner');
                        displayBloodInfo(item.blood_data);
                    };
                    div.innerHTML = `
                        <div class="history-header">
                            <strong style="color:#e2e8f0;">${item.blood_data.blood_id}</strong>
                            <span class="history-time">${new Date(item.scanned_at).toLocaleString()}</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;font-size:14px;color:#94a3b8;">
                            <span>${item.blood_data.blood_type} | ${item.blood_data.units} units</span>
                            <span class="status-badge status-${item.blood_data.status}">${item.blood_data.status}</span>
                        </div>
                    `;
                    list.appendChild(div);
                });
            } catch (error) {
                list.innerHTML = '<p style="text-align:center;color:#fca5a5;padding:30px;">Error loading history</p>';
            }
        }

        async function searchBlood() {
            const searchInput = document.getElementById('searchInput').value.trim();
            const resultsDiv = document.getElementById('searchResults');
            
            if (!searchInput) {
                showMessage('Please enter a Blood ID', 'warning');
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
            
            try {
                const response = await fetch(`/api/blood/search?id=${searchInput}`);
                const data = await response.json();
                
                if (data.success) {
                    switchTab('scanner');
                    displayBloodInfo(data.blood);
                } else {
                    resultsDiv.innerHTML = '<div class="alert alert-danger">Blood unit not found</div>';
                }
            } catch (error) {
                resultsDiv.innerHTML = '<div class="alert alert-danger">Search failed</div>';
            }
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            if (tabName === 'history') loadHistory();
            if (tabName === 'scanner' && scanner) stopScanner();
        }

        function toggleTorch() {
            // Torch functionality requires advanced camera API
            torchEnabled = !torchEnabled;
            document.getElementById('torchBtn').textContent = torchEnabled ? '🔦' : '💡';
        }

        // Enter key search
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') searchBlood();
            });
        });

        // Load initial stats
        loadStats();
        setInterval(loadStats, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scan', methods=['POST'])
def scan_qr():
    try:
        data = request.get_json()
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return jsonify({"success": False, "error": "No QR data provided"}), 400
        
        # Parse QR data
        try:
            blood_info = json.loads(qr_data)
            blood_id = blood_info.get('blood_id')
        except:
            blood_id = qr_data
        
        # Find blood unit in database
        blood_unit = blood_units.find_one({'blood_id': blood_id})
        
        if not blood_unit:
            return jsonify({"success": False, "error": "Blood unit not found in database"}), 404
        
        # Log the scan
        scan_logs.insert_one({
            'blood_id': blood_id,
            'scanned_at': datetime.now(),
            'blood_data': {
                'blood_id': blood_unit['blood_id'],
                'blood_type': blood_unit['blood_type'],
                'donor_id': blood_unit['donor_id'],
                'units': blood_unit['units'],
                'status': blood_unit.get('status', 'available'),
                'hospital': blood_unit.get('hospital', 'N/A'),
                'collected_date': blood_unit['collected_date'],
                'expiry_date': blood_unit['expiry_date']
            }
        })
        
        # Update activity log
        activities.insert_one({
            'type': 'mobile_scan',
            'blood_id': blood_id,
            'timestamp': datetime.now(),
            'message': f"Blood unit {blood_id} scanned via mobile"
        })
        
        # Convert ObjectId and datetime to strings
        blood_unit['_id'] = str(blood_unit['_id'])
        if isinstance(blood_unit.get('collected_date'), datetime):
            blood_unit['collected_date'] = blood_unit['collected_date'].isoformat()
        if isinstance(blood_unit.get('expiry_date'), datetime):
            blood_unit['expiry_date'] = blood_unit['expiry_date'].isoformat()
        
        return jsonify({
            "success": True,
            "blood": blood_unit
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/blood/mark-used/<blood_id>', methods=['POST'])
def mark_as_used(blood_id):
    try:
        blood_unit = blood_units.find_one({'blood_id': blood_id})
        
        if not blood_unit:
            return jsonify({"success": False, "error": "Blood unit not found"}), 404
        
        # Update status
        blood_units.update_one(
            {'blood_id': blood_id},
            {'$set': {
                'status': 'used',
                'used_at': datetime.now(),
                'location': 'used'
            }}
        )
        
        # Update hospital inventory
        from pymongo import MongoClient
        blood_inventory = mongo.db.blood_inventory
        blood_inventory.update_one(
            {'hospital_id': blood_unit.get('hospital_id')},
            {'$inc': {blood_unit['blood_type']: -blood_unit['units']}}
        )
        
        # Log activity
        activities.insert_one({
            'type': 'blood_used_mobile',
            'blood_id': blood_id,
            'timestamp': datetime.now(),
            'message': f"Blood unit {blood_id} marked as USED via mobile scanner"
        })
        
        # Get updated blood unit
        updated_unit = blood_units.find_one({'blood_id': blood_id})
        updated_unit['_id'] = str(updated_unit['_id'])
        if isinstance(updated_unit.get('collected_date'), datetime):
            updated_unit['collected_date'] = updated_unit['collected_date'].isoformat()
        if isinstance(updated_unit.get('expiry_date'), datetime):
            updated_unit['expiry_date'] = updated_unit['expiry_date'].isoformat()
        
        return jsonify({
            "success": True,
            "blood": updated_unit
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        # Today's scans
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        total_scans = scan_logs.count_documents({'scanned_at': {'$gte': today_start}})
        
        # Available units
        available_units = blood_units.count_documents({'status': 'available'})
        
        # Expiring soon (within 7 days)
        expiry_threshold = datetime.now() + timedelta(days=7)
        expiring_units = blood_units.count_documents({
            'status': 'available',
            'expiry_date': {'$lte': expiry_threshold, '$gte': datetime.now()}
        })
        
        return jsonify({
            "total_scans": total_scans,
            "available_units": available_units,
            "expiring_units": expiring_units
        })
    except Exception as e:
        return jsonify({
            "total_scans": 0,
            "available_units": 0,
            "expiring_units": 0
        })

@app.route('/api/scan-history')
def scan_history():
    try:
        # Get last 50 scans
        scans = list(scan_logs.find().sort('scanned_at', -1).limit(50))
        
        # Convert ObjectId to string
        for scan in scans:
            scan['_id'] = str(scan['_id'])
            if isinstance(scan.get('scanned_at'), datetime):
                scan['scanned_at'] = scan['scanned_at'].isoformat()
            if 'blood_data' in scan:
                if isinstance(scan['blood_data'].get('collected_date'), datetime):
                    scan['blood_data']['collected_date'] = scan['blood_data']['collected_date'].isoformat()
                if isinstance(scan['blood_data'].get('expiry_date'), datetime):
                    scan['blood_data']['expiry_date'] = scan['blood_data']['expiry_date'].isoformat()
        
        return jsonify(scans)
    except Exception as e:
        return jsonify([])

@app.route('/api/blood/search')
def search_blood():
    try:
        blood_id = request.args.get('id', '').strip()
        
        if not blood_id:
            return jsonify({"success": False, "error": "No blood ID provided"}), 400
        
        # Case-insensitive search
        blood_unit = blood_units.find_one({'blood_id': {'$regex': f'^{blood_id}$', '$options': 'i'}})
        
        if not blood_unit:
            return jsonify({"success": False, "error": "Blood unit not found"}), 404
        
        # Convert datetime to string
        blood_unit['_id'] = str(blood_unit['_id'])
        if isinstance(blood_unit.get('collected_date'), datetime):
            blood_unit['collected_date'] = blood_unit['collected_date'].isoformat()
        if isinstance(blood_unit.get('expiry_date'), datetime):
            blood_unit['expiry_date'] = blood_unit['expiry_date'].isoformat()
        
        return jsonify({
            "success": True,
            "blood": blood_unit
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/blood-details/<blood_id>')
def blood_details(blood_id):
    blood_unit = blood_units.find_one({'blood_id': blood_id})
    
    if not blood_unit:
        return "Blood unit not found", 404
    
    # Get hospital and donor info
    hospital = hospitals.find_one({'_id': blood_unit.get('hospital_id')})
    donor = donors.find_one({'donor_id': blood_unit.get('donor_id')})
    
    details_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blood Details - {blood_id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #0a0e27;
                color: #e2e8f0;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(15, 23, 42, 0.9);
                padding: 20px;
                border-radius: 15px;
            }}
            h1 {{
                text-align: center;
                color: #667eea;
            }}
            .info-section {{
                background: rgba(30, 41, 59, 0.7);
                padding: 15px;
                margin: 15px 0;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }}
            .label {{
                color: #94a3b8;
                font-size: 12px;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}
            .value {{
                font-size: 16px;
                font-weight: bold;
                color: #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🩸 Blood Unit Details</h1>
            
            <div class="info-section">
                <div class="label">Blood ID</div>
                <div class="value">{blood_unit['blood_id']}</div>
            </div>
            
            <div class="info-section">
                <div class="label">Blood Type</div>
                <div class="value">{blood_unit['blood_type']}</div>
            </div>
            
            <div class="info-section">
                <div class="label">Units</div>
                <div class="value">{blood_unit['units']} unit(s)</div>
            </div>
            
            <div class="info-section">
                <div class="label">Status</div>
                <div class="value">{blood_unit.get('status', 'available').upper()}</div>
            </div>
            
            <div class="info-section">
                <div class="label">Hospital</div>
                <div class="value">{hospital.get('name', 'N/A') if hospital else 'N/A'}</div>
            </div>
            
            <div class="info-section">
                <div class="label">Donor ID</div>
                <div class="value">{blood_unit['donor_id']}</div>
            </div>
            
            <div class="info-section">
                <div class="label">Collection Date</div>
                <div class="value">{blood_unit['collected_date']}</div>
            </div>
            
            <div class="info-section">
                <div class="label">Expiry Date</div>
                <div class="value">{blood_unit['expiry_date']}</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return details_html

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)
