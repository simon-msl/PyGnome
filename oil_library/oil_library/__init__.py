import os
from itertools import chain
from collections import namedtuple

from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from hazpy import unit_conversion
uc = unit_conversion

from oil_library.models import Oil, Density, DBSession
from oil_library.mock_oil import sample_oil_to_mock_oil
from oil_library.oil_props import OilProps


# Some standard oils - scope is module level, non-public
_sample_oils = {
    'oil_gas': {'oil_name': 'oil_gas',
                'api': uc.convert('Density', 'gram per cubic centimeter',
                                  'api degree', 0.75)},
    'oil_jetfuels': {'oil_name': 'oil_jetfuels',
                     'api': uc.convert('Density', 'gram per cubic centimeter',
                                       'api degree',
                                       0.81)},
    'oil_diesel': {'oil_name': 'oil_diesel',
                   'api': uc.convert('Density', 'gram per cubic centimeter',
                                     'api degree', 0.87)},
    'oil_4': {'oil_name': 'oil_4',
              'api': uc.convert('Density', 'gram per cubic centimeter',
                                'api degree', 0.90)},
    'oil_crude': {'oil_name': 'oil_crude',
                  'api': uc.convert('Density', 'gram per cubic centimeter',
                                    'api degree', 0.90)},
    'oil_6': {'oil_name': 'oil_6',
              'api': uc.convert('Density', 'gram per cubic centimeter',
                                'api degree', 0.99)},
    'oil_conservative': {'oil_name': 'oil_conservative',
                         'api': uc.convert('Density',
                                           'gram per cubic centimeter',
                                           'api degree', 1)},
    'chemical': {'oil_name': 'chemical',
                 'api': uc.convert('Density', 'gram per cubic centimeter',
                                   'api degree', 1)},
    }

'''
currently, the DB is created and located when package is installed
'''
_oillib_path = os.path.dirname(__file__)
_db_file = os.path.join(_oillib_path, 'OilLib.db')


def get_oil(oil_name, max_cuts=None):
    """
    function returns the Oil object given the name of the oil as a string.

    :param oil_: name of the oil that spilled. If it is one of the names
            stored in _sample_oil dict, then an Oil object with specified
            api is returned.
            Otherwise, query the database for the oil_name and return the
            associated Oil object.
    :type oil_: str

    Optional arg:

    :param max_cuts: This is ** only ** used for _sample_oils which dont have
        distillation cut information. For testing, this allows us to model the
        oil with variable number of cuts, with equally divided mass. For a
        real oil pulled from the database, this is ignored.
    :type max_cuts: int

    NOTE I:
    -------
    One issue is that the kwargs in Oil contain spaces, like 'oil_name'. This
    can be handled if the user defines a dict as follows:
        kw = {'oil_name': 'new oil', 'Field Name': 'field name'}
        get_oil(**kw)
    however, the following will not work:
        get_oil('oil_name'='new oil', 'Field Name'='field name')

    This is another reason, we need an interface between the SQL object and the
    end user.
    """
    if oil_name in _sample_oils.keys():
        return sample_oil_to_mock_oil(max_cuts=max_cuts,
                                      **_sample_oils[oil_name])

    else:
        '''
        db_file should exist - if it doesn't then create if first
        should we raise error here?
        '''

        # not sure we want to do it this way - but let's use for now
        engine = create_engine('sqlite:///' + _db_file)

        # let's use global DBSession defined in oillibrary
        # alternatively, we could define a new scoped_session
        # Not sure what's the proper way yet but this needs
        # to be revisited at some point.
        # session_factory = sessionmaker(bind=engine)
        # DBSession = scoped_session(session_factory)
        DBSession.bind = engine

        try:
            oil_ = DBSession.query(Oil).filter(Oil.oil_name == oil_name).one()
            return oil_
        except NoResultFound, ex:
            # or sqlalchemy.orm.exc.MultipleResultsFound as ex:
            ex.message = ("oil with name '{0}' not found in database. "
                          "{1}".format(oil_name, ex.message))
            ex.args = (ex.message, )
            raise ex


def get_oil_props(oil_name, max_cuts=None):
    '''
    returns the OilProps object
    max_cuts is only used for 'fake' sample_oils. It's a way to allow testing.
    When pulling record from database, this is ignored.
    '''
    oil_ = get_oil(oil_name, max_cuts)
    return OilProps(oil_)