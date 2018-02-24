from sqlalchemy import Column, String, Integer, Sequence, Table, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declared_attr, declarative_base

# engine = create_engine('postgresql+psycopg2://test_user:test_password@localhost/sqlalchemy_tests', echo=False)
from sqlalchemy.orm import relationship

Base = declarative_base()


#
# Mixins
#
class NamedAndDescribedModelMixin(object):
    """
    Mixin providing common name and description columns.
    """
    name = Column(String(100), nullable=False)
    description = Column(String(1000))


class CommonMixin(object):
    """
    Mixin providing some common code, like __tablename__ and __repr__().
    """

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # noinspection PyUnresolvedReferences
    def __repr__(self):
        fields = ["%s='%s'" % (c.name, getattr(self, c.name)) for c in self.__class__.__table__.c]
        return "<%s(%s)>" % (self.__class__.__name__, ', '.join(fields))


class IdMixin(object):
    """
    Mixin providing a sequence-generated primary key.
    """

    # noinspection PyMethodParameters,PyUnresolvedReferences
    @declared_attr
    def id(cls):
        return Column(Integer, Sequence('%s_id_seq' % cls.__tablename__), primary_key=True)


class CommonIdMixin(CommonMixin, IdMixin):
    """
    Combines CommonMixin and IdMixin for convenience.
    """
    pass

#
# Many-to-many association tables
#
ruleset_sport_association_table = Table('ruleset_sport_association_table',
                                        Base.metadata,
                                        Column('ruleset_id', Integer, ForeignKey('ruleset.id')),
                                        Column('sport_id', Integer, ForeignKey('sport.id')))
"""
Association table for the many-to-many relationship between the RuleSet and Sport tables. 
"""


tournament_competitor_association_table = Table('tournament_competitor_association',
                                                Base.metadata,
                                                Column('tournament_id', Integer, ForeignKey('tournament.id')),
                                                Column('competitor_id', Integer, ForeignKey('competitor.id')))
"""
Association table for the many-to-many relationship between the Tournament and Competitor tables. 
"""


#
# Static tables
#
class Status(CommonIdMixin, NamedAndDescribedModelMixin, Base):
    """
    Static table containing common status codes.
    """
    pass


class Sport(CommonIdMixin, NamedAndDescribedModelMixin, Base):
    """
    Static table containing sport descriptions.
    """
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    available_rulesets = relationship('RuleSet', secondary=ruleset_sport_association_table,
                                      back_populates='applicable_sports')
    """
    RuleSets that are available for use with this sport. 
    """


class RuleSet(CommonIdMixin, NamedAndDescribedModelMixin, Base):
    """
    Static table containing rulesets for users to choose from when planning a tournament. Rulesets are only applicable
    to specific sports, as defined in the mappings between RuleSet and Sport.
    """
    applicable_sports = relationship('Sport', secondary=ruleset_sport_association_table,
                                     back_populates='available_rulesets')
    """
    Sports that can make use of this rule set. 
    """


#
# Dynamic tables
#
class Rules(CommonIdMixin, NamedAndDescribedModelMixin, Base):
    """
    A combination of a ruleset and configured parameters, to be used by the associated tournament.
    """
    ruleset_id = Column(Integer, ForeignKey('ruleset.id'), nullable=False)
    ruleset = relationship('RuleSet')
    """
    The core rule set to be used. 
    """

    params = Column(postgresql.JSON)
    """
    The optional parameters to be passed to the associated rule set. 
    """

    tournament_id = Column(Integer, ForeignKey('tournament.id'), nullable=False, unique=True)
    tournament = relationship('Tournament', back_populates='rules')
    """
    The tournament to apply the configured rule set to. 
    """


class Competitor(CommonIdMixin, Base):
    """
    A human competitor. Can be a participant in multiple Tournaments.
    """
    email = Column(String(100), unique=True)
    """
    Unique identifier between competitors. 
    """

    first_name = Column(String(100), nullable=False)
    """
    Competitor's first name. 
    """

    last_name = Column(String(100), nullable=False)
    """
    Competitor's last name. 
    """

    affiliation = Column(String(500))
    """
    Competitor's affiliation, for example 'CKDF'. 
    """

    tournaments = relationship('Tournament', secondary=tournament_competitor_association_table,
                               back_populates='competitors')
    """
    The tournaments in which the competitor is competing. 
    """


class Tournament(CommonIdMixin, NamedAndDescribedModelMixin, Base):
    """
    A tournament, as represented by the combination of a sport, a rules object, a set of competitors, and a set of
    tournament stages.
    """
    def __init__(self, owner, sport, name, description=None):
        self.owner = owner
        self.sport = sport
        self.name = name
        self.description = description

    owner = Column(String(50), nullable=False)
    """
    The Cognito user that owns this tournament. They will be the only one allowed to alter it. 
    """

    sport_id = Column(Integer, ForeignKey('sport.id'), nullable=False)
    sport = relationship('Sport')
    """
    The sport that will be played in the tournament. 
    """

    competitors = relationship('Competitor', secondary=tournament_competitor_association_table,
                               back_populates='tournaments')
    """
    List of competitors included in the tournament. 
    """

    rules = relationship('Rules', back_populates='tournament', cascade='all')
    """
    The rules used by the tournament. 
    """

    stages = relationship('Stage', order_by='Stage.ordinality', back_populates='tournament', cascade='all')
    """
    The list of stages included in the tournament, in the order they should take place. 
    """


class Stage(CommonIdMixin, NamedAndDescribedModelMixin, Base):
    """
    Stage in the associated tournament. For example, 'pools', 'elims', 'finals', etc.
    """
    tournament_id = Column(Integer, ForeignKey('tournament.id'), nullable=False)
    tournament = relationship('Tournament', back_populates='stages')
    """
    Parent tournament. 
    """

    status_id = Column(Integer, ForeignKey('status.id'), nullable=False)
    status = relationship('Status')
    """
    Status of the stage. 
    """

    ordinality = Column(Integer, nullable=False)
    """
    Order in which the stages should be executed within their tournament. 
    """

    matchgroups = relationship('MatchGroup', order_by='MatchGroup.ordinality', back_populates='stage', cascade='all')
    """
    MatchGroups contained within the stage. 
    """


class MatchGroup(CommonIdMixin, NamedAndDescribedModelMixin, Base):
    """
    A group of matches, for example 'pool 1', 'elims group 1', 'finals', etc.
    """
    stage_id = Column(Integer, ForeignKey('stage.id'), nullable=False)
    stage = relationship('Stage', back_populates='matchgroups')
    """
    The containing tournament stage. 
    """

    status_id = Column(Integer, ForeignKey('status.id'), nullable=False)
    status = relationship('Status')
    """
    Status of the match group. 
    """

    ordinality = Column(Integer, nullable=False)
    """
    Order in which the match groups should be executed within their stage. 
    """

    matches = relationship('Match', order_by='Match.ordinality', back_populates='matchgroup', cascade='all')
    """
    Matches contained within the match group. 
    """


class Match(CommonIdMixin, Base):
    """
    A single match.
    """
    matchgroup_id = Column(Integer, ForeignKey('matchgroup.id'), nullable=False)
    matchgroup = relationship('MatchGroup', back_populates='matches')

    red_competitor_id = Column(Integer, ForeignKey('competitor.id'))
    red_competitor = relationship('Competitor', foreign_keys=[red_competitor_id])
    """
    The red competitor. 
    """

    blue_competitor_id = Column(Integer, ForeignKey('competitor.id'))
    blue_competitor = relationship('Competitor', foreign_keys=[blue_competitor_id])
    """
    The blue competitor. 
    """

    red_feeder_id = Column(Integer, ForeignKey('match.id'))
    red_feeder = relationship('Match', foreign_keys=[red_feeder_id])
    """
    The red feeder. In rule sets that rely on heirarchical structures (like single-elimination brackets), matches may 
    need to be created before the competitors are known (because they depend on other matches completing). This is a 
    pointer to the match whose winner will become the red competitor upon match completion. 
    """

    blue_feeder_id = Column(Integer, ForeignKey('match.id'))
    blue_feeder = relationship('Match', foreign_keys=[blue_feeder_id])
    """
    The blue feeder. In rule sets that rely on heirarchical structures (like single-elimination brackets), matches may 
    need to be created before the competitors are known (because they depend on other matches completing). This is a 
    pointer to the match whose winner will become the blue competitor upon match completion. 
    """

    red_score = Column(Integer)
    """
    Red competitor's score. 
    """

    blue_score = Column(Integer)
    """
    Blue competitor's score. 
    """

    status_id = Column(Integer, ForeignKey('status.id'))
    status = relationship('Status')
    """
    Status of the match. 
    """

    ordinality = Column(Integer, nullable=False)
    """
    Order in which the match should be executed within it's match group. 
    """
