from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from pymongo.errors import PyMongoError
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_session, get_mongo, get_audit_collection
from app.models import Admin, Note
from app.security import current_admin, create_token, password_hash, dummy_hash
from app.services import record_event
from app.views import NoteInput, NoteView, TokenView

router = APIRouter()


@router.post('/auth/token', response_model=TokenView, tags=['Authentication'])
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    admin = session.scalar(select(Admin).where(Admin.username == form.username))
    valid = password_hash.verify(form.password, admin.password_hash if admin else dummy_hash)
    if not admin or not valid:
        raise HTTPException(401, 'Incorrect username or password', headers={'WWW-Authenticate': 'Bearer'})
    return TokenView(access_token=create_token(admin.id))


@router.get('/health', tags=['Health'])
def health(session: Session = Depends(get_session)):
    try:
        session.execute(text('SELECT 1'))
        get_mongo().admin.command('ping')
    except (SQLAlchemyError, PyMongoError):
        raise HTTPException(503, 'Database unavailable')
    return {'status': 'ok'}


@router.get('/notes', response_model=list[NoteView], tags=['Notes'])
def list_notes(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
               admin: Admin = Depends(current_admin), session: Session = Depends(get_session)):
    return session.scalars(select(Note).where(Note.owner_id == admin.id).order_by(Note.id).offset(offset).limit(limit)).all()


def owned_note(note_id, admin, session):
    note = session.scalar(select(Note).where(Note.id == note_id, Note.owner_id == admin.id))
    if note is None:
        raise HTTPException(404, 'Note not found')
    return note


@router.get('/notes/{note_id}', response_model=NoteView, tags=['Notes'])
def read_note(note_id: int, admin: Admin = Depends(current_admin), session: Session = Depends(get_session)):
    return owned_note(note_id, admin, session)


@router.post('/notes', response_model=NoteView, status_code=201, tags=['Notes'])
def create_note(data: NoteInput, admin: Admin = Depends(current_admin), session: Session = Depends(get_session)):
    note = Note(**data.model_dump(), owner_id=admin.id)
    session.add(note)
    session.commit()
    session.refresh(note)
    record_event('created', admin.id, note.id)
    return note


@router.put('/notes/{note_id}', response_model=NoteView, tags=['Notes'])
def update_note(note_id: int, data: NoteInput, admin: Admin = Depends(current_admin), session: Session = Depends(get_session)):
    note = owned_note(note_id, admin, session)
    note.title, note.content = data.title, data.content
    session.commit()
    session.refresh(note)
    record_event('updated', admin.id, note.id)
    return note


@router.delete('/notes/{note_id}', status_code=204, tags=['Notes'])
def delete_note(note_id: int, admin: Admin = Depends(current_admin), session: Session = Depends(get_session)):
    note = owned_note(note_id, admin, session)
    session.delete(note)
    session.commit()
    record_event('deleted', admin.id, note_id)
    return Response(status_code=204)


@router.get('/audit', tags=['Audit'])
def audit(limit: int = Query(20, ge=1, le=100), admin: Admin = Depends(current_admin)):
    try:
        return list(get_audit_collection().find({'admin_id': admin.id}, {'_id': 0}).sort('created_at', -1).limit(limit))
    except PyMongoError:
        raise HTTPException(503, 'Audit database unavailable')
