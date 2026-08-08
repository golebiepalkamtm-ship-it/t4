"""
================================================================================
  EDC15VM+ PRO TUNER SUITE v3.0 — Ultra-Modern Web Application
  Software: Bosch EDC15VM+ (VAG 1.9 / 2.5 TDI VP37)
================================================================================
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse
import webbrowser
import threading
import traceback
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edc15_analyzer import (
    ECUBinaryReader, VCDSLogParser, EDC15Analyzer, 
    MAP_DEFINITIONS, MAP_AXES
)

# Stan aplikacji
APP_STATE = {
    "bin_path": r"d:\t4\cks ok" if os.path.exists(r"d:\t4\cks ok") else "",
    "csv_paths": [],
    "ecu": None,
    "vcds": None,
    "analyzer": None,
    "last_autotune_result": None
}

def init_app_state():
    if APP_STATE["bin_path"] and os.path.exists(APP_STATE["bin_path"]):
        try:
            APP_STATE["ecu"] = ECUBinaryReader(APP_STATE["bin_path"])
            APP_STATE["analyzer"] = EDC15Analyzer(APP_STATE["ecu"], APP_STATE["vcds"])
        except Exception as e:
            print(f"Błąd ładowania pliku BIN: {e}")

class EDC15APIHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_html(self, html_content: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        if path == "/" or path == "/index.html":
            return self._send_html(HTML_INTERFACE)

        elif path == "/api/status":
            ecu = APP_STATE["ecu"]
            vcds = APP_STATE["vcds"]
            info = {
                "bin_loaded": ecu is not None,
                "bin_path": APP_STATE["bin_path"],
                "bin_name": os.path.basename(APP_STATE["bin_path"]) if APP_STATE["bin_path"] else "Brak",
                "header_info": ecu.header_info if ecu else {},
                "vcds_loaded": vcds is not None and len(vcds.data_points) > 0,
                "vcds_count": len(vcds.data_points) if vcds else 0,
                "csv_paths": [os.path.basename(p) for p in APP_STATE["csv_paths"]]
            }
            return self._send_json(info)

        elif path == "/api/maps":
            ecu = APP_STATE["ecu"]
            if not ecu:
                return self._send_json({"error": "Plik BIN nie został wczytany"}, status=400)
            
            maps_list = []
            for key, md in MAP_DEFINITIONS.items():
                summary = ecu.get_map_summary(md, codeblock=5)
                summary["key"] = key
                summary["x_label"] = md.x_label
                summary["y_label"] = md.y_label
                maps_list.append(summary)
            return self._send_json(maps_list)

        elif path.startswith("/api/map/"):
            map_key = path.replace("/api/map/", "").strip()
            ecu = APP_STATE["ecu"]
            analyzer = APP_STATE["analyzer"]

            if not ecu or map_key not in MAP_DEFINITIONS:
                return self._send_json({"error": "Nieznana mapa lub brak BIN"}, status=400)

            md = MAP_DEFINITIONS[map_key]
            ecu_matrix = ecu.read_map(md, codeblock=5)
            axes = MAP_AXES.get(map_key, {"x": list(range(md.cols)), "y": list(range(md.rows)), "x_unit": "X", "y_unit": "Y"})

            log_matrix, diff_matrix = ([], [])
            if analyzer and APP_STATE["vcds"]:
                log_matrix, diff_matrix = analyzer.get_map_log_matrix(map_key, codeblock=5)

            data = {
                "key": map_key,
                "name": md.name,
                "dimsport": md.dimsport_code,
                "unit": md.unit,
                "factor": md.factor,
                "rows": md.rows,
                "cols": md.cols,
                "x_axis": axes["x"],
                "y_axis": axes["y"],
                "x_unit": axes.get("x_unit", ""),
                "y_unit": axes.get("y_unit", ""),
                "ecu_matrix": ecu_matrix,
                "log_matrix": log_matrix,
                "diff_matrix": diff_matrix
            }
            return self._send_json(data)

        elif path == "/api/audit":
            analyzer = APP_STATE["analyzer"]
            if not analyzer:
                return self._send_json({"findings": []})
            
            analyzer.audit_maps(codeblock=5)
            if APP_STATE["vcds"] and APP_STATE["vcds"].data_points:
                analyzer.execute_all_analysis()

            findings_data = []
            for f in analyzer.findings:
                findings_data.append({
                    "severity": f.severity,
                    "category": f.category,
                    "rpm_range": f.rpm_range,
                    "description": f.description,
                    "recommendation": f.recommendation,
                    "map_to_adjust": f.map_to_adjust
                })
            return self._send_json({"findings": findings_data})

        elif path == "/api/download_bin":
            ecu = APP_STATE["ecu"]
            if not ecu:
                return self._send_json({"error": "Brak wsadu BIN"}, status=400)

            output_file = os.path.join(r"d:\t4", "MODIFIED_TUNED_EDC15.bin")
            ecu.save_bin(output_file)
            return self._send_json({"success": True, "file_path": output_file, "message": f"Zapisano wsad do: {output_file}"})

        else:
            self.send_error(404, "Path Not Found")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length)
        
        try:
            body = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}
        except Exception:
            body = {}

        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        if path == "/api/load_bin":
            bin_path = body.get("bin_path", "").strip()
            if not bin_path or not os.path.exists(bin_path):
                return self._send_json({"error": f"Plik nie istnieje: {bin_path}"}, status=400)
            
            try:
                APP_STATE["bin_path"] = bin_path
                APP_STATE["ecu"] = ECUBinaryReader(bin_path)
                APP_STATE["analyzer"] = EDC15Analyzer(APP_STATE["ecu"], APP_STATE["vcds"])
                return self._send_json({"success": True, "header": APP_STATE["ecu"].header_info})
            except Exception as e:
                return self._send_json({"error": str(e)}, status=500)

        elif path == "/api/load_vcds":
            csv_paths = body.get("csv_paths", [])
            if isinstance(csv_paths, str):
                csv_paths = [csv_paths]
            
            valid_paths = [p for p in csv_paths if os.path.exists(p)]
            if not valid_paths:
                return self._send_json({"error": "Brak prawidłowych ścieżek do plików CSV logów"}, status=400)

            try:
                APP_STATE["csv_paths"] = valid_paths
                APP_STATE["vcds"] = VCDSLogParser(valid_paths)
                if APP_STATE["ecu"]:
                    APP_STATE["analyzer"] = EDC15Analyzer(APP_STATE["ecu"], APP_STATE["vcds"])
                return self._send_json({"success": True, "count": len(APP_STATE["vcds"].data_points)})
            except Exception as e:
                return self._send_json({"error": str(e)}, status=500)

        elif path.startswith("/api/save_map/"):
            map_key = path.replace("/api/save_map/", "").strip()
            ecu = APP_STATE["ecu"]
            new_matrix = body.get("matrix", [])

            if not ecu or map_key not in MAP_DEFINITIONS:
                return self._send_json({"error": "Brak pliku BIN lub nieznana mapa"}, status=400)

            md = MAP_DEFINITIONS[map_key]
            try:
                ecu.write_map(md, new_matrix, codeblock=5)
                ecu.write_map(md, new_matrix, codeblock=2)
                return self._send_json({"success": True, "message": f"Zapisano pomyślnie zmiany dla {md.name} (CB5 & CB2)."})
            except Exception as e:
                return self._send_json({"error": f"Błąd zapisu mapy: {e}"}, status=500)

        elif path == "/api/autotune":
            analyzer = APP_STATE["analyzer"]
            ecu = APP_STATE["ecu"]
            vcds = APP_STATE["vcds"]

            if not ecu or not vcds or not vcds.data_points:
                return self._send_json({"error": "Wymagany jest wczytany wsad BIN oraz logi VCDS!"}, status=400)

            try:
                res = analyzer.run_autotune_all(codeblock=5)
                for m_key, new_mat in res["modified_maps"].items():
                    m_def = MAP_DEFINITIONS.get(m_key)
                    if m_def:
                        ecu.write_map(m_def, new_mat, codeblock=5)
                        ecu.write_map(m_def, new_mat, codeblock=2)

                APP_STATE["last_autotune_result"] = res
                return self._send_json({
                    "success": True,
                    "total_changes": res["total_changes"],
                    "modified_maps": list(res["modified_maps"].keys()),
                    "changes_log": res["changes_log"]
                })
            except Exception as e:
                traceback.print_exc()
                return self._send_json({"error": f"Błąd podczas Auto-Tune: {e}"}, status=500)

        else:
            self.send_error(404, "Endpoint Not Found")


# ─────────────────────────────────────────────────────────────────────────────
# STATE-OF-THE-ART CYBERPUNK / PRO TUNER WEB INTERFACE (Plotly 3D + WinOLS Heatmap)
# ─────────────────────────────────────────────────────────────────────────────

HTML_INTERFACE = r"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDC15VM+ PRO TUNER STUDIO v3.0</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Plotly.js for 3D Surface Visualizations -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

    <style>
        :root {
            --bg-body: #070a11;
            --bg-card: #0e1422;
            --bg-card-hover: #141c30;
            --border-color: #1e293d;
            --border-highlight: #2e3e5c;
            
            --primary: #00f2fe;
            --primary-glow: rgba(0, 242, 254, 0.35);
            --secondary: #7928ca;
            --secondary-glow: rgba(121, 40, 202, 0.4);
            --accent-green: #00dfa2;
            --accent-amber: #ffb703;
            --accent-red: #ff0055;
            
            --text-heading: #ffffff;
            --text-main: #cbd5e1;
            --text-dim: #64748b;
            
            --font-main: 'Outfit', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: var(--font-main);
        }

        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(121, 40, 202, 0.07) 0%, transparent 45%);
        }

        /* Top Header */
        header {
            background: rgba(14, 20, 34, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-color);
            padding: 14px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .brand-container {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .brand-badge {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 22px;
            color: #000;
            box-shadow: 0 0 25px var(--primary-glow);
            letter-spacing: -1px;
        }

        .brand-text h1 {
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, #ffffff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-text span {
            font-size: 11px;
            color: var(--primary);
            font-family: var(--font-mono);
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .top-nav-stats {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .stat-pill {
            background: rgba(30, 41, 61, 0.6);
            border: 1px solid var(--border-color);
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: var(--font-mono);
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-red);
            box-shadow: 0 0 10px var(--accent-red);
        }

        .status-indicator.active {
            background: var(--accent-green);
            box-shadow: 0 0 10px var(--accent-green);
        }

        /* Layout Grid */
        .app-layout {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            padding: 20px 28px;
            flex: 1;
        }

        /* Sidebar Styling */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .panel-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
            transition: border-color 0.2s ease;
        }

        .panel-card:hover {
            border-color: var(--border-highlight);
        }

        .panel-title {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-dim);
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* Modern Custom Buttons */
        .btn-glow {
            width: 100%;
            padding: 12px 18px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 700;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-cyan {
            background: linear-gradient(135deg, #00f2fe, #00c6ff);
            color: #000;
            box-shadow: 0 4px 18px var(--primary-glow);
        }

        .btn-cyan:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 242, 254, 0.6);
        }

        .btn-autotune-pro {
            background: linear-gradient(135deg, #7928ca, #ff0080);
            color: #fff;
            font-size: 14px;
            padding: 16px;
            box-shadow: 0 4px 25px var(--secondary-glow);
            position: relative;
            overflow: hidden;
        }

        .btn-autotune-pro:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(255, 0, 128, 0.6);
        }

        .btn-autotune-pro::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(60deg, transparent, rgba(255,255,255,0.2), transparent);
            transform: rotate(30deg);
            transition: all 0.75s ease;
        }

        .btn-autotune-pro:hover::after {
            left: 100%;
        }

        .form-field {
            margin-bottom: 12px;
        }

        .form-field label {
            display: block;
            font-size: 11px;
            color: var(--text-dim);
            margin-bottom: 6px;
            font-family: var(--font-mono);
        }

        .input-dark {
            width: 100%;
            padding: 10px 14px;
            background: #090e17;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: #fff;
            font-size: 12px;
            font-family: var(--font-mono);
            transition: border-color 0.2s ease;
        }

        .input-dark:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 12px var(--primary-glow);
        }

        /* Map Selector List */
        .map-selector-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
            max-height: 400px;
            overflow-y: auto;
            padding-right: 4px;
        }

        .map-selector-list::-webkit-scrollbar {
            width: 5px;
        }
        .map-selector-list::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }

        .map-card-item {
            padding: 10px 14px;
            border-radius: 10px;
            background: #090e17;
            border: 1px solid transparent;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
            transition: all 0.2s ease;
        }

        .map-card-item:hover {
            background: var(--bg-card-hover);
            border-color: var(--border-highlight);
        }

        .map-card-item.active {
            background: rgba(0, 242, 254, 0.08);
            border-color: var(--primary);
            color: #fff;
            font-weight: 700;
        }

        .code-tag {
            font-family: var(--font-mono);
            font-size: 10px;
            padding: 2px 6px;
            background: #141c2e;
            border-radius: 4px;
            color: var(--primary);
            border: 1px solid rgba(0, 242, 254, 0.2);
        }

        /* Main Workspace View */
        .main-workspace {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        /* Toolbar Controls */
        .workspace-toolbar {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 18px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .map-meta-info h2 {
            font-size: 22px;
            font-weight: 800;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .map-meta-info p {
            font-size: 12px;
            color: var(--text-dim);
            font-family: var(--font-mono);
            margin-top: 4px;
        }

        .view-mode-tabs {
            display: flex;
            background: #090e17;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 4px;
            gap: 4px;
        }

        .view-tab {
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            color: var(--text-dim);
            transition: all 0.2s ease;
            border: none;
            background: transparent;
        }

        .view-tab.active {
            background: var(--bg-card-hover);
            color: var(--primary);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
        }

        /* Heatmap Matrix Table (WinOLS Mode) */
        .matrix-viewport {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            overflow-x: auto;
            min-height: 420px;
        }

        table.heatmap-matrix {
            border-collapse: separate;
            border-spacing: 3px;
            width: 100%;
        }

        table.heatmap-matrix th {
            padding: 8px;
            font-size: 11px;
            font-weight: 700;
            color: var(--text-dim);
            background: #090e17;
            border-radius: 6px;
            text-align: center;
            font-family: var(--font-mono);
        }

        table.heatmap-matrix td {
            border-radius: 6px;
            padding: 6px;
            text-align: center;
            min-width: 85px;
            position: relative;
            transition: all 0.15s ease;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        table.heatmap-matrix td:hover {
            transform: scale(1.06);
            z-index: 50;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.5);
            border-color: var(--primary) !important;
        }

        .cell-input {
            width: 100%;
            background: transparent;
            border: none;
            color: #fff;
            font-weight: 800;
            font-size: 13px;
            text-align: center;
            font-family: var(--font-mono);
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }

        .cell-input:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.25);
            border-radius: 4px;
        }

        .vcds-log-overlay {
            font-size: 9px;
            font-family: var(--font-mono);
            margin-top: 2px;
            padding: 2px;
            border-radius: 4px;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }

        .vcds-log-overlay.diff-positive {
            color: var(--accent-amber);
            border: 1px solid rgba(255, 183, 3, 0.4);
        }

        .vcds-log-overlay.diff-negative {
            color: var(--primary);
            border: 1px solid rgba(0, 242, 254, 0.4);
        }

        .vcds-log-overlay.diff-zero {
            color: var(--accent-green);
            border: 1px solid rgba(0, 223, 162, 0.4);
        }

        /* 3D Visualizer Viewport */
        #plotly3dContainer {
            width: 100%;
            height: 480px;
            border-radius: 12px;
            overflow: hidden;
            display: none;
        }

        /* Console Log Box */
        .console-terminal {
            background: #05080f;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px 18px;
            font-family: var(--font-mono);
            font-size: 11px;
            color: #38bdf8;
            max-height: 180px;
            overflow-y: auto;
            line-height: 1.5;
        }

        .log-entry { margin-bottom: 2px; }
        .log-entry.success { color: var(--accent-green); }
        .log-entry.error { color: var(--accent-red); }
        .log-entry.warn { color: var(--accent-amber); }

        /* Audit Findings Cards Grid */
        .audit-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 14px;
            margin-top: 14px;
        }

        .audit-card {
            background: #090e17;
            border-left: 4px solid var(--primary);
            border-radius: 10px;
            padding: 14px;
            font-size: 12px;
        }

        .audit-card.CRITICAL { border-left-color: var(--accent-red); }
        .audit-card.WARNING { border-left-color: var(--accent-amber); }
        .audit-card.INFO { border-left-color: var(--primary); }

        .audit-card-hdr {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-weight: 700;
            margin-bottom: 6px;
        }
    </style>
</head>
<body>

    <!-- Header Navigation -->
    <header>
        <div class="brand-container">
            <div class="brand-badge">EDC</div>
            <div class="brand-text">
                <h1>EDC15VM+ Pro Tuner Suite <span>v3.0 Master Engine</span></h1>
            </div>
        </div>

        <div class="top-nav-stats">
            <div class="stat-pill">
                <div id="statusLed" class="status-indicator"></div>
                <span id="statusLabel">Inicjalizacja...</span>
            </div>
            <button class="btn-glow btn-cyan" style="width: auto; padding: 8px 16px;" onclick="exportBinFile()">
                ⚡ Eksportuj BIN
            </button>
        </div>
    </header>

    <!-- Main Application Grid -->
    <div class="app-layout">
        <!-- Sidebar Controls -->
        <div class="sidebar">
            <!-- Files Card -->
            <div class="panel-card">
                <div class="panel-title">Wsad & Logi VCDS</div>
                <div class="form-field">
                    <label>Wsad ECU (.BIN):</label>
                    <input type="text" id="binPath" class="input-dark" value="d:\t4\cks ok">
                </div>
                <button class="btn-glow btn-cyan" onclick="loadBin()">Wczytaj Wsad BIN</button>

                <div class="form-field" style="margin-top: 14px;">
                    <label>Logi z jazdy VCDS (.CSV):</label>
                    <input type="text" id="vcdsPaths" class="input-dark" placeholder="Wklej ścieżkę logu CSV...">
                </div>
                <button class="btn-glow btn-cyan" onclick="loadVcds()">Wczytaj Logi CSV</button>
            </div>

            <!-- Auto-Tune Card -->
            <div class="panel-card" style="background: linear-gradient(180deg, #110e24, #0e1422);">
                <div class="panel-title" style="color: #c084fc;">Automatyczna Kalibracja</div>
                <p style="font-size: 11px; color: var(--text-dim); margin-bottom: 14px; line-height: 1.4;">
                    Analizuje N75 (przładowania/lag), Smoke Limiter (korekta dymienia MAF) oraz SOI (kąt wtrysku) bezpośrednio z odczytów VCDS.
                </p>
                <button class="btn-glow btn-autotune-pro" onclick="executeAutoTune()">
                    🚀 URUCHOM AUTO-TUNE
                </button>
            </div>

            <!-- Map List Card -->
            <div class="panel-card">
                <div class="panel-title">Mapy Sterownika</div>
                <div class="map-selector-list" id="mapListContainer">
                    <!-- Dynamic MAP cards -->
                </div>
            </div>
        </div>

        <!-- Main Workspace -->
        <div class="main-workspace">
            <!-- Workspace Toolbar -->
            <div class="workspace-toolbar">
                <div class="map-meta-info">
                    <h2 id="activeMapTitle">Wybierz mapę <span class="code-tag" id="activeMapCode">BS</span></h2>
                    <p id="activeMapSubtitle">Odczytaj i edytuj w skalowanych jednostkach fizycznych</p>
                </div>

                <div class="view-mode-tabs">
                    <button class="view-tab active" onclick="switchViewMode('heatmap')">📊 WinOLS Heatmap</button>
                    <button class="view-tab" onclick="switchViewMode('plotly')">🧊 Wykres 3D Surface</button>
                </div>

                <button class="btn-glow btn-cyan" style="width: auto; padding: 10px 20px;" onclick="saveMapChanges()">
                    💾 Zapisz Mapę w Pamięci (CB5 & CB2)
                </button>
            </div>

            <!-- Matrix Viewport -->
            <div class="matrix-viewport">
                <!-- Heatmap Table -->
                <div id="heatmapTableContainer">
                    <table class="heatmap-matrix" id="heatmapMatrixTable">
                        <!-- Rendered via JS -->
                    </table>
                </div>

                <!-- Plotly 3D Surface Container -->
                <div id="plotly3dContainer"></div>
            </div>

            <!-- Console Terminal & Audit Findings -->
            <div class="panel-card">
                <div class="panel-title">Konsola Operacyjna & Wyniki Audytu Logów</div>
                <div class="console-terminal" id="terminalLog">
                    <div class="log-entry">> System EDC15VM+ Pro Tuner Suite 3.0 gotowy.</div>
                </div>

                <div class="audit-cards-grid" id="auditGrid">
                    <!-- Audit cards rendered via JS -->
                </div>
            </div>
        </div>
    </div>

    <script>
        let activeMapKey = 'boost_target';
        let activeMapData = null;
        let currentViewMode = 'heatmap';

        async function updateStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();

                const led = document.getElementById('statusLed');
                const label = document.getElementById('statusLabel');

                if (data.bin_loaded) {
                    led.classList.add('active');
                    label.innerText = `BIN: ${data.bin_name} | SW: ${data.header_info.software || 'OK'} | Logi: ${data.vcds_count} pkt`;
                    document.getElementById('binPath').value = data.bin_path;
                } else {
                    led.classList.remove('active');
                    label.innerText = 'Brak wsadu BIN';
                }

                if (data.csv_paths && data.csv_paths.length > 0) {
                    document.getElementById('vcdsPaths').value = data.csv_paths.join(';');
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function fetchMaps() {
            try {
                const res = await fetch('/api/maps');
                const maps = await res.json();

                const container = document.getElementById('mapListContainer');
                container.innerHTML = '';

                maps.forEach(m => {
                    const el = document.createElement('div');
                    el.className = `map-card-item ${m.key === activeMapKey ? 'active' : ''}`;
                    el.onclick = () => selectMap(m.key);
                    el.innerHTML = `
                        <span>${m.name}</span>
                        <span class="code-tag">${m.dimsport}</span>
                    `;
                    container.appendChild(el);
                });
            } catch (e) {
                console.error(e);
            }
        }

        async function selectMap(key) {
            activeMapKey = key;
            await fetchMaps();
            await renderMap();
        }

        // Calculation of WinOLS style Heatmap RGB colors based on value percentile
        function getHeatmapColor(val, minVal, maxVal) {
            if (minVal === maxVal) return 'rgba(30, 41, 59, 0.8)';
            const ratio = Math.max(0, Math.min(1, (val - minVal) / (maxVal - minVal)));
            
            // Color ramp: Cool Blue (0.0) -> Cyan (0.25) -> Green (0.5) -> Yellow (0.75) -> Crimson Red (1.0)
            let r, g, b;
            if (ratio < 0.25) {
                const t = ratio / 0.25;
                r = Math.round(15 + t * (0 - 15));
                g = Math.round(23 + t * (180 - 23));
                b = Math.round(42 + t * (216 - 42));
            } else if (ratio < 0.5) {
                const t = (ratio - 0.25) / 0.25;
                r = Math.round(0 + t * (16 - 0));
                g = Math.round(180 + t * (185 - 180));
                b = Math.round(216 + t * (129 - 216));
            } else if (ratio < 0.75) {
                const t = (ratio - 0.5) / 0.25;
                r = Math.round(16 + t * (245 - 16));
                g = Math.round(185 + t * (158 - 185));
                b = Math.round(129 + t * (11 - 129));
            } else {
                const t = (ratio - 0.75) / 0.25;
                r = Math.round(245 + t * (239 - 245));
                g = Math.round(158 + t * (68 - 158));
                b = Math.round(11 + t * (68 - 11));
            }
            return `rgba(${r}, ${g}, ${b}, 0.75)`;
        }

        async function renderMap() {
            try {
                const res = await fetch(`/api/map/${activeMapKey}`);
                const data = await res.json();
                activeMapData = data;

                document.getElementById('activeMapTitle').innerHTML = `${data.name} <span class="code-tag" id="activeMapCode">${data.dimsport}</span>`;
                document.getElementById('activeMapSubtitle').innerText = `Rozmiar: ${data.rows}x${data.cols} | Jednostka: ${data.unit} | Osie: ${data.y_unit} x ${data.x_unit}`;

                // Calculate min/max for heatmap
                const allVals = data.ecu_matrix.flat();
                const minVal = Math.min(...allVals);
                const maxVal = Math.max(...allVals);

                // Render Heatmap Table
                const table = document.getElementById('heatmapMatrixTable');
                table.innerHTML = '';

                // Header (X Axis / RPM)
                const thead = document.createElement('thead');
                const hRow = document.createElement('tr');
                hRow.innerHTML = `<th>${data.y_unit} \\ ${data.x_unit}</th>` + 
                    data.x_axis.map(x => `<th>${x}</th>`).join('');
                thead.appendChild(hRow);
                table.appendChild(thead);

                // Body (Rows x Cols)
                const tbody = document.createElement('tbody');
                for (let r = 0; r < data.rows; r++) {
                    const tr = document.createElement('tr');
                    const yVal = (data.y_axis && data.y_axis[r] !== undefined) ? data.y_axis[r] : `R${r}`;
                    tr.innerHTML = `<th>${yVal}</th>`;

                    for (let c = 0; c < data.cols; c++) {
                        const val = data.ecu_matrix[r][c];
                        const logVal = (data.log_matrix && data.log_matrix[r] && data.log_matrix[r][c] !== null) ? data.log_matrix[r][c] : null;
                        const diff = (data.diff_matrix && data.diff_matrix[r] && data.diff_matrix[r][c] !== null) ? data.diff_matrix[r][c] : null;

                        const bgColor = getHeatmapColor(val, minVal, maxVal);

                        let logBadge = '';
                        if (logVal !== null) {
                            let diffClass = 'diff-zero';
                            let sign = '';
                            if (diff > 0) { diffClass = 'diff-positive'; sign = '+'; }
                            else if (diff < 0) { diffClass = 'diff-negative'; }

                            logBadge = `<div class="vcds-log-overlay ${diffClass}" title="Log VCDS: ${logVal}">
                                Log: ${logVal} (${sign}${diff})
                            </div>`;
                        }

                        const td = document.createElement('td');
                        td.style.backgroundColor = bgColor;
                        td.innerHTML = `
                            <input type="number" step="any" class="cell-input" data-row="${r}" data-col="${c}" value="${val}">
                            ${logBadge}
                        `;
                        tr.appendChild(td);
                    }
                    tbody.appendChild(tr);
                }
                table.appendChild(tbody);

                if (currentViewMode === 'plotly') {
                    renderPlotly3D();
                }

            } catch (e) {
                console.error(e);
            }
        }

        function switchViewMode(mode) {
            currentViewMode = mode;
            document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));

            if (mode === 'heatmap') {
                document.querySelectorAll('.view-tab')[0].classList.add('active');
                document.getElementById('heatmapTableContainer').style.display = 'block';
                document.getElementById('plotly3dContainer').style.display = 'none';
            } else {
                document.querySelectorAll('.view-tab')[1].classList.add('active');
                document.getElementById('heatmapTableContainer').style.display = 'none';
                document.getElementById('plotly3dContainer').style.display = 'block';
                renderPlotly3D();
            }
        }

        function renderPlotly3D() {
            if (!activeMapData) return;

            const zData = activeMapData.ecu_matrix;
            const xData = activeMapData.x_axis;
            const yData = activeMapData.y_axis;

            const trace = {
                z: zData,
                x: xData,
                y: yData,
                type: 'surface',
                colorscale: 'Jet',
                contours: {
                    z: { show: true, usecolormap: true, highlightcolor: "#00f2fe", project: { z: true } }
                }
            };

            const layout = {
                title: { text: `${activeMapData.name} - 3D Surface View`, font: { color: '#ffffff', family: 'Outfit' } },
                autosize: true,
                paper_bgcolor: '#0e1422',
                plot_bgcolor: '#0e1422',
                scene: {
                    xaxis: { title: activeMapData.x_unit, color: '#94a3b8' },
                    yaxis: { title: activeMapData.y_unit, color: '#94a3b8' },
                    zaxis: { title: activeMapData.unit, color: '#94a3b8' }
                },
                margin: { l: 0, r: 0, b: 0, t: 40 }
            };

            Plotly.newPlot('plotly3dContainer', [trace], layout);
        }

        async function saveMapChanges() {
            if (!activeMapData) return;

            const inputs = document.querySelectorAll('.cell-input');
            const newMatrix = JSON.parse(JSON.stringify(activeMapData.ecu_matrix));

            inputs.forEach(inp => {
                const r = parseInt(inp.getAttribute('data-row'));
                const c = parseInt(inp.getAttribute('data-col'));
                newMatrix[r][c] = parseFloat(inp.value);
            });

            try {
                const res = await fetch(`/api/save_map/${activeMapKey}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ matrix: newMatrix })
                });
                const resp = await res.json();

                const logBox = document.getElementById('terminalLog');
                if (resp.success) {
                    logBox.innerHTML += `<div class="log-entry success">> ZAPIS: ${resp.message}</div>`;
                    renderMap();
                } else {
                    logBox.innerHTML += `<div class="log-entry error">> BŁĄD: ${resp.error}</div>`;
                }
            } catch (e) {
                alert(`Błąd: ${e}`);
            }
        }

        async function executeAutoTune() {
            const logBox = document.getElementById('terminalLog');
            logBox.innerHTML += '<div class="log-entry warn">> Rozpoczęto automatyczne strojenie N75, Smoke Limiter & SOI z logów VCDS...</div>';

            try {
                const res = await fetch('/api/autotune', { method: 'POST' });
                const data = await res.json();

                if (data.success) {
                    logBox.innerHTML += `<div class="log-entry success">> AUTO-TUNE SUKCES: Zastosowano ${data.total_changes} korekt w mapach: ${data.modified_maps.join(', ')}</div>`;
                    data.changes_log.forEach(l => {
                        logBox.innerHTML += `<div class="log-entry">${l}</div>`;
                    });
                    renderMap();
                    fetchAudit();
                } else {
                    logBox.innerHTML += `<div class="log-entry error">> AUTO-TUNE BŁĄD: ${data.error}</div>`;
                }
            } catch (e) {
                logBox.innerHTML += `<div class="log-entry error">> AWARIA SYSTEMU: ${e}</div>`;
            }
        }

        async function fetchAudit() {
            try {
                const res = await fetch('/api/audit');
                const data = await res.json();

                const grid = document.getElementById('auditGrid');
                grid.innerHTML = '';

                data.findings.forEach(f => {
                    const card = document.createElement('div');
                    card.className = `audit-card ${f.severity}`;
                    card.innerHTML = `
                        <div class="audit-card-hdr">
                            <span>[${f.severity}] ${f.category}</span>
                            <span>${f.rpm_range}</span>
                        </div>
                        <div style="margin-bottom:6px; color: var(--text-main);">${f.description}</div>
                        <div style="color: var(--primary); font-weight: 600;">Zalecenie: ${f.recommendation}</div>
                    `;
                    grid.appendChild(card);
                });
            } catch (e) {
                console.error(e);
            }
        }

        async function loadBin() {
            const path = document.getElementById('binPath').value;
            const res = await fetch('/api/load_bin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bin_path: path })
            });
            const data = await res.json();

            if (data.success) {
                updateStatus();
                fetchMaps();
                renderMap();
                fetchAudit();
            } else {
                alert(`Błąd: ${data.error}`);
            }
        }

        async function loadVcds() {
            const paths = document.getElementById('vcdsPaths').value.split(';');
            const res = await fetch('/api/load_vcds', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ csv_paths: paths })
            });
            const data = await res.json();

            if (data.success) {
                updateStatus();
                renderMap();
                fetchAudit();
                alert(`Wczytano ${data.count} punktów WOT z VCDS!`);
            } else {
                alert(`Błąd: ${data.error}`);
            }
        }

        async function exportBinFile() {
            const res = await fetch('/api/download_bin');
            const data = await res.json();
            if (data.success) {
                alert(`${data.message}\n\nPamiętaj o przeliczeniu checksum przed wgraniem!`);
            }
        }

        // Init App
        (async function init() {
            await updateStatus();
            await fetchMaps();
            await renderMap();
            await fetchAudit();
        })();
    </script>
</body>
</html>
"""

def run_server(port=8080):
    init_app_state()
    handler = EDC15APIHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print("=" * 80)
        print(f"  EDC15VM+ Pro Tuner Suite 3.0 Uruchomiony: http://localhost:{port}")
        print("=" * 80)
        webbrowser.open(f"http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nZamykanie serwera EDC15 Pro Server.")

if __name__ == "__main__":
    run_server(8080)
