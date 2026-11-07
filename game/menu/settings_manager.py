DEFAULT_SETTINGS = {"music_volume": 1.0, "sfx_volume": 1.0}


class SettingsManager:
    def __init__(self, music_manager, sfx_manager):
        self.music = music_manager
        self.sfx = sfx_manager

    def settings_data_save(self):
        with open("game/text/settings.txt", "w") as settings:
            settings.write(f"music_volume\n{self.music.music_volume}\n")
            settings.write(f"sfx_volume\n{self.sfx.sfx_volume}\n")

    def settings_data_render(self):
        # reads settings.txt; anything missing, broken or out of 0-1 range falls back to the default
        music, sfx = DEFAULT_SETTINGS["music_volume"], DEFAULT_SETTINGS["sfx_volume"]
        try:
            with open("game/text/settings.txt", "r") as settings:
                settings_data = settings.read().splitlines()
            music = float(settings_data[1])
            sfx = float(settings_data[3])
            if not (0.0 <= music <= 1.0) or not (0.0 <= sfx <= 1.0):
                raise ValueError
        except (FileNotFoundError, IndexError, ValueError):
            music, sfx = DEFAULT_SETTINGS["music_volume"], DEFAULT_SETTINGS["sfx_volume"]

        self.music.music_volume = music
        self.sfx.sfx_volume = sfx
        self.settings_data_save()
