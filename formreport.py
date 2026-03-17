from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'reports.json'

def load_reports():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_reports(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_case_id():
    reports = load_reports()
    today = datetime.now().strftime('%Y%m%d')
    count = sum(1 for r in reports if r['case_id'].startswith(f"R{today}"))
    return f"R{today}-{count+1:04d}"

@app.route('/report', methods=['POST'])
def add_report():
    data = request.get_json()
    if not data:
        return jsonify({"error": "沒有收到任何資料"}), 400
    reports = load_reports()
    case_id = generate_case_id()
    report = {
        "case_id": case_id,
        "device": data.get("device"),
        "message": data.get("message"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    reports.append(report)
    save_reports(reports)
    return jsonify({"status": "success", "report": report}), 200

@app.route('/reports', methods=['GET'])
def get_reports():
    return jsonify(load_reports())

@app.route('/report/<case_id>', methods=['GET'])
def get_report_by_id(case_id):
    reports = load_reports()
    for r in reports:
        if r['case_id'] == case_id:
            return jsonify(r)
    return jsonify({"error": "案件編號不存在"}), 404

@app.route('/report/<case_id>', methods=['DELETE'])
def delete_report(case_id):
    reports = load_reports()
    filtered = [r for r in reports if r['case_id'] != case_id]
    if len(filtered) == len(reports):
        return jsonify({"error": "案件編號不存在"}), 404
    save_reports(filtered)
    return jsonify({"status": "success", "message": f"已刪除案件 {case_id}"}), 200

@app.route('/report/<case_id>', methods=['PUT'])
def edit_report(case_id):
    data = request.get_json()
    reports = load_reports()
    for r in reports:
        if r['case_id'] == case_id:
            if "device" in data:
                r["device"] = data["device"]
            if "message" in data:
                r["message"] = data["message"]
            save_reports(reports)
            return jsonify({"status": "success", "report": r}), 200
    return jsonify({"error": "案件編號不存在"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5002)
