import datetime

import bcrypt
import jwt
import pytz
from django.conf import settings


def generate_hash(data: str) -> str:
    return bcrypt.hashpw(data.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def generate_jwt_token(user_id: str) -> str:
    key = settings.SECRET_KEY
    algorithm = settings.JWT_ALGORITHM
    token: bytes = jwt.encode(
        {
            "iss": "me",
            "id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=14),
        },
        key,
        algorithm=algorithm,
    )

    return token.decode("utf-8")


def check_old_token(date: datetime.datetime) -> bool:
    gap = datetime.datetime.now(tz=pytz.utc) - date

    if gap > datetime.timedelta(days=1):
        return True
    return False
