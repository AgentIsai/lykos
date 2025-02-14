import argparse
import datetime
import time

import botconfig  # type: ignore

# Enforce a strict import ordering to ensure things are properly defined when they need to be

# Files with NO OTHER DEPENDENCIES on src
# This "bootstraps" the bot in preparation for importing the bulk of the code. Some imports
# change behavior based on whether or not we're in debug mode, so that must be established before
# we continue on to import other files
import src.settings as var
from src.logger import stream, stream_handler, debuglog, errlog, plog
from src import debug, events, lineparse, match

# Handle launch parameters

# Argument --debug means start in debug mode
#          --verbose means to print a lot of stuff (when not in debug mode)
#          --normal means to override the above and use nothing
# Settings can be defined in the config, but launch arguments override it

debug_mode = False
verbose = False
normal = False
lagcheck = 0

# Carry over settings from botconfig into settings.py

for setting, value in botconfig.__dict__.items():
    if not setting.isupper():
        continue # Not a setting
    if setting == "DEBUG_MODE":
        debug_mode = value
    if setting == "VERBOSE_MODE":
        verbose = value
    if setting == "NORMAL_MODE":
        normal = value
    if setting == "NIGHT_IDLE_PENALTIES":
        # backwards compat
        setting = "NIGHT_IDLE_PENALTY"
        value = var.IDLE_PENALTY if value else 0
    if setting not in var.__dict__.keys():
        continue # Don't carry over config-only settings

    # If we got that far, it's valid
    setattr(var, setting, value)

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--normal', action='store_true')
parser.add_argument('--lagcheck', action='store', nargs='?', const=15, default=lagcheck, type=int)

args = parser.parse_args()

if args.debug:
    debug_mode = True
if args.verbose:
    verbose = True
if args.normal:
    normal = True
if args.lagcheck > 0:
    lagcheck = args.lagcheck

botconfig.DEBUG_MODE = debug_mode if not normal else False
botconfig.VERBOSE_MODE = verbose if not normal else False

# Files with dependencies only on things imported in previous lines, in order
# The top line must only depend on things imported above in our "no dependencies" block
# All botconfig and settings are fully established at this point and are safe to use

from src import messages, cats
from src import context, functions, utilities
from src import db
from src import users
from src import channels, containers
from src import dispatcher
from src import decorators
from src import hooks, status, warnings
from src import pregame
from src import votes
from src import wolfgame
from src import handler

# Import the user-defined game modes
# These are not required, so failing to import it doesn't matter
# The file then imports our game modes
# Fall back to importing our game modes if theirs fail
# Do the same with roles

try:
    import roles as custom_roles # type: ignore
    if not custom_roles.CUSTOM_ROLES_DEFINED:
        raise AttributeError()
except (ModuleNotFoundError, AttributeError):
    from src import roles
    roles.import_builtin_roles()

try:
    import gamemodes as custom_gamemodes # type: ignore
    if not custom_gamemodes.CUSTOM_MODES_DEFINED:
        raise AttributeError()
except (ModuleNotFoundError, AttributeError):
    from src import gamemodes
    gamemodes.import_builtin_modes()
