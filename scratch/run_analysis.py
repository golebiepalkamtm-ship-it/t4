"""
Skrypt analizy: VCDS logi vs cks ok_stage1_pro.bin
"""
import sys
import os
import json

sys.path.insert(0, r"d:\t4")
from edc15_analyzer import (
    ECUBinaryReader, VCDSLogParser, EDC15Analyzer,
    MAP_DEFINITIONS, MAP_AXES, plot_advanced_diagnostics
)

BIN_FILE = r"d:\t4\cks ok_stage1_pro.bin"
CSV_FILES = [
    r"d:\t4\LOG-01-002-004-008.CSV",
    r"d:\t4\LOG-01-003-005-002.CSV",
    r"d:\t4\LOG-01-011-010-009.CSV",
    r"d:\t4\LOG-01-014-013-012.CSV",
    r"d:\t4\LOG-01-023-019-010.CSV",
]
OUTPUT_DIR = r"d:\t4\Raporty_EDC15"

print("="*80)
print("  FULL ANALYSIS: cks ok_stage1_pro.bin vs 5x VCDS Logs")
print("="*80)

# 1. Load BIN
print("\n[1] Wczytywanie pliku BIN...")
ecu = ECUBinaryReader(BIN_FILE)
print(f"    Header info: {ecu.header_info}")
print(f"    Rozmiar: {len(ecu.data)} bajtow")

# 2. Parse all CSV logs
print("\n[2] Parsowanie logow VCDS...")
vcds = VCDSLogParser(CSV_FILES)
print(f"    Zebrano: {len(vcds.data_points)} unikalnych profili RPM")

# Print parsed data summary
print("\n[3] Podsumowanie danych z logow:")
for dp in vcds.data_points:
    fields = []
    if dp.rpm > 0: fields.append(f"RPM={dp.rpm:.0f}")
    if dp.boost_req > 0: fields.append(f"BoostReq={dp.boost_req:.0f}")
    if dp.boost_act > 0: fields.append(f"BoostAct={dp.boost_act:.0f}")
    if dp.n75_duty > 0: fields.append(f"N75={dp.n75_duty:.1f}%")
    if dp.iq_driver > 0: fields.append(f"IQdrv={dp.iq_driver:.1f}")
    if dp.iq_torque > 0: fields.append(f"IQtorq={dp.iq_torque:.1f}")
    if dp.iq_smoke > 0: fields.append(f"IQsmoke={dp.iq_smoke:.1f}")
    if dp.maf_req > 0: fields.append(f"MAFreq={dp.maf_req:.0f}")
    if dp.maf_actual > 0: fields.append(f"MAFact={dp.maf_actual:.0f}")
    if dp.soi_req > 0: fields.append(f"SOIreq={dp.soi_req:.1f}")
    if dp.soi_act > 0: fields.append(f"SOIact={dp.soi_act:.1f}")
    if dp.pump_voltage > 0: fields.append(f"PumpV={dp.pump_voltage:.3f}")
    if dp.coolant_temp > 0: fields.append(f"Temp={dp.coolant_temp:.1f}C")
    print(f"    {' | '.join(fields)}")

# 4. Full map audit
print("\n[4] Audyt map (Codeblock 5):")
analyzer = EDC15Analyzer(ecu, vcds)
results = analyzer.audit_maps(codeblock=5)
for r in results:
    status = "[LOCKED] OFF" if r["is_flat"] else f"{r['min']} - {r['max']}"
    print(f"    {r['dimsport']:4s} | {r['name']:50s} | {r['address']:10s} | {status} {r['unit']}")

# 5. Execute all analyses
print("\n[5] Analiza diagnostyczna logow...")
analyzer.execute_all_analysis()

# 6. Print findings
print(f"\n[6] Odkrycia diagnostyczne ({len(analyzer.findings)}):")
for f in analyzer.findings:
    icon = {"CRITICAL": "[X]", "WARNING": "[!]", "INFO": "[i]"}.get(f.severity, "[-]")
    print(f"    {icon} [{f.severity}] {f.category}")
    print(f"        {f.description}")
    print(f"        >> {f.recommendation}")
    print(f"        >> Mapa: {f.map_to_adjust}")

# 7. Map-Log correlation for key maps
print("\n[7] Korelacja Map-Log (kluczowe mapy):")
for map_key in ["boost_target", "n75_duty", "smoke_limiter_15c", "soi_map", "driver_wish", "torque_limiter"]:
    log_mx, diff_mx = analyzer.get_map_log_matrix(map_key, codeblock=5)
    has_data = any(v is not None for row in log_mx for v in row)
    if has_data:
        map_def = MAP_DEFINITIONS[map_key]
        ecu_mx = ecu.read_map(map_def, codeblock=5)
        axes = MAP_AXES[map_key]
        
        print(f"\n    === {map_def.name} ===")
        print(f"    Osie X ({axes.get('x_unit', '')}): {axes['x'][:8]}...")
        print(f"    Osie Y ({axes.get('y_unit', '')}): {axes['y']}")
        
        for r_idx, (ecu_row, log_row, diff_row) in enumerate(zip(ecu_mx, log_mx, diff_mx)):
            y_val = axes['y'][r_idx] if r_idx < len(axes['y']) else '?'
            cells = []
            for c_idx, (ev, lv, dv) in enumerate(zip(ecu_row, log_row, diff_row)):
                if lv is not None:
                    arrow = "UP" if dv > 0 else ("DN" if dv < 0 else "==")
                    cells.append(f"ECU={ev:.1f}/LOG={lv:.1f}({dv:+.1f}{arrow})")
            if cells:
                print(f"    Y={y_val}: {' | '.join(cells[:5])}")

# 8. WOT data analysis
print("\n[8] Dane WOT (pelny gaz):")
wot_data = vcds.get_wot_data()
print(f"    Probek WOT: {len(wot_data)}")
for dp in wot_data:
    limiter = "?"
    iqs = {"DRV": dp.iq_driver, "TRQ": dp.iq_torque, "SMK": dp.iq_smoke}
    active_iqs = {k: v for k, v in iqs.items() if v > 0}
    if active_iqs:
        limiter = min(active_iqs, key=active_iqs.get)
    print(f"    RPM={dp.rpm:.0f} | Boost: req={dp.boost_req:.0f} act={dp.boost_act:.0f} (D={dp.boost_act-dp.boost_req:+.0f}) | N75={dp.n75_duty:.1f}% | IQ: drv={dp.iq_driver:.1f} trq={dp.iq_torque:.1f} smk={dp.iq_smoke:.1f} | Limiter={limiter} | MAF={dp.maf_actual:.0f} | SOI: {dp.soi_req:.1f}/{dp.soi_act:.1f}")

# 9. Auto-tune suggestions
print("\n[9] Auto-tune propozycje:")
autotune = analyzer.run_autotune_all(codeblock=5)
print(f"    Calkowita liczba zmian: {autotune['total_changes']}")
for change in autotune['changes_log']:
    print(f"    {change}")

# 10. Generate plots
print("\n[10] Generowanie wykresow...")
os.makedirs(OUTPUT_DIR, exist_ok=True)
try:
    plot_advanced_diagnostics(vcds, OUTPUT_DIR)
    print("    Wykresy zapisane do:", OUTPUT_DIR)
except Exception as e:
    print(f"    Blad generowania wykresow: {e}")

# 11. Dump full data to JSON for report
output_data = {
    "bin_file": BIN_FILE,
    "header_info": ecu.header_info,
    "csv_files": CSV_FILES,
    "data_points_count": len(vcds.data_points),
    "wot_count": len(wot_data),
    "map_audit": results,
    "findings": [
        {
            "severity": f.severity,
            "category": f.category,
            "rpm_range": f.rpm_range,
            "description": f.description,
            "recommendation": f.recommendation,
            "map_to_adjust": f.map_to_adjust
        }
        for f in analyzer.findings
    ],
    "autotune_total_changes": autotune["total_changes"],
    "autotune_changes": autotune["changes_log"],
    "wot_data": [
        {
            "rpm": dp.rpm,
            "boost_req": dp.boost_req,
            "boost_act": dp.boost_act,
            "boost_delta": round(dp.boost_act - dp.boost_req, 1),
            "n75_duty": dp.n75_duty,
            "iq_driver": dp.iq_driver,
            "iq_torque": dp.iq_torque,
            "iq_smoke": dp.iq_smoke,
            "maf_req": dp.maf_req,
            "maf_actual": dp.maf_actual,
            "soi_req": dp.soi_req,
            "soi_act": dp.soi_act,
            "pump_voltage": dp.pump_voltage,
            "coolant_temp": dp.coolant_temp,
        }
        for dp in wot_data
    ],
    "all_data": [
        {
            "rpm": dp.rpm,
            "boost_req": dp.boost_req,
            "boost_act": dp.boost_act,
            "n75_duty": dp.n75_duty,
            "iq_driver": dp.iq_driver,
            "iq_torque": dp.iq_torque,
            "iq_smoke": dp.iq_smoke,
            "maf_req": dp.maf_req,
            "maf_actual": dp.maf_actual,
            "soi_req": dp.soi_req,
            "soi_act": dp.soi_act,
            "pump_voltage": dp.pump_voltage,
            "coolant_temp": dp.coolant_temp,
        }
        for dp in vcds.data_points
    ],
}

json_path = os.path.join(OUTPUT_DIR, "analysis_data.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
print(f"\n[GOTOWE] Dane analityczne zapisane do: {json_path}")
print("="*80)
