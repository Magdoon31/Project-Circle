class SettingsManager:
    def __init__(self, music_manager, sfx_manager):
        self.music = music_manager
        self.sfx = sfx_manager

    def settings_data_save(self):
        with open("game/text/settings.txt", "w+") as settings:
                    settings.write(f"music_volume\n{self.music.music_volume}\n")
                    settings.write(f"sfx_volume\n{self.sfx.sfx_volume}\n")

    def settings_data_render(self):
        try:
            with open("game/text/settings.txt", "r+") as settings:
                settings_data = settings.read().splitlines()
            try:
                music = float(settings_data[1])
                sfx = float(settings_data[3])
            except IndexError or ValueError:
                with open("game/text/settings.txt", "w+") as settings:
                    settings.write("music_volume\n1.0\n")
                    settings.write("sfx_volume\n1.0\n")
                    music = 1.0
                    sfx = 1.0
            if 0 > music > 1.0 or 0 > sfx > 1.0:
                with open("game/text/settings.txt", "w+") as settings:
                    settings.write("music_volume\n1.0\n")
                    settings.write("sfx_volume\n1.0\n")
        except FileNotFoundError:
            with open("game/text/settings.txt", "w+") as settings:
                settings.write("music_volume\n1.0\n")
                settings.write("sfx_volume\n1.0\n")
        with open("game/text/settings.txt", "r+") as settings:
            settings_data = settings.read().splitlines()
        self.music.music_volume = float(settings_data[1])
        self.sfx.sfx_volume = float(settings_data[3])