"""
Pelna ocena pliku cks ok oraz logow VCDS.
Uruchamia: python scratch/full_eval.py
"""
import sys, os
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import (
    ECUBinaryReader, VCDSLogParser, EDC15Analyzer,
    MAP_DEFINITIONS, MAP_AXES, RPM_AXIS_16,
    plot_advanced_diagnostics
)

BIN_FILE = r"d:\t4\cks ok"
VCDS_LOGS = [
    r"d:\t4\LOG-01-002-004-008.CSV",
    r"d:\t4\LOG-01-003-005-002.CSV",
    r"d:\t4\LOG-01-011-010-009.CSV",
    r"d:\t4\LOG-01-014-013-012.CSV",
    r"d:\t4\LOG-01-023-019-010.CSV",
]
OUTPUT_DIR = r"d:\t4\Raporty_EDC15"

print("=" * 90)
print("  PELNA OCENA: Plik 'cks ok' + Logi VCDS (5 plikow, wszystkie grupy)")
print("=" * 90)

# 1. WCZYTANIE BIN
ecu = ECUBinaryReader(BIN_FILE)
print(f"\n[1] WSAD BIN: {BIN_FILE}")
print(f"    Rozmiar: {len(ecu.data)} bajtow ({len(ecu.data)/1024:.0f} KB)")
print(f"    VAG HW:  {ecu.header_info.get('vag_hw', '?')}")
print(f"    Bosch HW: {ecu.header_info.get('bosch_hw', '?')}")
print(f"    Software: {ecu.header_info.get('software', '?')}")

# 2. AUDYT MAP (cks ok)
print(f"\n[2] AUDYT MAP - cks ok (Codeblock 5):")
print(f"    {'Kod':4s} | {'Nazwa':50s} | {'Adres':10s} | {'Min':>8s} - {'Max':>8s} | {'Jedn.':8s} | Status")
print("    " + "-" * 110)
analyzer = EDC15Analyzer(ecu, None)
results = analyzer.audit_maps(codeblock=5)
for r in results:
    status = "[LOCKED] OFF" if r["is_flat"] else f"{r['min']:>8.1f} - {r['max']:>8.1f}"
    print(f"    {r['dimsport']:4s} | {r['name']:50s} | {r['address']:10s} | {status} | {r['unit']:8s} | {'FLAT' if r['is_flat'] else 'OK'}")

# 3. WCZYTANIE LOGOW VCDS
print(f"\n[3] WCZYTANIE LOGOW VCDS ({len(VCDS_LOGS)} plikow):")
for p in VCDS_LOGS:
    print(f"    - {os.path.basename(p)}")

vcds = VCDSLogParser(VCDS_LOGS)
print(f"\n    Zebrano {len(vcds.data_points)} unikalnych profili RPM z wszystkich logow.")

# 4. PODSUMOWANIE PUNKTOW DANYCH
print(f"\n[4] PODSUMOWANIE PUNKTOW DANYCH (RPM | Kluczowe parametry):")
print(f"    {'RPM':>6s} | {'IQ Act':>7s} | {'IQ Drv':>7s} | {'IQ Trq':>7s} | {'IQ Smk':>7s} | {'Boost R':>8s} | {'Boost A':>8s} | {'N75':>5s} | {'MAF R':>6s} | {'MAF A':>6s} | {'SOI R':>5s} | {'SOI A':>5s} | {'PumpV':>5s} | {'Atm':>5s}")
print("    " + "-" * 140)
for dp in vcds.data_points:
    if dp.rpm < 500: continue
    print(f"    {dp.rpm:>6.0f} | {dp.iq_actual:>7.1f} | {dp.iq_driver:>7.1f} | {dp.iq_torque:>7.1f} | {dp.iq_smoke:>7.1f} | {dp.boost_req:>8.0f} | {dp.boost_act:>8.0f} | {dp.n75_duty:>5.1f} | {dp.maf_req:>6.0f} | {dp.maf_actual:>6.0f} | {dp.soi_req:>5.1f} | {dp.soi_act:>5.1f} | {dp.pump_voltage:>5.2f} | {dp.atmos_press:>5.0f}")

# 5. DANE WOT (Wide Open Throttle)
wot = vcds.get_wot_data(min_rpm=1300)
print(f"\n[5] DANE WOT (min_rpm=1300, iq_driver>=35 lub boost_req>=1500): {len(wot)} punktow")
print(f"    {'RPM':>6s} | {'IQ Drv':>7s} | {'IQ Trq':>7s} | {'IQ Smk':>7s} | {'Boost R':>8s} | {'Boost A':>8s} | {'dBoost':>7s} | {'N75':>5s} | {'MAF A':>6s} | {'SOI R':>5s} | {'SOI A':>5s} | {'PumpV':>5s}")
print("    " + "-" * 120)
for dp in wot:
    delta_b = dp.boost_act - dp.boost_req
    active_limiter = ""
    iqs = {"DRV": dp.iq_driver, "TRQ": dp.iq_torque, "SMK": dp.iq_smoke}
    if all(v > 0 for v in iqs.values()):
        active_limiter = min(iqs, key=iqs.get)
    print(f"    {dp.rpm:>6.0f} | {dp.iq_driver:>7.1f} | {dp.iq_torque:>7.1f} | {dp.iq_smoke:>7.1f} | {dp.boost_req:>8.0f} | {dp.boost_act:>8.0f} | {delta_b:>+7.0f} | {dp.n75_duty:>5.1f} | {dp.maf_actual:>6.0f} | {dp.soi_req:>5.1f} | {dp.soi_act:>5.1f} | {dp.pump_voltage:>5.2f}  {('<- '+active_limiter) if active_limiter else ''}")

# 6. ANALIZA DIAGNOSTYCZNA
print(f"\n[6] ANALIZA DIAGNOSTYCZNA (korelacja log<->mapa):")
analyzer = EDC15Analyzer(ecu, vcds)
analyzer.audit_maps(codeblock=5)
analyzer.execute_all_analysis()

if analyzer.findings:
    print(f"\n    Znaleziono {len(analyzer.findings)} odkryc diagnostycznych:")
    for f in analyzer.findings:
        icon = {"CRITICAL": "[X] KRYTYCZNE", "WARNING": "[!] OSTRZEZENIE", "INFO": "[i] INFO"}.get(f.severity, "[-]")
        print(f"\n    {icon} [{f.category}] (RPM: {f.rpm_range})")
        print(f"      Opis: {f.description}")
        print(f"      Zalecenie: {f.recommendation}")
        if f.map_to_adjust:
            print(f"      Mapa: {f.map_to_adjust}")
else:
    print("    Brak odkryc diagnostycznych. Wszystko w normie.")

# 7. KORELACJA MAPA <-> LOG (macierze roznic)
print(f"\n[7] KORELACJA MAPA <-> LOG (macierze roznic dla kluczowych map):")
key_maps = ["boost_target", "n75_duty", "smoke_limiter_15c", "soi_map", "driver_wish", "torque_limiter"]
for map_key in key_maps:
    md = MAP_DEFINITIONS.get(map_key)
    if not md: continue
    log_matrix, diff_matrix = analyzer.get_map_log_matrix(map_key, codeblock=5)
    ecu_matrix = ecu.read_map(md, codeblock=5)
    axes = MAP_AXES.get(map_key, {})
    x_axis = axes.get("x", [])
    y_axis = axes.get("y", [])

    print(f"\n    -- {md.name} ({md.dimsport_code}) -- {md.rows}x{md.cols} {md.unit} --")
    # Naglowek X
    hdr = f"    {'Y\\X':>8s}"
    for x in x_axis[:md.cols]:
        hdr += f" | {x:>7.0f}"
    print(hdr)
    print("    " + "-" * (10 + 10 * md.cols))

    for r in range(md.rows):
        y_val = y_axis[r] if r < len(y_axis) else f"R{r}"
        row_str = f"    {y_val:>8.1f}"
        for c in range(md.cols):
            map_v = ecu_matrix[r][c]
            log_v = log_matrix[r][c] if log_matrix and r < len(log_matrix) and c < len(log_matrix[r]) else None
            diff = diff_matrix[r][c] if diff_matrix and r < len(diff_matrix) and c < len(diff_matrix[r]) else None
            if log_v is not None:
                cell = f"{map_v:.0f}->{log_v:.0f}({diff:+.0f})"
            else:
                cell = f"{map_v:.0f}"
            row_str += f" | {cell:>7s}"
        print(row_str)

# 8. ANALIZA LIMITEROW DAWKI
print(f"\n[8] ANALIZA AKTYWNYCH LIMITEROW DAWKI (WOT):")
stats = {"DRIVER_WISH": 0, "TORQUE_LIMITER": 0, "SMOKE_LIMITER": 0}
for dp in wot:
    iqs = {"DRIVER_WISH": dp.iq_driver, "TORQUE_LIMITER": dp.iq_torque, "SMOKE_LIMITER": dp.iq_smoke}
    if all(v > 0 for v in iqs.values()):
        active = min(iqs, key=iqs.get)
        stats[active] += 1
total = sum(stats.values())
if total > 0:
    for k, v in stats.items():
        pct = v / total * 100
        bar = "#" * int(pct / 5)
        print(f"    {k:20s}: {v:>3d}/{total} ({pct:>5.1f}%) {bar}")

# 9. ANALIZA BOOST DEVIATION
print(f"\n[9] ANALIZA BOOST DEVIATION (req vs act):")
lag_count = spike_count = 0
for dp in vcds.data_points:
    if dp.boost_req < 1200: continue
    delta = dp.boost_act - dp.boost_req
    if delta < -150: lag_count += 1
    elif delta > 150: spike_count += 1
print(f"    Turbo Lag (act < req - 150mBar): {lag_count} punktow")
print(f"    Boost Spike (act > req + 150mBar): {spike_count} punktow")

# 10. ANALIZA PUMP VOLTAGE
print(f"\n[10] ANALIZA NAPIECIA POMPY VP37 (N146):")
max_v = max([dp.pump_voltage for dp in vcds.data_points if dp.pump_voltage > 0], default=0)
print(f"    Maksymalne napiecie pompy: {max_v:.3f} V")
if max_v >= 4.45:
    print(f"    [X] KRYTYCZNE: Pompa osiaga limit fizyczny (4.5V). Wtryskiwacze moga byc za male.")
elif max_v >= 4.0:
    print(f"    [!] OSTRZEZENIE: Napiecie pompy wysokie (>4.0V). Zblizasz sie do limitu.")
else:
    print(f"    [OK] Napiecie pompy w bezpiecznym zakresie.")

# 11. ANALIZA MAF
print(f"\n[11] ANALIZA PRZEPLOWOMIERZA (MAF G70):")
low_maf = 0
for dp in wot:
    if dp.maf_actual > 0 and dp.maf_req > 0:
        ratio = dp.maf_actual / dp.maf_req
        if ratio < 0.9 and dp.boost_act > 1900:
            low_maf += 1
            print(f"    [!] RPM={dp.rpm:.0f}: MAF req={dp.maf_req:.0f}, act={dp.maf_actual:.0f} (stosunek {ratio*100:.1f}%) - MAF zaniza!")
if low_maf == 0:
    print("    [OK] MAF mierzy poprawnie w zakresie WOT.")

# 12. ANALIZA SOI
print(f"\n[12] ANALIZA KATA WTRYSKU (SOI):")
lag_count = 0
for dp in wot:
    if dp.soi_req > 0 and dp.soi_act > 0:
        delta = dp.soi_req - dp.soi_act
        if delta > 1.5:
            lag_count += 1
            print(f"    [!] RPM={dp.rpm:.0f}: SOI req={dp.soi_req:.1f}, act={dp.soi_act:.1f} (lag {delta:.1f}) - wtrysk opozniony!")
if lag_count == 0:
    print("    [OK] Kat wtrysku nadaza za mapa.")

# 13. WYKRESY
print(f"\n[13] GENEROWANIE WYKRESOW...")
plot_advanced_diagnostics(vcds, OUTPUT_DIR)
print(f"    Wykresy zapisane w: {OUTPUT_DIR}")

# 14. AUTO-TUNE (symulacja)
print(f"\n[14] AUTO-TUNE (symulacja korekt na podstawie logow):")
res = analyzer.run_autotune_all(codeblock=5)
if res["total_changes"] > 0:
    print(f"    Zaproponowano {res['total_changes']} korekt w mapach: {', '.join(res['modified_maps'].keys())}")
    for log_entry in res["changes_log"][:20]:
        print(f"    {log_entry}")
    if len(res["changes_log"]) > 20:
        print(f"    ... i {len(res['changes_log']) - 20} innych korekt.")
else:
    print("    Brak wymaganych korekt na podstawie logow.")

print("\n" + "=" * 90)
print("  OCENA ZAKONCZONA")
print("=" * 90)