import os
import re

files = [
    r"d:\t4\cks ok",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_A0FF.Stage1",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_3D43.Stage2",
    r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_992F.Stage3",
    r"d:\t4\VW_T4_2.5_TDI_1999_Turbodiesel___110.3KWKW_Bosch_0281001764_074906021M__356867-868_D28E.Original",
    r"d:\t4\VW_T4_2.5_TDI_1999_Turbodiesel___110.3KWKW_Bosch_0281001764_074906021M__356867-868_E040.Stage1",
]

for path in files:
    if os.path.exists(path):
        name = os.path.basename(path)
        with open(path, "rb") as f:
            data = f.read()
        
        # Search ASCII patterns
        ascii_text = "".join(chr(b) if 32 <= b <= 126 else " " for b in data)
        
        vag_hw = re.findall(r'074\s*906\s*\w+', ascii_text)
        bosch_hw = re.findall(r'0\s*281\s*\d{3}\s*\d{3}', ascii_text)
        sw_num = re.findall(r'1037\d{6}', ascii_text) or re.findall(r'3\d{5}', ascii_text)
        
        print(f"[{name}]")
        print(f"  VAG HW:   {set(vag_hw)}")
        print(f"  Bosch HW: {set(bosch_hw)}")
        print(f"  Software: {set(sw_num[:5])}")
        print()
