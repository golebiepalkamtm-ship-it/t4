import sys
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS, MapDefinition

def remap_file(input_path, output_path):
    ecu = ECUBinaryReader(input_path)
    
    # Pomocnicza funkcja transformująca wartości mapy 
    def apply_transform(map_def, codeblock, transform_fn):
        matrix = ecu.read_map(map_def, codeblock)
        for r in range(len(matrix)):
            for c in range(len(matrix[r])):
                val = matrix[r][c]
                matrix[r][c] = transform_fn(val)
        ecu.write_map(map_def, matrix, codeblock)

    # Transformacje:
    # 1. Torque Limiter -> od 45 mg w górę ciągniemy do ok 59.5 mg (skalowanie)
    def trans_torque(val):
        if val > 45.0:
            diff = val - 45.0
            # max stare to 50.85 (diff = 5.85). Chcemy u góry 59.5 (diff = 14.5). Mnożnik ok 2.47
            return round(45.0 + diff * 2.47, 2)
        return val

    # 2. Driver Wish -> gaz powyżej 45 wyciągamy na 61
    def trans_dw(val):
        if val > 45.0:
            diff = val - 45.0
            # stare max 55.0 (diff 10.0), chcemy 61.0 (diff 16.0). Mnożnik 1.6
            return round(45.0 + diff * 1.6, 2)
        return val

    # 3. Smoke limitery -> >45 na 60
    def trans_smoke(val):
        if val > 45.0:
            diff = val - 45.0
            # stare max 55.9 (diff 10.9), chcemy 60.0 (diff 15.0). Mnożnik 1.37
            return round(45.0 + diff * 1.37, 2)
        return val

    # 4. Boost Target -> >2000 mBar na 2380
    def trans_boost(val):
        if val > 2000.0:
            diff = val - 2000.0
            # max stare 2190 (diff 190), chcemy 2380 (diff 380). Mnożnik 2.0
            return round(2000.0 + diff * 2.0, 2)
        return val

    # 5. Boost Limiter -> tak jak boost, ale wyżej (np 2450)
    def trans_blimit(val):
        if val > 2000.0:
            diff = val - 2000.0
            # max stare 2190 (diff 190), chcemy 2450 (diff 450). Mnożnik 2.36
            return round(2000.0 + diff * 2.36, 2)
        return val

    # 6. Pump voltage -> od 4.0V rośnie
    def trans_pump(val):
        if val > 4.0:
            diff = val - 4.0
            # stare max 4.38 (diff 0.38), chcemy 4.55 (diff 0.55). Mnożnik 1.44
            return round(4.0 + diff * 1.44, 3)
        return val

    for cb in [2, 5]:
        apply_transform(MAP_DEFINITIONS['torque_limiter'], cb, trans_torque)
        apply_transform(MAP_DEFINITIONS['driver_wish'], cb, trans_dw)
        apply_transform(MAP_DEFINITIONS['smoke_limiter_0c'], cb, trans_smoke)
        apply_transform(MAP_DEFINITIONS['smoke_limiter_15c'], cb, trans_smoke)
        apply_transform(MAP_DEFINITIONS['smoke_limiter_30c'], cb, trans_smoke)
        apply_transform(MAP_DEFINITIONS['boost_target'], cb, trans_boost)
        apply_transform(MAP_DEFINITIONS['boost_limiter'], cb, trans_blimit)
        apply_transform(MAP_DEFINITIONS['pump_voltage'], cb, trans_pump)
        
    ecu.save_bin(output_path)
    print("REMAP ZAKOŃCZONY POMYŚLNIE!")
    print(f"Zapisano w {output_path}")

if __name__ == "__main__":
    input_f = r"C:\Users\manta\Desktop\cks ok"
    output_f = r"C:\Users\manta\Desktop\cks ok_v2_200km.bin"
    remap_file(input_f, output_f)
