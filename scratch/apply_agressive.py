"""
STAGE 2: Agresywne wysterowanie N75 i Driver Wish
"""
import struct

BIN_IN   = r"d:\t4\cks ok_fixed.bin"
BIN_OUT  = r"d:\t4\cks ok_fixed.bin" # Overwrite the previous fix directly

with open(BIN_IN, "rb") as f:
    data = bytearray(f.read())

def read_raw(addr): return struct.unpack_from('<H', data, addr)[0]
def write_raw(addr, val): struct.pack_into('<H', data, addr, max(0, min(65535, int(val))))

changes = 0

print("1. Modyfikacja N75 Precontrol (0x056852)")
N75_ADDR = 0x056852
for r in range(4, 11):      # RPM od ok 1000 do 2500
    for c in range(3, 13):  # IQ od umiarkowanego do MAX
        addr = N75_ADDR + (r*13 + c)*2
        val = read_raw(addr)
        
        # Obliczam bonus - najbardziej agresywnie w środku (r=6,7,8)
        bonus = 400  # bazowo +4.0%
        if 5 <= r <= 8:
            bonus = 700  # +7.0%
            
        new_val = min(8000, val + bonus) # Max limit 80.0%
        
        if new_val > val:
            write_raw(addr, new_val)
            changes += 1

print("2. Modyfikacja Driver Wish (Pedał Gazu) (0x04CC36)")
DW_ADDR = 0x04CC36
for r in range(4, 11):      # RPM row 4..10
    for c in range(2, 7):   # TPS col 2..6 (czyli wcisniety gaz ale nie w podloge)
        addr = DW_ADDR + (r*9 + c)*2
        val = read_raw(addr)
        
        # Zwiekszam zadanie by auto wydawalo sie bardzo zrywne
        bonus = 500  # +5.0 mg
        if 6 <= r <= 9:
            bonus = 700  # +7.0 mg
            
        new_val = min(5000, val + bonus) # Max 50.0 mg (i tak na koncu jest 55.0)
        
        # Ochrona monotonicznosci w wierszu (zeby gaz nie dzialal "do tylu")
        # upewniam sie ze mniejsze wcisniecie (c-1) nie ma wiekszej wartosci niz my, 
        # i ze wieksze wcisniecie (c+1) nie ma mniejszej
        left = read_raw(DW_ADDR + (r*9 + (c-1))*2)
        right = read_raw(DW_ADDR + (r*9 + (c+1))*2)
        
        new_val = max(left + 10, new_val)  # Musi byc przynajmniej > niz z lewej
        new_val = min(right - 10, new_val) # Musi byc mniejsze < niz z prawej
        
        if new_val > val:
            write_raw(addr, new_val)
            changes += 1

with open(BIN_OUT, "wb") as f:
    f.write(data)

print(f"Zakonczono pomyslnie! Wprowadzono {changes} modyfikacji poprawiajacych dynamike.")
