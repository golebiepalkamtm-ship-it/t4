ZELNOC IDELNAimport sys
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, VCDSLogParser, MAP_DEFINITIONS

vcds = VCDSLogParser([
    r"d:\t4\LOG-01-002-004-008.CSV",
    r"d:\t4\LOG-01-003-005-002.CSV",
    r"d:\t4\LOG-01-011-010-009.CSV",
    r"d:\t4\LOG-01-023-019-010.CSV",
])
ecu = ECUBinaryReader(r"d:\t4\cks ok")
egr = ecu.read_map(MAP_DEFINITIONS["egr"], codeblock=5)
n75 = ecu.read_map(MAP_DEFINITIONS["n75_duty"], codeblock=5)

print("=" * 80)
print("  DIAGNOSTYKA: Dymienie na wolnych + brak reakcji z dolu")
print("=" * 80)

print("\n[1] MAF i EGR przy niskich RPM (1300-2200):")
print("    RPM  | MAF req | MAF act | Ratio  | EGR duty")
print("    " + "-" * 60)
for dp in vcds.data_points:
    if dp.rpm > 2200 or dp.rpm < 1300:
        continue
    if dp.maf_req > 0 or dp.egr_duty > 0:
        ratio = (dp.maf_actual / dp.maf_req * 100) if dp.maf_req > 0 else 0
        print(f"    {dp.rpm:>4.0f} | {dp.maf_req:>7.0f} | {dp.maf_actual:>7.0f} | {ratio:>5.1f}% | {dp.egr_duty:>8.1f}%")

print("\n[2] Smoke Limiter tnie dawke przy niskich RPM:")
print("    RPM  | IQ Drv | IQ Trq | IQ Smk | Aktywny limiter")
print("    " + "-" * 60)
for dp in vcds.data_points:
    if dp.rpm > 2200 or dp.rpm < 1300:
        continue
    if dp.iq_driver > 30:
        iqs = {"DRV": dp.iq_driver, "TRQ": dp.iq_torque, "SMK": dp.iq_smoke}
        if all(v > 0 for v in iqs.values()):
            active = min(iqs, key=iqs.get)
            print(f"    {dp.rpm:>4.0f} | {dp.iq_driver:>6.1f} | {dp.iq_torque:>6.1f} | {dp.iq_smoke:>6.1f} | <- {active}")

print(f"\n[3] MAPA EGR (cks ok):")
print(f"    Wartosc: {egr[0][0]:.1f}% (flat - wszystkie komorki)")
if egr[0][0] > 50:
    print(f"    [!] KRYTYCZNE: EGR = {egr[0][0]:.0f}% - to NIE jest EGR off!")
    print(f"        85% duty = zawor EGR OTWARTY = maksymalny EGR!")
    print(f"        Aby wylaczyc EGR -> ustawic mape na 0%")

print(f"\n[4] MAPA N75 przy niskich RPM:")
print(f"    RPM 1500, IQ=0:  N75 = {n75[0][3]:.1f}%")
print(f"    RPM 1500, IQ=5:  N75 = {n75[1][3]:.1f}%")
print(f"    RPM 1500, IQ=15: N75 = {n75[3][3]:.1f}%")
print(f"    RPM 1750, IQ=0:  N75 = {n75[0][4]:.1f}%")
print(f"    RPM 1750, IQ=15: N75 = {n75[3][4]:.1f}%")

print(f"\n[5] BOOST DEVIATION przy niskich RPM:")
print("    RPM  | Boost req | Boost act | Delta  | Ocena")
print("    " + "-" * 60)
for dp in vcds.data_points:
    if dp.rpm > 2200 or dp.rpm < 1300:
        continue
    if dp.boost_req > 1100:
        delta = dp.boost_act - dp.boost_req
        ocena = "LAG!" if delta < -100 else "OK"
        print(f"    {dp.rpm:>4.0f} | {dp.boost_req:>9.0f} | {dp.boost_act:>9.0f} | {delta:>+6.0f} | {ocena}")

print("\n" + "=" * 80)
print("  PODSUMOWANIE DIAGNOSTYKI")
print("=" * 80)
print("""
PROBLEM 1: Dymienie na czarno na wolnych obrotach
  - MAF actual (530 mg/suw) = tylko 54% MAF req (980 mg/suw)
  - EGR duty = 24.7-62.2% przy niskich RPM (EGR aktywny!)
  - Mapa EGR = 85% (flat) - to NIE jest EGR off, to 85% duty!
  - EGR otwarty = mniej swiezego powietrza = czarny dym

PROBLEM 2: Brak reakcji na gaz z dolu
  - Smoke Limiter aktywny przy 1489-1510 RPM
  - Tnie dawke z 51 mg (driver wish) na 30-44 mg
  - Powod: MAF za niski (530 vs 980) = ECU mysli ze nie ma powietrza
  - Boost lag: -122 do -194 mBar przy niskich RPM

LANCUCH PRZYCZYN:
  1. EGR mapa = 85% (NIE wylaczony!)
  2. EGR otwarty -> spaliny z powrotem do dolotu
  3. Mniej swiezego powietrza -> MAF czyta 530 zamiast 980
  4. Smoke Limiter widzi niski MAF -> tnie dawke z 51 na 30 mg
  5. Mniej paliwa -> brak reakcji na gaz
  6. EGR + malo powietrza -> czarny dym

ROZWIAZANIE:
  1. Ustawic mape EGR na 0% (prawdziwe wylaczenie EGR)
  2. Sprawdzic/przeczyscic przeplywomierz MAF (G70)
  3. Sprawdzic szczelnosc dolotu (boost leak)
  4. Sprawdzic zawor N75 i uklad podcisnienia
""")