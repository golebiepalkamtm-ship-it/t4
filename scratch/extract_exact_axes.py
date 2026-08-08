import sys
import struct
import os

sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

ecu = ECUBinaryReader(r"d:\t4\cks ok")

for key, md in MAP_DEFINITIONS.items():
    addr = md.addr_cb5
    # Czytamy 128 bajtów przed mapą
    start = max(0, addr - 128)
    data_chunk = ecu.data[start:addr]
    vals = struct.unpack('<' + 'H' * (len(data_chunk)//2), data_chunk)
    print(f"\n--- {key} ({md.name}) @ {hex(addr)} ---")
    print("Ostatnie 40 wartości uint16 przed mapą:", vals[-40:])
