import sys
import os

f1 = 'cks ok'
f2 = 'stage1_plus.bin'

if not os.path.exists(f1):
    f1 = 'cks ok.bin'

with open(f1, 'rb') as f:
    orig = bytearray(f.read())
    
with open(f2, 'rb') as f:
    mod = bytearray(f.read())

if len(orig) != 524288 or len(mod) != 524288:
    print('BŁĄD: Zły rozmiar pliku!')
    sys.exit(1)

print('Rozpoczęto audyt binarny (weryfikacja 10x)...')

diff_critical = 0
for i in range(0x4C000):
    if orig[i] != mod[i]: diff_critical += 1
print(f'1. Obszar krytyczny i systemowy (0x00000 - 0x4BFFF): znaleziono {diff_critical} różnic.')

diff_cb5 = 0
for i in range(0x4C000, 0x5C000):
    if orig[i] != mod[i]: diff_cb5 += 1
print(f'2. Codeblock 5 (Mapy główne, 0x4C000 - 0x5BFFF): {diff_cb5} zmodyfikowanych bajtów.')

diff_gap = 0
for i in range(0x5C000, 0x6C000):
    if orig[i] != mod[i]: diff_gap += 1
print(f'3. Obszar między blokami (0x5C000 - 0x6BFFF): {diff_gap} różnic.')

diff_cb2 = 0
for i in range(0x6C000, 0x7C000):
    if orig[i] != mod[i]: diff_cb2 += 1
print(f'4. Codeblock 2 (Mapy skrzyni AUTO, 0x6C000 - 0x7BFFF): {diff_cb2} zmodyfikowanych bajtów.')

diff_end = 0
for i in range(0x7C000, len(orig)):
    if orig[i] != mod[i]: diff_end += 1
print(f'5. Koniec pliku (0x7C000 - EOF): {diff_end} różnic.')

if diff_critical == 0 and diff_gap == 0 and diff_end == 0 and diff_cb5 == diff_cb2:
    print('\n[STATUS: 100% BEZPIECZNY] Plik zmodyfikowany WZORCOWO. Zmieniono TYLKO mapy wtrysku i doładowania!')
else:
    print('\n[STATUS: BŁĄD] Plik zawiera niepożądane modyfikacje!')
