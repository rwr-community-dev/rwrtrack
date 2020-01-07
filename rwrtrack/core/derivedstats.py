from sqlalchemy import Float
from sqlalchemy.sql import cast
from sqlalchemy.ext.hybrid import hybrid_property

from .constants import EARTH_EQUAT_CIRC


class DerivedStats:
    """Implements derived statistics"""
    # Some special logic is needed in some places in this class to ensure float division is used by the db
    # SQLAlchemy constructs SQL statements from the hybrid properties automatically
    # However, whereas Python will return a float from the division of two integers, the db doesn't in SQL statements
    # In this edge case, expressions are defined for hybrid properties to ensure A is cast as Float in A/B
    # Note: derived properties that use time_played_hours or distance_moved_km, already Floats, don't need expressions

    # Time played in hours
    @hybrid_property
    def time_played_hours(self):
        # Division by a float is essential here to ensure the underlying db returns a float from division
        # This float will propagate into all SQL statements constructed from time_played_hours
        return self.time_played / 60.0

    # Distance moved in km
    @hybrid_property
    def distance_moved_km(self):
        # Division by a float is essential here to ensure the underlying db returns a float from division
        # This float will propagate into all SQL statements constructed from distance_moved_km
        return self.distance_moved / 1000.0

    # Score
    @hybrid_property
    def score(self):
        return self.kills - self.deaths

    # K/D ratio
    @hybrid_property
    def kdr(self):
        try:
            return self.kills / self.deaths
        except ZeroDivisionError:
            return 0

    @kdr.expression
    def kdr(cls):
        # Cast to ensure that SQL statements constructed for this variable return a float from division
        return cast(cls.kills, Float) / cls.deaths

    # XP per hour
    @hybrid_property
    def xp_per_hour(self):
        try:
            return self.xp / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Kills per hour
    @hybrid_property
    def kills_per_hour(self):
        try:
            return self.kills / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Deaths per hour
    @hybrid_property
    def deaths_per_hour(self):
        try:
            return self.deaths / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Targets destroyed per hour
    @hybrid_property
    def targets_destroyed_per_hour(self):
        try:
            return self.targets_destroyed / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Vehicles destroyed per hour
    @hybrid_property
    def vehicles_destroyed_per_hour(self):
        try:
            return self.vehicles_destroyed / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Soldiers healed per hour
    @hybrid_property
    def soldiers_healed_per_hour(self):
        try:
            return self.soldiers_healed / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Team kills per hour
    @hybrid_property
    def team_kills_per_hour(self):
        try:
            return self.team_kills / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Distance moved (in km) per hour
    @hybrid_property
    def distance_moved_km_per_hour(self):
        try:
            return self.distance_moved_km / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Shots fired per hour
    @hybrid_property
    def shots_fired_per_hour(self):
        try:
            return self.shots_fired / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Throwables thrown per hour
    @hybrid_property
    def throwables_thrown_per_hour(self):
        try:
            return self.throwables_thrown / self.time_played_hours
        except ZeroDivisionError:
            return 0

    # Kills per km moved
    @hybrid_property
    def kills_per_km_moved(self):
        try:
            return self.kills / self.distance_moved_km
        except ZeroDivisionError:
            return 0

    # XP per shot fired
    @hybrid_property
    def xp_per_shot_fired(self):
        try:
            return self.xp / self.shots_fired
        except ZeroDivisionError:
            return 0

    @xp_per_shot_fired.expression
    def xp_per_shot_fired(cls):
        # Cast to ensure that SQL statements constructed for this variable return a float from division
        return cast(cls.xp, Float) / cls.shots_fired

    # XP per kill
    @hybrid_property
    def xp_per_kill(self):
        try:
            return self.xp / self.kills
        except ZeroDivisionError:
            return 0

    @xp_per_kill.expression
    def xp_per_kill(cls):
        # Cast to ensure that SQL statements constructed for this variable return a float from division
        return cast(cls.xp, Float) / cls.kills

    # Shots fired per kill
    @hybrid_property
    def shots_fired_per_kill(self):
        try:
            return self.shots_fired / self.kills
        except ZeroDivisionError:
            return 0

    @shots_fired_per_kill.expression
    def shots_fired_per_kill(cls):
        # Cast to ensure that SQL statements constructed for this variable return a float from division
        return cast(cls.shots_fired, Float) / cls.kills

    # Team kills per kill
    @hybrid_property
    def team_kills_per_kill(self):
        try:
            return self.team_kills / self.kills
        except ZeroDivisionError:
            return 0

    @team_kills_per_kill.expression
    def team_kills_per_kill(cls):
        # Cast to ensure that SQL statements constructed for this variable return a float from division
        return cast(cls.team_kills, Float) / cls.kills

    # Runs around the Earth equator
    @hybrid_property
    def runs_around_the_equator(self):
        return self.distance_moved_km / EARTH_EQUAT_CIRC
