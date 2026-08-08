import os
import hashlib

files = [
    r"d:\t4\cks ok",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_A0FF.Stage1",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_3D43.Stage2",
    r"d:\t4\VW_T4_2.5_TDI_1999_Turbodiesel___110.3KWKW_Bosch_0281001764_074906021M__356867-868_D28E.Original",
]

print("=== PLIKI W D:\\t4 AND THEIR PROPERTIES ===")
bins = {}
for path in files:
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        name = os.path.basename(path)
        md5 = hashlib.md5(data).hexdigest()
        print(f"File: {name:<70} | Size: {len(data)} bytes | MD5: {md5}")
        bins[name] = data

# Check exact byte differences between 'cks ok' and '074906018AJ...8D73.Original'
if "cks ok" in bins and "VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original" in bins:
    d1 = bins["cks ok"]
    d2 = bins["VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original"]
    diffs = sum(1 for a, b in zip(d1, d2) if a != b)
    print(f"\nPorownanie 'cks ok' vs '074906018AJ.Original': {diffs} roznych bajtow na 524288.")

