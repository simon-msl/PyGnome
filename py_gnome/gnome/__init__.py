"""
__init__.py for the gnome package

"""
from itertools import chain

import sys
import logging
import json

import unit_conversion as uc

from gnomeobject import GnomeId, init_obj_log, AddLogger

__version__ = '0.2.1prev'


# a few imports so that the basic stuff is there

def initialize_log(config, logfile=None):
    '''
    helper function to initialize a log - done by the application using PyGnome
    config can be a file containing json or it can be a Python dict

    :param config: logging configuration as a json file or config dict
                   it needs to be in the dict config format used by ``logging.dictConfig``:
                   https://docs.python.org/2/library/logging.config.html#logging-config-dictschema

    :param logfile=None: optional name of file to log to

    '''
    if isinstance(config, basestring):
        config = json.load(open(config, 'r'))

    if logfile is not None:
        config['handlers']['file']['filename'] = logfile

    logging.config.dictConfig(config)


def initialize_console_log(level='debug'):
    '''
    Initializes the logger to simply log everything to the console (stdout)

    Likely what you want for scripting use

    :param level='debug': the level you want your log to show. options are,
                          in order of importance: "debug", "info", "warning",
                          "error", "critical"

    You will only get the logging messages at or above the level you set.

    '''
    levels = {"debug": logging.DEBUG,
              "info": logging.INFO,
              "warning": logging.WARNING,
              "error": logging.ERROR,
              "critical": logging.CRITICAL,
              }
    level = levels[level.lower()]
    format_str = '%(levelname)s - %(module)8s - line:%(lineno)d - %(message)s'
    logging.basicConfig(stream=sys.stdout,
                        level=level,
                        format=format_str,
                        )


def _valid_units(unit_name):
    'convenience function to get all valid units accepted by unit_conversion'
    _valid_units = uc.GetUnitNames(unit_name)
    _valid_units.extend(chain(*[val[1] for val in
                                uc.ConvertDataUnits[unit_name].values()]))
    return tuple(_valid_units)

# we have a sort of chicken-egg situation here.  The above functions need
# to be defined before we can import these modules.
from . import (map, environment,
               model, multi_model_broadcast,
               spill_container, spill,
               movers, outputters)

__all__ = [GnomeId,
           map,
           spill,
           spill_container,
           movers,
           environment,
           model,
           outputters,
           initialize_log,
           AddLogger,
           multi_model_broadcast]
