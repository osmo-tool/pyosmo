from random import Random


class OsmoModel:
    """ Abstract Osmo model. When using cli tool need to make your models as child class of this one """

    # This will be replaced with same random that osmo is using
    # When using this random inside model you can give seed for osmo and get same run
    osmo_random = Random()
