from ..database import create_db, Session
from ..models.coeffs import Coeff
from ..models.user import User
from ..models.media import MediaIds
from ..models.source import Source


def create_database(load_fake_data: bool = True) -> None:
    create_db()
