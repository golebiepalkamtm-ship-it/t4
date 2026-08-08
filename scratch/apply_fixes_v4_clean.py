"""
FIX SCRIPT v4 - Final Clean (Addresses fixed, EGR off)
"""
import struct
import sys
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import MAP_DEFINITIONS

BIN_IN   = r"d:\t4\cks ok"
BIN_OUT  = r"d:\t4\cks ok_fixed_v4.bin"

SM_RPM = [780, 1000, 1250, 1500, 1750, 1900, 2000, 2250, 2500, 3000, 3500, 4000, 4250, 4500, 4750, 5000]
SM_MAF = [250, 300, 350, 400, 450, 490, 530, 580, 620, 650, 680, 750, 870]

BT_RPM = [0, 780, 1000, 1250, 1500, 1750, 1900, 2000, 2250, 2500, 3000, 3500, 4000, 4250, 4500, 4750]
BT_IQ  = [0, 5, 10, 15, 20, 25, 30, 35, 40, 43]

DW_RPM = [0, 800, 1000, 1250, 1500, 2000, 2500, 3000, 3500, 4000, 4240, 4500, 4700, 4900, 5100, 5300]
DW_TPS = [0, 14, 28, 42, 56, 70, 84, 98, 100]

with open(BIN_IN, "rb") as f:
    data = bytearray(f.read())

def read_raw(base, r, c, cols):
    return struct.unpack_from('<H', data, base + (r * cols + c) * 2)[0]

def write_raw(base, r, c, cols, raw):
    raw = max(0, min(65535, int(round(raw))))
    struct.pack_into('<H', data, base + (r * cols + c) * 2, raw)

changes = 0

# 0. Sync Pump Voltage (Kopiowanie CB5 -> CB2)
md_pv = MAP_DEFINITIONS['pump_voltage']
for r in range(md_pv.rows):
    for c in range(md_pv.cols):
        val_cb5 = read_raw(md_pv.addr_cb5, r, c, md_pv.cols)
        val_cb2 = read_raw(md_pv.addr_cb2, r, c, md_pv.cols)
        if val_cb2 != val_cb5:
            write_raw(md_pv.addr_cb2, r, c, md_pv.cols, val_cb5)
            changes += 1

for cb_id in [5, 2]:
    print(f"\n[CB{cb_id}] PRZETWARZANIE...")

    # 1. NAPRAWA BLEDOW STRUKTURALNYCH
    # MAF Linearization
    md_maf = MAP_DEFINITIONS['maf_linearization']
    base_maf = md_maf.addr_cb5 if cb_id == 5 else md_maf.addr_cb2
    valid_max_maf = max([read_raw(base_maf, 0, c, md_maf.cols) for c in range(md_maf.cols) if read_raw(base_maf, 0, c, md_maf.cols) < 60000])
    for c in range(md_maf.cols):
        val = read_raw(base_maf, 0, c, md_maf.cols)
        if val >= 60000:
            write_raw(base_maf, 0, c, md_maf.cols, valid_max_maf)
            changes += 1

    # SOI Map (do 25.0 deg -> 2500)
    md_soi = MAP_DEFINITIONS['soi_map']
    base_soi = md_soi.addr_cb5 if cb_id == 5 else md_soi.addr_cb2
    valid_max_soi = max([read_raw(base_soi, r, c, md_soi.cols) for r in range(md_soi.rows) for c in range(md_soi.cols) if read_raw(base_soi, r, c, md_soi.cols) <= 2500])
    for r in range(md_soi.rows):
        for c in range(md_soi.cols):
            val = read_raw(base_soi, r, c, md_soi.cols)
            if val > 2500:
                write_raw(base_soi, r, c, md_soi.cols, valid_max_soi)
                changes += 1

    # N75 Map
    md_n75 = MAP_DEFINITIONS['n75_duty']
    base_n75 = md_n75.addr_cb5 if cb_id == 5 else md_n75.addr_cb2
    for r in range(md_n75.rows):
        for c in range(md_n75.cols):
            val = read_raw(base_n75, r, c, md_n75.cols)
            if val > 8500:
                write_raw(base_n75, r, c, md_n75.cols, 8500)
                changes += 1

    # 1.5. WYLACZENIE EGR (EGR OFF - wszystko na 0)
    md_egr = MAP_DEFINITIONS['egr']
    base_egr = md_egr.addr_cb5 if cb_id == 5 else md_egr.addr_cb2
    for r in range(md_egr.rows):
        for c in range(md_egr.cols):
            val = read_raw(base_egr, r, c, md_egr.cols)
            if val != 0:
                write_raw(base_egr, r, c, md_egr.cols, 0)
                changes += 1

    # 2. TUNING: BOOST LIMITER (Max 2300 mBar, zachowanie krzywej gorskiej)
    md_bl = MAP_DEFINITIONS['boost_limiter']
    base_bl = md_bl.addr_cb5 if cb_id == 5 else md_bl.addr_cb2
    for r in range(md_bl.rows):
        for c in range(md_bl.cols):
            val = read_raw(base_bl, r, c, md_bl.cols)
            new_val = min(2300, val + 150)
            if new_val != val:
                write_raw(base_bl, r, c, md_bl.cols, new_val)
                changes += 1

    # 3. TUNING: BOOST TARGET
    md_bt = MAP_DEFINITIONS['boost_target']
    base_bt = md_bt.addr_cb5 if cb_id == 5 else md_bt.addr_cb2
    for r in range(md_bt.rows):
        iq = BT_IQ[r]
        for c in range(md_bt.cols):
            rpm = BT_RPM[c]
            if 1000 <= rpm <= 2000 and 5 <= iq <= 30:
                val = read_raw(base_bt, r, c, md_bt.cols)
                add = 40 if rpm <= 1000 else (80 if rpm <= 1750 else 50)
                if iq < 10: add = int(add * 0.5)
                elif iq > 25: add = int(add * 0.8)
                new_val = val + add
                write_raw(base_bt, r, c, md_bt.cols, new_val)
                changes += 1
            
            val = read_raw(base_bt, r, c, md_bt.cols)
            if val > 2200:
                write_raw(base_bt, r, c, md_bt.cols, 2200)
                changes += 1

    # 4. TUNING: DRIVER WISH
    md_dw = MAP_DEFINITIONS['driver_wish']
    base_dw = md_dw.addr_cb5 if cb_id == 5 else md_dw.addr_cb2
    for r in range(md_dw.rows):
        tps = DW_TPS[r]
        for c in range(md_dw.cols):
            rpm = DW_RPM[c]
            if 14 <= tps <= 70 and 1000 <= rpm <= 2500:
                val = read_raw(base_dw, r, c, md_dw.cols)
                bonus = 700 if 1250 <= rpm <= 2000 else 500
                new_val = min(5000, val + bonus)
                if new_val > val:
                    write_raw(base_dw, r, c, md_dw.cols, new_val)
                    changes += 1

    # 5. TUNING: SMOKE LIMITERS
    for sm_name in ['smoke_limiter_0c', 'smoke_limiter_15c', 'smoke_limiter_30c']:
        md_sm = MAP_DEFINITIONS[sm_name]
        base_sm = md_sm.addr_cb5 if cb_id == 5 else md_sm.addr_cb2
        for r in range(md_sm.rows):
            maf = SM_MAF[r]
            if maf > 530: continue
            for c in range(md_sm.cols):
                rpm = SM_RPM[c]
                if rpm > 2500: continue
                val = read_raw(base_sm, r, c, md_sm.cols)
                iq_phys = val / 100.0
                max_iq = maf / 17.0
                if iq_phys > max_iq:
                    write_raw(base_sm, r, c, md_sm.cols, max_iq * 100.0)
                    changes += 1

    # 6. TUNING: N75 (Agresywne zamykanie)
    for r in range(md_n75.rows):
        for c in range(md_n75.cols):
            if 3 <= r <= 12 and 2 <= c <= 8:
                val = read_raw(base_n75, r, c, md_n75.cols)
                if val < 8500:
                    bonus = 700 if 4 <= c <= 6 else 400
                    new_val = min(8500, val + bonus)
                    if new_val > val:
                        write_raw(base_n75, r, c, md_n75.cols, new_val)
                        changes += 1

with open(BIN_OUT, "wb") as f:
    f.write(data)

print(f"\nZapisano do {BIN_OUT}. Dokonano {changes} pojedynczych operacji na komorkach.")
