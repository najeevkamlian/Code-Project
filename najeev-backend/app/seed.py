from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_engine, get_audit_collection
from app.models import Base, Admin, Note
from app.security import password_hash


def seed():
    settings = get_settings()
    Base.metadata.create_all(get_engine())
    with Session(get_engine()) as session:
        admin = session.scalar(select(Admin).where(Admin.username == settings.admin_username))
        if admin is None:
            admin = Admin(username=settings.admin_username, password_hash=password_hash.hash(settings.admin_password))
            session.add(admin)
            session.flush()
        for number in range(1, 21):
            title = f'Sample note {number:02d}'
            if session.scalar(select(Note.id).where(Note.owner_id == admin.id, Note.title == title)) is None:
                session.add(Note(title=title, content=f'This is sample note {number}. Edit it using the notes API.', owner_id=admin.id))
        session.commit()
    get_audit_collection().create_index([('admin_id', 1), ('created_at', -1)])
    print('Admin and 20 sample notes are ready.')


if __name__ == '__main__':
    seed()
