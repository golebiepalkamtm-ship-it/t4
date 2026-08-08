import sys
import os

sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, VCDSLogParser, EDC15Analyzer, MAP_DEFINITIONS, VCDSDataPoint

BIN_PATH = r"d:\t4\cks ok"
ecu = ECUBinaryReader(BIN_PATH)

print("Loaded ECU:", ecu.header_info)

# Test z podwójną osia dla N75
RPM_AXIS_16 = [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500]
LOAD_AXIS_13 = [0, 8, 17, 25, 34, 42, 51, 59, 67, 76, 84, 93, 101]

# Symulacja danych z logów VCDS (np. przładowanie przy 2000-2500 RPM)
mock_dps = []
for rpm in range(1500, 4000, 250):
    dp = VCDSDataPoint(
        timestamp=1.0,
        rpm=float(rpm),
        iq_actual=45.0,
        boost_req=2050.0,
        boost_act=2220.0 if 1800 <= rpm <= 2700 else 2060.0, # przeładowanie +170 mbar
        n75_duty=65.0,
        maf_actual=950.0,
        maf_req=850.0,
        soi_req=16.0,
        soi_act=14.5 if 2000 <= rpm <= 3000 else 16.0, # opóźnienie o 1.5°
        pump_voltage=4.1,
        iq_driver=55.0,
        iq_torque=48.0,
        iq_smoke=44.0
    )
    mock_dps.append(dp)

print(f"Wygenerowano {len(mock_dps)} punktów logów do testu.")

def calculate_n75_autotune(ecu, map_def, dps):
    current_matrix = ecu.read_map(map_def, codeblock=5)
    new_matrix = [row[:] for row in current_matrix]
    changes_count = 0

    for dp in dps:
        if dp.rpm < 1400 or dp.boost_req < 1500:
            continue
        
        delta_boost = dp.boost_act - dp.boost_req  # dodatnie = przeładowanie (spike), ujemne = lag
        
        # Znajdź najbliższą kolumnę (RPM)
        col_idx = min(range(len(RPM_AXIS_16)), key=lambda i: abs(RPM_AXIS_16[i] - dp.rpm))
        # Znajdź najbliższy wiersz (IQ)
        row_idx = min(range(len(LOAD_AXIS_13)), key=lambda j: abs(LOAD_AXIS_13[j] - dp.iq_actual))

        if abs(delta_boost) > 40.0:  # powyżej 40 mbar różnicy
            # Przepisy N75: jeśli spike (+boost), zwiększ N75 % (otwórz kierownice)
            # jeśli lag (-boost), zmniejsz N75 % (zamknij kierownice)
            adj = (delta_boost / 25.0)  # np. +170 mbar -> +6.8%
            adj = max(-10.0, min(10.0, adj))
            
            old_val = new_matrix[row_idx][col_idx]
            new_val = round(max(10.0, min(95.0, old_val + adj)), 2)
            
            if old_val != new_val:
                new_matrix[row_idx][col_idx] = new_val
                changes_count += 1
                print(f"RPM={dp.rpm:.0f}, IQ={dp.iq_actual:.1f}mg | Boost req={dp.boost_req:.0f}, act={dp.boost_act:.0f} (Delta={delta_boost:+.0f}mbar) => N75 cell [{row_idx}][{col_idx}]: {old_val}% -> {new_val}%")

    return new_matrix, changes_count

new_n75, n_changes = calculate_n75_autotune(ecu, MAP_DEFINITIONS["n75_duty"], mock_dps)
print(f"Wynik N75 Auto-Tune: dokonano {n_changes} korekt w mapie N75.")
