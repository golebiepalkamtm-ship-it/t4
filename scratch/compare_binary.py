"""
Porownanie binarne plikow Original vs Stage 1/2/3
Szukamy ROZNIC miedzy plikami, zeby zobaczyc co tuner zmienil
"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')

FILES = {
    "Original":  r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original",
    "Stage 1":   r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_A0FF.Stage1",
    "Stage 2":   r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_3D43.Stage2",
    "Stage 3":   r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_992F.Stage3",
    "cks ok":    r"d:\t4\cks ok",
}

SEP = "=" * 120

# Wczytaj pliki
data = {}
for name, path in FILES.items():
    with open(path, 'rb') as f:
        data[name] = bytearray(f.read())
    print(f"  {name:>12}: {len(data[name])} bajtow")

orig = data["Original"]

print(f"\n{SEP}")
print(f"  POROWNANIE BINARNE: Original vs Stage 1/2/3")
print(f"{SEP}\n")

# Porownaj kazdy stage z originalem
for stage_name in ["Stage 1", "Stage 2", "Stage 3"]:
    stage = data[stage_name]
    
    if len(orig) != len(stage):
        print(f"  {stage_name}: ROZNA DLUGOSC! orig={len(orig)} stage={len(stage)}")
        continue
    
    diffs = []
    for i in range(len(orig)):
        if orig[i] != stage[i]:
            diffs.append(i)
    
    print(f"  {stage_name}: {len(diffs)} bajtow rozni sie od Original")
    
    if len(diffs) == 0:
        print(f"    PLIKI SA IDENTYCZNE!")
        continue
    
    # Grupuj roznice w bloki (ciag zmian)
    blocks = []
    block_start = diffs[0]
    block_end = diffs[0]
    for d in diffs[1:]:
        if d <= block_end + 4:  # max 4 bajty przerwy
            block_end = d
        else:
            blocks.append((block_start, block_end))
            block_start = d
            block_end = d
    blocks.append((block_start, block_end))
    
    print(f"    {len(blocks)} blokow zmian:")
    for start, end in blocks[:30]:
        size = end - start + 1
        orig_bytes = orig[start:end+1]
        stage_bytes = stage[start:end+1]
        
        # Probuj interpretowac jako uint16 LE
        if size <= 8:
            orig_vals = []
            stage_vals = []
            for j in range(0, size, 2):
                if j + 2 <= size:
                    ov = struct.unpack('<H', orig_bytes[j:j+2])[0]
                    sv = struct.unpack('<H', stage_bytes[j:j+2])[0]
                    orig_vals.append(ov)
                    stage_vals.append(sv)
            
            orig_str = ",".join(str(v) for v in orig_vals)
            stage_str = ",".join(str(v) for v in stage_vals)
            print(f"    [{hex(start):>10} - {hex(end):>10}]  {size:>4} B  |  orig: {orig_str:<20}  stage: {stage_str:<20}")
        else:
            # Dla wiekszych blokow - pokaz ilosc i zakres wartosci
            orig_u16 = []
            stage_u16 = []
            for j in range(0, size - 1, 2):
                orig_u16.append(struct.unpack('<H', orig_bytes[j:j+2])[0])
                stage_u16.append(struct.unpack('<H', stage_bytes[j:j+2])[0])
            
            if orig_u16 and stage_u16:
                print(f"    [{hex(start):>10} - {hex(end):>10}]  {size:>4} B  ({size//2} wartosci)")
                print(f"      orig:  min={min(orig_u16):>6}  max={max(orig_u16):>6}  srednia={sum(orig_u16)/len(orig_u16):>8.1f}")
                print(f"      stage: min={min(stage_u16):>6}  max={max(stage_u16):>6}  srednia={sum(stage_u16)/len(stage_u16):>8.1f}")
                # Pokaz roznice
                diffs_vals = [s - o for o, s in zip(orig_u16, stage_u16)]
                print(f"      diff:  min={min(diffs_vals):>+6}  max={max(diffs_vals):>+6}  srednia={sum(diffs_vals)/len(diffs_vals):>+8.1f}")
    
    if len(blocks) > 30:
        print(f"    ... i {len(blocks)-30} wiecej blokow ...")

# Porownaj tez cks ok z Original
print(f"\n{SEP}")
print(f"  POROWNANIE: cks ok vs Original")
print(f"{SEP}")
cks = data["cks ok"]
if len(orig) != len(cks):
    print(f"  ROZNA DLUGOSC! orig={len(orig)} cks={len(cks)}")
    print(f"  To sa ROZNE wersje firmware!")
else:
    diffs_cks = [i for i in range(len(orig)) if orig[i] != cks[i]]
    print(f"  {len(diffs_cks)} bajtow rozni sie")

print(f"\n{SEP}")
