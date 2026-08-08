# RAPORT DIAGNOSTYCZNY: `cks ok_stage1_pro.bin` vs LOGI VCDS
## VW Transporter T4 2.5 TDI AXG (151 KM) — Bosch EDC15VM+ (074906018AJ)

**Data analizy:** 02.08.2026  
**Plik BIN:** `cks ok_stage1_pro.bin` (524 288 bajtów)  
**Logi VCDS:** 5 plików CSV z jazdy dynamicznej (VCDS AKP 20.4.2)  
**Zebrano:** 53 unikalne profile RPM, w tym **25 próbek WOT (pełny gaz)**

---

## 1. AUDYT MAP W PLIKU BIN (Codeblock 5)

| Mapa | Dimsport | Adres | Zakres | Jednostka | Status |
|:-----|:--------:|:-----:|:------:|:---------:|:------:|
| **Driver Wish** (Życzenie kierowcy) | B1 | `0x4CC36` | 0.0 – 55.0 | mg/hub | ✅ |
| **Torque Limiter** (Ogranicznik momentu) | LC | `0x4D2FE` | 0.0 – 55.0 | mg/hub | ⚠️ WYSOKI |
| **Smoke Limiter 0°C** | QS | `0x4D61C` | 2.2 – 57.9 | mg/hub | ✅ |
| **Smoke Limiter 15°C** | QS | `0x4D7BC` | 2.2 – 57.9 | mg/hub | ✅ |
| **Smoke Limiter 30°C** | QS | `0x4D95C` | 3.2 – 58.0 | mg/hub | ✅ |
| **Boost Target** (Zadane doładowanie) | BS | `0x56546` | 1050 – **2250** | mBar | 🔴 ZA WYSOKI |
| **Boost Limiter** (Ogranicznik ciśn.) | BL | `0x56B3C` | 1540 – 2350 | mBar | ⚠️ |
| **N75 Precontrol** (Geometria Turbo) | N75 | `0x567C6` | 0.0 – 599.7 | % | ✅ |
| **SOI** (Kąt Wtrysku) | SOI | `0x51F56` | 0.0 – 655.4 | °BTDC | ✅ |
| **EGR** (Recyrkulacja spalin) | EG | `0x55290` | FLAT 85.0 | % | ✅ OFF |
| **Pump Voltage** (N146 VP37) | PUMP | `0x54468` | 0.0 – 4.38 | V | ✅ |
| **MAF Linearization** | — | `0x54A38` | 0.4 – 6553.3 | kg/h | ✅ |

---

## 2. ODKRYCIA DIAGNOSTYCZNE

> [!CRITICAL]
> ### 🔴 BOOST TARGET ZBYT WYSOKI (2250 mBar)
> **Zadane ciśnienie doładowania w mapie BS wynosi 2250 mBar**, co przekracza bezpieczny limit dla seryjnej turbosprężarki Garrett VNT20/GT2252V.
> 
> **Zalecenie:** Obniż wartości Boost Target do max **2100 mBar** w zakresie 2000–4000 RPM.
> 
> **Jednak logi VCDS pokazują**, że w praktyce turbo osiąga max ~2203 mBar, a powyżej 4000 RPM spada do ~1877 mBar. Mapa jest agresywna, ale turbina nie dobija do limitu na górze obrotów.

> [!WARNING]
> ### ⚠️ OGRANICZNIK MOMENTU WYSOKI (55.0 mg/hub)
> **Torque Limiter** (LC) ma max wartość **55.0 mg/hub**, co jest wartością agresywną. 
> 
> **Ryzyko:** Zwiększone obciążenie dwumasowego koła zamachowego (DMF) i sprzęgła.
> 
> **Dane z logów:** Aktualny ogranicznik momentu w logu wynosi ~50.0–50.8 mg/hub w zakresie WOT (to go obcina, nie Driver Wish).

> [!NOTE]
> ### ✅ EGR WYŁĄCZONY
> Recyrkulacja spalin (EGR) jest poprawnie wyłączona — stała wartość 85.0% w mapie blokuje zawór N18 w pozycji zamkniętej.

---

## 3. ANALIZA LOGÓW VCDS — DANE Z JAZDY DYNAMICZNEJ

### 3.1 Turbosprężarka & Doładowanie (Grupa 011)

![Wykres Boost & N75](C:/Users/manta/.gemini/antigravity-ide/brain/8eba4bc1-a70b-494e-98d9-f7a4ec0e3263/wykres_01_boost_011.png)

| RPM | Boost Zadane | Boost Aktualne | Δ (mBar) | N75 Duty | Ocena |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1448 | 1183 | 1051 | **-132** | 31.9% | ⚠️ Lag |
| 1510 | 1163 | 1040 | **-122** | 31.9% | ⚠️ Lag |
| 2040 | 2142 | 1948 | **-194** | 45.0% | 🔴 **Turbo Lag!** |
| 2305 | 2162 | 2244 | **+82** | 48.6% | ⚡ Boost Spike! |
| 2570 | 2173 | 2173 | **0** | 51.8% | ✅ Perfect |
| 2815 | 2173 | 2173 | **0** | 52.6% | ✅ Perfect |
| 3060 | 2183 | 2203 | +20 | 55.0% | ✅ OK |
| 3305 | 2183 | 2203 | +20 | 55.8% | ✅ OK |
| 3550 | 2173 | 2193 | +20 | 57.4% | ✅ OK |
| 3774 | 2173 | 2193 | +20 | 58.2% | ✅ OK |
| 3978 | 2173 | 2173 | 0 | 59.0% | ✅ Perfect |
| 4182 | 2132 | 2142 | +10 | 59.4% | ✅ OK |
| 4345 | 2040 | 2050 | +10 | 59.8% | ✅ OK |
| 4488 | 1938 | 1928 | -10 | 55.8% | ✅ OK |
| 4570 | 1877 | 1867 | -10 | 53.8% | ✅ OK |

**Wnioski dotyczące Turbo:**
- **Przy 2040 RPM turbina nie nadąża (Δ = -194 mBar)** — klasyczna turbo dziura przy ostrej zmianie obciążenia
- **Przy 2305 RPM mały boost spike (+82 mBar)** — turbina reaguje z nadmiarową odpowiedzią
- **Od 2570 RPM wzwyż doładowanie jest idealnie stabilne** — turbina pracuje poprawnie
- **N75 rośnie liniowo 45%→60%** — mapa N75 Precontrol działa, geometria VNT reguluje poprawnie
- **Max ciśnienie realne: ~2203 mBar** (mimo że mapa pozwala na 2250 mBar)

---

### 3.2 Limitery Dawki (Grupa 008)

![Wykres Limiterów Dawki](C:/Users/manta/.gemini/antigravity-ide/brain/8eba4bc1-a70b-494e-98d9-f7a4ec0e3263/wykres_02_limiters_008.png)

| RPM | Driver Wish | Torque Limiter | Smoke Limiter | **Aktywny Limiter** |
|:---:|:---:|:---:|:---:|:---:|
| 1489 | 51.0 | 46.0 | **44.4** | 🔴 **SMOKE** |
| 1510 | 51.0 | 45.6 | **30.0** | 🔴 **SMOKE** |
| 1652 | 51.0 | **50.0** | 51.0 | ⚠️ TORQUE |
| 1938 | 51.0 | **50.4** | 51.0 | ⚠️ TORQUE |
| 2203 | 51.0 | **50.4** | 51.0 | ⚠️ TORQUE |
| 2489 | 51.0 | **50.4** | 51.0 | ⚠️ TORQUE |
| 2754 | 51.0 | **50.4** | 51.0 | ⚠️ TORQUE |
| 3019 | 51.0 | **50.6** | 51.0 | ⚠️ TORQUE |
| 3284 | 51.0 | **50.6** | 51.0 | ⚠️ TORQUE |
| 3550 | 51.0 | **50.6** | 51.0 | ⚠️ TORQUE |
| 3794 | 51.0 | **50.8** | 51.0 | ⚠️ TORQUE |
| 4019 | 51.0 | **48.2** | 51.0 | ⚠️ TORQUE |
| 4243 | 51.0 | **40.2** | 51.0 | ⚠️ TORQUE |

**Wnioski dotyczące Limiterów:**
- **W niskich obrotach (1489–1510 RPM) blokuje SMOKE LIMITER** — przepływomierz przy ruszaniu odczytuje mało powietrza, ECU tnie dawkę
- **Od 1652 RPM do odcięcia limituje TORQUE LIMITER** — to dobrze, znaczy że mapa BS/QS nie jest zbyt restrykcyjna
- **Driver Wish 51.0 mg/hub** — pedał gazu "prosi" o 51 mg, ale Torque go obcina do ~50 mg → driver wish jest OK, ale niewiele nad LC
- **Powyżej 4000 RPM Torque Limiter spada** (48.2 → 40.2 mg) — celowa ochrona silnika na górze

---

### 3.3 Kąt Wtrysku SOI (Grupa 004)

![Wykres SOI](C:/Users/manta/.gemini/antigravity-ide/brain/8eba4bc1-a70b-494e-98d9-f7a4ec0e3263/wykres_03_soi_004.png)

| RPM | SOI Zadane (°BTDC) | SOI Aktualne (°BTDC) | Δ (°) | Ocena |
|:---:|:---:|:---:|:---:|:---:|
| 1489 | 11.4 | 11.0 | -0.4 | ✅ OK |
| 1652 | 9.9 | 10.6 | +0.7 | ✅ OK |
| 1938 | 7.9 | 8.1 | +0.2 | ✅ Perfect |
| 2203 | 8.1 | 7.9 | -0.2 | ✅ Perfect |
| 2489 | 9.2 | 9.2 | 0.0 | ✅ Perfect |
| 2754 | 10.6 | 10.8 | +0.2 | ✅ Perfect |
| 3019 | 12.1 | 12.8 | +0.7 | ✅ OK |
| 3284 | 13.9 | 13.6 | -0.3 | ✅ OK |
| 3550 | 15.8 | 15.8 | 0.0 | ✅ Perfect |
| 3794 | 17.4 | 17.4 | 0.0 | ✅ Perfect |
| 4019 | 18.0 | 18.0 | 0.0 | ✅ Perfect |
| 4243 | 18.0 | 17.8 | -0.2 | ✅ OK |

**Wnioski dotyczące SOI:**
- **SOI jest IDEALNY** — pompa VP37 nadąża za mapą kąta wtrysku w całym zakresie obrotów
- Odchyłki max ±0.7° → w normie dla systemu VP37
- **Brak opóźnienia kąta wtrysku** — oznacza to, że ciśnienie wewnątrzpompy jest prawidłowe

---

### 3.4 Przepływomierz MAF (Grupa 003)

| RPM | MAF Żądane | MAF Zmierzone | Stosunek | Ocena |
|:---:|:---:|:---:|:---:|:---:|
| 1469 | 980 | 530 | 54.1% | 🔴 |
| 1612 | 980 | 685 | 69.9% | ⚠️ |
| 1836 | 980 | 895 | 91.3% | ✅ |
| 2101 | 980 | 980 | 100.0% | ✅ Perfect |
| 2366 | 980 | 945 | 96.4% | ✅ |
| 2632 | 980 | 970 | 99.0% | ✅ |
| 2897 | 980 | 945 | 96.4% | ✅ |
| 3142 | 980 | 980 | 100.0% | ✅ |
| 3386 | 980 | 980 | 100.0% | ✅ |
| 3631 | 980 | 975 | 99.5% | ✅ |
| 3856 | 980 | 970 | 99.0% | ✅ |
| 4080 | 980 | 940 | 95.9% | ✅ |
| 4284 | 980 | 905 | 92.3% | ✅ |

**Wnioski dotyczące MAF:**
- **Przepływomierz (G70) jest SPRAWNY** — od 1836 RPM wzwyż odczyt >91%
- W niskich obrotach (1469–1612 RPM) MAF odczytuje mniej, bo **turbina jeszcze się rozpędza** — to normalne
- **Brak konieczności wymiany MAF** — czujnik działa poprawnie

---

### 3.5 Diagnostyka Dodatkowa (Grupy 012, 014, 019, 023)

| Parametr | Wartość | Ocena |
|:---------|:--------|:-----:|
| **Napięcie akumulatora** | 13.38 V | ✅ Alternator OK |
| **Temperatura cieczy** | 91.8–94.5°C | ✅ Norma |
| **Ciśnienie atmosferyczne** | 989.4 mBar | ✅ (~na poziomie morza) |
| **Napięcie pompy VP37 (Gr.019)** | 0.760 V / 4.540 V | ✅ W normie |
| **Dawka korekty** (Gr.013) | 0.05 – 0.09 mg | ✅ Minimalna |
| **IQ Korektor życzenia** (Gr.014) | -0.82 – -0.85 mg | ✅ Normalna korekta |

---

## 4. SUGESTIE AUTO-TUNE

Na podstawie analizy logów, algorytm auto-tune proponuje **5 korekt**:

### N75 Precontrol (Geometria Turbo)
| Lokacja | Stara wartość | Nowa wartość | Powód |
|:--------|:---:|:---:|:------|
| `N75[0][6]` (2000 RPM, IQ=0) | 99.0% | 91.25% | Boost act=1948 vs req=2142 (-194 mBar lag) |
| `N75[0][7]` (2250 RPM, IQ=0) | 99.0% | 95.0% | Boost act=2244 vs req=2162 (+82 mBar spike) |

### Smoke Limiter (QS) — dla 0°C, 15°C, 30°C
| Lokacja | Stara wartość | Nowa wartość | Powód |
|:--------|:---:|:---:|:------|
| `QS[12][5]` (RPM~1938, MAF=535mg) | 6.4 / 6.4 / 7.4 mg | 31.47 mg | Mapa ogranicza dawkę zbyt agresywnie przy MAF=535 mg/hub na niskich obrotach |

---

## 5. PODSUMOWANIE OCENY `cks ok_stage1_pro.bin`

| Aspekt | Ocena | Uwagi |
|:-------|:-----:|:------|
| **EGR OFF** | ✅ POPRAWNE | Zawór N18 zablokowany |
| **Boost Target** | ⚠️ AGRESYWNE | Max 2250 mBar w mapie, ale realnie osiąga ~2203 |
| **Boost Limiter** | ✅ OK | 2350 mBar — wystarczający margines |
| **Torque Limiter** | ⚠️ WYSOKI | 55.0 mg — w logu limituje na 50.4 mg, ale mapa pozwala na więcej |
| **SOI (Kąt Wtrysku)** | ✅ IDEALNY | VP37 nadąża za mapą, odchyłki <1° |
| **N75 Precontrol** | ⚠️ DO KOREKTY | Turbo lag przy 2040 RPM, mini spike przy 2305 RPM |
| **Smoke Limiter** | ✅ OK | Blokuje dawkę w niskich obrotach (1489–1510), co jest normalne |
| **Pump Voltage** | ✅ OK | Max 4.38V — poniżej limitu fizycznego VP37 (4.5V) |
| **MAF Czujnik** | ✅ SPRAWNY | Odczyt >91% od 1836 RPM |
| **Temperatura** | ✅ NORMA | 91.8–94.5°C |
| **Alternator** | ✅ OK | 13.38V |

### OGÓLNA OCENA: ⚠️ STAGE 1 PRO — DZIAŁA, ALE WYMAGA DROBNYCH KOREKT

> [!IMPORTANT]
> **Kluczowe zalecenia:**
> 1. **Obniż Boost Target** z 2250 do max **2100 mBar** — bezpieczny limit dla seryjnego VNT
> 2. **Skoryguj N75 w zakresie 2000–2300 RPM** — usunie turbo lag/spike w tym zakresie
> 3. **Rozważ obniżenie Torque Limiter** z 55.0 do ~50.0 mg — ochrona DMF

---

*Raport wygenerowany automatycznie przez EDC15VM+ VCDS Master Analyzer na podstawie 5 logów VCDS i wsadu `cks ok_stage1_pro.bin`.*
