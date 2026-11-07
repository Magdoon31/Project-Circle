# Project Circle — lista potencjalnych zmian

> Roboczy plan rozwoju. Nic tutaj nie jest zatwierdzonym kanonem — to propozycje do omówienia.
> Stan kodu: 2 listopada 2026 (po etapie C: Core + Void).

Legenda priorytetu: **[P1]** zrobić najpierw · **[P2]** ważne · **[P3]** później / opcjonalne
Szczegóły zrobionych rzeczy i decyzje: `DECISIONS.md` (w projekcie), modowanie: `MODDING.md`.

---

## 0. Zrobione od ostatniej wersji (skrót)

- [x] **Świat z seeda** — zamiast map z plików: 4 poziomy generowane z jednego seeda (`game/world/`):
  - **Surface** — wioska (stały środek), Rainbow Fields, Candy, odcięta wioska, Tundra, Tundra Pass; klify, przejścia `||` z bossami, drogi, struktury.
  - **Cellar** — Underground Garden (ogromna jaskinia) z Factory jako kwadratowym blokiem (hale + korytarze, taśmociągi).
  - **Core** — "mechaniczne serce": hale + chaotyczne korytarze, stała końcówka z rdzeniem i Milo.
  - **Void** — labirynt z wysp i mostków, który nie wygląda jak labirynt.
- [x] Biom gracza = kafelek pod graczem (muzyka i przeciwnicy za nim idą); kafelki wspólne dla biomów, kolor zależy od biomu.
- [x] Portale między poziomami, stan per poziom (zebrane, pokonani, odkryte) w zapisie.
- [x] **Bossowie:** budynek bossa przy każdym `||` (wszystkie różne), boss1 tymczasowo wszędzie. Pokonany boss otwiera przejście **na stałe**, ale sam **wraca** przy następnej zwykłej walce.
- [x] **Mapa świata (M)** — pokazuje tylko zobaczone miejsca, zoom/przesuwanie, **zakładki innych poziomów** (Tab / Q / E / klik), % odkrycia liczony tylko z osiągalnych kafelków. W Void mapa **zapomina** po 60 s (Eyeballs: 15 min), boss Void zawsze widoczny.
- [x] Struktury (prefaby w plikach tekstowych) z itemami, złotem, NPC; **mody**: `mods/structures`, `mods/bosses`.
- [x] Płynny ruch (przyspieszenie/tarcie), ucieczka z walki (trzymanie R), overlay ciemności (Factory 1×, Garden 2×, Void 3×).
- [x] Drop z przeciwników: `EnemyDB.drops` (np. slime_big → Shrooms), `Combat.kill_enemy`, `Game.give_items`.
- [x] **Dialogi + pierwszy quest** (Milo, Angler, Bramble/sudoku, Dot/memory, Wanderer/mapa), lista questów pod przyciskiem Menu, minigry z odliczaniem i rosnącą ceną.
- [x] **Fabuła (szkielet):** Milo w Core — z Peace Gun otwiera Void, bez → tymczasowy *Main Ending*. Boss Void → tymczasowy *Extra Ending* (Secret Ending czeka na lore itemy przy NPC).
- [x] Klawisze testowe: 1–9 i `-` teleport do stref, 0 = itemy fabularne, `'` na mapie M = odkryj cały poziom.

---

## 1. Do sprawdzenia po poprawkach (balans)

- [✓] `death_spiral` używa teraz `bullets` z danych (rainbow_slime: 4 zamiast 12 pocisków, frozen_orb: 16, liche/fly/generator itd. też się zmieniły).
- [✓] `throw` i `mine` nakładają teraz efekty z danych (sugar_caster daje graczowi `speed`, robo-bomber podpala).
- [✓] Minigun (pixie, boss1) strzela 2× częściej — zgodnie z cooldownem w danych.
- [✓] Berserk i Guard działają teraz zgodnie z opisem (wcześniej Berserk *zmniejszał* obrażenia o 85%).
- [✓] Samurai Armor: dodana odporność na slow i bind (zgodnie z opisem).
- [✓] Boss1 minigun ma `spread = 0` (prosto w gracza) — może warto dać 10–20°.
- [ ] Nowe poziomy do przegrania w grze: wielkość Core / Void, ilość złota (`GOLD_PILES`), częstość walk (`ENCOUNTER_CHANCE`), czas pamięci mapy w Void (`MAP_MEMORY_MS`).

---

## 2. Porządki techniczne

- [x] **[P1] Ładowanie zasobów raz** *(`game/combat/combat_assets.py`)*.
- [x] **[P2] Ekwipunek > 16 itemów** *(limit 16, nadmiar → pieniądze, Unequip zablokowany przy pełnym)*.
- [x] **[P2] „Remove” z potwierdzeniem** *(okienko Remove / Cancel)*.
- [x] **[P2] Pozycja po przegranej** *(powrót na start wioski na Surface)*.
- [ ] **[P1] Commit w gicie** — czysty punkt odniesienia (dużo zmian od ostatniego).
- [x] **[P1] Seed przy nowym zapisie** *(pole na stronie trudności: dowolny tekst albo liczba, puste = losowy; zapis trzyma też wpisany tekst `seed_text`)*.
- [ ] **[P3] Seed na stronie Stats** w menu w grze.
- [x] **[P2] Autozapis** *(po wygranej z bossem, po przejściu przez portal, przy wyjściu do menu głównego i co 3 min chodzenia — `AUTOSAVE_MINUTES` w `game.py`; napis „Saving...” w lewym dolnym rogu)*.
- [ ] **[P2] Dane stop_move do poprawy** — candy_shroom `[60,32]` przy cooldownie 1.5 s i sugar_caster `[48,12]` przy 0.8 s stoją prawie cały czas (przed + po ≥ cooldown).
- [ ] **[P3] Tooltip broni** — „Fire Rate: 0.25” to cooldown. Pokazać strzały/s albo bazowy DPS.
- [ ] **[P3] Opis Eyeballs** — dopisać, że pomagają pamiętać Void (efekt `map_memory` już działa).
- [ ] **[P3] Niezaimplementowane efekty z danych:** `luck`, `angler`, `reveal_secret`, `pale_world`, lore itemy.
- [ ] **Przed wydaniem:** wyłączyć klawisze testowe (`DEBUG_BIOME_KEYS`, `DEBUG_STORY_ITEMS_KEY` w `game.py`, `DEBUG_REVEAL_KEY` i `DEBUG_CLICK_TELEPORT` w `world_map.py`).

---

## 3. Świat i fabuła

- [ ] **[P1] Skąd Peace Gun i 3 lore itemy** (Broken Bulb, Cassette Tape, Old Note) — do ustalenia; teraz tylko klawisz 0.
- [ ] **[P1] Lore itemy przy NPC** — Cassette Tape: od Hala, użycie u Wren ✔. Zostały Broken Bulb (Foreman?) i Old Note (Milo w Void).
  - *(pomysł autora)* — każdy trzeba *użyć* przy jakimś NPC w trakcie gry; to ustawia flagę `lore_used:<item>`, komplet 3 → Secret Ending.
- [x] **[P1] Dialogi NPC** — zrobione: Milo (wszystkie miejsca do Core), wioska, Sunny, Gus, Hal, Foreman, Oliver, Wren, Gardener, krąg grzybów. Zostało: Milo w Core/Void, zakończenia. Było: szkielet rozmów (NPC są już na mapie jako „?”: foreman w Factory, Milo w kapliczce Void, …).
- [ ] **[P2] Prawdziwe zakończenia** — Main / Extra / Secret są teraz tymczasowymi ekranami.
- [ ] **[P2] Pale World** — przełączanie wersji mapy (osobna warstwa kafelków), na tym oprą się sekretne przejścia (`reveal_secret` w Eyeballs).
  - **Straszny głos Milo** (`voice: scary`, czarne tło, cisza) — zostawić na Pale World i tam niech trwa **dłużej niż jedną kwestię** (cała scena). W kłótni Wren × Milo go już nie ma.
- [ ] **[P2] Więcej struktur** — zwłaszcza Surface i Garden (format w `MODDING.md`).
- [ ] **[P3] Nazwy i wygląd bossów** zamiast boss1 (każdy budynek bossa już jest inny).
- [ ] **[P2] Lunapark** — mini-biom Candy na osobnej mapie (wejście w Candy jak do Factory), wielkość ≈ separated village, własna muzyka, trochę złota, **NPC od hazardu** (stawiasz złoto albo przedmioty). Bez własnej mapy M — pokazuje mapę Surface.
- [ ] **[P2] Więcej NPC tylko pod questy** — żeby było więcej chodzenia w różne miejsca (część z nagrodą-mapą biomu, część z wyborem nagrody).
- [x] **[P2] Milo zmienia miejsce po bossach** (wioska → Rainbow → Candy → separated village → wejścia do Garden → przed Core) z dialogami; wybór drogi Factory/Tundra zamyka drugą drogę do bossa wybranej.
- [x] **[P2] NPC tracący cierpliwość** (Gus) po ~10 rozmowach (może dać quest na dobry item).
- [ ] **[P2] Niegrzeczność** → ceny +20 pp za każdego obrażonego NPC (kilku NPC) + trudne przeprosiny (STORY.md).
- [ ] **[P3] Struktury, do których trzeba coś zrobić, żeby wejść.**
- [ ] **[P2] NPC sprzedający teleporty do biomów** (jak testowe klawisze 1, 2, 3…) — pomysł autora.
- [ ] **[P2] Cutscenki zakończeń** (każde zakończenie: scenka + dialog/monolog, z voiceoverem autora). Milo w Core: dialog przed i po walce.
- [x] **[P2] NPC w biomach po kolei** (jeden na raz, z feedbackiem): Sunny (Rainbow) → Gus (Candy) → Hal (Tundra, minigra „połącz kable” w antenach → Cassette Tape) → Foreman (Factory, własny quest). Hazard: dopiero w lunaparku.
- [x] **[P3] Dźwięki minigier** — pliki w `assets/sfx/minigames/` (countdown, go, flip, match, wrong, write, win, lose); do tego czasu zastępcze dźwięki z gry.

---

## 4. Pozyskiwanie itemów — „item gathering”

**Pomysł autora:** po walce, na ekranie przejścia (transition screen) pokazuje się nazwa nowej broni/itemu. Po powrocie na mapę ikona itemu pojawia się i powoli znika.

- [x] **Kolejka nagród** — `Combat.loot` zbiera dropy, `Game.give_items` dodaje je po wygranej.
- [x] `Game.give_item(item)` — jedno wejście dla nowych itemów (pełny ekwipunek → $ + komunikat). Używają go już itemy leżące na mapie.
- [ ] **Ekran wygranej** (`Combat.draw`, sekcja `if self.win`) — pod kwotą pieniędzy linia „New item: *Nazwa*”. Przy kilku itemach — lista.
- [ ] **Animacja na mapie** — ikona nad graczem przez ~1,5 s lekko unosi się i zanika. Kilka itemów — po kolei.
- [ ] Dźwięk zdobycia itemu (np. istniejący `gain_effect`).
- [ ] Ten sam mechanizm dla sklepu i sekretów.

---

## 5. Sklep

W assetach jest już muzyka `shop`.

- [ ] **[P2] Sklep na mapie** (potrzebny do questa Foremana: Meter jest „ze sklepu”, na razie klawisz 0) — struktura z NPC-sklepikarzem; wejście zmienia stan na `GameState.SHOP`.
- [ ] **Asortyment per biom** — część itemów z biomu (3–5 losowych, odświeżanych po bossie albo co X walk). Część itemów *tylko* ze sklepu, część *tylko* z dropu.
- [ ] **Ceny** — punkty „p” z komentarzy w `item_database.py`: `cena = p × mnożnik biomu`. Warto przenieść „p” do danych (pole `power`).
- [ ] **Sprzedaż** — zamiast „Remove”: sprzedaż za np. 30–40% ceny.
- [ ] **Do ustalenia:** czy sklepikarz ma dialogi (lore, zmiana w Pale World)?

---

## 6. Item drop z przeciwników

- [x] **Tabela dropów per wróg** — `EnemyDB.drops` (nazwa itemu + szansa), losowane przy śmierci wroga (`Combat.kill_enemy`).
- [ ] Uzupełnić tabelę dla pozostałych wrogów.
- [ ] Opcjonalnie **tabela per biom** — szansa na „jakikolwiek item z biomu” po walce (`loot.ITEMS_BY_BIOME` już istnieje).
- [ ] Bossowie: gwarantowany drop (1 z puli bossa) + szansa na drugi. Uwaga: bossowie się odradzają — drop tylko za pierwszą wygraną albo mniejszy za kolejne?
- [ ] Ochrona przed duplikatami (opcjonalnie).
- [ ] Hard mode: trochę wyższa szansa na drop.

---

## 7. Luck

Efekt `luck` istnieje w danych (trinket **Dices**: `{"luck": [1]}`), ale nic nie robi. Autor: dropy mają mocno zależeć od luck.

- [ ] Wartość `luck` z trinketu (ewentualnie zbroi), przekazywana do `roll_drops`.
- [ ] Formuła do ustalenia, np. `szansa = bazowa × (1 + 0.5 × luck)` albo mocniej.
- [ ] Opis Dices zaktualizować na konkretny.

---

## 8. Ciekawe bossfighty

Obecnie boss to zwykły `Enemy` z kilkoma atakami na cooldownach (`boss1` jest testowy i stoi we wszystkich miejscach bossów).

### 8.1. Mechaniki silnika (najpierw)

- [ ] **[P1] Fazy** — boss zmienia zestaw ataków po progach HP. Dane: `"phases": [{"hp": 1.0, "attacks": {...}}, {"hp": 0.5, "attacks": {...}}]`. Przejście fazy: krótka nietykalność, wyczyszczenie pocisków, efekt/dźwięk.
- [ ] **Wzorce ataków (patterns)** — sekwencje zamiast niezależnych cooldownów.
- [ ] **Nowe typy ataków** — obrotowa spirala, ściana z luką, laser z ostrzeżeniem, szarża, pociski dzielące się, strefy na ziemi.
- [ ] **Telegrafowanie** mocnych ataków.
- [ ] **Areny** — inne tło / przeszkody per boss.
- [ ] **Nazwa bossa nad paskiem HP** (w danych mapy są już nazwy `Milo`, `Void`).

### 8.2. Nagrody

- [ ] Gwarantowany drop z puli bossa (pkt 6) + pokazanie go na ekranie item gathering (pkt 4).
- [x] Odblokowanie dalszej drogi na mapie.
- [ ] Osiągnięcia za bossów (np. bez obrażeń, w hard mode).

---

## 8b. Walka — do zrobienia (6.11)
- [x] *(7.11: split, pulse, wall, sprinkler, line, wave, `repeat`, throw + pierścień, pełzające miny — opis typów na górze `enemy.py`, tabela w BALANCE.md)* **Lepsze ataki przeciwników** w stylu Enter the Gungeon: np. rosnące koło pocisków, które rozszerza się falami „2 kroki do przodu, 1 do tyłu”; więcej wzorów do czytania i unikania zamiast pocisków lecących prosto w gracza.
- [x] *(7.11: test z botem unikającym — nowe wzory do uniknięcia; zostają: dotyk biegaczy, granat robo-bombera, miny scrap_beetle)* Ataki, których nie da się uniknąć — przejrzeć i poprawić (za szybkie / za gęste / bez przerw).
- [ ] Zbroje + HP gracza + obrażenia wrogów („za szybko umieram”).
- [ ] Bossy (teraz wszędzie boss1, 900 HP).
- [ ] Sekrety, które dają Sigile (11 sztuk).
- [ ] Dystrybucja itemów (najsłabsze łatwo, najlepsze rzadko) + ceny wg weight.

## 9. Proponowana kolejność

1. Commit w gicie.
2. Dialogi NPC → lore itemy przy NPC → skąd Peace Gun (fabuła domyka zakończenia).
3. Item gathering + dropy + luck (jeden system nagród).
4. Sklep.
5. Fazy i wzorce ataków bossów → pierwszy prawdziwy boss (Village) jako test systemu.
6. Pale World i sekretne przejścia.
