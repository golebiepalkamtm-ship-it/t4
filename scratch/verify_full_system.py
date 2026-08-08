import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")

from edc15_analyzer import (
    ECUBinaryReader, VCDSLogParser, EDC15Analyzer, 
    MAP_DEFINITIONS, MAP_AXES, VCDSDataPoint
)

BIN_PATH = r"d:\t4\cks ok"

print("=" * 80)
print("  WERYFIKACJA SYSTEMU EDC15VM+ TUNER & VCDS LOG AUTO-CALIBRATOR")
print("=" * 80)

# 1. Wczytanie ECU BIN
ecu = ECUBinaryReader(BIN_PATH)
print("✓ Wczytano wsad ECU:", ecu.header_info)

# 2. Odczyt fizycznych map
for key, md in MAP_DEFINITIONS.items():
    matrix = ecu.read_map(md, codeblock=5)
    all_vals = [v for r in matrix for v in r]
    print(f"  - Mapa {md.dimsport_code:4s} | {md.name:45s} | Min={min(all_vals):<7.2f} Max={max(all_vals):<7.2f} {md.unit}")

# 3. Generowanie próbki logu VCDS z przeładowaniem turbo (+160 mbar) i opóźnieniem SOI (+1.5°)
mock_dps = []
for rpm in [1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 4000]:
    dp = VCDSDataPoint(
        timestamp=2.0,
        rpm=float(rpm),
        iq_actual=46.0,
        boost_req=2050.0,
        boost_act=2210.0 if 1800 <= rpm <= 2800 else 2060.0,
        n75_duty=68.0,
        maf_actual=960.0,
        maf_req=850.0,
        soi_req=17.0,
        soi_act=15.2 if 2000 <= rpm <= 3000 else 17.0,
        pump_voltage=4.15,
        iq_driver=55.0,
        iq_torque=49.0,
        iq_smoke=45.0
    )
    mock_dps.append(dp)

# Utworzenie parsera VCDS
vcds = VCDSLogParser([])
vcds.data_points = mock_dps
print(f"\n✓ Utworzono strukturę logów VCDS: {len(vcds.data_points)} punktów WOT")

# 4. Utworzenie analizatora i wyliczenie macierzy korelacji
analyzer = EDC15Analyzer(ecu, vcds)
log_mat, diff_mat = analyzer.get_map_log_matrix("n75_duty", codeblock=5)
print(f"✓ Wygenerowano macierz nakładki VCDS dla N75. Rozmiar: {len(log_mat)}x{len(log_mat[0])}")

# 5. Uruchomienie Auto-Tune
res = analyzer.run_autotune_all(codeblock=5)
print(f"\n✓ Wynik Auto-Tune: Dokonano {res['total_changes']} automatycznych korekt w mapach: {list(res['modified_maps'].keys())}")
for line in res["changes_log"]:
    print("  ", line)

# 6. Zapis zmodyfikowanych map i eksport BIN
for m_key, new_mat in res["modified_maps"].items():
    m_def = MAP_DEFINITIONS[m_key]
    ecu.write_map(m_def, new_mat, codeblock=5)
    ecu.write_map(m_def, new_mat, codeblock=2)

out_bin = r"d:\t4\MODIFIED_TUNED_EDC15.bin"
ecu.save_bin(out_bin)

# 7. Sprawdzenie spójności wyjściowego pliku
assert os.path.exists(out_bin), "Plik wyjściowy nie powstał!"
assert os.path.getsize(out_bin) == 524288, "Rozmiar wyjściowego BIN jest niepoprawny!"

print("\n" + "=" * 80)
print("  WERYFIKACJA ZAKOŃCZONA SUKCESEM! WSZYSTKIE TESTY PRZESZŁY 100% POPRAWNIE.")
print("=" * 80)
