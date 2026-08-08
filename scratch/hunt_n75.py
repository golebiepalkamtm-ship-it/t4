import struct

BIN_IN = r"d:\t4\cks ok"
with open(BIN_IN, "rb") as f:
    data = f.read()

def get_u16(addr):
    return struct.unpack_from('<H', data, addr)[0]

print("Hunting for N75 map (13x16 or 16x13) in 0x050000 - 0x060000")
# szukamy osi IQ: 13 elementów, wartości idące od 0 w górę do max ~600-800
# szukamy osi RPM: 16 elementów, zazwyczaj 0..5000

for i in range(0x050000, 0x060000, 2):
    # Sprawdzam czy to może być oś RPM (16 elementów)
    v0 = get_u16(i)
    if v0 not in [0, 780, 800, 850, 900, 1000]:
        continue
    
    # sprawdz czy rośnie
    valid = True
    last = -1
    for j in range(16):
        v = get_u16(i + j*2)
        if v <= last or v > 6000:
            valid = False
            break
        last = v
        
    if valid:
        print(f"Possible RPM axis (16) at 0x{i:06X}: {[get_u16(i + k*2) for k in range(16)]}")

for i in range(0x050000, 0x060000, 2):
    # Sprawdzam oś IQ (13 elementów, zazwyczaj w jednostkach * 100 -> wiec np 500, 1000)
    v0 = get_u16(i)
    if v0 != 0: continue
    
    valid = True
    last = -1
    for j in range(13):
        v = get_u16(i + j*2)
        if v < last or v > 7000: # 70mg max typically
            valid = False
            break
        last = v
        
    if valid and last > 3000:
        print(f"Possible IQ axis (13) at 0x{i:06X}: {[get_u16(i + k*2) for k in range(13)]}")

