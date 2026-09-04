import json

class SaveManager:
    def __init__(self, player, inventory, map):
        self.player = player
        self.inventory = inventory
        self.map = map
        
    def save_game(self, nr):
        if nr in (1,2,3):
            save_data = {
                        "player": {
                            "x": self.player.x,
                            "y": self.player.y,
                            "money": self.player.money,
                            "playtime" : self.player.play_time
                        },
                        "inventory": {
                            "active_items": [item.name for item in self.inventory.active_items.values() if item is not None],
                            "items": [item.name for item in self.inventory.items]
                        },
                        "map": {
                            "layout" : self.map.layout
                        }
                    }
            with open(f"game/text/save{nr}.json", "w") as f:
                json.dump(save_data, f, indent=4)

    def load_game(self, nr, game):
        game.inventory.items = []
        if nr in (1,2,3):
            try:
                with open(f"game/text/save{nr}.json", "r") as f:
                    save_data = json.load(f)
                    game.player.x = save_data["player"]["x"]
                    game.player.y = save_data["player"]["y"]
                    game.player.money = save_data["player"]["money"]
                    game.player.play_time = save_data["player"]["playtime"]
                    game.map.layout = save_data["map"]["layout"]
                    for item_name in save_data["inventory"]["active_items"]:
                        item = game.inventory.ItemDB.get_item(item_name)
                        if item is not None:
                            game.inventory.active_items[item.type] = item
                    for item_name in save_data["inventory"]["items"]:
                        item = game.inventory.ItemDB.get_item(item_name)
                        if item is not None:
                            game.inventory.items.append(item)
            except (FileNotFoundError, json.JSONDecodeError):
                game.player.x = 128
                game.player.y = 128
                game.player.money = 0
                game.player.play_time = 0
                game.map.layout = ["1122111222","1111122112","2221121112","1211111122","2112221112","2111111112","2111111112","2111111112","2111111132","2222222222"]
                game.inventory.active_items["weapon"] = game.inventory.ItemDB.get_item("Simple Blaster")
                game.inventory.items = [game.inventory.ItemDB.get_item("Simple Pistol")]

    def get_save_info(self,nr):
        if nr in (1,2,3):
            try:
                with open(f"game/text/save{nr}.json", "r") as f:
                    save_data = json.load(f)
                    time = int(save_data['player']['playtime'])
                    return [f"Save {nr}","Time Played:", f"{time//3600}:{(time//60)%60:02d}",f"Money: {save_data['player']['money']}"]
            except (FileNotFoundError, json.JSONDecodeError):
                    return [f"Save {nr}"," ",f"EMPTY"]
                