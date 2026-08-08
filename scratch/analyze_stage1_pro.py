import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")

from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

path_orig = r"d:\t4\cks ok"
path_pro  = r"d:\t4\cks ok_stage1_pro.bin"

ecu_orig = ECUBinaryReader(path_orig)
ecu_pro  = ECUBinaryReader(path_pro)

print("=== ANALIZA PORÓWNAWCZA: cks ok (Stary Stage 1) VS cks ok_stage1_pro.bin (Stage 1 Pro) ===")

print("\n--- 1. NAGŁÓWEK IRZESYŃ ECU ---")
print("  Oryginał:", ecu_orig.header_info)
print("  Stage 1 Pro:", ecu_pro.header_info)

print("\n--- 2. PORÓWNAWCZE STATYSTYKI MAP (CODEBLOCK 5 & CODEBLOCK 2) ---")
print(f"  {'Nazwa Mapy':<35} | {'Stary Max':<10} | {'Pro Max':<10} | {'Delta':<10} | Status")
print("  " + "-" * 85)

HW_LIMITS = {
    "driver_wish":       65.0,
    "torque_limiter":    56.0,
    "smoke_limiter_0c":  62.0,
    "smoke_limiter_15c": 62.0,
    "smoke_limiter_30c": 62.0,
    "boost_target":      2400.0,
    "boost_limiter":     2500.0,
    "pump_voltage":      4.45,
}

for key, md in MAP_DEFINITIONS.items():
    orig_sum = ecu_orig.get_map_summary(md, codeblock=5)
    pro_sum  = ecu_pro.get_map_summary(md, codeblock=5)
    
    o_max = orig_sum['max']
    p_max = pro_sum['max']
    diff = round(p_max - o_max, 2)
    
    limit = HW_LIMITS.get(key, 999999)
    if p_max > limit:
        status = "⚠️ PRZEKROCZONY LIMIT!"
    elif p_max == limit:
        status = "🎯 NA MAX LIMICIE"
    elif diff > 0:
        status = f"▲ +{diff}"
    elif diff < 0:
        status = f"▼ {diff}"
    else:
        status = "= Bez zmian"
        
    print(f"  {md.name[:35]:<35} | {o_max:<10} | {p_max:<10} | {diff:<+10} | {status}")

print("\n--- 3. DETEKCJA ZMIAN BINARNYCH BAJT PO BAJCIE ---")
diff_bytes = [i for i in range(len(ecu_orig.data)) if ecu_orig.data[i] != ecu_pro.data[i]]
print(f"Liczba zmodyfikowanych bajtów: {len(diff_bytes)} z {len(ecu_orig.data)} bajtów ({len(diff_bytes)/len(ecu_orig.data)*100:.2f}%)")

# Wyciągamy zakresy zmienionych adresów
if diff_bytes:
    blocks = []
    b_start = diff_bytes[0]
    b_end = diff_bytes[0]
    for d in diff_bytes[1:]:
        if d <= b_end + 4:
            b_end = d
        else:
            blocks.append((b_start, b_end))
            b_start = d
            b_end = d
    blocks.append((b_start, b_end))
    
    print(f"Wszystkich złączonych bloków zmian: {len(blocks)}")
    for b_s, b_e in blocks:
        sz = b_e - b_s + 1
        print(f"  * Bloku adresów [0x{b_s:05X} - 0x{b_e:05X}] ({sz} bajtów / {sz//2} słów 16-bit)")
