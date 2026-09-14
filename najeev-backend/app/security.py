from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_session
from app.models import Admin

password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash('unused-timing-equalization-password')
oauth2 = OAuth2PasswordBearer(tokenUrl='/auth/token')


def create_token(admin_id: int):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(admin_id), 'iat': now,
                       'exp': now + timedelta(minutes=settings.access_token_minutes)},
                      settings.jwt_secret, algorithm='HS256')


def current_admin(token: str = Depends(oauth2), session: Session = Depends(get_session)):
    error = HTTPException(401, 'Invalid or expired credentials', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=['HS256'],
                             options={'require': ['sub', 'iat', 'exp']})
        admin_id = int(payload['sub'])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise error
    admin = session.get(Admin, admin_id)
    if admin is None:
        raise error
    return admin
