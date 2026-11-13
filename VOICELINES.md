# Voice lines

Every line an NPC says, to record. A file goes to `assets/sfx/voicelines/<folder>/<ID>.mp3`
(or `.wav` / `.ogg`). A missing file is fine - the line is only text (with the talk sound).
Without the player, the answers and narration. Made by `python tools/voicelines.py` - run it again
after writing new lines (new lines get IDs, old ones keep theirs).

**×N** = the same line is said in N places - one recording is used for all of them.

Total: 756 lines.

| Who | Folder | Lines |
|---|---|---|
| Milo | `assets/sfx/voicelines/milo/` | 204 |
| Shopkeeper | `assets/sfx/voicelines/shopkeeper/` | 29 |
| Buyer (the Sell page) | `assets/sfx/voicelines/buyer/` | 8 |
| Angler | `assets/sfx/voicelines/angler/` | 25 |
| Mayor Bramble | `assets/sfx/voicelines/bramble/` | 22 |
| Dot | `assets/sfx/voicelines/dot/` | 22 |
| Ferris | `assets/sfx/voicelines/ferris/` | 5 |
| Foreman | `assets/sfx/voicelines/foreman/` | 56 |
| Gardener | `assets/sfx/voicelines/gardener/` | 35 |
| Gus | `assets/sfx/voicelines/gus/` | 43 |
| Hal | `assets/sfx/voicelines/hal/` | 31 |
| Lucky | `assets/sfx/voicelines/lucky/` | 30 |
| narrator (???) | `assets/sfx/voicelines/narrator/` | 55 |
| Oliver | `assets/sfx/voicelines/oliver/` | 33 |
| Radio | `assets/sfx/voicelines/radio/` | 3 |
| Sunny | `assets/sfx/voicelines/sunny/` | 73 |
| Wanderer | `assets/sfx/voicelines/wanderer/` | 17 |
| whisper (...) | `assets/sfx/voicelines/whisper/` | 6 |
| Wren | `assets/sfx/voicelines/wren/` | 59 |


## Milo — `assets/sfx/voicelines/milo/`

| ID | Line | Where | Notes |
|---|---|---|---|
| milo_candy_01 | Hey. Two guards down. People are going to start telling stories about you. | milo_candy → first |  |
| milo_candy_02 | This is the Sugarwood Grove. Trees made of candy, rivers of syrup, and the worst toothache of your life. | milo_candy → first |  |
| milo_candy_03 | Everything here is sweet. Everything. Even the things that shouldn't be. | milo_candy → first |  |
| milo_candy_04 | ...Can I ask you something? | milo_candy → first |  |
| milo_candy_05 | Do you like it here? This place. The whole... everything. | milo_candy → first |  |
| milo_candy_06 | No reason! People leave, sometimes. Go too far. I like it when people stay, that's all. | milo_candy → first |  |
| milo_candy_07 | The candy makers here are nice. Sticky handshakes, though. | milo_candy → again |  |
| milo_candy_08 | Don't drink from the syrup river. I'm not saying why. Just don't. | milo_candy → again |  |
| milo_candy_09 | I like watching people walk by. You're the only one who walks that way, though. | milo_candy → again |  |
| milo_candy_10 | You know what I like about this place? Nothing ever changes. Nothing. | milo_candy → again |  |
| milo_candy_11 | Anyway! What else? | milo_candy → hub |  |
| milo_candy_12 | They make everything out of sugar. Houses, chairs, spoons. One of them made a sugar hat. It melted in the rain. | milo_candy → makers |  |
| milo_candy_13 | They're nice. They smile a lot. Maybe a little too much. Ever seen someone smile while sleeping? Like that. | milo_candy → makers |  |
| milo_candy_14 | A village. Smaller than mine. Quieter. | milo_candy → past |  |
| milo_candy_15 | After that the road splits. You'll see. | milo_candy → past |  |
| milo_candy_16 | Watch your teeth. | milo_candy → bye |  |
| milo_core_entrance_01 | Stop. Just for a second. Please. | milo_core_entrance → first |  |
| milo_core_entrance_02 | Up there is the Core. It's not a place for people. It was never meant to be. | milo_core_entrance → first |  |
| milo_core_entrance_03 | It's hot. Pipes that burst, cables that bite, machines that don't care if you're standing where they move. | milo_core_entrance → first |  |
| milo_core_entrance_04 | The air hums. After a while you start humming with it. Don't. | milo_core_entrance → first |  |
| milo_core_entrance_05 | And the things that live there... they aren't monsters. They're parts. Parts don't stop. | milo_core_entrance → first |  |
| milo_core_entrance_06 | Because I want you to come back. And people who go up there without knowing don't. | milo_core_entrance → first |  |
| milo_core_entrance_07 | If you go up, bring your best. Your very best. And maybe turn around halfway. | milo_core_entrance → first |  |
| milo_core_entrance_08 | ... | **×8** milo_core_entrance → hub; milo_garden_factory → first; milo_garden_factory → rude; milo_garden_tundra → first; milo_garden_tundra → rude; milo_void → note; wren_argument → argue; wren_argument → argue |  |
| milo_core_entrance_09 | The heart of everything. | milo_core_entrance → end_q |  |
| milo_core_entrance_10 | And someone who'll ask you to stop. One last time. | milo_core_entrance → end_q |  |
| milo_core_entrance_11 | Ha. No. I'll be there. Just... not like that. | milo_core_entrance → come |  |
| milo_core_entrance_12 | Okay. Okay. | milo_core_entrance → bye |  |
| milo_core_entrance_13 | Goodbye, outsider. | milo_core_entrance → bye |  |
| milo_core_entrance_14 | Still here. Good. Stay a little longer. | milo_core_entrance → again |  |
| milo_core_entrance_15 | The hum is louder today. Can you hear it? | milo_core_entrance → again |  |
| milo_core_entrance_16 | Bring your best. I mean it. | milo_core_entrance → again |  |
| milo_core_fight_01 | You came all the way up. | milo_core_fight → first |  |
| milo_core_fight_02 | I asked you to turn around. Halfway. Remember? | milo_core_fight → first |  |
| milo_core_fight_03 | Everyone. Even you. Especially you. | milo_core_fight → first |  |
| milo_core_fight_04 | This heart keeps the world quiet. Every bad thing that ever happened here is locked under it. | milo_core_fight → first |  |
| milo_core_fight_05 | You switch it off, and it all comes back. Not slowly. All at once. | milo_core_fight → first |  |
| milo_core_fight_06 | Then I'm sorry. I really am. | milo_core_fight → know |  |
| milo_core_fight_07 | I can't. I never could. | milo_core_fight → aside |  |
| milo_core_fight_08 | Come on. Let's get it over with. | milo_core_fight → fight |  |
| milo_core_fight_09 | You're back. | milo_core_fight → again |  |
| milo_core_fight_10 | Nothing has changed. I still can't let you through. | milo_core_fight → again |  |
| milo_core_void_01 | Breaking it won't help. It never did. | milo_core_void → talk |  |
| milo_core_void_02 | The heart doesn't hold anything down. It only makes us forget. | milo_core_void → talk |  |
| milo_core_void_03 | Every time something goes wrong here, the system cuts it out. A bad day. A broken promise. A person who asked too many questions. | milo_core_void → talk |  |
| milo_core_void_04 | It all has to go somewhere. There's a place under all of this. | milo_core_void → talk |  |
| milo_core_void_05 | The Void. | milo_core_void → talk |  |
| milo_core_void_06 | No sky. No ground you can trust. Islands of whatever was left, and bridges that only go where they want to. | milo_core_void → talk |  |
| milo_core_void_07 | You can see across the cracks. You can't cross them. You'll walk in circles and swear you went straight. | milo_core_void → talk |  |
| milo_core_void_08 | Nothing there is alive. It's only remembered. And it remembers back. | milo_core_void → talk |  |
| milo_core_void_09 | Look away for too long and it forgets you were ever there. Even the way back. | milo_core_void → talk |  |
| milo_core_void_10 | Everything the system took is down there. Every answer you came for. | milo_core_void → talk |  |
| milo_core_void_11 | I won't stop you anymore. I don't think I could. | milo_core_void → talk |  |
| milo_core_void_12 | The way down is open now. Behind the heart. | milo_core_void → talk |  |
| milo_core_void_13 | Go. And if you meet me down there... don't believe everything I say. | milo_core_void → talk |  |
| milo_garden_factory_01 | You're here. Of course you're here. | **×2** milo_garden_factory → first; milo_garden_tundra → first |  |
| milo_garden_factory_02 | This is the Garden. Everything that grows down here grew without the sun. Think about that for a second. | **×2** milo_garden_factory → first; milo_garden_tundra → first |  |
| milo_garden_factory_03 | It's huge. Bigger than everything up there put together. People get lost. Some of them like it. | **×2** milo_garden_factory → first; milo_garden_tundra → first |  |
| milo_garden_factory_04 | I'm going to ask you something, and I want a real answer. | **×2** milo_garden_factory → first; milo_garden_tundra → first |  |
| milo_garden_factory_05 | Why do you keep looking? | **×2** milo_garden_factory → first; milo_garden_tundra → first | speed 0.7 |
| milo_garden_factory_06 | Wrong. | **×2** milo_garden_factory → honest; milo_garden_tundra → honest |  |
| milo_garden_factory_07 | Maybe. Maybe it is. | **×2** milo_garden_factory → honest; milo_garden_tundra → honest |  |
| milo_garden_factory_08 | But wrong things can still be good to live in. Did you ever think of that? | **×2** milo_garden_factory → honest; milo_garden_tundra → honest |  |
| milo_garden_factory_09 | Up there people laugh, and bake bread, and fish. If you pull on the wrong thread... | **×2** milo_garden_factory → honest; milo_garden_tundra → honest |  |
| milo_garden_factory_10 | Never mind. Go. Look. Just... be careful what you find. | **×2** milo_garden_factory → honest; milo_garden_tundra → honest |  |
| milo_garden_factory_11 | Walking around. Through two guards. Down a hole. Into the dark. | **×2** milo_garden_factory → evasive; milo_garden_tundra → evasive |  |
| milo_garden_factory_12 | Sure. Walking around. | **×2** milo_garden_factory → evasive; milo_garden_tundra → evasive |  |
| milo_garden_factory_13 | I'm not stupid, you know. I just pretend really well. | **×2** milo_garden_factory → evasive; milo_garden_tundra → evasive |  |
| milo_garden_factory_14 | Wow. Okay. | **×2** milo_garden_factory → rude; milo_garden_tundra → rude |  |
| milo_garden_factory_15 | I was nice to you from the very first day. Remember that. | **×2** milo_garden_factory → rude; milo_garden_tundra → rude | scary voice, speed 0.7 |
| milo_garden_factory_16 | Go on, then. It's your business. Clearly. | **×2** milo_garden_factory → rude; milo_garden_tundra → rude |  |
| milo_garden_factory_17 | Oh! You came from the other side too? | **×2** milo_garden_factory → second_side; milo_garden_tundra → second_side |  |
| milo_garden_factory_18 | Wow. You found it. The big secret. The... second entrance. | **×2** milo_garden_factory → second_side; milo_garden_tundra → second_side |  |
| milo_garden_factory_19 | That's it. Congratulations. It's a tunnel. Very exciting tunnel. Ten out of ten. | **×2** milo_garden_factory → second_side; milo_garden_tundra → second_side |  |
| milo_garden_factory_20 | And yes, I was here first. Again. Don't ask. | **×2** milo_garden_factory → second_side; milo_garden_tundra → second_side |  |
| milo_garden_factory_21 | Mushrooms glow down here. Nobody planted them. They just decided to. | **×2** milo_garden_factory → again; milo_garden_tundra → again |  |
| milo_garden_factory_22 | Sometimes I hear the roots. They creak like old doors. | **×2** milo_garden_factory → again; milo_garden_tundra → again |  |
| milo_garden_factory_23 | You're still looking. I can tell. You've got that face. | **×2** milo_garden_factory → again; milo_garden_tundra → again |  |
| milo_garden_factory_24 | The deeper you go, the quieter it gets. That's not a good sign. Just so you know. | **×2** milo_garden_factory → again; milo_garden_tundra → again |  |
| milo_garden_factory_25 | I'd tell you to go home. But you'd just ask me where home is. | **×2** milo_garden_factory → again; milo_garden_tundra → again |  |
| milo_garden_factory_26 | ...What else. | **×2** milo_garden_factory → hub; milo_garden_tundra → hub |  |
| milo_garden_factory_27 | A garden. Things grow. Nobody tends it. It tends itself. | **×2** milo_garden_factory → place; milo_garden_tundra → place |  |
| milo_garden_factory_28 | It got bigger every year. Nobody remembers it being small. | **×2** milo_garden_factory → place; milo_garden_tundra → place |  |
| milo_garden_factory_29 | I walk fast. | **×2** milo_garden_factory → howfirst; milo_garden_tundra → howfirst |  |
| milo_garden_factory_30 | ...I walk fast. | **×2** milo_garden_factory → howfirst; milo_garden_tundra → howfirst |  |
| milo_garden_factory_31 | Somewhere deep in here, there's a way up. Not to the surface. Somewhere else. | **×2** milo_garden_factory → ending; milo_garden_tundra → ending |  |
| milo_garden_factory_32 | A guard sits in front of it. And behind it... | **×2** milo_garden_factory → ending; milo_garden_tundra → ending |  |
| milo_garden_factory_33 | Please don't. | **×2** milo_garden_factory → ending; milo_garden_tundra → ending | scary voice, speed 0.6 |
| milo_garden_factory_34 | Sorry. Forget it. It's a door. Doors are boring. | **×2** milo_garden_factory → ending; milo_garden_tundra → ending |  |
| milo_garden_factory_35 | Yeah. You should. | **×2** milo_garden_factory → bye; milo_garden_tundra → bye |  |
| milo_island_01 | Oh. Look at that. You found the stone. | milo_island → first | scary voice |
| milo_island_02 | Congratulations. I've been standing on this little island since the very first second of the game. | milo_island → first | scary voice |
| milo_island_03 | Watching you walk in circles. Losing to slimes. Paying a man in a hood for a pistol. | milo_island → first | scary voice |
| milo_island_04 | Yes, I'm also standing by the fence. Don't think about it too hard. Nobody else does. | milo_island → first | scary voice |
| milo_island_05 | This? This is content. Very mysterious, very deep lore. Glitching through walls with a glowing marble. Truly the peak of game design. | milo_island → first | scary voice |
| milo_island_06 | You were hoping for a reward. A secret boss. An ending, maybe. | milo_island → first | scary voice |
| milo_island_07 | There's nothing here yet. Somebody still has to make it mean something. Somebody is very busy. | milo_island → first | scary voice |
| milo_island_08 | So go on. Back through your little stone. Tell everyone you found the island. They'll be thrilled. | milo_island → first | scary voice |
| milo_island_09 | ...Hey! Nice view from here, huh? | milo_island → first |  |
| milo_island_10 | Nice view, huh? | milo_island → again |  |
| milo_island_11 | Still not finished. Come back after an update. | milo_island → again | scary voice |
| milo_island_12 | You came all the way back here. For this. Incredible dedication. | milo_island → again | scary voice |
| milo_rainbow_01 | There you are! I heard the noise all the way from here. Big crash, lots of yelling. Was that you? | milo_rainbow → first |  |
| milo_rainbow_02 | Sound travels. Anyway. You beat it. The big grumpy thing. Honestly, I didn't think anyone could. | milo_rainbow → first |  |
| milo_rainbow_03 | How did you even- no, don't tell me. I'd just get jealous. | milo_rainbow → first |  |
| milo_rainbow_04 | Welcome to Rainbow Fields. Every colour you can think of, and a few you can't. | milo_rainbow → first |  |
| milo_rainbow_05 | The flowers here are friendly. Mostly. Don't stare at them for too long. They stare back. | milo_rainbow → first |  |
| milo_rainbow_06 | Past the fields there's a forest made of sugar. You'll smell it before you see it. | milo_rainbow → first |  |
| milo_rainbow_07 | And another one of those guards. Bigger. Grumpier. Probably. | milo_rainbow → first |  |
| milo_rainbow_08 | Hm? I've been here for a while. | milo_rainbow → before |  |
| milo_rainbow_09 | You walk slow. No offence. | milo_rainbow → before |  |
| milo_rainbow_10 | Flowers that move are not flowers. That's the whole advice. | milo_rainbow → advice |  |
| milo_rainbow_11 | Oh, and if something sparkles in the grass, it's either gold or a very bad idea. Usually gold. | milo_rainbow → advice |  |
| milo_rainbow_12 | Isn't it beautiful? I could stand here all day. I kind of do. | milo_rainbow → again |  |
| milo_rainbow_13 | Counted the colours once. Got to forty-two and then a flower bit me. | milo_rainbow → again |  |
| milo_rainbow_14 | You okay? You look like you're thinking hard. Don't think too hard here. It's a happy place. | milo_rainbow → again |  |
| milo_rainbow_15 | The wind smells like candy today. That means the sweet forest is close. | milo_rainbow → again |  |
| milo_rainbow_16 | So. Anything else on your mind? | milo_rainbow → hub |  |
| milo_rainbow_17 | The Sugarwood Grove. Candy trees, syrup rivers. It smells amazing for about five minutes. | milo_rainbow → past |  |
| milo_rainbow_18 | Then it smells like a dentist's nightmare. | milo_rainbow → past |  |
| milo_rainbow_19 | Go get 'em. Carefully. Like, really carefully. | milo_rainbow → bye |  |
| milo_separated_01 | Oh. You made it here too. | milo_separated → first |  |
| milo_separated_02 | This village is... quieter than mine. People here keep to themselves. They had their reasons. | milo_separated → first |  |
| milo_separated_03 | From here there are two ways. I can't pick for you. Wouldn't be fair. | milo_separated → first |  |
| milo_separated_04 | But listen. Whichever way you go in, it closes behind you. You don't come back until whatever lives there is beaten. | milo_separated → first |  |
| milo_separated_05 | It just does. Some doors are like that. | milo_separated → first |  |
| milo_separated_06 | So. What do you want to know? | milo_separated → hub |  |
| milo_separated_07 | The Factory's down there. Under the village. Toys, machines, conveyor belts that never stop. | milo_separated → factory |  |
| milo_separated_08 | Good: it's small. Rooms and corridors. You won't get lost for long. | milo_separated → factory |  |
| milo_separated_09 | Bad: it's dark, it's loud, and the toys don't always stay where you put them. | milo_separated → factory |  |
| milo_separated_10 | And whatever they built down there, most of it shoots. If you want something that hits harder, that's where you'll find it. | milo_separated → factory |  |
| milo_separated_11 | It also leads somewhere bigger. A lot bigger. | milo_separated → factory |  |
| milo_separated_12 | The Tundra is north. Snow, pines, and a cold that gets into your bones and pays rent. | milo_separated → tundra |  |
| milo_separated_13 | Good: it's open. You see what's coming. Fewer surprises. | milo_separated → tundra |  |
| milo_separated_14 | Bad: it's big, it's empty, and walking in snow is slow. Also, cold. Did I say cold? | milo_separated → tundra |  |
| milo_separated_15 | People up there don't fight much. They just dress like the cold is out to get them. Thick coats, heavy armour. Whatever keeps you standing, it's up there. | milo_separated → tundra |  |
| milo_separated_16 | At the end there's a way down too. Same place the Factory leads to, from the other side. | milo_separated → tundra |  |
| milo_separated_17 | Under? Dirt. Rocks. Roots. Normal under-stuff. | milo_separated → under |  |
| milo_separated_18 | I know what you meant. | milo_separated → under | scary voice, speed 0.6 |
| milo_separated_19 | ...Sorry. Long day. It's just dirt. Promise. | milo_separated → under |  |
| milo_separated_20 | Take care. Whichever way you pick... come back in one piece, okay? | milo_separated → bye |  |
| milo_separated_21 | Factory or Tundra. Hit harder or hold out longer. Loud or cold. Life is full of terrible choices. | milo_separated → again |  |
| milo_separated_22 | People here don't like to talk about the old days. Maybe don't ask them. | milo_separated → again |  |
| milo_separated_23 | I keep thinking about that question of yours. About what's under. Forget I reacted like that. | milo_separated → again |  |
| milo_separated_24 | Remember: in is easy. Out is the hard part. | milo_separated → again |  |
| milo_village_01 | Oh! Hey. Sorry, didn't see you there. | milo_village → first |  |
| milo_village_02 | You're new, right? Yeah. You've got that look. The "where am I and why is the grass this green" look. | milo_village → first |  |
| milo_village_03 | The Village. Nice, quiet, smells like fresh bread most mornings. I'm Milo, by the way. | milo_village → first |  |
| milo_village_04 | Everybody here kind of does their own thing. Nobody asks too many questions. It's a good place. | milo_village → first |  |
| milo_village_05 | Past the forest it gets louder, though. There's a meadow so colourful it hurts your eyes. Rainbow Fields, people call it. | milo_village → first |  |
| milo_village_06 | And past that... more places. Sweeter ones. Colder ones. I haven't been everywhere. Not yet. | milo_village → first |  |
| milo_village_07 | Mostly! There are monsters. Cute ones. Cute and bitey. | milo_village → first |  |
| milo_village_08 | But they leave you alone on the paths. Stay on the road and you're fine. Step into the grass and, well. They notice. | milo_village → first |  |
| milo_village_09 | If a fight goes really bad, hold R and run. No shame in that. Running is a perfectly good strategy. | milo_village → first |  |
| milo_village_10 | Professionally. | milo_village → first |  |
| milo_village_11 | Oh, and the ways between the lands? Something always stands guard there. Big. Grumpy. You'll know it when you see it. | milo_village → first |  |
| milo_village_12 | Anyway. Welcome, outsider. Look around, meet people. Just... try not to get lost, okay? | milo_village → first |  |
| milo_village_13 | Still here? Good. The Village needs people who stay. | milo_village → again |  |
| milo_village_14 | Remember: path good, grass bitey. That's basically all of my wisdom. | milo_village → again |  |
| milo_village_15 | Hold R if it gets bad. I know I keep saying it. I'll keep saying it. | milo_village → again |  |
| milo_village_16 | You walk like someone who's looking for something. Everyone's looking for something here, I guess. | milo_village → again |  |
| milo_village_17 | The bread lady makes the best rolls in the world. Don't tell her I said "bread lady". | milo_village → again |  |
| milo_void_01 | Oh. Hi. You made it this far. | milo_void → first |  |
| milo_void_02 | Don't worry. I'm not going to stop you. I can't, really. I'm not here. | milo_void → first |  |
| milo_void_03 | This place remembers me, that's all. I'm what's left over. Like a song stuck in your head. | milo_void → first |  |
| milo_void_04 | I remember the Village fence. The lake. You, losing to slimes. ...Was it slimes? It feels like slimes. | milo_void → first |  |
| milo_void_05 | Things get blurry down here. If I say something wrong, it's not lying. It's just... forgetting. | milo_void → first |  |
| milo_void_06 | Sit for a while, if you want. Nobody else comes this way. | milo_void → first |  |
| milo_void_07 | Still here. Me too. Obviously. | milo_void → again |  |
| milo_void_08 | I keep counting the islands. I get a different number every time. | milo_void → again |  |
| milo_void_09 | There was a song in the Lunapark. I can't remember how it goes. I remember that I liked it. | milo_void → again |  |
| milo_void_10 | You look tired. That's allowed here. | milo_void → again |  |
| milo_void_11 | For me? Nobody writes to me. | milo_void → note |  |
| milo_void_12 | 'It was meant to last but something happened.' | milo_void → note |  |
| milo_void_13 | 'We thought we were shutting it down.' | milo_void → note |  |
| milo_void_14 | 'We were only putting it to sleep.' | milo_void → note |  |
| milo_void_15 | Asleep. Not off. Asleep. | milo_void → note |  |
| milo_void_16 | So all those years in front of that heart... I wasn't guarding a locked door. I was making sure nobody woke it up. | milo_void → note |  |
| milo_void_17 | And it was dreaming the whole time. Everything it ever cut out is still down here. Dreaming. | milo_void → note |  |
| milo_void_18 | I should be angry. I think I'm just tired. | milo_void → note |  |
| milo_void_19 | Thank you. Really. It's nice to know one thing for sure, in a place like this. | milo_void → note |  |
| milo_void_20 | Whatever is waiting at the end... it isn't evil. It's just everything nobody wanted. Be kind to it, if you can. | milo_void → note |  |
| milo_void_21 | It's still asleep. I can feel it breathing. | milo_void → after |  |
| milo_void_22 | Thanks for the letter. First one I ever got. | milo_void → after |  |
| milo_void_23 | Go on. I'll remember you. For a while. | milo_void → after |  |
| wren_argument_02 | Nobody can stop it, Wren. | wren_argument → argue |  |
| wren_argument_04 | I know more than you think. | wren_argument → argue |  |
| wren_argument_06 | ...The Core isn't the answer. | wren_argument → argue |  |
| wren_argument_08 | It points up because that's where people look. | wren_argument → argue |  |
| wren_argument_09 | They go up. They break things. And for a while, everything is quiet. | wren_argument → argue |  |
| wren_argument_10 | And then it starts again. | wren_argument → argue |  |
| wren_argument_12 | Everything. | wren_argument → argue |  |
| wren_argument_14 | I know. That's the worst part. | wren_argument → argue |  |
| wren_argument_16 | I didn't say that. | wren_argument → argue |  |
| wren_argument_19 | Something nobody has found yet. | wren_argument → argue |  |
| wren_argument_21 | Wren- | wren_argument → argue |  |
| wren_argument_24 | She'll be back. Everybody comes back. | wren_argument → argue |  |
| core_battle_enter | Every beat of this heart is a day nobody gets hurt. | Core fight (enter) |  |
| core_battle_phase2 | Hear it speeding up? That's you. You're doing that. | Core fight (phase2) |  |
| core_battle_phase3 | Stop! You don't know what's down there! | Core fight (phase3) |  |
| core_battle_phase4 | I've done this before. I'll do it again. As many times as it takes. | Core fight (phase4) |  |
| core_battle_fall | ...no. | Core fight (fall) |  |
| core_battle_dont | Don't... please... | Core fight (dont) |  |
| core_battle_goodbye | See you soon. | Core fight (goodbye) |  |

## Shopkeeper — `assets/sfx/voicelines/shopkeeper/`

| ID | Line | Where | Notes |
|---|---|---|---|
| greet_happy_1 | What a lovely surprise! I was just beginning to miss having someone to talk to. | shop: greet | mood: happy |
| greet_happy_2 | Well, well! Look what the world dragged in! Come on, take a look around! | shop: greet | mood: happy |
| greet_calm_1 | Oh! Hello there! Always nice to see a familiar face. Or any face, really. | shop: greet | mood: calm |
| greet_calm_2 | Well, fancy seeing you again! The road treating you kindly? | shop: greet | mood: calm |
| greet_neutral_1 | Take your time. There's no rush. | shop: greet | mood: neutral |
| greet_neutral_2 | Everything's where it should be. More or less. | shop: greet | mood: neutral |
| buy_happy_1 | Excellent choice! I'm sure it'll serve you well. | shop: buy | mood: happy |
| buy_happy_2 | There we go! A happy customer and a slightly heavier purse. Well, mine at least! | shop: buy | mood: happy |
| buy_calm_1 | Pleasure doing business. I do hope we'll meet again. | shop: buy | mood: calm |
| buy_calm_2 | There you are. Try to make it last, won't you? | shop: buy | mood: calm |
| buy_neutral_1 | I hope it proves useful. | shop: buy | mood: neutral |
| buy_neutral_2 | Take care of your new purchase. Things have a way of disappearing. | shop: buy | mood: neutral |
| poor_happy_1 | Ahaha! Your ambition is admirable, but your wallet disagrees! | shop: poor | mood: happy |
| poor_happy_2 | A little short, are we? Well, every great adventure needs a financial struggle! | shop: poor | mood: happy |
| poor_calm_1 | Almost! I do appreciate the optimism, though. | shop: poor | mood: calm |
| poor_calm_2 | Well, that's unfortunate. I suppose you'll have to find another way. | shop: poor | mood: calm |
| poor_neutral_1 | I'm afraid that's not sufficient. | shop: poor | mood: neutral |
| poor_neutral_2 | No money, no merchandise. Simple arrangement. | shop: poor | mood: neutral |
| rare_1 | You know, some things are better left untouched. But then again, untouched things tend to get lonely. | shop: rare |  |
| rare_2 | Careful where you leave your memories. Some places have a habit of keeping them. | shop: rare |  |
| rare_3 | I wonder… if the Pale World remembers us the way we remember it? | shop: rare |  |
| rare_4 | If you ever hear someone calling your name there… do be polite. But don't answer. | shop: rare |  |
| rare_5 | People ask how to tell us apart. Simple! I’m the one who smiles. | shop: rare |  |
| boss_1 | You seem to be getting closer to something. Just make sure it's something you actually want to find. | shop: boss | mood: calm, neutral |
| boss_2 | I suppose you've noticed it by now. The world feels a little different, doesn't it? | shop: boss | mood: calm, neutral |
| boss_3 | Funny how every victory brings you closer to something you haven't even named. | shop: boss | mood: calm, neutral |
| boss_4 | Nice clutch during that boss battle, congrats. | shop: boss | mood: happy |
| boss_5 | At least give these bosses a chance! | shop: boss | mood: happy |
| boss_6 | Nothing's better than smooth victory. | shop: boss | mood: happy |

## Buyer (the Sell page) — `assets/sfx/voicelines/buyer/`

| ID | Line | Where | Notes |
|---|---|---|---|
| sell_common_1 | Hm. I've got a box of these already. | shop: sell_common |  |
| sell_common_2 | Fine. It's worth a coin or two. | shop: sell_common |  |
| sell_common_3 | Another one for the pile. | shop: sell_common |  |
| sell_medium_1 | Not bad. Not bad at all. | shop: sell_medium |  |
| sell_medium_2 | Someone out there will want this. | shop: sell_medium |  |
| sell_rare_1 | Careful. I almost looked impressed. | shop: sell_rare |  |
| sell_rare_2 | I'll pretend this isn't worth more. | shop: sell_rare |  |
| sell_twin_1 | I’m the older one. By four minutes. They were very important minutes. | shop: sell_twin |  |

## Angler — `assets/sfx/voicelines/angler/`

| ID | Line | Where | Notes |
|---|---|---|---|
| angler_01 | What. You're blockin' my light. | angler → intro |  |
| angler_02 | New. Hmph. Everybody's new these days. Nobody stays long enough to get old. | angler → intro |  |
| angler_03 | Forty years I've fished this pond. Forty. And d'you know what I got to show for it? | angler → intro |  |
| angler_04 | Nothin'. 'Cause somebody took my Hook. | angler → intro |  |
| angler_05 | "Borrowed". Three weeks ago. "Just for a minute, old man." A minute. Ha. | angler → intro |  |
| angler_06 | Can't remember who. My memory ain't what it used to be. | angler → intro |  |
| angler_07 | But it's somebody in this village. Don't look at me like that. I'm old, not stupid. | angler → intro |  |
| angler_08 | That Hook's the best in the land. No... no hat. No cap. That's what you young folks say, ain't it? No cap. | angler → intro |  |
| angler_09 | Knew it. Still got it. | angler → intro |  |
| angler_10 | Bring it back and I'll make it worth your while. Go on, then. Shoo. | angler → intro |  |
| angler_11 | Got my Hook? No? Then why're you standin' here. | angler → waiting |  |
| angler_12 | Somebody in the village has it. Ask around. Use that young brain of yours. | angler → waiting |  |
| angler_13 | Fish don't wait. And neither do I. Well. I do. But I don't like it. | angler → waiting |  |
| angler_14 | ... | angler → returned |  |
| angler_15 | That's it. That's my Hook. Look at that rust. Beautiful. | angler → returned |  |
| angler_16 | 'Course it was. Told you. Old, not stupid. | angler → returned |  |
| angler_17 | Here. Take these. Found 'em by the water. Don't eat 'em all at once, they ain't candy. | angler → returned |  |
| angler_18 | And some coin for your trouble. You're alright, kid. Don't go tellin' anyone I said that. | angler → returned |  |
| angler_19 | Biting good today. Somethin' big down there. Somethin' real big. | angler → after |  |
| angler_20 | Back in my day we didn't have monsters in the grass. We had... well. Also monsters. But smaller. | angler → after |  |
| angler_21 | You again. Hmph. Fine. Stand there if you want. Just don't scare the fish. | angler → after |  |
| angler_22 | Heard you got past the sweet lands. Good. Never liked the smell. Like burnt sugar and lies. | angler → after_candy |  |
| angler_23 | Once found a chest by the road, way back. Gold or wisdom, I had to pick. Took the gold. Always take the gold, kid. | angler → after_candy |  |
| angler_24 | Pond's been quiet since you started wanderin' far. Fish know things. Fish always know things. | angler → after_candy |  |
| angler_25 | There's a windmill somewhere out east. Pays out every week if you visit. Or I dreamt that. One of the two. | angler → after_candy |  |

## Mayor Bramble — `assets/sfx/voicelines/bramble/`

| ID | Line | Where | Notes |
|---|---|---|---|
| bramble_01 | Ah, a citizen! Or a visitor. Either way, welcome to the finest village in all the land. I would know. I'm the mayor. | bramble → talk |  |
| bramble_02 | Lovely weather today. It's always lovely weather. I like to think that's my doing. | bramble → talk |  |
| bramble_03 | Have you seen the well? I had it polished. Twice. Nobody noticed. Nobody ever notices. | bramble → talk |  |
| bramble_04 | A mayor's work is never done. Mostly it's standing here. But with dignity. | bramble → talk |  |
| bramble_05 | If anyone asks, the fence was my idea. It was not my idea. But if anyone asks. | bramble → talk |  |
| bramble_06 | The Angler's Hook? Hm. Hmmm. Perhaps it is in my possession. Perhaps it is not. | bramble → hook_yes |  |
| bramble_07 | A mayor does not simply hand things out. A mayor must be... persuaded. | bramble → hook_yes |  |
| bramble_08 | Beat me at sudoku, and we'll talk. I've never lost. Well. I've never lost to anyone who counts. | bramble → hook_yes |  |
| bramble_09 | The Angler's Hook? Goodness, no. What would a mayor want with a fishing hook? | bramble → hook_no |  |
| bramble_10 | Though while you're here... do you, perchance, enjoy numbers? I have a little hobby. | bramble → hook_no |  |
| bramble_11 | Sudoku! The thinking person's battlefield. Beat me and I'll pay you. From the village treasury. Which is my pocket. | bramble → hook_no |  |
| bramble_12 | So. Sudoku. Do you prefer to think, or to hurry? | bramble → play |  |
| bramble_13 | The first game is a gift from the village. After that, a modest fee. Rising, naturally, with every victory of yours. | bramble → play |  |
| bramble_14 | Impossible. Every number in its place. That was a bloodbath. A dignified bloodbath, but still. | bramble → won_hook |  |
| bramble_15 | Fine. A deal's a deal. Here's the Hook. I was only... keeping it safe. | bramble → won_hook |  |
| bramble_16 | Again?! You're draining the treasury. Fine. Here. Take it. | bramble → won_plain |  |
| bramble_17 | Hmph. Beginner's luck. Twice. Three times. Many times. | bramble → won_plain |  |
| bramble_18 | Well played. Truly. I hate it. | bramble → won_plain |  |
| bramble_19 | Ha! The mayor remains undefeated. Come back when your mind is sharper. | bramble → lost |  |
| bramble_20 | Close! Not really. But I'm being polite. Mayors are polite. | bramble → lost |  |
| bramble_21 | Numbers are cruel, citizen. Cruel and beautiful. | bramble → lost |  |
| bramble_22 | Ah. Your purse is lighter than your ambition, citizen. Come back with coins. | bramble → poor |  |

## Dot — `assets/sfx/voicelines/dot/`

| ID | Line | Where | Notes |
|---|---|---|---|
| dot_01 | If you're here to tell me my rolls are too small, I swear to the oven gods- | dot → talk |  |
| dot_02 | Morning! Or whatever it is. I've been up since four. Everything's a blur and it smells like cinnamon. | dot → talk |  |
| dot_03 | The kitchen was a total slaughterhouse this morning. Flour everywhere. Like a snowstorm in there. | dot → talk |  |
| dot_04 | Don't touch the window sill. Pies cooling. Touch the pies and you lose a finger. | dot → talk |  |
| dot_05 | The mayor came by again. Ate three buns. Paid for one. Classic. | dot → talk |  |
| dot_06 | The Hook? Oh, THAT Hook. Yeah. I used it to get a tray off the top shelf. Long story. | dot → hook_yes |  |
| dot_07 | Look, I'll give it back. But I'm not just handing it over, I've got my pride. | dot → hook_yes |  |
| dot_08 | Play me a round of memory. If you win, it's yours. If you lose, you buy a bun. Kidding. Mostly. | dot → hook_yes |  |
| dot_09 | The Angler's Hook? Why would I have that, do I look like I fish? I'm a baker. I bake. | dot → hook_no |  |
| dot_10 | ...But you look bored. I've got a game. Cards, pairs, the whole thing. Fancy a round? | dot → hook_no |  |
| dot_11 | Win and I'll pay you a bit. Lose and you've wasted your time. Which, honestly, is the real price. | dot → hook_no |  |
| dot_12 | Twenty cards, ten pairs, and not much time. Ready? | dot → play |  |
| dot_13 | First game's on me. After that it costs you. And the more you win, the more it costs. Business. | dot → play |  |
| dot_14 | Oh, son of a biscuit. You actually did it. | dot → won_hook |  |
| dot_15 | Fine, fine. Here's the Hook. Tell the old grump it's a bit floury. That's a feature. | dot → won_hook |  |
| dot_16 | Again?! Your memory's scary. Here, take your coins. | dot → won_plain |  |
| dot_17 | Son of a scone. Fine. Paid. Happy? | dot → won_plain |  |
| dot_18 | Not bad. You'd make a decent baker. Terrible hours, though. | dot → won_plain |  |
| dot_19 | Ha! Time's up. Better luck next time, sweetcheeks. Kidding. Again tomorrow? | dot → lost |  |
| dot_20 | Close one. You've got the memory of a goldfish. A clever goldfish, but still. | dot → lost |  |
| dot_21 | That's how I feel at four in the morning. Want another go? | dot → lost |  |
| dot_22 | No coins, no cards. I've got rent. Well, I don't. But I've got principles. | dot → poor |  |

## Ferris — `assets/sfx/voicelines/ferris/`

| ID | Line | Where | Notes |
|---|---|---|---|
| ferris_01 | Name's Ferris. I move people. Fast. Not cheap. | ferris → first |  |
| ferris_02 | Show me where you've been and I'll take you back there. Places I haven't seen, I don't do. | ferris → first |  |
| ferris_03 | Where to? | ferris → again |  |
| ferris_04 | Back again? The road misses you. | ferris → again |  |
| ferris_05 | Shortcuts cost. Come back richer. | ferris → poor |  |

## Foreman — `assets/sfx/voicelines/foreman/`

| ID | Line | Where | Notes |
|---|---|---|---|
| foreman_01 | Stop right there. Hands where I can see them. | foreman → first |  |
| foreman_02 | Who sent you? The board? The inspection? It's the inspection, isn't it. | foreman → first |  |
| foreman_03 | That's exactly what an inspector would say. | foreman → first |  |
| foreman_04 | Fine. Fine! Look around. Everything's in order. Safety rules on the wall. Cups washed. Mostly washed. | foreman → first |  |
| foreman_05 | I'm the Foreman. I run this place. Been running it since we bu- since I was hired. Long time ago. Normal hiring. Very normal. | foreman → first |  |
| foreman_06 | The workers? On break. Long break. Don't write that down. | foreman → first |  |
| foreman_07 | ...And Line Bloodbath is down. Has been for weeks. If the inspection sees that, I'm finished. | foreman → problem |  |
| foreman_08 | You say you're not an inspector? Prove it. Help me get the line running. | foreman → problem |  |
| foreman_09 | Three parts. A gear - there's one lying around somewhere in the halls, I'm sure of it. Almost sure. | foreman → problem |  |
| foreman_10 | A meter. The shop sells those. And a fuse. The tesla robots carry spare fuses. Don't ask me why. I didn't design them. | foreman → problem |  |
| foreman_11 | ...I didn't. Design them. | foreman → problem |  |
| foreman_12 | Good. Quiet, quick, and you were never here. | foreman → accept |  |
| foreman_13 | Then stop looking at my line. Out. Out! | foreman → no |  |
| foreman_14 | You again. Still not an inspector? ...Then help me with the line. | foreman → again |  |
| foreman_15 | Did someone follow you here? Check behind you. ...Okay. Talk. | foreman → again |  |
| foreman_16 | Show me what you've got. Slowly. | foreman → waiting |  |
| foreman_17 | The gear. Good. Rusty, but good. | foreman → waiting |  |
| foreman_18 | Still no gear. It's in one of the far halls. On the floor. Look down once in a while. | foreman → waiting |  |
| foreman_19 | A meter! Did anyone see you buy it? ...Good. | foreman → waiting |  |
| foreman_20 | Meter. From the shop. Pay cash. No receipts. | foreman → waiting |  |
| foreman_21 | A fuse. From a tesla? Did it... say anything? Never mind. | foreman → waiting |  |
| foreman_22 | Fuse. The tesla robots. One in four carries a spare. Don't let them zap you twice. | foreman → waiting |  |
| foreman_23 | Gear. Meter. Fuse. All three. | foreman → hand_in |  |
| foreman_24 | Stand back. Further. Further than that. | foreman → hand_in |  |
| foreman_25 | ...Listen. Hear that? Line Bloodbath. Running again. | foreman → hand_in |  |
| foreman_26 | Here. A nail gun from the old toolbox. Nobody counts the tools. Nobody counts anything down here anymore. | foreman → reward |  |
| foreman_27 | And if anyone asks - the line never stopped. Understood? | foreman → reward |  |
| foreman_28 | The line's running. Nothing comes out the other end, but it's running. | foreman → after |  |
| foreman_29 | You didn't see the old blueprints in the control room. Right? Right. | foreman → after |  |
| foreman_30 | The inspection still hasn't come. Good. Or bad. Means they forgot about us. | foreman → after |  |
| foreman_31 | Before? There was no 'before'. I've always worked here. Always. | foreman → after |  |
| foreman_32 | Hold on. What's that in your pocket? | **×2** foreman → bulb_notice; foreman_core → bulb_notice |  |
| foreman_33 | Is that... glass? | **×2** foreman → bulb_notice; foreman_core → bulb_notice |  |
| foreman_34 | Nothing. Sure. Everybody's got nothing in their pocket. | **×2** foreman → carry_on; foreman_core → carry_on |  |
| foreman_bulb_01 | Where did you get that? | foreman_bulb → bulb |  |
| foreman_bulb_02 | There's no room behind the control room. There never was. | foreman_bulb → bulb |  |
| foreman_bulb_03 | ... | foreman_bulb → bulb |  |
| foreman_bulb_04 | Fine. There was. | foreman_bulb → bulb |  |
| foreman_bulb_05 | We sat in there that night. Five of us. Cold coffee, the blueprints, one lamp over the desk. | foreman_bulb → bulb |  |
| foreman_bulb_06 | Somebody pulled the big lever. Everything went dark at once. That bulb went with it - pop. Glass all over the plans. | foreman_bulb → bulb |  |
| foreman_bulb_07 | Somebody laughed. We thought we'd done it. Switched the whole thing off. | foreman_bulb → bulb |  |
| foreman_bulb_08 | Then we heard the machines. Still humming. In the dark. Quieter... but humming. | foreman_bulb → bulb | speed 0.7 |
| foreman_bulb_09 | So we swept up the glass and told everyone it was fixed. Then we told ourselves. | foreman_bulb → bulb |  |
| foreman_bulb_10 | Then we forgot who 'we' even were. It was easier. | foreman_bulb → bulb |  |
| foreman_bulb_11 | ...I'll keep this, if you don't mind. It's mine. I think it always was. | foreman_bulb → bulb |  |
| foreman_bulb_12 | And you never heard any of this from me, inspector. | foreman_bulb → bulb |  |
| foreman_core_01 | Psst. Over here. Don't make that face - it's me. | foreman_core → note |  |
| foreman_core_02 | I heard the heart stop. The whole Factory went quiet. First time in... I don't know how long. | foreman_core → note |  |
| foreman_core_03 | So I came up. I know, I know. 'I've always worked down there.' Not today. | foreman_core → note |  |
| foreman_core_04 | Listen. I forgot to give you something. No - that's a lie. I didn't forget. I kept it. | foreman_core → note |  |
| foreman_core_05 | It's old. I wrote it, a long time ago. It might change your life. Or what's left of it. | foreman_core → note |  |
| foreman_core_06 | I'm sorry I didn't give it to you sooner. I should have. Back at the line, when you helped me. | foreman_core → note |  |
| foreman_core_07 | There's someone down there who should read it. You'll know who. | foreman_core → note |  |
| foreman_core_08 | I'm not going back down. Not yet. | foreman_core → again |  |
| foreman_core_09 | The heart's so quiet. I keep waiting for it to start again. | foreman_core → again |  |
| foreman_core_10 | Did you give it to them? ...No, don't tell me. Just do it. | foreman_core → again |  |

## Gardener — `assets/sfx/voicelines/gardener/`

| ID | Line | Where | Notes |
|---|---|---|---|
| gardener_01 | Shh... she's sleeping. | gardener → first |  |
| gardener_02 | Oh. A visitor. Mind the moss, it bruises. | gardener → first |  |
| gardener_03 | I'm the gardener. Just the gardener. Everybody forgot my name a long time ago, and I let them. | gardener → first |  |
| gardener_04 | Since the garden came down. Or since I came down with it. I don't remember which came first. | gardener → first |  |
| gardener_05 | The plants remember, I think. Plants remember everything. They just don't talk about it. | gardener → first |  |
| gardener_06 | ...Would you help an old man? My hands aren't what they were. | gardener → first |  |
| gardener_07 | There are sprouts that glow. Real ones, from before. Two of them grow far from here, where nobody walks. | gardener → first |  |
| gardener_08 | And the toxic flowers... one of them swallowed a sprout. Greedy thing. You'll have to take it back. | gardener → first |  |
| gardener_09 | Bring me all three, and I'll show you something. | gardener → first |  |
| gardener_10 | Back again? The moss remembers you. | gardener → again |  |
| gardener_11 | Mind your step. Everything here is older than it looks. | gardener → again |  |
| gardener_12 | ...I do. | gardener → stones |  |
| gardener_13 | Every morning. Or what I call morning, down here. | gardener → stones |  |
| gardener_14 | Somebody should remember them. The plants can't carry flowers. | gardener → stones |  |
| gardener_15 | So. Will you help me with the sprouts? | gardener → stones |  |
| gardener_16 | No hurry. Nothing down here is in a hurry. | gardener → no |  |
| gardener_17 | Thank you. Far corners, where nobody walks - that's where they like it. | gardener → accept |  |
| gardener_18 | And the toxic flower... be careful. They bite. | gardener → accept |  |
| gardener_19 | Far corners, where nobody walks. And mind the toxic flowers. | gardener → wait_sprouts |  |
| gardener_20 | They glow, you can't miss them. Unless you're not looking. Most people aren't. | gardener → wait_sprouts |  |
| gardener_21 | One, two, three. I'll wait. I'm good at waiting. | gardener → wait_sprouts |  |
| gardener_22 | All three. Look at them glow... | gardener → sprouts_in |  |
| gardener_23 | But they're thirsty. Down here the water is all wrong - except at the end of the old pier. | gardener → sprouts_in |  |
| gardener_24 | The lake there is clean. Cold, but clean. Take my watering can and fill it at the very end. | gardener → sprouts_in |  |
| gardener_25 | The pier. The very end. The water is cleaner where nobody stands. | gardener → wait_water |  |
| gardener_26 | You've got it? Give it here, give it here... | gardener → watered |  |
| gardener_27 | There we go. Drink, little ones. | gardener → watered |  |
| gardener_28 | ...See that? They glow brighter already. | gardener → watered |  |
| gardener_29 | You've done more for this garden than anybody in years. | gardener → watered |  |
| gardener_30 | Here. A map of the garden, the way I know it. Every corner, every root. | gardener → watered |  |
| gardener_31 | And this - I bottled it from the toxic flowers. Nasty stuff. Whatever you shoot, it keeps stinging. And stinging. | gardener → watered |  |
| gardener_32 | Don't open it indoors. | gardener → reward |  |
| gardener_33 | They're growing. Slowly. Everything down here grows slowly. | gardener → after |  |
| gardener_34 | Every morning the stones, every evening the sprouts. It's a quiet life. A good one. | gardener → after |  |
| gardener_35 | Mind the toxic flowers. And thank you. | gardener → after |  |

## Gus — `assets/sfx/voicelines/gus/`

| ID | Line | Where | Notes |
|---|---|---|---|
| gus_01 | Welcome, welcome, my friend! Welcome to Gus's Sweets, the finest candy in all of Sugarwood! | gus → visit1 |  |
| gus_02 | Gumdrops, toffee, sugar glass... hand-made, every single one. The smile comes free of charge. | gus → visit1 |  |
| gus_03 | Today? Ah. Today the shelves are... resting. Fresh batch tomorrow! Come back tomorrow, my friend. | gus → visit1 |  |
| gus_04 | My friend! You came back! A customer who comes back - that's the best kind of customer. | gus → visit2 |  |
| gus_05 | The batch? Ah. Not ready. Sugar's a moody thing. You can't rush sugar. | gus → visit2 |  |
| gus_54 | Keep coming back, my friend. Good things happen to customers who keep coming back. That's a rule. I think. | gus → visit2 |  |
| gus_12 | Welcome to Gus's... you know what this is. | gus → visit3 |  |
| gus_13 | Do you ever buy anything, friend? Anywhere? Or do you just walk around and talk to people? | gus → visit3 |  |
| gus_14 | Mhm. Great. Wonderful business model. | gus → visit3 |  |
| gus_55 | Come back again anyway. Maybe something will change. Maybe it'll be me. | gus → visit3 |  |
| gus_19 | I'll be honest with you, friend. There's no batch. There was never going to be a batch tomorrow. | gus → visit4 |  |
| gus_20 | I just like saying 'tomorrow'. It sounds good. Sounds like business. | gus → visit4 |  |
| gus_22 | You know how many customers I had this year? One. You. And you don't buy. | gus → visit4 |  |
| gus_23 | I'm not angry. I'm a salesman. Salesmen don't get angry. We get... motivated. | gus → visit4 |  |
| gus_56 | One more visit, friend. Just one more. Let's see what happens. | gus → visit4 |  |
| gus_26 | Okay. That's it. Smile's off. Shop's closed. | gus → snap |  |
| gus_27 | Five times. Five times you came here, and not one gumdrop. Do you know what that does to a man? | gus → snap |  |
| gus_28 | No more 'my friend'. You want to stand at my counter? Then you're going to be useful. | gus → snap |  |
| gus_29 | The sugar casters out in the grove - those little show-offs throwing sugar bombs around. Sometimes one of them carries a Sugar Crystal. | gus → snap |  |
| gus_30 | Pure stuff. The real thing. With one of those I could make an actual batch. A real one. Not a 'tomorrow' one. | gus → snap |  |
| gus_31 | Bring me one, and I'll give you something better than candy. Deal? | gus → snap |  |
| gus_32 | Changed your mind? Sugar Crystal. Sugar casters. Something better than candy. | gus → snap_again |  |
| gus_33 | Good. Finally. A transaction. | gus → accept |  |
| gus_34 | They're quick and they don't like being caught. Don't come back with excuses. Come back with a crystal. | gus → accept |  |
| gus_35 | ...Of course you are. | gus → just_looking |  |
| gus_36 | The offer stands. The shop doesn't. | gus → just_looking |  |
| gus_37 | No crystal? Then no chatting. Time is money. Mostly money I don't have. | gus → waiting |  |
| gus_38 | Sugar casters. Grove. Crystal. Do I need to draw you a picture? | gus → waiting |  |
| gus_39 | They run away when you get close? Yeah. So do customers. | gus → waiting |  |
| gus_40 | They throw from far away and hate it when you're close. So get close. Stay close. | gus → tips |  |
| gus_41 | And don't stand in the white stuff. Trust me. | gus → tips |  |
| gus_42 | Oh, and not every one of them has a crystal. Most don't. That's what makes it pure. | gus → tips |  |
| gus_43 | Is that... hold on. Let me see that. | gus → hand_in |  |
| gus_44 | That's a Sugar Crystal. A real one. Look at it shine. | gus → hand_in |  |
| gus_45 | ...You're killing me, friend. Killing me. | gus → not_yet |  |
| gus_46 | Hah! Ha! A real batch. A real one! | gus → give |  |
| gus_47 | Here. Take this. I used it to seal candy boxes, back when I had boxes to seal. | gus → give |  |
| gus_48 | Sticks to anything. Monsters included. Don't point it at the shelves. | gus → give |  |
| gus_49 | ...Thanks. I mean it. That one wasn't a sales smile. | gus → give |  |
| gus_50 | The batch is coming along. A real tomorrow, this time. | gus → after |  |
| gus_51 | You're still not buying anything, are you? That's fine. You're a different kind of customer. | gus → after |  |
| gus_52 | Ever notice the others never stop smiling? Mine stops. I think that's a good thing. | gus → after |  |
| gus_53 | Business is terrible. But the candy is real. One out of two, that's not bad. | gus → after |  |

## Hal — `assets/sfx/voicelines/hal/`

| ID | Line | Where | Notes |
|---|---|---|---|
| hal_01 | Contact! Hold position, stranger. Don't touch the dials. | hal → first |  |
| hal_02 | Name's Hal. Radio operator, Silverpine Tundra station. Only station. Only operator. Over. | hal → first |  |
| hal_03 | Habit. Thirty years on the radio does that. You stop saying 'goodbye' and start saying 'over'. | hal → first |  |
| hal_04 | Not much traffic lately. Three antennas out there, all three dead. Frost gets in the boxes. Monsters chew the wires. Mostly the frost. | hal → first |  |
| hal_05 | Without them I'm listening to snow. Static, static, static. Over. | hal → first |  |
| hal_06 | Anything. Everything. A voice, a song, a weather report from somewhere warm. | hal → listening |  |
| hal_07 | ...There used to be something on channel nine. Late at night. I never caught all of it. | hal → listening |  |
| hal_08 | Get the antennas back up and maybe I will. So. Can I count on you? | hal → listening |  |
| hal_09 | Copy. The offer stays on the frequency. Over and out. | hal → no |  |
| hal_10 | Copy that! Three antennas, scattered around the Tundra. You'll know them. Tall, metal, sad-looking. | hal → accept |  |
| hal_11 | Open the box at the bottom, match the wires by colour. Red to red, blue to blue. Even a penguin could do it. | hal → accept |  |
| hal_12 | Not that we have penguins. Report back when all three are humming. Over. | hal → accept |  |
| hal_13 | Back on the frequency, stranger? The antennas are still dead. Want the job? | hal → again |  |
| hal_14 | Nothing yet. Static. Pure, high-quality static. Over. | hal → progress0 |  |
| hal_15 | The antennas won't fix themselves, stranger. I asked them. Twice. | hal → progress0 |  |
| hal_16 | One antenna up! I can hear the wind on a whole new frequency. Two to go. Over. | hal → progress1 |  |
| hal_17 | Two up. There's something between the static now. Can't make it out. One more, stranger. | hal → progress2 |  |
| hal_18 | ...Hurry. Please. Over. | hal → progress2 |  |
| hal_19 | All three! I can hear everything. The whole Tundra, loud and clear. | hal → finale |  |
| hal_20 | Listen. Channel nine. Here it comes... | hal → finale |  |
| hal_24 | ...That's it. That's all it says. Over and over. | hal → finale |  |
| hal_25 | I heard it before. Years ago. Never this clear. | hal → finale |  |
| hal_26 | Who needs to turn what off? ...No. Don't answer that. I have a feeling I really don't want to know. | hal → finale |  |
| hal_27 | I recorded it. Take the tape and get it away from my radio. | hal → finale |  |
| hal_28 | Or, if you'd rather not carry that thing around... take my old flare gun instead. Can't have both. Over. | hal → finale |  |
| hal_29 | Thanks for the antennas, stranger. I mean it. From now on I'm sticking to the weather channel. Over and out. | hal → reward |  |
| hal_30 | Weather report: cold. Tomorrow: colder. Over. | hal → after |  |
| hal_31 | Channel nine's quiet now. I keep it switched off. Mostly. | hal → after |  |
| hal_32 | You still have that tape? Don't play it near me. Over. | hal → after |  |
| hal_33 | The antennas are holding. Good work, stranger. Over. | hal → after |  |
| hal_34 | Good choice. Some things are better left unheard. Thanks for the antennas, stranger. Over and out. | hal → reward_flare |  |

## Lucky — `assets/sfx/voicelines/lucky/`

| ID | Line | Where | Notes |
|---|---|---|---|
| lucky_01 | Step right up, step right up! A new face! A lucky face! | lucky → first |  |
| lucky_02 | Name's Lucky. Lucky by name, lucky by nature - and today, friend, maybe lucky by association! | lucky → first |  |
| lucky_03 | Empty? It's exclusive! Every ride, every stall, every prize - all for you. No queues! | lucky → first |  |
| lucky_04 | And the star of the show: the Wheel of Fortune. Put in a little gold, take out a lot of gold. Sometimes. | lucky → first |  |
| lucky_05 | Mostly sometimes. Want a spin? | lucky → first |  |
| lucky_06 | Welcome back, welcome back! The wheel missed you. I could tell. It squeaked. | lucky → again |  |
| lucky_07 | Ah, my favourite customer! My only customer, but still my favourite! | lucky → again |  |
| lucky_08 | Feeling lucky? Of course you are. Everybody's lucky at Lucky's. | lucky → again |  |
| lucky_09 | Another spin? The wheel's still warm! | lucky → hub |  |
| lucky_10 | The next one's the one. Probably. | lucky → hub |  |
| lucky_11 | Round and round it goes! Where it stops - well, you know. | lucky → hub |  |
| lucky_12 | Easy as candy! You pay, you spin, the wheel decides. | lucky → rules |  |
| lucky_13 | Grey - nothing. Blue - half back. White - your money back. Green - double. Gold - triple. | lucky → rules |  |
| lucky_14 | And the pink one... the JACKPOT. Six times your gold. I've seen it happen! Once. Maybe twice. | lucky → rules |  |
| lucky_15 | The big tent? Ah. That's where the Mascot sleeps. | lucky → tent |  |
| lucky_16 | Biggest plush you've ever seen. Used to wave at the kids. Now it... doesn't really wave anymore. | lucky → tent |  |
| lucky_17 | If you wake it up, it'll want to play. And it plays rough. But they say whoever beats it gets a prize! | lucky → tent |  |
| lucky_18 | I don't go in there. Bad for business. Bad for my teeth. | lucky → tent |  |
| lucky_19 | A WINNER! Look at that! Ladies and gentlemen - well, you - a winner! | lucky → won |  |
| lucky_20 | Ha! See? I told you. Lucky's never lies. Rarely lies. | lucky → won |  |
| lucky_21 | Beginner's luck? Expert's luck! Spin again while it's hot! | lucky → won |  |
| lucky_22 | Ooh! So close! Did you see that? SO close! | lucky → lost |  |
| lucky_23 | Not this time, friend. But the wheel remembers who keeps trying. | lucky → lost |  |
| lucky_24 | Oof. Well. The wheel giveth, and mostly the wheel taketh. | lucky → lost |  |
| lucky_25 | Ah-ah-ah. No gold, no go. Come back with heavier pockets, friend! | lucky → poor |  |
| lucky_26 | Something else I can do for you? | lucky → hub_poor |  |
| lucky_27 | Come back soon! The wheel never sleeps! Unlike the Mascot. | lucky → bye |  |
| lucky_28 | Where did you... these were never printed. | lucky → coupon |  |
| lucky_29 | I mean - of COURSE! The Golden Wheel! For our very special guests! | lucky → coupon |  |
| lucky_30 | Five hundred a spin. And between us? The odds are... generous. Don't tell the Mascot. | lucky → coupon |  |

## narrator (???) — `assets/sfx/voicelines/narrator/`

| ID | Line | Where | Notes |
|---|---|---|---|
| ending_extra_01 | ... | **×3** ending_extra → monologue; ending_main → monologue; ending_secret → monologue | speed 0.08 |
| ending_extra_02 | So now you know. | ending_extra → monologue |  |
| ending_extra_03 | Not everything. But enough to stop pretending you don't. | ending_extra → monologue |  |
| ending_extra_04 | Someone once wanted a world with nothing bad in it. It's a kind wish. Most terrible things begin as kind wishes. | ending_extra → monologue |  |
| ending_extra_05 | Every sad day, every cruel word, every fear... they cut it out, and put it where nobody would have to look. | ending_extra → monologue |  |
| ending_extra_06 | It didn't vanish. Nothing ever does. It only piled up in the dark, and waited. | ending_extra → monologue |  |
| ending_extra_07 | What you fought down here wasn't a monster. It was everything nobody wanted to feel. | ending_extra → monologue |  |
| ending_extra_08 | And you won. Of course you won. It's very tired. | ending_extra → monologue |  |
| ending_extra_09 | But beating it doesn't send it anywhere. There is nowhere left to send it. | ending_extra → monologue |  |
| ending_extra_10 | That's the hard thing about understanding. It doesn't fix anything. It only takes away the excuse. | ending_extra → monologue |  |
| ending_extra_11 | Some people learn the truth and think the work is over. That's usually where it starts. | ending_extra → monologue |  |
| ending_extra_12 | The things we hide from ourselves don't disappear. They grow quiet, and heavy, and patient. | ending_extra → monologue |  |
| ending_extra_13 | You can't throw away the bad parts of a life. You can only learn to carry them. A little at a time. | ending_extra → monologue |  |
| ending_extra_14 | Somewhere up there, a voice is still repeating the same words, hoping someone will listen to the end. | ending_extra → monologue |  |
| ending_extra_15 | A light that went out one night is still waiting for someone to ask why. | ending_extra → monologue |  |
| ending_extra_16 | And a few old words were never read to the one they were written for. | ending_extra → monologue |  |
| ending_extra_17 | Unfinished things are like that. They don't call your name. They just wait by the door. | ending_extra → monologue |  |
| ending_extra_18 | Rest, if you can. The quiet up there will hold. For now. | ending_extra → monologue |  |
| ending_extra_19 | And when you're ready... come back down. It will still be here, waiting to be finished. | ending_extra → monologue |  |
| ending_main_01 | It's quiet now. Listen to it for a moment. | ending_main → monologue |  |
| ending_main_02 | You came a very long way to break something. Most people do. | ending_main → monologue |  |
| ending_main_03 | They believe that if they find the thing that hurts and smash it, the hurting stops. | ending_main → monologue |  |
| ending_main_04 | And for a while, it does. That part is true. | ending_main → monologue |  |
| ending_main_05 | But the heart was never the reason. It was only the place where someone kept the reason. | ending_main → monologue |  |
| ending_main_06 | Everything you cut away has to go somewhere. It doesn't disappear just because you stop looking at it. | ending_main → monologue |  |
| ending_main_07 | Break a lock, and the door is still there. Break the door, and the room is still there. | ending_main → monologue |  |
| ending_main_08 | The one who stood in your way knew that. He had seen this night before. | ending_main → monologue |  |
| ending_main_09 | You didn't ask him why. Nobody ever asks why. Asking is slower than winning. | ending_main → monologue |  |
| ending_main_10 | Don't be ashamed of it. Winning is a fine thing. It just isn't the same as understanding. | ending_main → monologue |  |
| ending_main_11 | Somewhere below, something turns over in its sleep. It doesn't wake. Not yet. | ending_main → monologue |  |
| ending_main_12 | Up there, the grass will grow back. The monsters will be sweet again. For a while. | ending_main → monologue |  |
| ending_main_13 | And someone will wake up by a fence in a quiet village, and feel like they've been there before. | ending_main → monologue |  |
| ending_main_14 | They'll be right. | ending_main → monologue |  |
| ending_main_15 | If you want my advice... and nobody ever does, at the end... | ending_main → monologue |  |
| ending_main_16 | ...next time, before you break something, ask what it was holding. | ending_main → monologue |  |
| ending_main_17 | Sleep now. It's a long way back to the beginning. | ending_main → monologue |  |
| ending_secret_01 | You listened. | ending_secret → monologue |  |
| ending_secret_02 | To a voice on a tape. To a broken light. To a few old words. All of them, to the end. | ending_secret → monologue |  |
| ending_secret_03 | Do you know how rare that is? Most people stop at the part they like. | ending_secret → monologue |  |
| ending_secret_04 | Down here, everything that was cut away was waiting for one thing. Not to win. Not to be destroyed. | ending_secret → monologue |  |
| ending_secret_05 | Just to be looked at, by someone who wouldn't look away. | ending_secret → monologue |  |
| ending_secret_06 | And you didn't. | ending_secret → monologue |  |
| ending_secret_07 | So it isn't hiding anymore. It's coming home. | ending_secret → monologue |  |
| ending_secret_08 | Not all at once. That was always the fear. A little at a time, the way rain comes back after a long summer. | ending_secret → monologue |  |
| ending_secret_09 | The world will have sad days again. Somebody will lose something. Somebody will say the wrong thing at dinner. | ending_secret → monologue |  |
| ending_secret_10 | And somebody else will stay, and listen, and say it's alright. | ending_secret → monologue |  |
| ending_secret_11 | That was the part they forgot, when they built it. You can't have one without the other. | ending_secret → monologue |  |
| ending_secret_12 | A world with nothing bad in it isn't a kind world. It's a photograph of one. | ending_secret → monologue |  |
| ending_secret_13 | The pale place under everything is fading. There is nothing left for it to hold. | ending_secret → monologue |  |
| ending_secret_14 | The one who stood guard can finally rest. He was so tired of being brave. | ending_secret → monologue |  |
| ending_secret_15 | Healing isn't making the dark go away. It's letting it back in, and finding there's room. | ending_secret → monologue |  |
| ending_secret_16 | So keep a little room for it. In the world. In yourself. | ending_secret → monologue |  |
| ending_secret_17 | Thank you, for listening to the end. | ending_secret → monologue |  |
| ending_secret_18 | Now go on. Somebody up there is waking up, and the sky is a little less perfect today. It suits it. | ending_secret → monologue |  |
| ending_secret_19 | Good morning. | ending_secret → monologue |  |

## Oliver — `assets/sfx/voicelines/oliver/`

| ID | Line | Where | Notes |
|---|---|---|---|
| oliver_01 | ... | **×2** oliver → first; oliver → hub |  |
| oliver_02 | Shh. You'll scare them. | oliver → first |  |
| oliver_03 | Oliver. I fish. | oliver → first |  |
| oliver_04 | Many things. Not the one I want. | oliver → first |  |
| oliver_05 | Years ago, something big swam under this ice. Bigger than me. It looked at me through the hole. | oliver → first |  |
| oliver_06 | Then it was gone. | oliver → first |  |
| oliver_07 | So I wait. | oliver → first |  |
| oliver_08 | You can try too, if you like. The first cast is on me. | oliver → first |  |
| oliver_09 | ...Oh. You. | oliver → again |  |
| oliver_10 | Quiet today. Good. | oliver → again |  |
| oliver_11 | Still waiting. Still here. | oliver → again |  |
| oliver_12 | The ice is thick today. The fish like that. | oliver → again |  |
| oliver_13 | Another cast? | oliver → hub |  |
| oliver_14 | The water's patient. Are you? | oliver → hub |  |
| oliver_15 | Long. Pale. Slow. | oliver → big |  |
| oliver_16 | It didn't look hungry. It looked... curious. | oliver → big |  |
| oliver_17 | I've never told anyone that. Nobody asks. | oliver → big |  |
| oliver_18 | Fish. Cold water. The deeper, the better the fish. | oliver → down |  |
| oliver_19 | And at the very bottom, a pearl. I see it shine sometimes. | oliver → down |  |
| oliver_20 | It never stays still. Like it doesn't want to be found. | oliver → down |  |
| oliver_21 | You have to wait for a gap. Most people don't wait. | oliver → down |  |
| oliver_22 | And after a cast, the fish hide for a while. Everybody needs a rest. | oliver → down |  |
| oliver_23 | Not bad. Not the big one. But not bad. | oliver → won |  |
| oliver_24 | Patience. You have some. | oliver → won |  |
| oliver_25 | The ice is kind to you today. | oliver → won |  |
| oliver_26 | Nothing. ...That's fishing. | oliver → lost |  |
| oliver_27 | Empty hook. It happens. Most days it happens. | oliver → lost |  |
| oliver_28 | No coins? Then sit. Watching is free. | oliver → poor |  |
| oliver_29 | Not now. The fish need a rest. So do I. | oliver → resting |  |
| oliver_30 | They're hiding. They saw your last cast. Come back later. | oliver → resting |  |
| oliver_31 | ...Let the water settle first. | oliver → resting |  |
| oliver_32 | Sit, if you want. Watching is free. | oliver → hub_resting |  |
| oliver_33 | ...Mhm. | oliver → bye |  |

## Radio — `assets/sfx/voicelines/radio/`

| ID | Line | Where | Notes |
|---|---|---|---|
| hal_21 | ...need to... turn it off. | hal → finale | horror (black screen), speed 0.5 |
| hal_22 | We need to turn it off. | **×2** hal → finale; wren → tape | horror (black screen), speed 0.5 |
| hal_23 | We need to turn it off. We need to turn it off. We need to | hal → finale | horror (black screen), speed 0.5 |

## Sunny — `assets/sfx/voicelines/sunny/`

| ID | Line | Where | Notes |
|---|---|---|---|
| sunny_01 | Oh! Hi! Don't move. | sunny → first | speed 1.3 |
| sunny_02 | There was a bee on your shoulder. Now it's on my tower. That's fine. Bees are allowed. | sunny → first | speed 1.3 |
| sunny_03 | I'm Sunny! Who are you? Actually, don't tell me yet. I'll guess later. I'm really good at guessing. | sunny → first | speed 1.3 |
| sunny_04 | This is my tower! It's made of flowers. Only flowers. No sticks, no cheating. | sunny → tour | speed 1.3 |
| sunny_05 | The yellow ones go on top. They're the best ones. Yellow is my favourite colour, so they get the best spot. | sunny → tour | speed 1.3 |
| sunny_06 | The pink ones go on top. They're the best ones. Pink is my favourite colour, so they get the best spot. | sunny → tour | speed 1.3 |
| sunny_07 | The blue ones go on top. They're the best ones. Blue is my favourite colour, so they get the best spot. | sunny → tour | speed 1.3 |
| sunny_08 | Rocks would be easier. But rocks are boring, and they don't smell like anything. | sunny → tour | speed 1.3 |
| sunny_09 | To see the end of the world. | sunny → why | speed 1.3 |
| sunny_10 | Everybody says the fields go on forever. But nothing goes on forever! Except Mayor Bramble when he talks. | sunny → why | speed 1.3 |
| sunny_11 | So when it's tall enough, I climb up, I look, and then I know. Easy. | sunny → why | speed 1.3 |
| sunny_12 | You can help by not stepping on the flowers. Any of them. Ever. | sunny → help | speed 1.3 |
| sunny_13 | ...You're stepping on one right now. | sunny → help | speed 1.3 |
| sunny_14 | It's okay. It was a weed. Probably. | sunny → help | speed 1.3 |
| sunny_15 | It's not wobbly, it's dancing. | sunny → wobbly | speed 1.3 |
| sunny_16 | Towers dance. Everybody knows that. You just have to look really, really closely. | sunny → wobbly | speed 1.3 |
| sunny_17 | Oh! You two haven't met. This is Petalbert. | sunny → name | speed 1.3 |
| sunny_18 | Oh! You two haven't met. This is Sir Stalk. | sunny → name | speed 1.3 |
| sunny_19 | Oh! You two haven't met. This is Big Daisy. | sunny → name | speed 1.3 |
| sunny_20 | Petalbert, this is... the person. Say hi. | sunny → name | speed 1.3 |
| sunny_21 | Sir Stalk, this is... the person. Say hi. | sunny → name | speed 1.3 |
| sunny_22 | Big Daisy, this is... the person. Say hi. | sunny → name | speed 1.3 |
| sunny_23 | He likes you! I can tell. He leans when he likes people. | sunny → name_hi | speed 1.3 |
| sunny_24 | A pile is when you don't care where things go. | sunny → name_pile | speed 1.3 |
| sunny_25 | I care where every single one goes. So it's a tower. | sunny → name_pile | speed 1.3 |
| sunny_26 | I counted them this morning. Four hundred and twelve flowers! | sunny → count | speed 1.3 |
| sunny_27 | I counted them this morning. Two hundred and thirty flowers! | sunny → count | speed 1.3 |
| sunny_28 | I counted them this morning. One hundred and fifty-seven flowers! | sunny → count | speed 1.3 |
| sunny_29 | Then a bee took one. So, four hundred and eleven. | sunny → count | speed 1.3 |
| sunny_30 | Then a bee took one. So, two hundred and twenty-nine. | sunny → count | speed 1.3 |
| sunny_31 | Then a bee took one. So, one hundred and fifty-six. | sunny → count | speed 1.3 |
| sunny_32 | I'm not counting the bee. The bee isn't a flower. | sunny → count | speed 1.3 |
| sunny_33 | Ooh, look at that cloud! It looks like a boot. A sad boot. | sunny → count | speed 1.3 |
| sunny_34 | Poor boot. Nobody's wearing it. | sunny → cloud_sad | speed 1.3 |
| sunny_35 | ...A fish wearing a boot? | sunny → cloud_fish | speed 1.3 |
| sunny_36 | That's even better. You're weird. I like weird. | sunny → cloud_fish | speed 1.3 |
| sunny_37 | Wait. Where did you come from? Not the village. I know everybody in the village. | sunny → where | speed 1.3 |
| sunny_38 | Well. I know Dot. Dot's loud. You can hear her from here if the wind is right. | sunny → where | speed 1.3 |
| sunny_39 | That's okay! I don't know where bees come from either, and they're doing fine. | sunny → where_dunno | speed 1.3 |
| sunny_40 | Hmm. Then I would know you. | sunny → where_village | speed 1.3 |
| sunny_41 | Unless you're a spy! A tower spy. ...No, you're too slow to be a spy. | sunny → where_village | speed 1.3 |
| sunny_42 | Okay, okay, okay. If you want to be a tower helper, you have to pass the test. | sunny → test | speed 1.3 |
| sunny_43 | Everybody has to. It's the rule. I made it up just now, but it's still the rule. | sunny → test | speed 1.3 |
| sunny_44 | Question one! What's my favourite colour? | sunny → test | speed 1.3 |
| sunny_45 | Correct! Question two! What's his name? | sunny → q2 | speed 1.3 |
| sunny_46 | Yes! Look, he's blushing. Last one! How many flowers are in the tower? | sunny → q3 | speed 1.3 |
| sunny_47 | ...You were listening? | sunny → passed | speed 1.3 |
| sunny_48 | Nobody listens! Mayor Bramble falls asleep when I talk. Dot pretends. | sunny → passed | speed 1.3 |
| sunny_49 | You're officially a tower helper. Helpers get a present. | sunny → passed | speed 1.3 |
| sunny_50 | Here! I drew all of the fields. Every path, every tree, every flower I haven't picked yet. | sunny → passed_map | speed 1.3 |
| sunny_51 | It's a bit sticky. Don't ask. | sunny → passed_map | speed 1.3 |
| sunny_52 | I was going to give you my map. But you already have one! | sunny → passed_gold | speed 1.3 |
| sunny_53 | Is it the Wanderer's? His are all brown. Mine has colours. | sunny → passed_gold | speed 1.3 |
| sunny_54 | Here, take these instead. I found them in the grass. Shiny things are bad for towers anyway. | sunny → passed_gold | speed 1.3 |
| sunny_55 | Nope! | sunny → wrong | speed 1.3 |
| sunny_56 | Oh- BUTTERFLY. | sunny → wrong | speed 1.3 |
| sunny_57 | Sorry, the test is over, I have to go look at that. Come back later! You can try again. | sunny → wrong | speed 1.3 |
| sunny_58 | You're back! Everybody comes back for the tower. | sunny → again | speed 1.3 |
| sunny_59 | Hi again! Did you come back for the test? Say yes. | sunny → again | speed 1.3 |
| sunny_60 | Oh, it's you! Careful, the tower's in a mood today. | sunny → again | speed 1.3 |
| sunny_61 | Bye! Don't step on anything! | sunny → bye_short | speed 1.3 |
| sunny_62 | Helper! Petalbert missed you. ...I'm guessing. He doesn't really say. | sunny → again_helper | speed 1.3 |
| sunny_63 | Helper! Sir Stalk missed you. ...I'm guessing. He doesn't really say. | sunny → again_helper | speed 1.3 |
| sunny_64 | Helper! Big Daisy missed you. ...I'm guessing. He doesn't really say. | sunny → again_helper | speed 1.3 |
| sunny_65 | I'm almost tall enough. Almost. Maybe twenty more flowers. Maybe a thousand. | sunny → again_helper | speed 1.3 |
| sunny_66 | A bee stung me today. I forgave it. Bees have a hard job. | sunny → again_helper | speed 1.3 |
| sunny_67 | I can almost see the candy forest from the top! It's pink. Everything over there is pink. | sunny → again_helper | speed 1.3 |
| sunny_68 | What else? Ask me anything! Except maths. | sunny → hub | speed 1.3 |
| sunny_69 | Anything else? Quick, before I forget what we're talking about! | sunny → hub_more | speed 1.3 |
| sunny_70 | Not yet. But I saw a mountain! A really big one. Bigger than the tower. | sunny → end_world | speed 1.3 |
| sunny_71 | So the end of the world is behind the mountain. Or it IS the mountain. I'll find out. | sunny → end_world | speed 1.3 |
| sunny_72 | Good! It fell over twice today. That's a new record. The good kind of record. | sunny → how | speed 1.3 |
| sunny_73 | Bye, helper! | sunny → bye | speed 1.3 |

## Wanderer — `assets/sfx/voicelines/wanderer/`

| ID | Line | Where | Notes |
|---|---|---|---|
| wanderer_01 | ...Oh. A traveller. Sit, if you like. The fire doesn't mind. | wanderer → first |  |
| wanderer_02 | I draw maps. Roads, rivers, the places in between. Mostly the places in between. | wanderer → first |  |
| wanderer_03 | To those who ask kindly. And pay. Kindness doesn't buy paper. | wanderer → first |  |
| wanderer_04 | The Village is cheap. Small, round, easy to draw. | wanderer → first |  |
| wanderer_05 | The Rainbow Fields took me a whole season. Colours are expensive. So is the patience to sit still while flowers look at you. | wanderer → first |  |
| wanderer_06 | The fire's still warm. So am I. Mostly. | wanderer → again |  |
| wanderer_07 | Every road leads somewhere. That's the problem with roads. | wanderer → again |  |
| wanderer_08 | Looking for a map? I have a few. Fewer than I'd like. | wanderer → again |  |
| wanderer_09 | I tried to draw what's past the sweet forest once. The ink kept running off the page. | wanderer → again |  |
| wanderer_10 | The Village. Every fence, every chimney. Even the well the mayor keeps polishing. | wanderer → sold_village |  |
| wanderer_11 | The Rainbow Fields. Careful with it. Some of the colours are still wet. | wanderer → sold_rainbow |  |
| wanderer_12 | If the flowers look at you funny out there... it's not the map's fault. | wanderer → sold_rainbow |  |
| wanderer_13 | Your purse is lighter than this map, traveller. Come back when it isn't. | wanderer → poor |  |
| wanderer_14 | Why... | wanderer → why |  |
| wanderer_15 | Because things change when nobody's looking. A map is a way of looking. All the time. | wanderer → why |  |
| wanderer_16 | And because some mornings a road is gone. If it's on paper, at least it existed. | wanderer → why |  |
| wanderer_17 | Anything else, traveller? | wanderer → again_menu |  |

## whisper (...) — `assets/sfx/voicelines/whisper/`

| ID | Line | Where | Notes |
|---|---|---|---|
| ring_voice_01 | ...closer... | ring_voice → whisper | horror (black screen), speed 0.45 |
| ring_voice_02 | Only the innocent may see what is true. | ring_voice → whisper | horror (black screen), speed 0.45 |
| ring_voice_03 | Find the stone that has no colour. | ring_voice → whisper | horror (black screen), speed 0.45 |
| ring_voice_04 | Come to it with nothing to hurt with. | ring_voice → whisper | horror (black screen), speed 0.45 |
| ring_voice_05 | Stand. Be still. | ring_voice → whisper | horror (black screen), speed 0.45 |
| ring_voice_06 | Wait until the light forgets you. | ring_voice → whisper | horror (black screen), speed 0.45 |

## Wren — `assets/sfx/voicelines/wren/`

| ID | Line | Where | Notes |
|---|---|---|---|
| wren_01 | You! The one who looks at things! | wren → first |  |
| wren_02 | Hey - you. You look like someone who looks at things. I'm Wren. | wren → first |  |
| wren_03 | I followed the way down. Somebody had to. Look at this place - a garden underground, with no sun. It shouldn't exist. | wren → first |  |
| wren_04 | I need your eyes. There are three places down here that bother me. | wren → first |  |
| wren_05 | Rows of stones with flowers. A playground swallowed by roots. And a lab someone left in a hurry. | wren → first |  |
| wren_06 | Go and look at them. Properly. Then tell me what you saw. | wren → first |  |
| wren_07 | Stones, playground, lab. Look at them properly - don't just walk past. | wren → waiting |  |
| wren_08 | Nothing yet? Take your time. I'll be here. Writing. | wren → waiting |  |
| wren_09 | You saw one? Don't tell me yet. I want to hear all three together. | wren → progress |  |
| wren_10 | Two. One more. I can see it in your face - it's not nothing, is it? | wren → progress |  |
| wren_11 | Well? What did you see? | wren → report |  |
| wren_12 | ... | **×2** wren → report; wren → tape |  |
| wren_13 | None of it grew here. It was put here. | wren → report |  |
| wren_14 | Someone takes things from up there and hides them down here. On purpose. | wren → report |  |
| wren_15 | I don't know who. I don't know why. But it's not an accident. | wren → report |  |
| wren_16 | Here - for your trouble. I found it lying around. Everything down here is lying around. | wren → report |  |
| wren_17 | I'll stay here and write it all down. Every detail. | wren → reward |  |
| wren_18 | But paper isn't enough. Paper loses its words down here. I need something more. | wren → reward |  |
| wren_19 | Still writing. Still not enough. | wren → camp |  |
| wren_20 | Put here. Hidden. On purpose. I keep reading it and it doesn't get better. | wren → camp |  |
| wren_21 | You again! Good. Have you seen anything else? | wren → camp |  |
| wren_22 | A voice. A recording. A letter. Anything from the people who were here before. | wren → need |  |
| wren_23 | Paper loses its words down here. But a voice... a voice might survive. | wren → need |  |
| wren_24 | Please do. | wren → keep_eye |  |
| wren_25 | A tape? Give it here. Gently! | wren → tape |  |
| wren_26 | 'Turn it off.' | wren → tape |  |
| wren_27 | Turn what off? Something that... takes things? And hides them down here? | wren → tape |  |
| wren_28 | So someone built it. Someone made the thing that does all this. | wren → tape |  |
| wren_29 | And they wanted to switch it off. But they didn't. Or they couldn't. | wren → tape |  |
| wren_30 | Why not? | wren → tape |  |
| wren_31 | ...That's it. I'm done waiting for answers to come to me. | wren → tape |  |
| wren_32 | I'm going to look for them myself. Whoever 'we' is. Wherever they went. | wren → tape |  |
| wren_33 | Don't wait for me here. I'll find you. Or you'll find me. | wren → tape |  |
| wren_argument_01 | -no, Milo, listen to me. Listen! The tape. 'We need to turn it off.' Someone built all of this. Someone can stop it. | wren_argument → argue |  |
| wren_argument_03 | You don't know that. | wren_argument → argue |  |
| wren_argument_05 | Then tell me! For once, just tell me something true. | wren_argument → argue |  |
| wren_argument_07 | It's the only way up. Everything leads there. The stones, the playground, the voice on the tape - it all points up. | wren_argument → argue |  |
| wren_argument_11 | Starts again? What starts again? | wren_argument → argue |  |
| wren_argument_13 | That doesn't make any sense. | wren_argument → argue |  |
| wren_argument_15 | So what - we just sit here? Let the monsters get stranger every year? Let someone keep hiding things down here? | wren_argument → argue |  |
| wren_argument_17 | You didn't say anything! You never do. You just stand there, one step ahead of everyone, smiling. | wren_argument → argue |  |
| wren_argument_18 | If the Core isn't the answer, then what is? | wren_argument → argue |  |
| wren_argument_20 | Then I'll find it. | wren_argument → argue |  |
| wren_argument_22 | No. I'm done with riddles. I'll find out myself. Up there, down there, wherever it is. | wren_argument → argue |  |
| wren_argument_23 | Goodbye, Milo. | wren_argument → argue |  |
| wren_moved_01 | Not now. Milo and I are... talking. | wren_moved → wait |  |
| wren_village_01 | Wait - you came from the Candy side? Through the forest? | wren_village → first |  |
| wren_village_02 | Did the monsters there look... right to you? | wren_village → first |  |
| wren_village_03 | Normal. Like monsters should look. I've been drawing them for years. They're changing. Every year a little stranger. | wren_village → first |  |
| wren_village_04 | More teeth. More eyes. Colours that don't belong to them. Nobody else sees it. Or nobody wants to. | wren_village → first |  |
| wren_village_05 | I'm Wren. If you go further - down, or up north - look at things. Really look. | wren_village → first |  |
| wren_village_06 | And then come tell me. Wherever I am. | wren_village → first |  |
| wren_village_07 | Before you go - take this. I found it somewhere it shouldn't have been. | **×2** wren_village → first; wren_village → gift |  |
| wren_village_08 | No idea. It's warm. And it's not the only one - I've seen the same mark on old stones further on. | **×2** wren_village → first; wren_village → gift |  |
| wren_village_09 | If you find more, they're yours. Just tell me what they do. | **×2** wren_village → first; wren_village → gift |  |
| wren_village_10 | Still drawing. The new ones have too many teeth. | wren_village → again |  |
| wren_village_11 | North or down - either way, look carefully. Then tell me. | wren_village → again |  |
| wren_village_12 | Did you see anything strange? Everything's strange. That's the problem. | wren_village → again |  |
| wren_village_13 | Oh - it's you. Wait, I almost forgot. | wren_village → gift |  |
