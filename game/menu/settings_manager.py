# SETTINGS MANAGER (11.11): the bridge between the settings (options.py) and the game - it loads and saves them
# and passes a changed volume on to the music and the sounds (master x music / sounds).

from game.menu import options as OPT


class SettingsManager:
    def __init__(self, music_manager, sfx_manager):
        self.music = music_manager
        self.sfx = sfx_manager

    def settings_data_save(self):
        OPT.save()

    def settings_data_render(self):
        """Loads the settings (game/text/settings.json; the old settings.txt once) and applies the volumes."""
        OPT.load()
        self.apply_volumes()
        OPT.save()

    def apply(self, option):
        """A setting was changed on the Settings screen."""
        if option.endswith("_volume"):
            self.apply_volumes()
        OPT.save()

    def apply_volumes(self):
        self.music.music_volume = OPT.volume("music")
        self.sfx.sfx_volume = OPT.volume("sfx")
        self.music.update_volume()
        self.sfx.update_volume()
