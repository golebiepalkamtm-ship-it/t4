import struct

with open(r"d:\t4\cks ok", "rb") as f:
    data = f.read()

def u16(addr): return struct.unpack_from('<H', data, addr)[0]

print("--- N75 (0x056852) 16x13 ---")
# Załóżmy X (IQ) = 13 (z XDF to prawdopodobnie adresy przed mapą)
# Załóżmy Y (RPM) = 16 
for r in range(16):
    row = [u16(0x056852 + (r*13 + c)*2) for c in range(13)]
    print(f"RPM row {r}: {[v/100.0 for v in row]}")

print("\n--- Driver Wish (0x04CC36) 16x9 ---")
for r in range(16):
    row = [u16(0x04CC36 + (r*9 + c)*2) for c in range(9)]
    # Zwykle to IQ w formacie raw * 0.01
    print(f"RPM row {r}: {[v/100.0 for v in row]}")

