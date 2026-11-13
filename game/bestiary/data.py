# THE BESTIARY'S ENTRIES (13.11) - BESTIARY.md in the project. Every enemy you can meet, by place, and the bosses.
#   id = the enemy's name in EnemyDB (its numbers and drops come from there), "mascot" = the song fight's Mascot
#   (not an EnemyDB enemy). A picture of its own: assets/img/bestiary/<id>.png (else a drawn medallion).
# What an entry shows grows with the kills on this save: STAGES.

STAGES = {"name": 1, "lore": 5, "drops": 15}      # kills needed: name + picture / description + numbers / drops
BOSS_STAGES = {"name": 1, "lore": 1, "drops": 1}  # a boss: all of it at once (Milo and the Void fall only once)

PLACES = [   # (key, shown as, its colour)
    ("village", "Village", (150, 210, 120)),
    ("rainbow_fields", "Rainbow Fields", (240, 150, 210)),
    ("sugarwood_grove", "Sugarwood Grove", (250, 170, 190)),
    ("toy_factory", "Toy Factory", (230, 160, 90)),
    ("silverpine_tundra", "Silverpine Tundra", (160, 210, 250)),
    ("underground_garden", "Underground Garden", (130, 200, 150)),
    ("the_core", "The Core", (250, 140, 90)),
    ("the_void", "The Void", (180, 140, 250)),
    ("bosses", "Bosses", (250, 210, 120)),
]
PLACE_COLOUR = {key: colour for key, _, colour in PLACES}

ENTRIES = [
    ("slime_small", "Small Slime", "village", "A hop, a bounce, a squish. The first thing every newcomer learns to shoot."),
    ("slime_big", "Big Slime", "village", "Too much slime in one place. Pop it and it falls apart into smaller ones."),
    ("shooter", "Shooter", "village", "Keeps its distance and takes potshots. Nobody remembers where it learned to aim."),
    ("rainbow_slime", "Rainbow Slime", "rainbow_fields",
     "A slime that swallowed a rainbow. When it bursts, the colours fly out in a ring."),
    ("flower_spitter", "Flower Spitter", "rainbow_fields",
     "Spits seeds that split in the air and drift after you. Likes to stay out of reach."),
    ("rainbow_guard", "Rainbow Guard", "rainbow_fields",
     "Stands between the fields and the road. Answers every question with a shotgun."),
    ("gum_goblin", "Gum Goblin", "sugarwood_grove", "Chews, aims, spits. Whatever it hits stays stuck for a moment."),
    ("candy_shroom", "Candy Shroom", "sugarwood_grove", "Spins on the spot and sprays sweet, poisonous spores everywhere."),
    ("toffee_runner", "Toffee Runner", "sugarwood_grove", "Never runs in a straight line. Never stops running, either."),
    ("sugar_caster", "Sugar Caster", "sugarwood_grove",
     "Throws sugar bombs from a safe distance. Sometimes it carries something precious."),
    ("shroom_guard", "Shroom Guard", "sugarwood_grove",
     "The Shroom Mother's bodyguard. While one of them stands, she can't be hurt."),
    ("toy_soldier", "Toy Soldier", "toy_factory", "Wound up once, marching ever since. Its key never stops turning."),
    ("portable_factory", "Portable Factory", "toy_factory", "A factory on legs. Builds more toys while it shoots at you."),
    ("robo-tesla", "Robo-Tesla", "toy_factory", "Crackles with stray current. Its waves leave you weaker."),
    ("robo-bomber", "Robo-Bomber", "toy_factory", "Lobs burning bombs over everything. Loves the sound of explosions."),
    ("scrap_beetle", "Scrap Beetle", "toy_factory", "Made from leftovers. Leaves mines wherever it crawls."),
    ("line_soldier", "Line Soldier", "toy_factory", "Fresh off the Assembly Line. Still smells of paint."),
    ("line_beetle", "Line Beetle", "toy_factory", "A half-finished beetle. It doesn't know it isn't done."),
    ("belt_turret", "Belt Turret", "toy_factory", "Rides the conveyor belt and fires down the line."),
    ("bomb_crate", "Bomb Crate", "toy_factory", "Fragile. Do not shake. Goes off in a ring of bullets."),
    ("frost_wolf", "Frost Wolf", "silverpine_tundra", "Hunts in the snow. No tricks, just teeth and speed."),
    ("ice_shooter", "Ice Shooter", "silverpine_tundra", "Its icy bolts slow you down. Patient, cold, always a step back."),
    ("frozen_orb", "Frozen Orb", "silverpine_tundra", "A pulsing ball of ice. Its bullets bounce off the walls."),
    ("tundra_watcher", "Tundra Watcher", "silverpine_tundra",
     "Watches the snow for anything that moves. Answers with icicles."),
    ("pixie", "Pixie", "underground_garden", "Blinks from place to place and fires a stream of dizzying sparks."),
    ("rainbow_pixie", "Rainbow Pixie", "underground_garden", "Harmless-looking until it bursts. Then there are more of them."),
    ("poison_skeleton", "Poison Skeleton", "underground_garden",
     "Bones held together by poison. Keeps its distance and keeps shooting."),
    ("inferno_flower", "Inferno Flower", "underground_garden", "A flower that grew where nothing should. Its seeds burn."),
    ("frost_flower", "Frost Flower", "underground_garden",
     "A flower that grew where nothing should. Its seeds freeze and weaken."),
    ("toxic_flower", "Toxic Flower", "underground_garden",
     "A flower that grew where nothing should. Its seeds poison and melt armour."),
    ("firefly_queen", "Firefly Queen", "underground_garden", "Glows, then dashes. Catch her mid-dash if you're feeling lucky."),
    ("skeleton", "Skeleton", "the_core", "Walks at you. That's all it does. It's enough."),
    ("mecha-skeleton", "Mecha-Skeleton", "the_core",
     "A skeleton someone upgraded: binding mines, burning shots, and friends."),
    ("liche", "Liche", "the_core", "Old and patient. Everything it casts makes the world spin."),
    ("guard", "Guard", "the_core", "Guards the Core. Very tough, very slow, very sure it's doing the right thing."),
    ("fly", "Fly", "the_core", "Buzzes at you and bursts into poison when swatted."),
    ("generator", "Generator", "the_core", "Keeps the Core running. Builds walls of glue to keep you out."),
    ("voidling", "Voidling", "the_void", "A piece of the Void that learned to walk. More of them come out of it."),
    ("red_crystal", "Red Crystal", "the_void", "Burns everything it looks at."),
    ("purple_crystal", "Purple Crystal", "the_void", "Turns your world upside down, then breaks into smaller pieces."),
    ("blue_crystal", "Blue Crystal", "the_void", "Cold walls and waves that won't let you think straight."),
    ("void_soldier", "Void Soldier", "the_void", "A Toy Soldier the Void remembers wrong. Bigger. Angrier."),
    ("void_beetle", "Void Beetle", "the_void", "The Void's own Scrap Beetle. Its mines are darker."),
    ("slime_king", "Slime King", "bosses", "The biggest slime there is. Hops at you, throws slime and calls its children."),
    ("prism", "Prism", "bosses", "A hanging crystal that splits the light into bullets."),
    ("shroom_mother", "Shroom Mother", "bosses",
     "Leaps out of sight and lands in a cloud of spores. Her guards keep her safe."),
    ("frost_golem", "Frost Golem", "bosses", "Raises walls of ice, cracks the ground and calls the snowstorm."),
    ("assembly_line", "Assembly Line", "bosses", "A factory that defends itself. Break its machines to reach its core."),
    ("night_bloom", "Night Bloom", "bosses",
     "Blooms in the dark and hides among its copies. Only the real one casts a shadow."),
    ("mascot", "Mascot", "bosses", "Sings. You dodge. Somebody is grading you."),
    ("milo", "Milo", "bosses", "He kept everyone safe. Every beat of the heart."),
    ("void_boss", "???", "bosses", "Everything the system cut away, stuck together. Its name never stays the same."),
]
ENTRY = {e[0]: e for e in ENTRIES}
BOSSES = {e[0] for e in ENTRIES if e[2] == "bosses"}


def stages_for(entry_id):
    return BOSS_STAGES if entry_id in BOSSES else STAGES
