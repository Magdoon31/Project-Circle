# Project Circle: lista przed wydaniem (release)

Spisane z kodu 23.11.2026. Przy każdym releasie przejdź od góry do dołu. Gdy dodajesz nową rzecz testową, dopisz ją tutaj.

## 1. Klawisze i funkcje testowe: wyłączyć

| co | gdzie | jak wyłączyć |
|---|---|---|
| Teleport do stref (`1`–`9`, `-`), itemy fabularne i sigile (`0`), walka (`F`), walka testowa (`T`, `Shift+T`), następna faza bossa (`F9`) | `game/game.py` | `DEBUG_BIOME_KEYS = False` (wszystkie te klawisze siedzą pod tą jedną flagą) |
| Odkrycie całego poziomu (`'` na mapie M) | `game/map/world_map.py` | `DEBUG_REVEAL_KEY = False` |
| Teleport prawym kliknięciem na mapie M | `game/map/world_map.py` | `DEBUG_CLICK_TELEPORT = False` |
| Przeładowanie sprite'ów (`F5`) | `game/game.py`, `RELOAD_SPRITES_KEY` | nie ma flagi, działa zawsze; zdecyduj, czy zostaje (graczowi nie szkodzi) |
| Testowy Milo z testowym dialogiem | `game/world/surface_map.py` | `TEST_DIALOGUE_NPC = False` (już jest `False`) |

## 2. Rzeczy tymczasowe w danych: zdecydować

- [ ] `STORY_ITEMS` w `game/game.py`: `"Meter"` jest tam „TEST ONLY until the shop exists”. Gdy Meter będzie w sklepie, usuń go z listy.
- [ ] Skąd naprawdę biorą się itemy fabularne i sigile (`0` daje je testowo). W `game/inventory/sigils.py` sekrety są wciąż „to be designed”.
- [ ] Pokój testowy w `game/combat/rooms.py` (`TEST_ROOM`…) i `start_test_fight()` w `game.py`: mogą zostać, bo bez `DEBUG_BIOME_KEYS` nic ich nie wywołuje. Albo usuń.
- [ ] Testowy dialog: `game/dialogue/data/test_milo.json` i wpis `"milo_test"` w `game/dialogue/speakers.py`. Do usunięcia razem z blokiem `TEST_DIALOGUE_NPC` w `surface_map.py`.

## 3. Pliki i foldery: nie wrzucać do wydania

| co | dlaczego |
|---|---|
| `game/text/save*.json`, `settings.json`, `achievements.json` | Twoje zapisy, ustawienia i osiągnięcia; gracz ma zacząć od zera |
| `Claude outputs/` | podglądy i obrazki robocze |
| `backups/` | kopie zapasowe (zip ponad 50 MB) |
| `build/`, stare `main.exe` | pozostałości po PyInstallerze; exe buduj na czysto |
| `handoff/` | paczka przekazania dla Claude |
| `tools/` (z `tools/output/`) | skrypty deweloperskie (podglądy map, generatory ikon i płotka, voicelines) |
| `wiki_assets/` | obrazki do wiki |
| wszystkie `__pycache__/` | skompilowany Python, odtworzy się sam |
| `.git/`, `.gitignore` | repozytorium |
| `SPRITES.md`, `VOICELINES.md`, `ROADMAP.md`, `RELEASE_CHECKLIST.md`, `game/dialogue/README.md` | dokumenty robocze; `MODDING.md` i `mods/` mogą zostać, jeśli mody mają być dla graczy |

## 4. Build: sprawdzić

- [ ] **Folder `game/text` musi istnieć** w wydanej grze. Git nie zapisuje pustych folderów, a gra sama go nie tworzy (błąd `No such file or directory: 'game/text/save1.json'` z 22.11). Najlepiej poprawić `game/menu/save_manager.py`, żeby tworzył folder przed zapisem.
- [ ] **Ścieżki liczą się od folderu uruchomienia**, nie od folderu gry. Skrót z innym „Rozpocznij w” wywali grę. Do poprawy razem z punktem wyżej.
- [ ] `main.spec` ma `datas=[]`: exe nie zawiera `assets/` ani `game/text`. Dołącz je do `datas` albo wydawaj exe razem z folderem `assets/` obok.
- [ ] Zbuduj exe od nowa (`pyinstaller main.spec`) i uruchom go na czysto, z innego folderu: nowa gra, walka, autozapis, wczytanie zapisu, ustawienia.
- [ ] `console=False` w `main.spec` zostaje (bez czarnego okna).

## 5. Grafika i dźwięk zastępcze: sprawdzić, czy już są prawdziwe

Gra działa bez nich, tylko rysuje zastępstwa:
- sklep (tło, sklepikarz, buyer): `game/shop/shop.py`, `PLACEHOLDER`;
- postacie w dialogach (figura z nazwą pozy): `game/dialogue/dialogue.py`;
- muzyka do dialogów i brakujące utwory (gra puszcza zamiennik): `game/lib/music_manager.py`;
- itemy bez obrazka (kwadrat z „?”): `game/inventory/items/item_database.py`;
- pluszak-wabik: `game/combat/combat_assets.py`;
- sprite'y z listy w `SPRITES.md`, których jeszcze nie ma.

## 6. Ostatnie sprawdzenie

- [ ] `python -m py_compile` na wszystkich plikach `.py`.
- [ ] Szukanie w kodzie słów `TEST`, `DEBUG`, `PLACEHOLDER`: każde trafienie jest świadomie zostawione.
- [ ] Tytuł gry, wersja, napisy końcowe (`game/story/credits.txt`).
