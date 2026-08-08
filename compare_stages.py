import os
import sys

# Dodajemy folder główny do ścieżki
sys.path.append(r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

files = [
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_A0FF.Stage1",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_3D43.Stage2",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_992F.Stage3",
    r"C:\Users\manta\Desktop\cks ok"
]

results = {}

for path in files:
    try:
        basename = os.path.basename(path)
        if "Original" in basename: name = "Original"
        elif "Stage1" in basename: name = "Stage 1"
        elif "Stage2" in basename: name = "Stage 2"
        elif "Stage3" in basename: name = "Stage 3"
        elif "cks ok" in basename: name = "cks ok"
        else: name = basename
        
        ecu = ECUBinaryReader(path)
        stats = {}
        for map_key, map_def in MAP_DEFINITIONS.items():
            summary = ecu.get_map_summary(map_def, codeblock=5)
            # Zbieramy max wartości dla map żeby zobaczyć ile "dolano" paliwa lub powietrza
            stats[map_def.name] = summary['max']
            
        results[name] = stats
    except Exception as e:
        print(f"Error reading {path}: {e}")

print(f"{'Mapa (Wartość MAX)':<45} | {'Original':<10} | {'Stage 1':<10} | {'Stage 2':<10} | {'Stage 3':<10} | {'cks ok':<10}")
print("-" * 110)
for map_key in MAP_DEFINITIONS.values():
    m = map_key.name
    v_orig = results.get("Original", {}).get(m, "-")
    v_s1 = results.get("Stage 1", {}).get(m, "-")
    v_s2 = results.get("Stage 2", {}).get(m, "-")
    v_s3 = results.get("Stage 3", {}).get(m, "-")
    v_cks = results.get("cks ok", {}).get(m, "-")
    print(f"{m[:43]:<45} | {str(v_orig):<10} | {str(v_s1):<10} | {str(v_s2):<10} | {str(v_s3):<10} | {str(v_cks):<10}")
