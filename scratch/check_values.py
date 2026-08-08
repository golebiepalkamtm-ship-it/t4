"""
Szczegolowy odczyt wszystkich wartosci map z pliku BIN EDC15
Plik: d:\t4\cks ok
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

BIN_FILE = r"d:\t4\cks ok"
ecu = ECUBinaryReader(BIN_FILE)

# Osie RPM dla większości map (16 kolumn)
RPM_AXIS_16 = [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500]
RPM_AXIS_23 = [600,700,800,900,1000,1100,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500,4750,5000,5250]

PEDAL_AXIS   = [0, 10, 20, 30, 40, 50, 60, 70, 80]           # Driver Wish Y
LOAD_AXIS_10 = [0,8,17,25,34,42,51,59,67,76]                  # Boost Y (10 wierszy)
LOAD_AXIS_13 = [0,8,17,25,34,42,51,59,67,76,84,93,101]        # Smoke/N75/SOI/EGR/PUMP (13 wierszy)
LOAD_AXIS_14 = [0,8,17,25,34,42,51,59,67,76,84,93,101,109]    # SOI/PUMP (14 wierszy)
ATMOS_AXIS_3 = [750,1013,1100]                                 # Torque Limiter Y (3 wiersze)

Y_AXES = {
    "driver_wish":       PEDAL_AXIS,
    "torque_limiter":    ATMOS_AXIS_3,
    "smoke_limiter_0c":  LOAD_AXIS_13,
    "smoke_limiter_15c": LOAD_AXIS_13,
    "smoke_limiter_30c": LOAD_AXIS_13,
    "boost_target":      LOAD_AXIS_10,
    "boost_limiter":     LOAD_AXIS_10,
    "n75_duty":          LOAD_AXIS_13,
    "soi_map":           LOAD_AXIS_14,
    "egr":               LOAD_AXIS_13,
    "pump_voltage":      LOAD_AXIS_14,
    "maf_linearization": None,
}

X_AXES = {
    "torque_limiter": RPM_AXIS_23,
}

SEP = "─" * 120

for key, md in MAP_DEFINITIONS.items():
    matrix = ecu.read_map(md, codeblock=5)
    all_vals = [v for row in matrix for v in row]
    vmin, vmax, vmean = min(all_vals), max(all_vals), sum(all_vals)/len(all_vals)

    # Flaga problemów
    flags = []
    if key == "boost_target" and vmax > 2200:
        flags.append("[CRITICAL] BOOST ZA WYSOKI!")
    if key == "boost_limiter" and vmax > 2300:
        flags.append("[CRITICAL] LIMITER ZA WYSOKI!")
    if key == "pump_voltage" and vmax > 4.5:
        flags.append("[CRITICAL] NAPIECIE VP37 > 4.5V!")
    if key == "torque_limiter" and vmax > 55:
        flags.append("[WARNING] MOMENT WYSOKI (>55mg)")
    if key == "driver_wish" and vmax > 60:
        flags.append("[WARNING] DRIVER WISH WYSOKI")
    if key == "smoke_limiter_0c" and vmax > 60:
        flags.append("[WARNING] SMOKE LIMITER WYSOKI")

    flag_str = "  " + " ".join(flags) if flags else "  [OK]"

    print(f"\n{SEP}")
    print(f"  MAP: {md.name}  [{md.dimsport_code}]  @CB5={hex(md.addr_cb5)}  Rozmiar: {md.rows}x{md.cols}  Jednostka: {md.unit}")
    print(f"  Min={vmin}  Max={vmax}  Średnia={round(vmean,2)}{flag_str}")
    print(SEP)

    x_axis = X_AXES.get(key, RPM_AXIS_16)
    y_axis = Y_AXES.get(key)

    # Nagłówek osi X
    if md.rows > 1:
        if x_axis and len(x_axis) >= md.cols:
            header = f"{'Y\\RPM':>8} | " + " ".join(f"{v:>7}" for v in x_axis[:md.cols])
        else:
            header = f"{'Y\\COL':>8} | " + " ".join(f"{c:>7}" for c in range(md.cols))
        print(header)
        print("─" * len(header))

    for r, row in enumerate(matrix):
        if md.rows > 1 and y_axis and r < len(y_axis):
            row_label = f"{y_axis[r]:>8}"
        elif md.rows > 1:
            row_label = f"{'Row'+str(r):>8}"
        else:
            row_label = f"{'':>8}"

        vals_str = " ".join(f"{v:>7}" for v in row)
        if md.rows > 1:
            print(f"{row_label} | {vals_str}")
        else:
            # 1D — drukuj parami (MAF linearization 32 punkty)
            for i in range(0, len(row), 8):
                chunk = row[i:i+8]
                print(f"  [{i:02d}-{i+len(chunk)-1:02d}]: " + "  ".join(f"{v:>8}" for v in chunk))

print(f"\n{SEP}")
print("  KONIEC AUDYTU — Plik: d:\\t4\\cks ok")
print(SEP)
