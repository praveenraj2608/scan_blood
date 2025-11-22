from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# Sample blood data
BLOOD_DATA = {
    "BLD35C17A4D0390": {
        "blood_id": "BLD35C17A4D0390",
        "blood_type": "B+",
        "donor_id": "DNRD573CF36",
        "units": 2,
        "collected_date": "2025-11-21 08:00:49",
        "expiry_date": "2025-12-22 01:23:11",
        "hospital_id": "6920c32657eea97e83cb4802",
        "hospital": "Manipal Hospital",
        "status": "available",
        "location": "storage"
    },
    "BLDBACCAE9141D2": {
        "blood_id": "BLDBACCAE9141D2",
        "blood_type": "A+",
        "donor_id": "DNRD123456",
        "units": 2,
        "collected_date": "2025-11-20 10:30:00",
        "expiry_date": "2025-12-22 10:30:00",
        "hospital_id": "6920c32657eea97e83cb4802",
        "hospital": "Apollo Hospital",
        "status": "available",
        "location": "storage"
    }
}

# Mobile-Optimized Dark Theme HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0a0e27">
    <title>Blood Bank QR Scanner</title>
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

        .header p {
            color: #94a3b8;
            font-size: 0.95rem;
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
        }

        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            width: 100%;
            max-width: 280px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:active {
            transform: scale(0.98);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
        }

        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }

        .btn-danger:active {
            transform: scale(0.98);
        }

        .btn-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }

        .btn-small {
            padding: 10px 20px;
            font-size: 14px;
            width: auto;
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

        .result-card h2 {
            color: #e2e8f0;
            margin-bottom: 20px;
            font-size: 1.5rem;
            text-align: center;
        }

        .blood-info {
            display: grid;
            gap: 15px;
            margin-top: 15px;
        }

        .info-item {
            background: rgba(30, 41, 59, 0.7);
            padding: 15px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }

        .info-label {
            font-size: 11px;
            text-transform: uppercase;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 6px;
            letter-spacing: 0.5px;
        }

        .info-value {
            font-size: 18px;
            font-weight: 700;
            color: #e2e8f0;
            word-break: break-word;
        }

        .blood-type {
            display: inline-block;
            padding: 8px 16px;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            border-radius: 8px;
            font-size: 22px;
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
            box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
        }

        .status-reserved {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3);
        }

        .status-used {
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            color: white;
            box-shadow: 0 4px 10px rgba(107, 114, 128, 0.3);
        }

        .message {
            padding: 12px;
            border-radius: 8px;
            margin-top: 15px;
            display: none;
            text-align: center;
            font-size: 14px;
        }

        .error-message {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }

        .success-message {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #6ee7b7;
        }

        .message.show {
            display: block;
        }

        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 3px solid rgba(99, 102, 241, 0.2);
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .action-buttons {
            margin-top: 20px;
            display: grid;
            gap: 10px;
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

        .inventory-item {
            background: rgba(30, 41, 59, 0.7);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 12px;
            border-left: 4px solid #667eea;
        }

        .inventory-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }

        .inventory-id {
            font-weight: 700;
            color: #e2e8f0;
            font-size: 16px;
        }

        .inventory-details {
            display: grid;
            gap: 8px;
            font-size: 13px;
            color: #94a3b8;
        }

        .camera-guide {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 13px;
            text-align: center;
        }

        .camera-guide strong {
            color: #818cf8;
        }

        @media (max-width: 480px) {
            .header h1 {
                font-size: 1.5rem;
            }
            
            .btn {
                font-size: 15px;
                padding: 12px 24px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩸 Blood Bank Scanner</h1>
            <p>Mobile QR Code Scanner</p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('scanner')">📱 Scanner</button>
            <button class="tab" onclick="switchTab('inventory')">📋 Inventory</button>
        </div>

        <div id="scanner-tab" class="tab-content active">
            <div class="scanner-wrapper">
                <div class="camera-guide">
                    <strong>📸 Tip:</strong> Point your phone camera at the QR code and hold steady
                </div>
                <div id="reader"></div>
                <div class="controls">
                    <button id="startBtn" class="btn btn-primary">🎥 Start Camera</button>
                    <button id="stopBtn" class="btn btn-danger" style="display: none;">⏹️ Stop Camera</button>
                </div>
                <div class="message error-message" id="errorMessage"></div>
                <div class="message success-message" id="successMessage"></div>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="color: #94a3b8;">Loading blood info...</p>
            </div>

            <div class="result-card" id="resultCard">
                <h2>📋 Blood Unit Details</h2>
                <div class="blood-info" id="bloodInfo"></div>
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="scanAnother()">🔄 Scan Another</button>
                    <button class="btn btn-success btn-small" onclick="updateStatus('reserved')" id="reserveBtn">Mark Reserved</button>
                    <button class="btn btn-danger btn-small" onclick="updateStatus('used')" id="useBtn">Mark Used</button>
                </div>
            </div>
        </div>

        <div id="inventory-tab" class="tab-content">
            <div class="scanner-wrapper">
                <h2 style="margin-bottom: 15px; font-size: 1.3rem;">Blood Inventory</h2>
                <div class="loading" id="inventoryLoading">
                    <div class="spinner"></div>
                    <p style="color: #94a3b8;">Loading...</p>
                </div>
                <div id="inventoryList"></div>
            </div>
        </div>
    </div>

    <script>
        let html5QrcodeScanner;
        let isScanning = false;
        let currentBloodId = null;

        function showError(message) {
            const errorMsg = document.getElementById('errorMessage');
            const successMsg = document.getElementById('successMessage');
            errorMsg.textContent = message;
            errorMsg.classList.add('show');
            successMsg.classList.remove('show');
            setTimeout(() => errorMsg.classList.remove('show'), 5000);
        }

        function showSuccess(message) {
            const successMsg = document.getElementById('successMessage');
            const errorMsg = document.getElementById('errorMessage');
            successMsg.textContent = message;
            successMsg.classList.add('show');
            errorMsg.classList.remove('show');
            setTimeout(() => successMsg.classList.remove('show'), 3000);
        }

        function formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        }

        function displayBloodInfo(blood) {
            document.getElementById('loading').classList.remove('show');
            document.getElementById('resultCard').classList.add('show');
            currentBloodId = blood.blood_id;

            const statusClass = `status-${blood.status}`;
            document.getElementById('bloodInfo').innerHTML = `
                <div class="info-item">
                    <div class="info-label">Blood ID</div>
                    <div class="info-value">${blood.blood_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Blood Type</div>
                    <div class="info-value">
                        <span class="blood-type">${blood.blood_type}</span>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">Units</div>
                    <div class="info-value">${blood.units} unit(s)</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="info-value">
                        <span class="status-badge ${statusClass}">${blood.status}</span>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">Donor ID</div>
                    <div class="info-value">${blood.donor_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Hospital</div>
                    <div class="info-value">${blood.hospital}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Collection Date</div>
                    <div class="info-value">${formatDate(blood.collected_date)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Expiry Date</div>
                    <div class="info-value">${formatDate(blood.expiry_date)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Location</div>
                    <div class="info-value">${blood.location}</div>
                </div>
            `;

            document.getElementById('reserveBtn').style.display = 
                blood.status === 'available' ? 'inline-block' : 'none';
            document.getElementById('useBtn').style.display = 
                blood.status !== 'used' ? 'inline-block' : 'none';
        }

        async function onScanSuccess(decodedText) {
            if (isScanning) return;
            isScanning = true;

            html5QrcodeScanner.stop().then(() => {
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
            });

            document.getElementById('loading').classList.add('show');

            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ qr_data: decodedText })
                });

                const data = await response.json();
                if (data.success) {
                    displayBloodInfo(data.blood);
                } else {
                    document.getElementById('loading').classList.remove('show');
                    showError(data.error || 'Blood record not found');
                    isScanning = false;
                }
            } catch (error) {
                document.getElementById('loading').classList.remove('show');
                showError('Failed to fetch: ' + error.message);
                isScanning = false;
            }
        }

        document.getElementById('startBtn').addEventListener('click', () => {
            html5QrcodeScanner = new Html5Qrcode("reader");
            
            html5QrcodeScanner.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: { width: 250, height: 250 } },
                onScanSuccess
            ).then(() => {
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
                document.getElementById('resultCard').classList.remove('show');
                isScanning = false;
            }).catch(err => {
                showError('Camera access denied or not available');
            });
        });

        document.getElementById('stopBtn').addEventListener('click', () => {
            html5QrcodeScanner.stop().then(() => {
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
                isScanning = false;
            });
        });

        function scanAnother() {
            document.getElementById('resultCard').classList.remove('show');
            isScanning = false;
            currentBloodId = null;
        }

        async function updateStatus(newStatus) {
            if (!currentBloodId) return;
            try {
                const response = await fetch(`/api/blood/update/${currentBloodId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();
                if (data.success) {
                    showSuccess(`Marked as ${newStatus}!`);
                    const bloodResponse = await fetch(`/api/blood/${currentBloodId}`);
                    const bloodData = await bloodResponse.json();
                    displayBloodInfo(bloodData);
                }
            } catch (error) {
                showError('Update failed');
            }
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');
            if (tabName === 'inventory') loadInventory();
        }

        async function loadInventory() {
            const loading = document.getElementById('inventoryLoading');
            const list = document.getElementById('inventoryList');
            loading.style.display = 'block';
            list.innerHTML = '';

            try {
                const response = await fetch('/api/blood/list');
                const data = await response.json();
                loading.style.display = 'none';

                if (data.length === 0) {
                    list.innerHTML = '<p style="text-align:center;color:#94a3b8;">No records</p>';
                    return;
                }

                data.forEach(blood => {
                    const item = document.createElement('div');
                    item.className = 'inventory-item';
                    item.onclick = () => {
                        switchTab('scanner');
                        displayBloodInfo(blood);
                    };
                    item.innerHTML = `
                        <div class="inventory-header">
                            <span class="inventory-id">${blood.blood_id}</span>
                            <span class="status-badge status-${blood.status}">${blood.status}</span>
                        </div>
                        <div class="inventory-details">
                            <div><strong>Type:</strong> ${blood.blood_type} | <strong>Units:</strong> ${blood.units}</div>
                            <div><strong>Hospital:</strong> ${blood.hospital}</div>
                            <div><strong>Expires:</strong> ${formatDate(blood.expiry_date)}</div>
                        </div>
                    `;
                    list.appendChild(item);
                });
            } catch (error) {
                loading.style.display = 'none';
                list.innerHTML = '<p style="text-align:center;color:#fca5a5;">Error loading</p>';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/blood/<blood_id>')
def api_blood_details(blood_id):
    if blood_id in BLOOD_DATA:
        return jsonify(BLOOD_DATA[blood_id])
    return jsonify({"error": "Blood record not found"}), 404

@app.route('/api/scan', methods=['POST'])
def scan_qr():
    try:
        data = request.get_json()
        qr_data = data.get('qr_data')
        if not qr_data:
            return jsonify({"error": "No QR data provided"}), 400
        try:
            blood_info = json.loads(qr_data)
            blood_id = blood_info.get('blood_id', qr_data)
        except:
            blood_id = qr_data
        if blood_id in BLOOD_DATA:
            return jsonify({"success": True, "blood": BLOOD_DATA[blood_id]})
        return jsonify({"success": False, "error": "Blood record not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blood/list')
def list_blood():
    return jsonify(list(BLOOD_DATA.values()))

@app.route('/api/blood/update/<blood_id>', methods=['PUT'])
def update_blood_status(blood_id):
    try:
        data = request.get_json()
        status = data.get('status')
        if blood_id in BLOOD_DATA:
            BLOOD_DATA[blood_id]['status'] = status
            return jsonify({"success": True, "message": "Status updated"})
        return jsonify({"success": False, "message": "Blood ID not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)
