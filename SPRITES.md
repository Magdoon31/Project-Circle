# Sprite'y – lista i opisy (13.11)

Każdy folder ma też plik `_README.txt` z tą samą listą. Brakujący plik = gra rysuje jak dotąd (kształt/kolor), więc możesz wrzucać sprite'y pojedynczo. **F5** w grze wczytuje grafiki od nowa (bez restartu).

**Co gra już wczytuje (13.11):** walka – gracz (8 kierunków + klatki chodu), przeciwnicy, bossowie (z fazami), podłogi (z wariantami), przeszkody (filary 3 rozmiary, ściany z kawałków), lodowa ściana Frost Golema; Bestiary bierze sprite z walki, gdy nie ma własnego obrazka. **Jeszcze nie:** mapa (kafle, gracz, NPC, obiekty, budynki) i reszta `combat/objects` (taśma, nasiona światła, lampion, wieżyczki i broń w Void, mina Milo), podłoga Voida.

**Widok w walce: od góry po skosie (3/4)** – widać przód postaci. Postać stoi stopami na dole swojego koła (hitboxu), głowa może wystawać ponad nie. Przeciwnika gra sama odbija lewo/prawo, w stronę, w którą idzie (rysuj go patrzącego w prawo). Filar/ściana: kolizja to podstawa, górna część może wystawać w górę. Pociski i podłogi – czysto z góry.

**Styl:** walka = pixel art (rysuj w skali 1:2, gra powiększy ×2 bez wygładzania), mapa = rysowany (gra zmniejsza z wygładzaniem). Wszystko PNG z przezroczystym tłem (oprócz podłóg i kafli ziemi).

## WALKA – `assets/img/combat/`

Rozmiar „na ekranie” = średnica hitboxa w 1080p. Plik pixel art = połowa (gra ×2). Rysunek może trochę wystawać poza okrąg (ok. ×1.2).

### Gracz – `combat/player/`  (pixel art, 8 kierunków)

Na ekranie ~50×50 px → plik **25×25** (albo 32×32 z marginesem). Pliki: `n.png`, `ne.png`, `e.png`, `se.png`, `s.png`, `sw.png`, `w.png`, `nw.png` – kierunek, w którym gracz idzie (n = w górę ekranu). Opcjonalnie animacja chodu: `<kierunek>_1.png`, `<kierunek>_2.png`…

### Przeciwnicy – `combat/enemies/<id>.png`  (pixel art)

| plik | gdzie | na ekranie | plik (1:2) | jak ma wyglądać |
|---|---|---|---|---|
| `slime_small.png` | Village | 36×36 | 18×18 | Mały zielony glut, błyszczący, prosta buzia. Skacze na gracza. |
| `slime_big.png` | Village | 72×72 | 36×36 | Duży zielony glut, w środku widać 2–3 małe gluty (po śmierci się rozpada). |
| `shooter.png` | Village | 44×44 | 22×22 | Mały człowieczek z prostą procą/pistoletem, trzyma dystans. |
| `rainbow_slime.png` | Rainbow Fields | 48×48 | 24×24 | Glut z tęczowymi pasami w środku, lekko przezroczysty. |
| `flower_spitter.png` | Rainbow Fields | 46×46 | 23×23 | Kwiat z otwartą „paszczą” w środku, z której pluje nasionami; liście jak nóżki. |
| `rainbow_guard.png` | Rainbow Fields | 60×60 | 30×30 | Strażnik w tęczowej zbroi/hełmie z krótką strzelbą. |
| `gum_goblin.png` | Sugarwood Grove | 52×52 | 26×26 | Goblin z różowej gumy do żucia, nadmuchany balon gumy przy pysku. |
| `candy_shroom.png` | Sugarwood Grove | 48×48 | 24×24 | Grzyb z cukierkowym kapeluszem w kropki (lukier), kręci się w miejscu. |
| `toffee_runner.png` | Sugarwood Grove | 36×36 | 18×18 | Mały brązowy stworek z toffi, smukły, w biegu (rozmazane nóżki). |
| `sugar_caster.png` | Sugarwood Grove | 50×50 | 25×25 | Mag w szacie z cukru/lukru, trzyma cukrową bombę; czasem kryształ cukru. |
| `shroom_guard.png` | Sugarwood Grove | 60×60 | 30×30 | Duży grzyb-strażnik Shroom Mother, różowy z tarczą/hełmem z kapelusza. |
| `toy_soldier.png` | Toy Factory | 40×40 | 20×20 | Ołowiany żołnierzyk z kluczykiem nakręcającym na plecach, karabinek. |
| `portable_factory.png` | Toy Factory | 80×80 | 40×40 | Mała fabryka na nóżkach: komin, taśma, wyrzuca zabawki. |
| `robo-tesla.png` | Toy Factory | 46×46 | 23×23 | Robot z cewką Tesli na głowie, iskry wokół. |
| `robo-bomber.png` | Toy Factory | 46×46 | 23×23 | Robot z moździerzem/wyrzutnią bomb na plecach. |
| `scrap_beetle.png` | Toy Factory | 28×28 | 14×14 | Żuk poskładany ze złomu (śrubki, blacha), zostawia miny. |
| `line_soldier.png` | Toy Factory | 32×32 | 16×16 | Świeży żołnierzyk z taśmy Assembly Line – czerwony, błyszczący lakier. |
| `line_beetle.png` | Toy Factory | 24×24 | 12×12 | Niedokończony żuk z taśmy: brakuje części pancerza, widać druty. |
| `belt_turret.png` | Toy Factory | 48×48 | 24×24 | Ciemnoszara wieżyczka na podstawce jadąca po taśmie (rysowana jako kwadrat). |
| `bomb_crate.png` | Toy Factory | 44×44 | 22×22 | Drewniana skrzynka z napisem FRAGILE i lontem (rysowana jako kwadrat). |
| `frost_wolf.png` | Silverpine Tundra | 52×52 | 26×26 | Biały wilk ze szronem na sierści, lodowe oczy. |
| `ice_shooter.png` | Silverpine Tundra | 52×52 | 26×26 | Postać w futrze z lodową kuszą. |
| `frozen_orb.png` | Silverpine Tundra | 56×56 | 28×28 | Pulsująca kula lodu z kryształkami, lekko świeci. |
| `tundra_watcher.png` | Silverpine Tundra | 70×70 | 35×35 | Wysoka postać w kapturze/wieżyczka obserwacyjna z jednym wielkim okiem. |
| `pixie.png` | Underground Garden | 40×40 | 20×20 | Mała wróżka ze świecącymi skrzydełkami. |
| `rainbow_pixie.png` | Underground Garden | 40×40 | 20×20 | Wróżka w tęczowych kolorach, trochę większe skrzydła. |
| `poison_skeleton.png` | Underground Garden | 56×56 | 28×28 | Szkielet z zielonymi, trującymi plamami i kapiącą trucizną. |
| `inferno_flower.png` | Underground Garden | 52×52 | 26×26 | Kwiat w kolorach ognia (czerwień/pomarańcz), płatki jak płomienie. |
| `frost_flower.png` | Underground Garden | 52×52 | 26×26 | Kwiat z lodowymi płatkami (biel/błękit). |
| `toxic_flower.png` | Underground Garden | 52×52 | 26×26 | Kwiat trujący (zieleń/fiolet), kapiący kwas. |
| `firefly_queen.png` | Underground Garden | 52×52 | 26×26 | Duży świetlik z koroną, świecący odwłok (rzadka). |
| `skeleton.png` | The Core | 42×42 | 21×21 | Zwykły szkielet, idzie prosto na gracza. |
| `mecha-skeleton.png` | The Core | 70×70 | 35×35 | Szkielet z mechanicznymi częściami (ramię-działo, płyty pancerza). |
| `liche.png` | The Core | 52×52 | 26×26 | Liczowaty mag-szkielet w szacie, z laską i fioletową poświatą. |
| `guard.png` | The Core | 44×44 | 22×22 | Ciężki strażnik Core w pełnej zbroi, wolny i wytrzymały. |
| `fly.png` | The Core | 36×36 | 18×18 | Duża mucha z trującym, zielonkawym odwłokiem. |
| `generator.png` | The Core | 52×52 | 26×26 | Generator/akumulator z kablami, świecący rdzeń, kapiący klej. |
| `voidling.png` | The Void | 28×28 | 14×14 | Mały stworek z czarnej pustki z fioletowymi oczami. |
| `red_crystal.png` | The Void | 50×50 | 25×25 | Czerwony kryształ unoszący się w powietrzu, płonące krawędzie. |
| `purple_crystal.png` | The Void | 50×50 | 25×25 | Fioletowy kryształ, pęknięty (rozpada się na mniejsze). |
| `blue_crystal.png` | The Void | 60×60 | 30×30 | Niebieski, większy kryształ, zimna poświata. |
| `void_soldier.png` | The Void | 40×40 | 20×20 | Toy Soldier „zapamiętany źle” przez Void: większy, fioletowo-czarny, zniekształcony. |
| `void_beetle.png` | The Void | 28×28 | 14×14 | Scrap Beetle w wersji Void: ciemny, fioletowe żyłki. |
| `assembly_machine_1.png` | Toy Factory (boss) | 84×84 | 42×42 | Maszyna Assembly Line – mała prasa produkująca zabawki (kwadrat). |
| `assembly_machine_2.png` | Toy Factory (boss) | 84×84 | 42×42 | Maszyna Assembly Line – większa, robi wieżyczki i skrzynki (kwadrat). |
| `assembly_machine_3.png` | Toy Factory (boss) | 84×84 | 42×42 | Maszyna Assembly Line – najszybsza, rozgrzana (kwadrat). |
| `milo_core.png` | The Core (boss) | 160×160 | 80×80 | Serce Core: wielkie, bijące, czerwone serce-maszyna z kablami (pulsuje). |

Kopie Night Bloom i Voida używają sprite'a bossa (nie trzeba osobnych).

### Bossowie – `combat/bosses/<id>.png`  (pixel art)

Opcjonalnie inne wyglądy faz: `<id>_f2.png`, `<id>_f3.png`… (bez nich gra użyje podstawowego i lekko przebarwi).

| plik | na ekranie | plik (1:2) | jak ma wyglądać |
|---|---|---|---|
| `slime_king.png` | 180×180 | 90×90 | Ogromny zielony glut z koroną. Fazy: 2 – ciemniejsza zieleń, 3 – najciemniejsza. |
| `prism.png` | 104×104 | 52×52 | Wiszący kryształ-pryzmat rozszczepiający światło (tęczowe odbicia). |
| `shroom_mother.png` | 160×160 | 80×80 | Wielka matka-grzyb, różowy kapelusz w kropki, łagodna twarz; skacze i ląduje w chmurze zarodników. |
| `frost_golem.png` | 170×170 | 85×85 | Golem z lodu i kamienia, ogromne pięści, szron; w fazie 3 śnieżyca. |
| `assembly_line.png` | 140×140 | 70×70 | Rdzeń fabryki: maszyna na górze areny, ekran/oko, rury do taśm (rysowany jako kwadrat). |
| `night_bloom.png` | 120×120 | 60×60 | Nocny kwiat świecący w ciemności (fiolet/róż), ma cień – kopie go nie mają. |
| `mascot.png` | 140×140 | 70×70 | Maskotka lunaparku śpiewająca na scenie (piosenka). Może mieć 2–3 klatki „śpiewu”. |
| `milo.png` | 64×64 | 32×32 | Milo – postać znana z dialogów (fiolet), w walce mały, ciepłe bursztynowe światło. |
| `void_boss.png` | 140×140 | 70×70 | Void – „wszystko, co system wyciął, sklejone w jedno”: glitchowa, zmieniająca się postać (fiolet). |

### Podłogi – `combat/floors/<nazwa>.png`

Kafel, który się powtarza (bez szwów), **64×64** pixel art – gra powiększy go **×4** (na ekranie 256×256) i ułoży. Opcjonalnie `<nazwa>_2.png`, `_3` jako warianty losowane.

| plik | jak ma wyglądać |
|---|---|
| `village.png` | Trawa wioski, jasna zieleń. |
| `rainbow_fields.png` | Łąka z drobnymi kwiatkami, pastelowa. |
| `sugarwood_grove.png` | Różowa ziemia cukierkowego lasu, okruszki cukru. |
| `toy_factory.png` | Metalowa podłoga fabryki, nity, linie bezpieczeństwa. |
| `silverpine_tundra.png` | Śnieg, ślady, gdzieniegdzie lód. |
| `underground_garden.png` | Ciemna ziemia jaskini z mchem. |
| `the_core.png` | Ciemny metal z kablami, czerwone światło. |
| `the_void.png` | Fioletowa „podłoga” Void, lekko przezroczysta. |
| `arena_ice.png` | Arena Frost Golema: śliski lód (faza z lodem). |
| `arena_core.png` | Arena Milo wokół serca (koncentryczne pierścienie). |
| `void_abyss.png` | Otchłań pod wyspami Voida (ciemna, gwiazdy/glitche). |
| `void_island.png` | Wyspa Voida (okrągła, kamienna, widziana z góry). |
| `void_bridge.png` | Most między wyspami (powtarzalny kawałek). |
| `song_floor.png` | Scena walki z Maskotką (piosenka). |

### Przeszkody w walkach – `combat/obstacles/`

Przeszkody w grze mają różne rozmiary (filary 70–150 px, ściany grube 40–50 px i długie 180–640 px, krótkie grube ściany do ~300×85 px). Dlatego na każdy biom jest kilka plików (pixel art, rysuj w połowie – gra ×2; dłuższą ścianę gra ułoży z kawałków):

| plik | na ekranie | plik (1:2) | co to |
|---|---|---|---|
| `<biom>_pillar_small.png` | 70–100 px | 40×40 px | mały filar / kamień |
| `<biom>_pillar_medium.png` | 100–130 px | 56×56 px | średni filar |
| `<biom>_pillar_large.png` | 130–150 px | 72×72 px | duży filar (sam na środku areny) |
| `<biom>_wall_h.png` | grubość ~45 px | 32×24 px | środek ściany poziomej, powtarzalny w poziomie |
| `<biom>_wall_h_end.png` | | 12×24 px | koniec ściany poziomej (lewy; prawy = odbicie) |
| `<biom>_wall_v.png` | grubość ~45 px | 24×32 px | środek ściany pionowej, powtarzalny w pionie |
| `<biom>_wall_v_end.png` | | 24×12 px | koniec ściany pionowej (górny; dolny = odbicie) |
| `<biom>_wall_thick_h.png` | grubość ~85 px | 32×44 px | gruba krótka ściana (pozioma; pionową gra obróci) |

Opcjonalnie 2. wariant filara: `<biom>_pillar_medium_2.png` itd. Styl na biom:

| biom | styl |
|---|---|
| `village` | żywopłot |
| `rainbow_fields` | kryształy |
| `sugarwood_grove` | cukierkowe laski/paski |
| `toy_factory` | metalowe bloki |
| `silverpine_tundra` | lodowe skały |
| `underground_garden` | omszałe kamienie |
| `the_core` | metal z czerwonymi światłami |
| `the_void` | fioletowe kryształy |

### Inne rzeczy w walce – `combat/objects/`

| plik | jak ma wyglądać |
|---|---|
| `ice_wall.png` | Lodowa ściana Frost Golema (prostokąt, pęka po 5 trafieniach: można dać ice_wall_cracked.png). |
| `crate.png` | Skrzynka-osłona (niszczalna). |
| `belt.png` | Taśmociąg w walce z Assembly Line (powtarzalny kawałek, strzałki). |
| `light_seed.png` | Nasiono światła w walce z Night Bloom (zbierane, świeci). |
| `lantern.png` | Rzucany lampion Night Bloom. |
| `void_turret.png` | Wieżyczka wyrastająca z wyspy w F5 Voida. |
| `lost_weapon.png` | Wytrącona broń leżąca na wyspie Voida. |
| `disarm_shot.png` | Pocisk Voida, który wytrąca broń. |
| `milo_mine.png` | Mina Milo (Core), mruga przed wybuchem. |

**Pociski:** wszystkie typy pocisków mają już obrazki (`combat/projectiles/`) – nic nie brakuje. Wybuchy (boom, nova_boom, frost_boom) i zap też są.

## MAPA – `assets/img/map/`  (styl rysowany)

Kafel mapy na ekranie ≈ 83×83 px (1080p). Rysuj **128×128** (gra zmniejszy z wygładzaniem).

### Gracz – `map/player/`  (rysowany, 8 kierunków)

Plik **128×128**, postać ok. 80–90 px wysokości, stopy przy dolnej krawędzi. Pliki: `n.png`, `ne.png`, `e.png`, `se.png`, `s.png`, `sw.png`, `w.png`, `nw.png`. Opcjonalnie klatki chodu `<kierunek>_1.png`, `_2.png`.

### Kafle – `map/tiles/<biom>/<kafel>.png`  (128×128)

Tylko kafle, które naprawdę występują w danym biomie (sprawdzone na wygenerowanej mapie). Kafle ziemi bez przezroczystości; obiekty (drzewo, skała, studnia…) mogą mieć przezroczyste tło – gra położy je na trawie/podłodze. Pale World: gra sama odbarwi zwykłe kafle (nie trzeba osobnych).

| kafel | co to |
|---|---|
| `grass` | ziemia/trawa (podstawowy kafel, powinien się dobrze powtarzać) |
| `path` | ścieżka |
| `floor` | podłoga w budynkach i obozach |
| `flowers` | kwiaty |
| `dead_flowers` | zwiędłe kwiaty |
| `bridge` | most (deski) |
| `gate` | przejście zamknięte do pokonania bossa (bariera) |
| `tree` | drzewo (widziane z góry/z ukosa, może wystawać ponad kafel) |
| `rock` | skała |
| `wall` | ściana (jaskinia / fabryka / ruiny) |
| `fence` | płotek |
| `house` | ściana/dach domu (powtarzalny kawałek) |
| `door` | drzwi |
| `water` | woda (już jest assets/img/map/water.png) |
| `well` | studnia |
| `campfire` | ognisko |
| `cliff` | klif – granica między biomami |
| `mountain` | lita skała poza biomami |
| `metal_floor` | metalowa podłoga |
| `conveyor_right` | taśmociąg w prawo |
| `conveyor_left` | taśmociąg w lewo |
| `conveyor_up` | taśmociąg w górę |
| `conveyor_down` | taśmociąg w dół |
| `machine` | maszyna 1×1 |
| `cable` | świecący kabel na podłodze |
| `gold_cable` | złoty kabel (sekret Core) |
| `pipe` | rura |
| `crate` | skrzynka |
| `pale_stone` | bezbarwny kamień ołtarza (Pale Orb) |
| `glitch_stone` | glitchowy kamień Pale World |

Każdy biom ma **własny komplet** kafli w swoim folderze (np. `map/tiles/sugarwood_grove/tree.png`). Brakujący kafel w biomie = gra użyje kafla z `village`, a jak i tam go nie ma – koloru jak teraz.

**Warianty:** częste kafle mają kilka wersji (`grass.png`, `grass_2.png`, …) – gra losuje je po pozycji, żeby mapa nie była w kratkę. Warianty mają być podobne (ten sam kolor i jasność), różnić się szczegółami (kępka, kamyk, pęknięcie). Wystarczy narysować pierwszy – reszta opcjonalna.

**Pod spodem:** „pełny kafel” = rysujesz cały kwadrat bez przezroczystości. Kafel z podanym podłożem (np. drzewo → `grass`) rysujesz na przezroczystym tle – gra najpierw położy pod nim to podłoże z tego samego biomu (drzewo w Village stoi na trawie z Village, w Tundrze na śniegu). Drzewa i skały mogą wystawać poza kafel w górę.

#### village – `map/tiles/village/`

Ciepła, zwykła wieś: soczysta zieleń, drewno, czerwone dachy. Punkt odniesienia dla reszty.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `grass.png` | pełny kafel | `grass.png`, `grass_2.png`, `grass_3.png`, `grass_4.png` | Soczysta zielona trawa, kilka źdźbeł i drobnych plamek (kafel podstawowy – musi się ładnie powtarzać). |
| `tree.png` | `grass` (przezroczyste tło) | `tree.png`, `tree_2.png`, `tree_3.png` | Liściaste drzewo z okrągłą koroną, widziane z góry/ukosa, cień pod spodem. |
| `water.png` | pełny kafel | `water.png`, `water_2.png` | Niebieska woda stawu, lekkie fale (gra ma już water.png – możesz go zastąpić). |
| `path.png` | pełny kafel | `path.png`, `path_2.png`, `path_3.png` | Ubita brązowa ścieżka z kamyczkami. |
| `cliff.png` | pełny kafel | `cliff.png`, `cliff_2.png` | Kamienny klif / skarpa – granica biomu, szare skały z trawą na górze. |
| `fence.png` | `grass` (przezroczyste tło) | – | Drewniany płotek (sztachety), kafel łączy się w poziomie i pionie. |
| `house.png` | pełny kafel | – | Kawałek ściany/dachu domu (czerwone dachówki) – zapas, gdy budynek nie ma własnego sprite'a. |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Deski podłogi w domach i stodole. |
| `flowers.png` | `grass` (przezroczyste tło) | `flowers.png`, `flowers_2.png`, `flowers_3.png` | Kolorowe kwiatki (różowe, żółte, białe) – trawa pod spodem jest z grass. |
| `rock.png` | `grass` (przezroczyste tło) | `rock.png`, `rock_2.png`, `rock_3.png` | Szary głaz. |
| `gate.png` | `path` (przezroczyste tło) | – | Brama/bariera przed bossem – świecąca biała zapora (zniknie po wygranej). |
| `door.png` | pełny kafel | – | Drewniane drzwi. |
| `bridge.png` | `water` (przezroczyste tło) | – | Drewniany mostek z desek nad wodą. |
| `crate.png` | `floor` (przezroczyste tło) | – | Drewniana skrzynka. |
| `well.png` | `grass` (przezroczyste tło) | – | Kamienna studnia z daszkiem i wiadrem. |

#### rainbow_fields – `map/tiles/rainbow_fields/`

Pastelowa łąka pełna kwiatów, jaśniej i weselej niż wioska; tęczowe akcenty.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `grass.png` | pełny kafel | `grass.png`, `grass_2.png`, `grass_3.png`, `grass_4.png` | Jasnozielona, pastelowa trawa, delikatniejsza niż w wiosce. |
| `flowers.png` | `grass` (przezroczyste tło) | `flowers.png`, `flowers_2.png`, `flowers_3.png` | Gęste kwiaty w różnych kolorach (róż, fiolet, żółty, błękit) – dużo, to biom kwiatów. |
| `tree.png` | `grass` (przezroczyste tło) | `tree.png`, `tree_2.png`, `tree_3.png` | Okrągłe drzewko o jasnej koronie, może z kwiatami. |
| `path.png` | pełny kafel | `path.png`, `path_2.png`, `path_3.png` | Jasna, piaskowa ścieżka. |
| `cliff.png` | pełny kafel | `cliff.png`, `cliff_2.png` | Klif z jasnego kamienia porośnięty kwiatami. |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Biały marmur (pawilon bossa, ruiny). |
| `rock.png` | `grass` (przezroczyste tło) | `rock.png`, `rock_2.png`, `rock_3.png` | Jasny kamień, czasem z tęczowym połyskiem. |
| `wall.png` | pełny kafel | `wall.png`, `wall_2.png`, `wall_3.png` | Ściany ruin z białego kamienia porośnięte kwiatami. |
| `water.png` | pełny kafel | `water.png`, `water_2.png` | Jasnoniebieska woda. |
| `dead_flowers.png` | `grass` (przezroczyste tło) | `dead_flowers.png`, `dead_flowers_2.png` | Szare, zwiędłe kwiaty (wokół kapliczki – coś je wysysa). |
| `gate.png` | `path` (przezroczyste tło) | – | Bariera przed bossem (jak w wiosce, w kolorach tęczy). |

#### sugarwood_grove – `map/tiles/sugarwood_grove/`

Cukierkowy las: różowa ziemia, drzewa jak lizaki i lukier, czekolada zamiast wody.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `tree.png` | `grass` (przezroczyste tło) | `tree.png`, `tree_2.png`, `tree_3.png` | Drzewo-lizak / drzewo z waty cukrowej, czerwono-białe paski na pniu. |
| `grass.png` | pełny kafel | `grass.png`, `grass_2.png`, `grass_3.png`, `grass_4.png` | Różowa „ziemia” z okruszkami cukru i posypką. |
| `water.png` | pełny kafel | `water.png`, `water_2.png` | Rzeka płynnej czekolady (brązowa, błyszcząca). |
| `path.png` | pełny kafel | `path.png`, `path_2.png`, `path_3.png` | Ścieżka z jasnego, kremowego lukru lub kostki z herbatników. |
| `cliff.png` | pełny kafel | `cliff.png`, `cliff_2.png` | Klif z ciasta / czekolady, warstwy jak w torcie. |
| `flowers.png` | `grass` (przezroczyste tło) | `flowers.png`, `flowers_2.png`, `flowers_3.png` | Cukrowe kwiatki (żółte, jak cukierki). |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Podłoga z herbatników / wafli. |
| `wall.png` | pełny kafel | `wall.png`, `wall_2.png`, `wall_3.png` | Ściana z piernika z lukrowymi zdobieniami (forteca bossa, ruina sklepu). |
| `fence.png` | `grass` (przezroczyste tło) | – | Płotek z lasek cukrowych (biało-czerwony). |
| `house.png` | pełny kafel | – | Ściana piernikowej chatki (zapas). |
| `rock.png` | `grass` (przezroczyste tło) | `rock.png`, `rock_2.png`, `rock_3.png` | Różowa skała z cukru / kamień z karmelu. |
| `gate.png` | `path` (przezroczyste tło) | – | Bariera przed bossem (różowa). |
| `door.png` | pełny kafel | – | Drzwi z czekolady. |

#### silverpine_tundra – `map/tiles/silverpine_tundra/`

Zimno: śnieg, srebrne świerki, lód, szare kamienie, ciepłe światło ognisk.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `grass.png` | pełny kafel | `grass.png`, `grass_2.png`, `grass_3.png`, `grass_4.png` | Śnieg, biały z niebieskawymi cieniami, gdzieniegdzie ślady. |
| `tree.png` | `grass` (przezroczyste tło) | `tree.png`, `tree_2.png`, `tree_3.png` | Ciemnozielony świerk przysypany śniegiem. |
| `water.png` | pełny kafel | `water.png`, `water_2.png` | Lód / zamarznięta woda (jasnoniebieski, pęknięcia). |
| `path.png` | pełny kafel | `path.png`, `path_2.png`, `path_3.png` | Wydeptana ścieżka w śniegu (szaroniebieska). |
| `cliff.png` | pełny kafel | `cliff.png`, `cliff_2.png` | Szare skały z czapą śniegu. |
| `rock.png` | `grass` (przezroczyste tło) | `rock.png`, `rock_2.png`, `rock_3.png` | Szary kamień ze śniegiem. |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Deski chatki / ubity śnieg w obozie. |
| `wall.png` | pełny kafel | `wall.png`, `wall_2.png`, `wall_3.png` | Ściany lodowej fortecy (bloki lodu). |
| `house.png` | pełny kafel | – | Ściana drewnianej chatki ze śniegiem na dachu (zapas). |
| `gate.png` | `path` (przezroczyste tło) | – | Bariera przed bossem (lodowa). |
| `bridge.png` | `water` (przezroczyste tło) | – | Drewniany most nad fosą fortecy. |
| `door.png` | pełny kafel | – | Drzwi chatki, oszronione. |
| `campfire.png` | `grass` (przezroczyste tło) | – | Ognisko w kręgu kamieni – ciepłe światło na tle śniegu. |

#### toy_factory – `map/tiles/toy_factory/`

Podziemna fabryka zabawek: szary metal, nity, żółto-czarne pasy, taśmociągi.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `wall.png` | pełny kafel | `wall.png`, `wall_2.png`, `wall_3.png` | Ciemnoszara ściana fabryki, nity, rury. |
| `metal_floor.png` | pełny kafel | `metal_floor.png`, `metal_floor_2.png`, `metal_floor_3.png` | Metalowa podłoga hal (blacha ryflowana) – tu są walki. |
| `machine.png` | `metal_floor` (przezroczyste tło) | – | Maszyna 1×1 (prasa, panel z kontrolkami). |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Gładka podłoga pokoi (socjalny, magazyn). |
| `crate.png` | `metal_floor` (przezroczyste tło) | – | Skrzynka z zabawkami. |
| `conveyor_up.png` | pełny kafel | – | Taśmociąg – strzałki/rolki w górę. |
| `conveyor_down.png` | pełny kafel | – | Taśmociąg – w dół. |
| `conveyor_right.png` | pełny kafel | – | Taśmociąg – w prawo. |
| `conveyor_left.png` | pełny kafel | – | Taśmociąg – w lewo (wystarczy 1 taśmociąg, gra może obracać – ale 4 osobne wyglądają lepiej przy świetle z góry). |
| `gate.png` | `floor` (przezroczyste tło) | – | Bariera przed bossem (żółto-czarne pasy). |

#### underground_garden – `map/tiles/underground_garden/`

Ogromna jaskinia zarośnięta roślinami: ciemna zieleń, świecące grzyby (miętowa poświata), korzenie.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `wall.png` | pełny kafel | `wall.png`, `wall_2.png`, `wall_3.png` | Ściana jaskini – ciemna skała z mchem i korzeniami. |
| `grass.png` | pełny kafel | `grass.png`, `grass_2.png`, `grass_3.png`, `grass_4.png` | Ciemnozielony mech na ziemi jaskini. |
| `tree.png` | `grass` (przezroczyste tło) | `tree.png`, `tree_2.png`, `tree_3.png` | Wielki świecący grzyb albo gruby korzeń (jasna zieleń) – drzewa tej jaskini. |
| `flowers.png` | `grass` (przezroczyste tło) | `flowers.png`, `flowers_2.png`, `flowers_3.png` | Świecące grzybki / kwiaty (miętowa poświata). |
| `water.png` | pełny kafel | `water.png`, `water_2.png` | Ciemna, spokojna woda podziemnego jeziora. |
| `dead_flowers.png` | `grass` (przezroczyste tło) | `dead_flowers.png`, `dead_flowers_2.png` | Zwiędłe, fioletowo-szare rośliny. |
| `rock.png` | `grass` (przezroczyste tło) | `rock.png`, `rock_2.png`, `rock_3.png` | Omszały kamień. |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Kamienne płyty (świątynia, szklarnia, obozy). |
| `path.png` | pełny kafel | `path.png`, `path_2.png`, `path_3.png` | Wydeptana ścieżka w mchu. |
| `fence.png` | `grass` (przezroczyste tło) | – | Stary płotek oplątany pnączami (plac zabaw). |
| `house.png` | pełny kafel | – | Ściana chatki ogrodnika z pnączami (zapas). |
| `well.png` | `grass` (przezroczyste tło) | – | Stara studnia w jaskini. |
| `gate.png` | `path` (przezroczyste tło) | – | Bariera przed bossem (zielona poświata). |
| `bridge.png` | `water` (przezroczyste tło) | – | Kładka z desek nad wodą. |
| `machine.png` | `floor` (przezroczyste tło) | – | Porzucona maszyna (zabłąkana z Factory). |
| `door.png` | pełny kafel | – | Drzwi chatki ogrodnika. |

#### the_core – `map/tiles/the_core/`

Mechaniczne serce: ciemny fioletowo-szary metal, czerwone świecące kable, rury, para.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `wall.png` | pełny kafel | `wall.png`, `wall_2.png`, `wall_3.png` | Bardzo ciemna ściana z metalu, czerwone lampki. |
| `metal_floor.png` | pełny kafel | `metal_floor.png`, `metal_floor_2.png`, `metal_floor_3.png` | Ciemny fioletowo-szary metal – podłoga hal (walki). |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Płyty podłogi pokoi Core. |
| `cable.png` | `metal_floor` (przezroczyste tło) | `cable.png`, `cable_2.png` | Świecący czerwony kabel na podłodze (puls). |
| `gold_cable.png` | `metal_floor` (przezroczyste tło) | – | Złoty kabel – ten sam co cable, ale złoty (prowadzi do sekretu). |
| `pipe.png` | `metal_floor` (przezroczyste tło) | – | Gruba rura z parą (łączy się w poziomie i pionie). |
| `machine.png` | `metal_floor` (przezroczyste tło) | – | Maszyna Core (serwer, generator 1×1). |
| `crate.png` | `metal_floor` (przezroczyste tło) | – | Metalowa skrzynia z częściami. |

#### the_void – `map/tiles/the_void/`

Pustka: prawie czarny fiolet, wszystko jak zapamiętane źle – kolory przygaszone, lekko świecące krawędzie.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `grass.png` | pełny kafel | `grass.png`, `grass_2.png`, `grass_3.png`, `grass_4.png` | „Podłoga” Void: ciemny fiolet z ledwo widocznymi glitchami / gwiazdkami. |
| `water.png` | pełny kafel | `water.png`, `water_2.png` | Szczeliny między wyspami – prawie czarne, głębia (mapa = labirynt, ma być widać przez nie, ale nie przejść). |
| `dead_flowers.png` | `grass` (przezroczyste tło) | `dead_flowers.png`, `dead_flowers_2.png` | Martwe kwiaty w szarym fiolecie. |
| `flowers.png` | `grass` (przezroczyste tło) | `flowers.png`, `flowers_2.png`, `flowers_3.png` | Fioletowe świecące kwiaty. |
| `bridge.png` | `water` (przezroczyste tło) | – | Mostek między wyspami, fioletowy, jakby z kryształu/światła. |
| `tree.png` | `grass` (przezroczyste tło) | `tree.png`, `tree_2.png`, `tree_3.png` | Fioletowe drzewo-kryształ, jasne (jedyne jasne rzeczy w Void). |
| `rock.png` | `grass` (przezroczyste tło) | `rock.png`, `rock_2.png`, `rock_3.png` | Fioletowy kamień. |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Płyty kapliczki Void (obóz w połowie drogi). |

#### lunapark – `map/tiles/lunapark/`

Pastelowy lunapark: róż, krem, biel, niebieskie i żółte akcenty, wesoło ale trochę opuszczony.

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `grass.png` | pełny kafel | `grass.png`, `grass_2.png`, `grass_3.png`, `grass_4.png` | Pastelowo-różowa trawa / sztuczna murawa. |
| `fence.png` | `grass` (przezroczyste tło) | – | Biały płotek lunaparku. |
| `path.png` | pełny kafel | `path.png`, `path_2.png`, `path_3.png` | Kremowa kostka brukowa. |
| `floor.png` | pełny kafel | `floor.png`, `floor_2.png`, `floor_3.png` | Deski (w namiocie Maskotki). |
| `flowers.png` | `grass` (przezroczyste tło) | `flowers.png`, `flowers_2.png`, `flowers_3.png` | Różowe kwiaty w donicach / rabatach. |
| `tree.png` | `grass` (przezroczyste tło) | `tree.png`, `tree_2.png`, `tree_3.png` | Przystrzyżone, okrągłe drzewko (miętowe). |
| `crate.png` | `grass` (przezroczyste tło) | – | Drewniana skrzynka z balonami / nagrodami. |

#### outside – `map/tiles/outside/`

Teren poza biomami (nie do przejścia).

| plik | pod spodem | warianty | jak ma wyglądać |
|---|---|---|---|
| `mountain.png` | pełny kafel | `mountain.png`, `mountain_2.png` | Lita ciemna skała – wszystko poza biomami (i lita skała w cellar). Jeden plik dla całej gry; opcjonalnie wersja na biom w jego folderze. |


### Duże obiekty (jeden sprite na całość) – `map/objects/<nazwa>.png`

Rozmiar = dokładnie tyle pikseli, ile podano (podstawa). Mogą wystawać w górę (perspektywa) – wtedy dorysuj ponad, gra wyrówna do dołu.

| plik | rozmiar pliku | jak ma wyglądać |
|---|---|---|
| `antenna.png` | 384×512 px | Antena radiowa Hala (Tundra) – maszt ze skrzynką; ewentualnie antenna_fixed.png po naprawie. |
| `radio_antenna.png` | 128×256 px | Mała antena na chatce radiowej Hala. |
| `flower_tower.png` | 640×512 px | Wieża/stos kwiatów Sunny (Rainbow Fields). |
| `ferris_wheel.png` | 1920×1920 px | Diabelski młyn w lunaparku (widziany z ukosa). |
| `carousel.png` | 1664×1664 px | Karuzela w lunaparku (okrągła, z koniami). |
| `big_tent.png` | 2688×1408 px | Wielki namiot cyrkowy Maskotki w lunaparku (z wejściem na dole). |
| `booth.png` | 384×384 px | Budka z grą w lunaparku (koło Lucky'ego). |
| `the_core.png` | 640×896 px | Obiekt Core w komnacie Core (świecący, czerwony). |
| `pale_altar.png` | 640×384 px | Bezbarwny ołtarz Pale Orb w Garden. |
| `control_desk.png` | 896×128 px | Pulpit sterowniczy w Core. |
| `sigil_shrine.png` | 256×256 px | Kapliczka sigila: krąg kamieni, piedestał, świeci (Garden; kolor sigila nakłada gra). |
| `portal_open.png` | 128×128 px | Portal/zejście (otwarty, fioletowy). |
| `portal_sealed.png` | 128×128 px | Portal zamknięty (szary). |
| `gold_pile.png` | 128×128 px | Kupka złota do podniesienia. |
| `item_spot.png` | 128×128 px | Podkładka pod przedmiot leżący na ziemi (ikonę przedmiotu dorysuje gra). |
| `quest_mark.png` | 48×48 px | Znacznik questa nad NPC (wykrzyknik). |
| `marble_pillar.png` | 128×128 px | Rainbow Fields: biała marmurowa kolumna otwartego pawilonu bossa (Prism) – 8 sztuk w kręgu. |
| `slide.png` | 128×256 px | (dekoracja) zjeżdżalnia na zarośniętym placu zabaw (Garden), jaskrawa farba pod mchem. |
| `lamp_post.png` | 128×128 px | (dekoracja) stara latarnia przy ścieżce (lamp_path); może wystawać w górę. |
| `picnic_blanket.png` | 768×512 px | (dekoracja) koc piknikowy w kratkę z koszykiem i talerzami (picnic_spot). |
| `pier.png` | 128×512 px | (dekoracja) drewniany pomost nad wodą (sunken_pier, hook_pond – tam 256×256 px). |
| `ice_hole.png` | 128×128 px | (dekoracja) przerębel z wędką Olivera (ice_fishing_camp). |
| `stone_shrine.png` | 384×384 px | (dekoracja) kamienna kapliczka w kręgu kwiatów (flower_shrine) / blok w korzeniach (root_shrine: też 384×384 px). |

### Budynki – `map/buildings/<nazwa>.png`  (jeden sprite na budynek)

**Decyzja (13.11): „dach znika”.** Budynek z zewnątrz = jeden sprite (ściany + dach) położony na kaflach. Środek zostaje z kafli (podłoga, NPC, przedmioty, boss). Gdy gracz wejdzie przez drzwi, sprite płynnie robi się przezroczysty; po wyjściu wraca.

- rozmiar pliku = podany w tabeli (dach/komin/wieże mogą wystawać w górę – gra wyrówna do dołu),
- drzwi / bramy rysuj tam, gdzie w prefabie jest wejście,
- „WCHODZI SIĘ” = ma środek, reszta (małe domy i chatki) to pełne bryły, do których się nie wchodzi – zwykły sprite,
- opcjonalnie `<nazwa>_floor.png` – ładniejsza podłoga środka.

| plik | rozmiar pliku | jak ma wyglądać |
|---|---|---|
| `village_house.png` | 512×384 px / 384×256 px / 512×256 px | Domy w wiosce startowej (kilka rozmiarów – możesz dać village_house_4x3.png itd.). |
| `angler_shack.png` | 512×256 px | Chatka Anglera przy stawie. |
| `forest_cabin.png` | 384×256 px | Chatka w lesie. |
| `frozen_cabin.png` | 640×256 px | Zamarznięta chatka (Tundra). |
| `gardener_hut.png` | 640×256 px | Chatka ogrodnika (Garden). |
| `gingerbread_hut.png` | 384×384 px | Piernikowa chatka Gusa (Sugarwood). |
| `radio_hut.png` | 896×384 px | Chatka radiowa Hala (Tundra). |
| `boss_barn.png` | 1152×1024 px | WCHODZI SIĘ (dach znika). Village: stara stodoła bossa (Slime King), siano i 2 skrzynki w środku, drzwi przód i tył. |
| `boss_gingerbread_fortress.png` | 1664×1408 px | WCHODZI SIĘ. Sugarwood: piernikowa forteca z wieżami z lasek cukrowych w rogach; w środku mała piernikowa kaplica bossa (640×640 px) – może być osobno: boss_gingerbread_chapel.png. |
| `boss_ice_fortress.png` | 1408×1152 px | WCHODZI SIĘ. Tundra: lodowa forteca, bramy góra i dół (fosa i mosty zostają z kafli). |
| `boss_sunken_temple.png` | 1408×1408 px | WCHODZI SIĘ. Garden: zatopiona świątynia oplątana korzeniami, świecące grzyby, sadzawki; wejścia z lewej i prawej. |
| `greenhouse.png` | 1408×896 px | WCHODZI SIĘ. Garden: szklarnia, szklany dach przebity przez rośliny; drzwi na dole. |
| `wren_tent.png` | 640×384 px | WCHODZI SIĘ. Garden: namiot Wren, lampa, kartki przypięte do korzeni; wejście na dole. |

### NPC – `map/npcs/<id>.png`  (rysowany, 128×128, przodem)

| plik | kto |
|---|---|
| `milo.png` | Milo (we wszystkich miejscach ten sam sprite; wersja „scary” opcjonalnie milo_scary.png). |
| `angler.png` | Angler – stary rybak, wędka, kapelusz. |
| `bramble.png` | Mayor Bramble – burmistrz wioski. |
| `dot.png` | Dot – kobieta z wioski (memory). |
| `wanderer.png` | Wanderer – wędrowiec. |
| `sunny.png` | Sunny – dziewczyna przy wieży kwiatów. |
| `gus.png` | Gus – cukiernik z piernikowej chatki. |
| `hal.png` | Hal – radiowiec w Tundrze. |
| `foreman.png` | Foreman – brygadzista z Factory (kask). |
| `oliver.png` | Oliver – rybak z przerębla. |
| `wren.png` | Wren – badaczka z notesem. |
| `gardener.png` | Gardener – ogrodnik w Garden. |
| `lucky.png` | Lucky – NPC od koła fortuny w lunaparku. |
| `ferris.png` | Ferris – kurier z wielkim plecakiem. |
| `shopkeeper.png` | (opcjonalnie) sklepikarz na mapie, jeśli kiedyś się pojawi. |

### Bossowie na mapie – `map/bosses/<id>.png`  (rysowany, 128×128; stoją przy swoich bramach)

`slime_king.png`, `prism.png`, `shroom_mother.png`, `frost_golem.png`, `assembly_line.png`, `night_bloom.png`, `mascot.png`, `milo.png`, `void_boss.png`

### Bestiary

Obrazki do Bestiary: `assets/img/bestiary/<id>.png` (już działa). Gdy ich nie ma, podepnę sprite z `combat/enemies` / `combat/bosses`.
