"""Settings - used to store and ref setting."""
import json
import os
import globalvars
"""
This class is used to gather and store settings so that
the application can be adapted to an env without having to
edit src code. There are 3 main settings.

user_settings - Sets renderers and custom settings
path_settings - Gets or sets path settings
display_settings - settings for the GUI

Try to keep path as procedual as posible but allow overrides
"""


class Settings():
    """Settings - used to store and ref setting."""

    def __init__(self):
        """INIT."""
        self.folderpath = globalvars.APP_ROOT
        print "Init settings object"
        # Sets renderers and custom settings
        self.user_settings = {}
        self.init_user_settings()

        # Dict of settings used to find locations
        self.path_settings = {}
        self.init_path_settings()

        # Display settings
        self.disp_settings = {}
        self.init_disp_settings()

    """
    Init setting from a json file.
    """
    def init_user_settings(self):
        """Set up the user settings."""
        try:
            p = os.path.join(self.folderpath,"settings", "user.json")
            with open(p, 'r') as f:
                self.user_settings = json.load(f)

            # Check for env variables
            for key, value in self.user_settings.iteritems():
                if "$" in value:
                    value = os.environ.get(str(value).replace("$", ""))
                    self.user_settings[key] = value
            # print self.user_settings
        except:
            print "Unable to import settings! - Error 001"

    def init_path_settings(self):
        """Set up the path settings."""
        try:
            p = os.path.join(self.folderpath, "settings", "path.json")
            with open(p, 'r') as f:
                self.path_settings = json.load(f)

            if 'current_dir' not in self.path_settings:
                current_dir = os.path.dirname(os.path.dirname(__file__))
                current_dir = current_dir.replace("/lib/", "/")

                self.path_settings['current_dir'] = current_dir

            for key, value in self.path_settings.iteritems():
                if "$" in value:
                    value = os.environ.get(str(value).replace("$", ""))
                    self.path_settings[key] = value
            # print self.path_settings
        except:
            print "Unable to import settings! - Error 002"

    def init_disp_settings(self):
        """Set up the disp settings."""
        try:
            p = os.path.join(self.folderpath, "settings", "display.json")
            with open(p, 'r') as f:
                self.display_settings = json.load(f)

            for key, value in self.display_settings.iteritems():
                if "$" in value:
                    value = os.environ.get(str(value).replace("$", ""))
                    self.display_settings[key] = value
            print self.display_settings

        except:
            print "Unable to import settings! - Error 003"
