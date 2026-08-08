import sys
import os
import csv
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")

from edc15_analyzer import ECUBinaryReader, VCDSLogParser, EDC15Analyzer, MAP_DEFINITIONS

bin_path = r"d:\t4\cks ok"
csv_files = [
    r"d:\t4\LOG-01-002-004-008.CSV",
    r"d:\t4\LOG-01-003-005-002.CSV",
    r"d:\t4\LOG-01-014-013-012.CSV",
    r"d:\t4\LOG-01-011-010-009.CSV",
    r"d:\t4\LOG-01-023-019-010.CSV"
]

ecu = ECUBinaryReader(bin_path)
parser = VCDSLogParser(csv_files)
analyzer = EDC15Analyzer(ecu, parser)

analyzer.audit_maps(codeblock=5)
analyzer.execute_all_analysis()

print("=== SPECYFIKACJA SEKCJI POMIAROWYCH DLA LOGÓW VCDS ===")
print(f"Liczba odczytanych profili obrotowych: {len(parser.data_points)}")

print("\n--- 1. PODSUMOWANIE OBSERWACJI DIAGNOSTYCZNYCH ---")
for f in analyzer.findings:
    print(f"  [{f.severity}] {f.category} ({f.rpm_range}): {f.description}")
    print(f"      Zalecenie: {f.recommendation} | Mapa: {f.map_to_adjust}")

print("\n--- 2. PARAMETRY KLUCZOWE W PRÓBACH WOT (PEŁNY GAZ) ---")
wot_dps = parser.get_wot_data(min_rpm=1300)
print(f"Liczba ramek danych WOT: {len(wot_dps)}")
for dp in wot_dps[:15]:
    print(f"  RPM: {dp.rpm:4.0f} | Boost req: {dp.boost_req:4.0f}, act: {dp.boost_act:4.0f} (N75 {dp.n75_duty:4.1f}%) | "
          f"IQ drv: {dp.iq_driver:4.1f}, trq: {dp.iq_torque:4.1f}, smk: {dp.iq_smoke:4.1f} | MAF act: {dp.maf_actual:4.0f} | "
          f"VP37: {dp.pump_voltage:.3f}V | SOI req: {dp.soi_req:4.1f}°, act: {dp.soi_act:4.1f}°")

print("\n--- 3. AUTOTUNE KOREKTY KONTROLNE ---")
autotune_res = analyzer.run_autotune_all(codeblock=5)
print(f"Łącznie proponowanych automatycznych korekt w mapach: {autotune_res['total_changes']}")
for change in autotune_res['changes_log'][:20]:
    print("  *", change)
