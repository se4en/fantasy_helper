import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from fantasy_helper.db.database import Base, db_engine
from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.models.source import Source
from fantasy_helper.db.models.user import User
from fantasy_helper.db.models.lineup import Lineup
from fantasy_helper.db.models.player import Player
from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.db.models.table import Table
from fantasy_helper.db.models.schedule import Schedule
from fantasy_helper.db.models.actual_player import ActualPlayer
from fantasy_helper.db.models.fbref_schedule import FbrefSchedule
from fantasy_helper.db.models.players_match import PlayersMatch
from fantasy_helper.db.models.feature_store.fs_coeffs import FSCoeffs
from fantasy_helper.db.models.feature_store.fs_lineups import FSLineups
from fantasy_helper.db.models.feature_store.fs_players_stats import FSPlayersStats
from fantasy_helper.db.models.feature_store.fs_players_free_kicks import (
    FSPlayersFreeKicks,
)
from fantasy_helper.db.models.feature_store.fs_sports_players import FSSportsPlayers
from fantasy_helper.db.models.feature_store.fs_calendars import FSCalendars
from fantasy_helper.db.models.ml.team_name import TeamName
from fantasy_helper.db.models.ml.player_name import PlayerName

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata



def get_database_url():
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'password')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    db = os.getenv('POSTGRES_DB', 'fantasy_helper')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
