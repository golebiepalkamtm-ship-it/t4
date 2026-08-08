import sys
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import MAP_DEFINITIONS, ECUBinaryReader
import struct

f = r"d:\t4\cks ok_fixed_v4.bin"
reader = ECUBinaryReader(f)
data = bytearray(reader.data)
md = MAP_DEFINITIONS['egr']

for cb in [5, 2]:
    base = md.addr_cb5 if cb == 5 else md.addr_cb2
    for r in range(md.rows):
        for c in range(md.cols):
            # Set to 8500 (850 mg/str) - standard EDC15 EGR OFF
            struct.pack_into('<H', data, base + (r * md.cols + c) * 2, 8500)

with open(f, 'wb') as out:
    out.write(data)

print("EGR map restored to 8500 (EGR Closed)")
