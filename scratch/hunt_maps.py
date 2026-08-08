import struct

with open(r"d:\t4\cks ok", "rb") as f:
    data = f.read()

def u16(addr): return struct.unpack_from('<H', data, addr)[0]

print("Szukam DRIVER WISH (8x16 lub 16x8, RPM x TPS -> IQ)")
# TPS to typowo 0, 10, 20, 30, 40, 50, 60, 70, 80, 100% -> 0..10000 dla % lub 0..100
for i in range(0x40000, 0x80000, 2):
    v = u16(i)
    if v == 0:
        # Check if it looks like TPS (8 vals)
        tps = [u16(i+k*2) for k in range(8)]
        if tps[0]==0 and 100 <= tps[-1] <= 10000 and all(tps[a] < tps[a+1] for a in range(7)):
            print(f"Possible TPS axis (8) at 0x{i:06X}: {tps}")

print("\nSzukam N75 (okolo 0x0567XX)")
for i in range(0x056760, 0x056800, 2):
    print(f"0x{i:06X}: {u16(i)}")

