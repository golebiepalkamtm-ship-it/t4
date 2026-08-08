"""
Porównanie profesjonalnych plików tuningowych:
  Original vs Stage 1 vs Stage 2 vs Stage 3 vs cks ok (Twój Stage 1)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

FILES = {
    "Original":  r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original",
    "Stage 1":   r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_A0FF.Stage1",
    "Stage 2":   r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_3D43.Stage2",
    "Stage 3":   r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_992F.Stage3",
    "cks ok":    r"d:\t4\cks ok",
}

MAPS_TO_CHECK = [
    "driver_wish",
    "torque_limiter",
    "smoke_limiter_0c",
    "smoke_limiter_15c",
    "smoke_limiter_30c",
    "boost_target",
    "boost_limiter",
    "n75_duty",
    "pump_voltage",
    "soi_map",
    "egr",
]

SEP = "=" * 140
sep = "-" * 140

print(f"\n{SEP}")
print(f"  POROWNANIE PROFESJONALNYCH PLIKOW TUNINGOWYCH — VW T4 2.5 TDI AXG 151KM")
print(f"  ECU: 074 906 018 AJ  |  Bosch 0281010461  |  EDC15VM+")
print(f"{SEP}\n")

# Wczytaj wszystkie pliki
ecus = {}
for name, path in FILES.items():
    try:
        ecus[name] = ECUBinaryReader(path)
    except Exception as e:
        print(f"  [BLAD] Nie mozna wczytac {name}: {e}")

# Tabela porownawcza
print(f"\n{sep}")
print(f"  {'MAPA':<45} ", end="")
for name in FILES:
    print(f"{'[' + name + ']':>16}", end="")
print()
print(f"  {'-'*45} ", end="")
for _ in FILES:
    print(f"{'─'*16}", end="")
print()

for map_key in MAPS_TO_CHECK:
    if map_key not in MAP_DEFINITIONS:
        continue
    md = MAP_DEFINITIONS[map_key]
    label = md.name[:44]
    print(f"  {label:<45} ", end="")
    
    for name in FILES:
        if name not in ecus:
            print(f"{'N/A':>16}", end="")
            continue
        try:
            matrix = ecus[name].read_map(md, codeblock=5)
            all_vals = [v for row in matrix for v in row]
            vmax = max(all_vals)
            
            unit = md.unit
            if "mbar" in unit.lower() or "mBar" in unit:
                print(f"{vmax:>13.0f} mb", end="")
            elif "V" in unit or "volt" in unit.lower():
                print(f"{vmax:>14.3f}V", end="")
            elif "%" in unit:
                print(f"{vmax:>14.1f}%", end="")
            else:
                print(f"{vmax:>13.2f} mg", end="")
        except Exception:
            print(f"{'ERR':>16}", end="")
    print()

# Szczegolowe porownanie kluczowych map
print(f"\n\n{SEP}")
print(f"  SZCZEGOLOWE POROWNANIE KLUCZOWYCH MAP (wartosci MAX)")
print(f"{SEP}\n")

for map_key in ["torque_limiter", "driver_wish", "smoke_limiter_0c", "boost_target", "pump_voltage"]:
    md = MAP_DEFINITIONS[map_key]
    print(f"\n{sep}")
    print(f"  {md.name}")
    print(sep)
    
    for name in FILES:
        if name not in ecus:
            continue
        matrix = ecus[name].read_map(md, codeblock=5)
        all_vals = [v for row in matrix for v in row]
        vmin = min(all_vals)
        vmax = max(all_vals)
        vmean = sum(all_vals) / len(all_vals)
        
        # Policz ile komorek rozni sie od Original
        if "Original" in ecus and name != "Original":
            orig_matrix = ecus["Original"].read_map(md, codeblock=5)
            orig_vals = [v for row in orig_matrix for v in row]
            diff_count = sum(1 for a, b in zip(all_vals, orig_vals) if abs(a - b) > 0.01)
            diff_pct = diff_count / len(all_vals) * 100
            diff_str = f"  ({diff_count} komorek zmieniono, {diff_pct:.0f}%)"
        else:
            diff_str = "  (BAZA)"
        
        print(f"    {name:>12}:  min={vmin:>8.2f}  max={vmax:>8.2f}  srednia={vmean:>8.2f}{diff_str}")

# Porownanie Torque Limiter wiersz po wierszu (tylko wiersz 1100 mbar - normalny)
print(f"\n\n{SEP}")
print(f"  TORQUE LIMITER — wiersz 1100 mbar (normalne cisnienie atmosferyczne)")
print(f"  RPM: 600  700  800  900 1000 1100 1250 1500 1750 2000 2250 2500 2750 3000 3250 3500 3750 4000 4250 4500 4750 5000 5250")
print(SEP)

for name in FILES:
    if name not in ecus:
        continue
    md = MAP_DEFINITIONS["torque_limiter"]
    matrix = ecus[name].read_map(md, codeblock=5)
    # Wiersz 2 (indeks 2) = 1100 mbar
    row = matrix[2] if len(matrix) > 2 else matrix[-1]
    vals_str = " ".join(f"{v:>4.0f}" for v in row)
    print(f"  {name:>12}: {vals_str}")

# Porownanie Boost Target - ostatni wiersz (max load)
print(f"\n\n{SEP}")
print(f"  BOOST TARGET — ostatni wiersz (max load)")
print(f"  RPM: 750 1000 1250 1500 1750 2000 2250 2500 2750 3000 3250 3500 3750 4000 4250 4500")
print(SEP)

for name in FILES:
    if name not in ecus:
        continue
    md = MAP_DEFINITIONS["boost_target"]
    matrix = ecus[name].read_map(md, codeblock=5)
    row = matrix[-1]  # ostatni wiersz = max load
    vals_str = " ".join(f"{v:>5.0f}" for v in row)
    print(f"  {name:>12}: {vals_str}")

print(f"\n{SEP}")
print(f"  KONIEC POROWNANIA")
print(SEP)
