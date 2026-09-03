class Achievements:
    def __init__(self):
        self.achievements = {"First Blood": {"description": "Defeat the first enemy",
                                                "completed": False,
                                                "image": "assets/achievements/first_blood.png"},
                                                
                            "Monster Slayer": {"description": "Defeat 10 monsters",
                                                "completed": True,
                                                "image": "assets/achievements/monster_slayer.png"},

                            "100 Bucks": {"description": "Earn 100$",
                                                "completed": False,
                                                "image": "assets/achievements/100_bucks.png"},
                            "Treasure Hunter": {"description": "Find 5 hidden treasures",
                                                "completed": False,
                                                "image": "assets/achievements/treasure_hunter.png"},
                            "Master of Combat": {"description": "Defeat 50 enemies in a single combat",
                                                "completed": False,
                                                "image": "assets/achievements/master_of_combat.png"},
                            "Legendary Collector": {"description": "Collect 10 unique items",
                                                "completed": False,
                                                "image": "assets/achievements/legendary_collector.png"},
                            "Unbeatable Player": {"description": "Defeat 100 enemies in a single game",
                                                "completed": False,
                                                "image": "assets/achievements/unbeatable_player.png"},
                            "Boss Slayer": {"description": "Defeat the final boss",
                                                "completed": False,
                                                "image": "assets/achievements/boss_slayer.png"},
                            "Speed Runner": {"description": "Complete the game in under 30 minutes",
                                                "completed": False,
                                                "image": "assets/achievements/speed_runner.png"},
                            }
    def complete_achievement(self, name):
        if name in self.achievements:
            self.achievements[name]["completed"] = True