"""
EDC15VM+ PROFESJONALNY STAGE 1 REMAP — VW T4 2.5 TDI AXG (151hp)
Cel: Maksymalna moc ze stock turbo KKK K14 / GT1749 + VP37

METODA: Skalowanie procentowe map — zachowujemy KSZTALT mapy, podnosimy proporcjonalnie.
Nie robimy plaskich wartosci — mapa musi wygladac jak profesjonalna robota.

Baza:     d:\t4\cks ok  (aktualny plik w aucie)
Wyjscie:  d:\t4\cks ok_stage1_pro.bin

ZMIANY:
  Driver Wish (B1):    +10% skalowanie (wiecej zyczenia kierowcy)
  Torque Limiter (LC): +5%  (ostroznisejsze, chroni DMF)
  Smoke Limiter (QS):  +8%  (proporcjonalne do boostu)
  Boost Target (BS):   +5%  z max cap 2100 mBar (stock turbo bezpieczne)
  Boost Limiter (BL):  +5%  z max cap 2200 mBar
  Pump Voltage (PUMP): +4%  tylko komorki > 3.0V (high load WOT)
  SOI / N75 / EGR:     bez zmian

Limity absolutne (nigdy nie przekraczamy):
  Boost:  2100 mBar
  Pump:   4.45 V
  Driver: 65 mg/hub
  Torque: 56 mg/hub
  Smoke:  62 mg/hub
"""

import sys, copy
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

INPUT_BIN  = r"d:\t4\cks ok"
OUTPUT_BIN = r"d:\t4\cks ok_stage1_pro.bin"

ecu = ECUBinaryReader(INPUT_BIN)

# ─── DEFINICJA REMAPOW ───────────────────────────────────────────────────────
# format: (scale_percent, abs_max, min_threshold_to_scale)
# scale_percent       = o ile % podnosimy wartosci
# abs_max             = absolutny limit (nigdy nie przekraczamy)
# min_threshold       = skaluj tylko jesli wartosc >= tego (0 = skaluj wszystko)
REMAPS = {
    "driver_wish":       (10.0,  65.0,  1.0),   # +10%, max 65 mg/hub
    "torque_limiter":    (5.0,   56.0,  1.0),   # +5%,  max 56 mg/hub
    "smoke_limiter_0c":  (8.0,   62.0,  5.0),   # +8%,  max 62 mg/hub
    "smoke_limiter_15c": (8.0,   62.0,  5.0),
    "smoke_limiter_30c": (8.0,   62.0,  5.0),
    "boost_target":      (5.0,   2400.0, 1400.0), # +5%, cap 2400 — NIE obniżamy 2190!
    "boost_limiter":     (3.0,   2500.0, 1500.0), # +3%, cap 2500
    "pump_voltage":      (4.0,   4.45,  3.0),   # +4% tylko komorki WOT (>3.0V)
}

SEP = "=" * 100
sep = "-" * 100

print(f"\n{SEP}")
print(f"  EDC15VM+ STAGE 1 PRO REMAP — VW T4 2.5 TDI AXG (151hp -> ~175hp)")
print(f"  Wejscie: {INPUT_BIN}")
print(f"  Wyjscie: {OUTPUT_BIN}")
print(f"{SEP}\n")

total_cells = 0

for key, md in MAP_DEFINITIONS.items():
    if key not in REMAPS:
        continue

    scale_pct, abs_max, min_thresh = REMAPS[key]
    scale_factor = 1.0 + (scale_pct / 100.0)

    matrix_orig = ecu.read_map(md, codeblock=5)
    matrix_new  = copy.deepcopy(matrix_orig)
    changed = []

    for r in range(md.rows):
        for c in range(md.cols):
            v = matrix_orig[r][c]

            # Pomijamy komorki ponizej progu (np. biegi jalowe, low load)
            if v < min_thresh:
                continue

            v_new = round(v * scale_factor, 3)

            # Absolutny cap
            if v_new > abs_max:
                v_new = abs_max

            if abs(v_new - v) > 0.001:
                changed.append((r, c, v, v_new))
                matrix_new[r][c] = v_new

    orig_vals = [v for row in matrix_orig for v in row if v >= min_thresh]
    new_vals  = [matrix_new[r][c] for r in range(md.rows) for c in range(md.cols) if matrix_orig[r][c] >= min_thresh]

    print(f"{sep}")
    print(f"  MAPA: {md.name}  [{md.dimsport_code}]  Skalowanie: +{scale_pct}%  Abs.max: {abs_max} {md.unit}")

    if changed:
        total_cells += len(changed)
        print(f"  Przed: min={min(orig_vals):.3f}  max={max(orig_vals):.3f}  {md.unit}")
        print(f"  Po:    min={min(new_vals):.3f}  max={max(new_vals):.3f}  {md.unit}")
        print(f"  Zmienionych komorek: {len(changed)} / {md.rows*md.cols}")

        # Pokaz tylko pierwsze i ostatnie zmiany
        show = changed[:8] + (changed[-4:] if len(changed) > 12 else [])
        if len(changed) > 12:
            print(f"\n  {'R':>4} {'C':>4} {'Stara':>10} {'Nowa':>10} {'Delta':>10}")
            print(f"  {'-'*4} {'-'*4} {'-'*10} {'-'*10} {'-'*10}")
            for i, (r, c, v_o, v_n) in enumerate(show):
                if i == 8:
                    print(f"  ... ({len(changed)-12} wiecej) ...")
                print(f"  {r:>4} {c:>4} {v_o:>10.3f} {v_n:>10.3f} {v_n-v_o:>+10.3f}  {md.unit}")
        else:
            print(f"\n  {'R':>4} {'C':>4} {'Stara':>10} {'Nowa':>10} {'Delta':>10}")
            for r, c, v_o, v_n in changed:
                print(f"  {r:>4} {c:>4} {v_o:>10.3f} {v_n:>10.3f} {v_n-v_o:>+10.3f}  {md.unit}")

        ecu.write_map(md, matrix_new, codeblock=5)
        ecu.write_map(md, matrix_new, codeblock=2)
    else:
        print(f"  [INFO] Brak zmian (wszystkie wartosci juz na lub powyzej abs_max={abs_max})")

    print()

print(f"{SEP}")
print(f"  PODSUMOWANIE STAGE 1 PRO:")
print(f"  Lacznie zmodyfikowanych komorek: {total_cells}")
print()
print(f"  Spodziewany wynik (szacunek):")
print(f"    Moc:    ~151hp  ->  ~172-180hp")
print(f"    Moment: ~295Nm  ->  ~350-370Nm")
print(f"    Boost:  max 2190mBar -> max 2100mBar (bezpieczny cap stock turbo)")
print(f"    Pompa:  max 4.377V  -> max 4.45V (WOT cells only)")
print(f"{SEP}\n")

ecu.save_bin(OUTPUT_BIN)
print(f"  [SUKCES] Zapisano profesjonalny Stage 1: {OUTPUT_BIN}")
print(f"  [UWAGA]  WYMAGANE przeliczenie sumy kontrolnej przed wgraniem!")
print(f"           Narzedzia: WinOLS, TunerPro RT, lub ECM Titanium")
print()
