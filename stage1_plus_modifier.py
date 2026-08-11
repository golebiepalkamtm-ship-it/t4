"""
================================================================================
  EDC15VM+ Stage 1+ Max Stock Modifier — VW T4 2.5 TDI AXG (074906018AJ)
  
  Modyfikuje 'cks ok' -> 'stage1_plus.bin' (bez tykania obszarow CKS/system)
  Cel: ~185-190KM, 410Nm, max paliwo 60mg, max boost 1.35 bar, poprawa spoola.
================================================================================
"""

import struct
import os
import sys

INPUT_FILE = "cks ok.bin" # The original binary name from earlier, I should check the exact name, let me use "cks ok" instead of "cks ok.bin" if that's what was listed, but earlier the user said "cks ok" is the file name. Wait, the `ls` showed "cks ok". Let's assume it's just "cks ok" and if not, we handle it.

def read_u16(buf, addr):
    return struct.unpack('<H', buf[addr:addr+2])[0]

def write_u16(buf, addr, val):
    val = max(0, min(65535, int(round(val))))
    struct.pack_into('<H', buf, addr, val)

def read_map(buf, addr, rows, cols, factor=0.01):
    matrix = []
    for r in range(rows):
        row = []
        for c in range(cols):
            raw = read_u16(buf, addr + (r * cols + c) * 2)
            row.append(round(raw * factor, 3))
        matrix.append(row)
    return matrix

def write_map(buf, addr, rows, cols, matrix, factor=0.01):
    for r in range(rows):
        for c in range(cols):
            raw_val = int(round(matrix[r][c] / factor))
            write_u16(buf, addr + (r * cols + c) * 2, raw_val)

# Map addresses (Codeblock 5)
ADDR_DRIVER_WISH    = 0x4CC36
ADDR_TORQUE_LIMITER = 0x4D2FE
ADDR_SMOKE_0C       = 0x4D61C
ADDR_SMOKE_15C      = 0x4D7BC
ADDR_SMOKE_30C      = 0x4D95C
ADDR_PUMP_VOLTAGE   = 0x54468
ADDR_BOOST_TARGET   = 0x56546
ADDR_BOOST_LIMITER  = 0x56B3C
ADDR_N75_DUTY       = 0x56852
ADDR_SOI            = 0x58FBC

def modify_torque_limiter(buf, base_addr):
    print("[1/9] Modyfikacja Torque Limiter (60.0 mg)...")
    tl = read_map(buf, base_addr, 3, 23, 0.01)
    new_row2 = [0.0, 25.0, 29.0, 30.0, 32.0, 44.0, 50.0, 56.0, 58.5, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 59.5, 58.0, 56.0, 54.0, 48.0, 36.0, 16.0, 0.0]
    new_row1 = [0.0, 25.0, 29.0, 29.0, 30.0, 36.0, 41.0, 46.0, 48.5, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 49.5, 48.0, 46.5, 45.0, 40.0, 29.0, 16.0, 0.0]
    new_row0 = [0.0, 25.0, 29.0, 28.0, 28.0, 34.0, 38.0, 42.0, 43.5, 45.0, 45.0, 45.0, 45.0, 45.0, 45.0, 44.5, 43.0, 42.5, 41.0, 36.0, 26.0, 16.0, 0.0]
    tl[0] = new_row0
    tl[1] = new_row1
    tl[2] = new_row2
    write_map(buf, base_addr, 3, 23, tl, 0.01)

def modify_driver_wish(buf, base_addr):
    print("[2/9] Modyfikacja Driver Wish (60.0 mg, agresywniejszy pedal)...")
    dw = read_map(buf, base_addr, 9, 16, 0.01)
    for r in range(9):
        for c in range(16):
            val = dw[r][c]
            if val >= 50.0: dw[r][c] = 60.0
            elif val >= 40.0: dw[r][c] = 55.0
            elif val >= 30.0: dw[r][c] = 42.0
            elif val >= 20.0: dw[r][c] = 28.0
            elif val >= 10.0: dw[r][c] = 16.0
            dw[r][c] = min(60.0, dw[r][c])
    write_map(buf, base_addr, 9, 16, dw, 0.01)

def modify_smoke_limiter(buf, base_addr, temp_label):
    print(f"[3/9] Modyfikacja Smoke Limiter {temp_label} (60.0 mg)...")
    sl = read_map(buf, base_addr, 13, 16, 0.01)
    boost_amounts = {0: 5.0, 1: 6.0, 2: 5.0, 3: 4.0}
    for row_idx, boost in boost_amounts.items():
        old_max = max(sl[row_idx])
        new_cap = min(old_max + boost, 55.0)
        for c in range(16):
            old_val = sl[row_idx][c]
            if old_val >= old_max * 0.85:
                sl[row_idx][c] = min(old_val + boost, new_cap)
            elif old_val >= old_max * 0.7:
                sl[row_idx][c] = min(old_val + boost * 0.7, new_cap)
    for row_idx in range(8, 13):
        old_max = max(sl[row_idx])
        for c in range(16):
            old_val = sl[row_idx][c]
            if old_val >= old_max * 0.9:
                sl[row_idx][c] = min(old_val + 6.0, 60.0)
    write_map(buf, base_addr, 13, 16, sl, 0.01)

def modify_boost_target(buf, base_addr):
    print("[4/9] Modyfikacja Boost Target (2350 mBar)...")
    bt = read_map(buf, base_addr, 10, 16, 1.0)
    boost_additions = {
        (4, 2): 60, (4, 3): 100, (4, 4): 130, (4, 5): 130,
        (5, 2): 70, (5, 3): 120, (5, 4): 150, (5, 5): 150,
        (6, 2): 110, (6, 3): 140, (6, 4): 170, (6, 5): 140,
        (7, 2): 110, (7, 3): 140, (7, 4): 170, (7, 5): 140,
        (8, 2): 110, (8, 3): 150, (8, 4): 180, (8, 5): 160,
        (9, 2): 110, (9, 3): 150, (9, 4): 190, (9, 5): 160,
    }
    for (r, c), add_mbar in boost_additions.items():
        bt[r][c] = min(bt[r][c] + add_mbar, 2350)
    for r in [8, 9]:
        for c in range(6, 12):
            if bt[r][c] < 2350:
                bt[r][c] = min(bt[r][c] + 80, 2350)
    write_map(buf, base_addr, 10, 16, bt, 1.0)

def modify_iq_limiters(buf, offset_cb=0):
    print("[9/9] Odblokowanie Limitow Diagnostycznych VCDS (70mg)...")
    known_blocks = [(0x4C7F4, 0x4C80A), (0x4C94E, 0x4C950), (0x4E1EE, 0x4E1F0), (0x4E22A, 0x4E22C), (0x52434, 0x52450), (0x52668, 0x5266A), (0x52AE6, 0x52AE8), (0x54446, 0x54448), (0x549E2, 0x549E4), (0x54BB4, 0x54BB6), (0x55270, 0x55272), (0x55452, 0x55454), (0x55470, 0x55472)]
    for (start, end) in known_blocks:
        for addr in range(start + offset_cb, end + offset_cb, 2):
            if read_u16(buf, addr) == 5100:
                write_u16(buf, addr, 7000)

def modify_boost_limiter(buf, base_addr):
    print("[5/9] Odblokowanie Boost Limiter (2400 mBar)...")
    bl = read_map(buf, base_addr, 10, 10, 1.0)
    for r in range(4, 10):
        for c in range(10):
            if bl[r][c] >= 2190:
                bl[r][c] = 2400
            elif bl[r][c] >= 2000:
                bl[r][c] = 2250
    write_map(buf, base_addr, 10, 10, bl, 1.0)

def modify_n75(buf, base_addr):
    print("[6/9] Modyfikacja N75 Precontrol (eliminacja turbo-dziury)...")
    n75 = read_map(buf, base_addr, 13, 16, 0.01)
    for r in range(4, 13):
        for c in range(2, 6):
            old_val = n75[r][c]
            reduction = min(4.5 + (r - 4) * 0.5, 7.5)
            new_val = max(old_val - reduction, 35.0)
            if old_val != new_val:
                n75[r][c] = new_val
    write_map(buf, base_addr, 13, 16, n75, 0.01)

def modify_soi(buf, base_addr):
    print("[7/9] Korekta SOI pod 60mg...")
    soi = read_map(buf, base_addr, 14, 16, 0.01)
    for r in range(8, 14):
        for c in range(2, 6):
            soi[r][c] = max(soi[r][c] - 0.5, 4.0)
        for c in range(9, 14):
            soi[r][c] = min(soi[r][c] + 0.5, 16.5)
    write_map(buf, base_addr, 14, 16, soi, 0.01)

def modify_pump_voltage(buf, base_addr):
    print("[8/9] Optymalizacja Napiecia Pompy (dla 60mg na seryjnych wtryskach)...")
    pv = read_map(buf, base_addr, 14, 16, 0.00122)
    for r in range(8, 14):
        pv[r][14] = min(pv[r][14] + 0.150, 4.60)
        pv[r][15] = min(pv[r][15] + 0.280, 4.65)
    write_map(buf, base_addr, 14, 16, pv, 0.00122)

def modify_all_maps(buf, offset_cb=0):
    modify_torque_limiter(buf, ADDR_TORQUE_LIMITER + offset_cb)
    modify_driver_wish(buf, ADDR_DRIVER_WISH + offset_cb)
    modify_smoke_limiter(buf, ADDR_SMOKE_30C + offset_cb, "30C")
    modify_smoke_limiter(buf, ADDR_SMOKE_15C + offset_cb, "15C")
    modify_smoke_limiter(buf, ADDR_SMOKE_0C + offset_cb, "0C")
    modify_boost_target(buf, ADDR_BOOST_TARGET + offset_cb)
    modify_boost_limiter(buf, ADDR_BOOST_LIMITER + offset_cb)
    modify_n75(buf, ADDR_N75_DUTY + offset_cb)
    modify_soi(buf, ADDR_SOI + offset_cb)
    modify_pump_voltage(buf, ADDR_PUMP_VOLTAGE + offset_cb)
    modify_iq_limiters(buf, offset_cb)

def main():
    input_f = "cks ok"
    if not os.path.exists(input_f):
        # Fallback to cks ok.bin if needed
        if os.path.exists("cks ok.bin"):
            input_f = "cks ok.bin"
        else:
            print("BLAD: Plik zrodlowy nie istnieje!")
            sys.exit(1)
            
    with open(input_f, 'rb') as f:
        buf = bytearray(f.read())
        
    print("\n--- MODYFIKACJE CODEBLOCK 5 ---")
    modify_all_maps(buf, offset_cb=0)
    
    print("\n--- MODYFIKACJE CODEBLOCK 2 ---")
    modify_all_maps(buf, offset_cb=0x20000)
    
    with open("stage1_plus.bin", 'wb') as f:
        f.write(buf)
    
    print("\n[SUKCES] Wygenerowano plik: stage1_plus.bin (bez liczenia CKS - zrob to w LSuite!)")

if __name__ == "__main__":
    main()
