# KOMPLEKSOWA DOKUMENTACJA TECHNICZNA I DIAGNOSTYCZNA
## STEROWNIK BOSCH EDC15VM+ — VW TRANSPORTER T4 2.5 TDI (151 KM / AXG)

---

### 1. DANE IDENTYFIKACYJNE STEROWNIKA I POJAZDU

| Parametr | Wartość | Opis / Uwagi |
| :--- | :--- | :--- |
| **Numer OEM VAG** | **`074 906 018 AJ`** (074906018AJ 0301) | Numer części wg katalogu Volkswagen |
| **Numer produkcyjny Bosch** | **`0 281 010 461`** (0281010461) | Numer sprzętowy sterownika (Hardware ID) |
| **Numer oprogramowania Bosch** | **`1037362445`** (362445) | Wersja oprogramowania układowego (Software ID) |
| **Wersja oprogramowania (SG)** | **`SG 3908 28SA5172`** | Oznaczenie wersji zbioru danych produkcyjnych |
| **Pojazd / Model** | **VW Transporter T4 / Caravelle / Multivan** | Lata produkcji 2000 – 2003 |
| **Silnik / Oznaczenie** | **2.5 TDI R5 10V (Kod: AXG)** | 5-cylindrowy rzędowy, wtrysk rozdzielaczowy VP37 |
| **Moc / Moment fabryczny** | **111 kW / 151 KM** @ 4000 RPM | **310 Nm** @ 1900–2500 RPM |
| **Turbosprężarka** | Garrett VNT (Zmienna geometria) | Model VNT20 / GT2252V |
| **Skrzynia biegów** | Manualna 5-biegowa | Oznaczenie przekładni `02G` |
| **Układ sterowania** | **Bosch EDC15VM+25** | Sterownik pompy rozdzielaczowej VP37 |
| **Układ pamięci Flash** | AM29F400BT (PSOP44) | Rozmiar: **524 288 bajtów (512 KB / 4 Mbit)** |
| **Mikrokontroler główny** | Siemens / Infineon C167 (16-bit) | Architektura procesora 16-bit |
| **Pamięć konfiguracji EEPROM**| 24C04 (SOIC8) | Zawiera dane Immobilizera (Immo 3), VIN, Softcoding |

---

### 2. ANALIZA I ZAWARTOŚĆ PLIKÓW PROJEKTOWYCH

#### A. Wsad Binarny: `cks ok` (Pulpit)
* **Wielkość:** 524 288 bajtów (512 KB).
* **Nagłówek w pamięci (offset `0x538D4`):**
  `074906018AJ 2,5l R5 EDC SG 3908 28SA5172 0281010461 EFCTE10FHEX074906018AJ 0301`
* **Status:** Przeliczona i spójna suma kontrolna (**Checksum OK**). Plik gotowy do bezpiecznego wgrywania przez złącze diagnostyczne OBD2 (MPPS, KESS v2, Dimsport Genius).
* **Tożsamość:** Plik `cks ok` jest w 100% bity w bity identyczny z plikiem `t4 stg1 - stg1 (1).bin` znajdującym się na pulpicie (0 bajtów różnicy).

#### B. Plik Definicji Map: `cks ok.xdf` (Pulpit)
* **Format:** Definicja map TunerPro XDF (wersja 1.1).
* **Autor:** Dilemma (`EDC15P XDF by Dilemma`).
* **Liczba zdefiniowanych tabel:** 778 bloków tabel, w tym 86 zmapowanych nazw dla dwóch bloków kodu:
  * **Codeblock 5** (zakres adresowy `0x04C000` – `0x05B000`)
  * **Codeblock 2 - skrzynia manualna** (zakres adresowy `0x06C000` – `0x07B000`)
* **Format kodowania danych:** 16-bit Little-Endian (Format Intel / LoHi).

#### C. Dokumentacja Dimsport: `Bosch_EDC15VM_VAG_PL.txt` (Katalog `d:\t4`)
* Polska transkrypcja oficjalnego przewodnika Dimsport Race dla sterowników EDC15VM+, zawierająca zalecenia i zakresy bezpiecznych zmian wartości parametrów dawkowań i ciśnień.

---

### 3. CROSS-REFERENCE: OZNACZENIA DIMSPORT ↔ MAPY TUNERPRO XDF

| Oznaczenie Dimsport | Nazwa mapy w dokumencie | Nazwa w pliku `cks ok.xdf` | Adres Codeblock 5 | Adres Codeblock 2 | Zastosowanie / Opis |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **B1** | Mapa wtrysku | **`Driver wish`** | `0x04CC36` | `0x06CC36` | Życzenie kierowcy – reakcja na pedał gazu (Pozycja pedału vs RPM ➔ Dawka mg/hub) |
| **LC** | Ogranicznik momentu | **`Torque limiter`** | `0x04D2FE` | `0x06D2FE` | Maksymalny moment obrotowy (RPM vs Dawka mg/hub) |
| **QS** | Ogranicznik dymienia | **`Smoke limiter (0°C, 15°C, 30°C)`** | `0x04D61C`<br>`0x04D7BC`<br>`0x04D95C` | `0x06D61C`<br>`0x06D7BC`<br>`0x06D95C` | Limit dawki paliwa w zależności od zassanego powietrza (MAF) |
| **BS** | Zadane doładowanie | **`Boost target map (1)`** | `0x056546` | `0x076546` | Docelowe ciśnienie turbosprężarki (IQ vs RPM ➔ mBar) |
| **BL / B3**| Ogranicznik doładowania | **`Boost limit map`** | `0x056B3C` | `0x076B3C` | Maksymalne dopuszczalne ciśnienie doładowania w f. ciśnienia atm. |
| **EG** | Recyrkulacja spalin | **`EGR 01`** | `0x055290` | `0x075290` | Mapa wysterowania zaworu N18 recyrkulacji spalin |
| **IS** | Początek wtrysku | **`Start of injection (SOI) -30°C do 71°C`** | `0x058A7C` do `0x059A3C` | `0x078A7C` do `0x079A3C` | Kąty wyprzedzenia wtrysku paliwa |
| — | Dawka rozruchowa | **`Start IQ (1 & 2)`** | `0x04CE70`, `0x04CF52` | `0x06CE70`, `0x06CF52` | Dawka paliwa przy rozruchu (dla tzw. Hot Start Fix) |
| — | Napięcie pompy VP37 | **`N146 Pump voltage map (1)`** | `0x054468` | `0x074468` | Wyskalowanie napięcia nastawnika pompy N146 w stosunku do dawki |
| — | Linearyzacja MAF | **`MAF linearization`** | `0x054A38` | `0x074A38` | Przelicznik napięcia przepływomierza G70 na mg/hub powietrza |
| — | Procedura startowa | **`Launch control map`** | `0x04C1C6` | `0x06C1C6` | Mapa kontroli procedury startu |

---

### 4. AUDYT POPRAWNOŚCI MODYFIKACJI W PLIKU `cks ok` (STAGE 1)

Wynik audytu: **MODYFIKACJA POPRAWNA, ZROBIONA ZGODNIE ZE SZTUKĄ I BEZPIECZNA**.

1. **Recyrkulacja Spalin (EGR OFF):**
   * Pod adresem `0x055290` i `0x75290` ustawiono stałą wartość **`8500` (85.0%)**.
   * **Efekt:** Zawór N18 zostaje trwale zablokowany w pozycji zamkniętej. Zapobiega zanieczyszczeniu dolotu nagarem i poprawia reakcję na gaz przy niskich obrotach.
2. **Ogranicznik Momentu Obrotowego (Torque Limiter):**
   * *Przebieg:* 1500 RPM (27.0 mg/hub) ➔ 1750 RPM (30.4 mg) ➔ 2000 RPM (38.4 mg) ➔ **2500–4000 RPM (40.00 mg/hub - płaska półka)**.
   * **Efekt:** Płynny wzrost momentu obrotowego chroniący koło zamachowe dwumasowe i sprzęgło przed przeciążeniem.
3. **Zadane Ciśnienie Doładowania (Boost Target):**
   * *Przebieg:* 1900 RPM (1850 mBar) ➔ 2000 RPM (1900 mBar) ➔ **2500–4000 RPM (1955 mBar)**.
   * **Efekt:** Bezpieczne podniesienie doładowania turbosprężarki Garrett VNT.
4. **Ogranicznik Ciśnienia Doładowania (Boost Limiter):**
   * Ustawiony na **`2190 mBar`** na poziomie morza.
   * **Efekt:** Margines **+235 mBar** powyżej ciśnienia zadanego (1955 mBar) eliminuje ryzyko wpadania silnika w tryb awaryjny (Notlauf / błąd `17965 / P1557`).
5. **Suma Kontrolna (Checksum):**
   * Status: **CKS OK (Przeliczona)**. Wsad jest gotowy do wgrania do autka.

---

### 5. PROCEDURA DIAGNOSTYCZNA VCDS — DIAGNOSTYKA TURBO DZIURY / TURBO LAG

Jeśli w pojeździe odczuwalna jest tzw. „turbo dziura” (opóźnione wstawanie turbiny), należy wykonać **logi dynamiczne w programie VCDS / VAG-COM**.

#### A. Wymagane Pakiety Grup do Logowania:

1. **Pakiet Główny (Doładowanie + Limitory Dawki): GRUPY `011` + `008`** *(Najważniejszy!)*
   * **Grupa 011:** Obroty RPM | Ciśnienie Zadane (mBar) | Ciśnienie Aktualne (mBar) | Wysterowanie N75 (%)
   * **Grupa 008:** Obroty RPM | Życzenie Kierowcy (mg) | Ogranicznik Momentu (mg) | Ogranicznik Dymienia MAF (mg)
   * *Cel:* Sprawdzenie, czy opóźnienie wynika ze zbyt wolnego wstawania turbiny, czy też uszkodzony przepływomierz MAF ogranicza dawkę paliwa.
2. **Pakiet Dolotu i Przepływki: GRUPY `003` + `011`**
   * **Grupa 003:** Obroty RPM | Masa Powietrza Zadana | Masa Powietrza Zmierzona (MAF g/s / mg) | Wysterowanie EGR
   * *Cel:* Ocenienie sprawności przepływomierza G70 oraz szczelności układu dolotowego.
3. **Pakiet Kąta Wtrysku i Pompy VP37: GRUPY `004` + `001`**
   * **Grupa 004:** Obroty RPM | Kąt Wtrysku Zadany | Kąt Wtrysku Aktualny | Wysterowanie N108
   * *Cel:* Sprawdzenie dynamicznego regulowania kąta wtrysku przez pompę VP37 pod obciążeniem.

#### B. Instrukcja Krok po Kroku do Wykonania Logu Dynamicznego:
1. Rozgrzej silnik do temperatury roboczej (**min. 80–90°C**).
2. Wyłącz klimatyzację i ogrzewanie ruszając na prosty i bezpieczny odcinek drogi.
3. Włącz **3. bieg** (lub 4. bieg w skrzyni manualnej).
4. Zwolnij do obrotów **1400 – 1500 obr./min**.
5. W VCDS otwórz bloki pomiarowe (`Engine 01` ➔ `Measuring Blocks 08`), wpisz numery grup **`011` i `008`**, kliknij **`LOG`** ➔ **`Start`**.
6. **Wciśnij pedał gazu na 100% w podłogę (WOT) i trzymaj BEZ PUSZCZANIA aż silnik osiągnie 4000 obr./min.**
7. Po osiągnięciu 4000 RPM puść gaz i kliknij **`Stop`**.

#### C. Interpretacja Wyników Logu w VCDS:
* **Problem z przepływomierzem (MAF):** W grupie `008` dawka z *Smoke Limiter* przy 2000 RPM jest bardzo niska (np. <30 mg), mimo wciśnięcia gazu w 100%. Auto nie przyspiesza, bo brakuje sygnału masy powietrza.
* **Problem ze zmienną geometrią VNT lub nieszczelność podciśnienia:** W grupie `011` ciśnienie zadane wynosi 1955 mBar, a ciśnienie aktualne do 2500 RPM osiąga np. tylko 1300 mBar. Zawór N75 idzie w max wysterowanie (np. 94.4%), próbuje zamknąć kierownice, ale układ podciśnienia nie reaguje.
* **Nieszczelność układu dolotowego (dziura w intercoolerze / wężach):** Przepływka w grupie `003` wskazuje ogromną masę powietrza (>1100 mg), ale w grupie `011` ciśnienie aktualne nie osiąga zadanej wartości, a auto dymi z rury wydechowej.

---
*Dokumentacja wygenerowana automatycznie w dniu 28.07.2026 r. na podstawie analizy binarnej i definicji XDF.*
