# Project Circle: przekazanie pracy nowemu czatowi Claude (stan na 14.11.2026)

> **Do Claude w nowym czacie:** pracujesz z Filipem nad jego grą **Project Circle**. Ten plik streszcza ~2 tygodnie wspólnej pracy. Przeczytaj go w całości, a dokumenty z folderu `docs/` czytaj wtedy, gdy temat ich dotyczy. Filip wgra Ci folder gry albo pojedyncze pliki.

---

## 1. Zasady pracy (ustalone z Filipem, trzymaj się ich)

- **Język:** z Filipem rozmawiasz **po polsku**. Komentarze w kodzie i teksty w grze (dialogi, UI, opisy) są **po angielsku**.
- **Nie wymyślaj kanonu.** Fabułę, nowe mechaniki, nazwy i treść najpierw **proponujesz**, kilka wersji naraz (najlepiej pytaniem z opcjami do wyboru), a Filip zatwierdza. Teksty dialogów pisane przez Claude to zawsze propozycja do poprawek.
- **Szanuj zmiany Filipa.** Filip często sam edytuje pliki, np. zmienia liczby w bazie wrogów. Zanim zmienisz plik, weź jego aktualną wersję i nanieś swoją zmianę na nią. Nigdy nie nadpisuj jego wersji starszą.
- **Styl kodu:** Clean Code. Krótkie funkcje z nazwami, które mówią, co robią, i nazwane stałe zamiast „magicznych liczb”. Komentarz z datą przy zmianie, np. `# (13.11) ...`. Pliki `.py` mają końce linii **CRLF** (Windows). Po zmianie sprawdź składnię (`python -m py_compile`).
- **Testuj** zmiany przed oddaniem: uruchom grę bez okna (SDL dummy), zasymuluj sytuację, zrób zrzut ekranu i obejrzyj go.
- **Raport po każdej zmianie:** krótko, co zmienione i w których plikach.
- **Dokumenty projektu** (folder `docs/`) aktualizuj, gdy zmieniasz system, który opisują.
- **Dialogi i voice lines:** po zmianie linii dialogów uruchom `python tools/voicelines.py`. Nadaje ID liniom i odświeża `VOICELINES.md`.
- **Sprzątanie po testach:** testy tworzą `game/text/achievements.json`, `save1.json`, `save3.json` i `settings.json`. Nie zostawiaj ich w kodzie oddawanym Filipowi.
- Gdy plik trzeba **usunąć**, napisz Filipowi który, a on usunie go sam.
- **Pytania:** gdy decyzja należy do Filipa, zadaj krótkie pytanie z kilkoma opcjami i zaznacz polecaną.

---

## 2. Gra w skrócie

- **Gatunek:** bullet hell + RPG. Eksploracja świata z kafli, losowe walki w osobnym ekranie, bossowie przed przejściami między biomami.
- **Technika:** Python + **pygame-ce**. Start: `main.py` (build `.exe`: `main.spec`). Rozdzielczość bazowa 1920×1080.
- **Świat z seeda:** 4 poziomy generowane z jednego seeda (`game/world/`):
  - **Surface:** Village (stały środek) → Rainbow Fields → Sugarwood Grove (Candy) → odcięta wioska → Silverpine Tundra → Tundra Pass. Lunapark to osobna mała mapa (wejście w Sugarwood).
  - **Cellar:** ogromny Underground Garden z Toy Factory w środku (hale, taśmociągi).
  - **Core:** „mechaniczne serce”. Na końcu stała komnata z rdzeniem i Milo.
  - **Void:** labirynt z wysp i mostków.
  - **Pale World:** blade odbicie świata, wejście przez glitch stones z **Pale Orb**. Pod nim labirynt Nowhere → Nowhere 2 → **###**.
- **Bossowie:**
  - Slime King (Village), Prism (Rainbow), Shroom Mother (Candy), Frost Golem (Tundra), Assembly Line (Factory), Night Bloom (Garden).
  - Mascot: walka do piosenki w Lunaparku, opcjonalna.
  - **Milo** (Core) i **Void** (ostatni, 5 faz + interludium + finał do muzyki).
  - Szczegóły: `docs/BOSSES.md`, `BOSS_MILO.md`, `BOSS_VOID.md`.
- **Zakończenia:**
  - Milo pokonany **bez Peace Gun** → Main Ending (pętla: budzisz się w wiosce, stąd „Circle”).
  - Milo pokonany **z Peace Gun** → otwiera się Void. Void → Extra Ending.
  - **Secret Ending**: wymaga użycia 3 lore itemów przy NPC (`docs/LORE_ITEMS.md`).
- **Peace Gun** leży w **###** (dno labiryntu Pale World).

### Klawisze testowe (wyłączyć przed wydaniem)
- `1`–`9` i `-`: teleport do stref.
- `0`: itemy fabularne i wszystkie sigile.
- `F`: walka.
- `F9`: następna faza bossa.
- `F5`: przeładuj sprite'y.
- `'` na mapie M: odkryj cały poziom.

---

## 3. Systemy (gdzie co jest)

| system | pliki | uwagi |
|---|---|---|
| główna pętla, stany, zapis gry | `game/game.py`, `game/states.py`, `game/menu/save_manager.py` | autozapis po bossie, portalu, wyjściu do menu i co 3 min |
| walka | `game/combat/combat.py`, `enemy/enemy.py`, `enemy/enemy_database.py`, `player/shooter.py`, `projectile.py`, `rooms.py` | wrogowie, ataki, fazy bossów, dropy (`EnemyDB.drops`), pokoje z przeszkodami |
| poziom trudności | `game/difficulty.py` | **Easy „I Have a Job”**: −25% obrażeń, wolniejsze ataki, −1 wróg, mniej pocisków. Normal. **Hard**: bossowie +33% HP, `hard_tweaks` w danych bossów |
| mapa | `game/map/map.py`, `map_ui.py`, `world_map.py` (mapa M), `player.py` | przyciski na mapie: Inventory, Shop, Bestiary, Menu (ESC) |
| generatory świata | `game/world/*` (`surface_map`, `cellar_map`, `core_map`, `void_map`, `lunapark_map`, `pale_world`, `hash_room`, `tiles`, prefaby w `prefabs/`) | prefaby to pliki tekstowe, mody w `mods/` (`MODDING.md`) |
| dialogi | `game/dialogue/` (JSON w `data/`, `speakers.py`), voice lines `game/lib/voicelines.py` | pełny ekran, jedna postać na środku, linie mają ID, nagrania w `assets/sfx/voicelines/<kto>/<id>` |
| sklep | `game/shop/` | sklepikarz w środku, buyer od startu, rerolle |
| ekwipunek, sigile | `game/inventory/` (`item_database.py`, `sigils.py`) | 16 miejsc, `docs/SIGILS.md` |
| osiągnięcia | `game/achievements/` | 67 osiągnięć, globalne (`game/text/achievements.json`), postęp per zapis, `docs/ACHIEVEMENTS.md` |
| Bestiary | `game/bestiary/` | przycisk na mapie. Etapy: 1/5/15 pokonań (boss: 1). Na etapie dropów od razu widać wszystkie dropy z % (14.11). Pola: HP, Defence, Touch, Shots, Kind |
| statystyki | `game/stats/` | ESC → Stats, 4 karty |
| ustawienia | `game/menu/settings_screen.py`, `options.py`, `game/controls.py` | Audio / Video / Controls / Gameplay |
| minigry | `game/minigames/` | sudoku, memory, koło Lucky'ego |
| sprite'y | `game/lib/sprites.py` (loader), `game/combat/sprites.py` (walka) | patrz punkt 5 |

---

## 4. Najnowsze zmiany (13–14.11)

- **Ferris:** gdy nie stać cię na skrót, w okienku mapy pojawia się „Shortcuts cost. Come back richer.” z jego głosem: nagranie `ferris_05` albo jego dźwięk mówienia.
- **Bestiary:**
  - przeniesiony z menu ESC na przycisk na mapie, obok Shop;
  - dodane pole Defence;
  - dropy widać od razu na etapie 15 pokonań (boss: 1).
- **Eyeballs:** dropi je **Tundra Watcher (5%)**. Wcześniej nie było ich skąd zdobyć.
- **### (bicie serca):** pod podłogą śpi serce Core.
  - Co 2,6 s słychać uderzenie, głośniejsze przy środku, a na podłodze pulsuje czerwone światło.
  - Napis na podłodze zmienia się przy każdej wizycie: „Not yet.” → „Still asleep.” → „Not off. Asleep.” → „It heard you.”, potem od początku.
  - Kod: `game/world/hash_room.py`.
- **Przedmioty na ziemi** zostają, gdy ekwipunek jest pełny. Pojawia się napis „Inventory full - make room to pick it up”.
- **Walka z Voidem:**
  - zanim boss się pojawi, nie da się zejść z wyspy;
  - w F2, gdy boss wyskakuje w górę, strzałka przy krawędzi ekranu pokazuje, gdzie wyląduje. Wcześniej pokazywała lewy górny róg.
- **Sprite'y:** lista i opisy w `SPRITES.md`. Walka już wczytuje grafiki (punkt 5).

---

## 5. Sprite'y (w toku)

- **`SPRITES.md`** (w folderze gry) to pełna lista grafik do narysowania: walka, mapa, kafle per biom z wariantami i podłożem, budynki, NPC i rozmiary w pikselach. Każdy folder w `assets/img/...` ma `_README.txt`.
- **Styl:**
  - walka: **pixel art, widok 3/4 (od góry po skosie)**, gra powiększa ×2; **podłogi walki ×4** (plik 64×64 → 256×256);
  - mapa: styl rysowany, kafel 128×128;
  - gracz: 8 kierunków (`n, ne, e, se, s, sw, w, nw`) w walce i na mapie.
- **Gra już wczytuje (walka):**
  - gracz (8 kierunków + klatki chodu);
  - wrogowie i bossowie (fazy `_f2`, odbicie lewo/prawo);
  - podłogi z wariantami;
  - przeszkody: filary w 3 rozmiarach, ściany z kawałków;
  - lodowa ściana Frost Golema;
  - Bestiary bierze sprite z walki.
  - Brak pliku = stary wygląd (koło/kolor).
- **Jeszcze nie podpięte:**
  - cała **mapa**: kafle z wariantami i podłożem, gracz, NPC, obiekty;
  - **budynki z dachem znikającym**, gdy gracz wejdzie do środka (decyzja Filipa);
  - reszta obiektów walki: taśma, nasiona światła, lampion, wieżyczki i broń w Void, mina Milo;
  - podłoga Voida.

---

## 6. Do zrobienia i otwarte sprawy

- Podpiąć sprite'y mapy (punkt 5), gdy Filip zacznie je wrzucać.
- Filip ma usunąć stary nieużywany plik `game/menu/achivements.py`.
- Treść wyspy Milo w Pale World (Village). ### jest już zrobione.
- Przed wydaniem: wyłączyć klawisze testowe (`DEBUG_*` w `game.py` i `world_map.py`).
- Teksty do zatwierdzenia przez Filipa: monolog Voida, linie ###, część dialogów.
- Szerszy plan: `ROADMAP.md`. Pomysły, o których rozmawialiśmy ostatnio:
  - tryb New Game+ / boss rush;
  - codzienny seed;
  - więcej struktur;
  - dźwięki do UI.

---

## 7. Dokumenty

**W folderze gry** (aktualne, wgrane na komputer Filipa):
- `ROADMAP.md`
- `SPRITES.md`
- `VOICELINES.md`
- `MODDING.md`

**W paczce `docs/`** (kopie z projektu Claude):
- `ACHIEVEMENTS.md`
- `BESTIARY.md`

**Jeszcze w projekcie „Project circle” na claude.ai.** Filip, skopiuj je, zanim stracisz dostęp: otwórz projekt, otwórz każdy plik i zapisz jego treść w folderze `docs/`.
- `DECISIONS.md`: decyzje autora, najważniejsze.
- `BOSSES.md`: wszyscy bossowie i ich fazy.
- `PALE_WORLD.md`: Pale World, labirynt i ###.
- `STORY.md`: fabuła, NPC, zakończenia.
- `LORE_ITEMS.md`
- `BOSS_MILO.md`
- `BOSS_VOID.md`
- `SIGILS.md`
- `BALANCE.md`: liczby HP i obrażeń.
- `SHOP_LINES.md`

`CHANGELOG.txt` w paczce to pełna lista zmian (229 commitów), od najnowszych.
