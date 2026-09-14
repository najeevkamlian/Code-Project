import os
from unittest.mock import MagicMock

os.environ.update(DATABASE_URL='sqlite://', MONGODB_URL='mongodb://localhost:27017',
                  JWT_SECRET='test-secret-that-is-long-enough-for-jwt', ADMIN_PASSWORD='test-password-123')

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models import Base, Admin, Note
from app.security import password_hash, create_token


@pytest.fixture
def api(monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([Admin(username='admin', password_hash=password_hash.hash('test-password-123')),
                         Admin(username='other', password_hash=password_hash.hash('other-password'))])
        session.commit()
    def sessions():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = sessions
    monkeypatch.setattr('app.services.get_audit_collection', lambda: MagicMock())
    with TestClient(app) as client:
        yield client, engine
    app.dependency_overrides.clear()
    engine.dispose()


def test_auth_and_crud(api):
    client, _ = api
    assert client.get('/notes').status_code == 401
    assert client.post('/auth/token', data={'username': 'admin', 'password': 'wrong'}).status_code == 401
    login = client.post('/auth/token', data={'username': 'admin', 'password': 'test-password-123'})
    assert login.status_code == 200
    headers = {'Authorization': 'Bearer ' + login.json()['access_token']}
    created = client.post('/notes', json={'title': 'First', 'content': 'A note'}, headers=headers)
    assert created.status_code == 201
    note_id = created.json()['id']
    assert client.get('/notes', headers=headers).json()[0]['title'] == 'First'
    other = {'Authorization': 'Bearer ' + create_token(2)}
    for method in ('get', 'put', 'delete'):
        kwargs = {'json': {'title': 'Stolen', 'content': 'No'}} if method == 'put' else {}
        assert getattr(client, method)(f'/notes/{note_id}', headers=other, **kwargs).status_code == 404
    assert client.put(f'/notes/{note_id}', json={'title': 'Edited', 'content': 'New'}, headers=headers).json()['title'] == 'Edited'
    assert client.post('/notes', json={'title': ' ', 'content': 'x'}, headers=headers).status_code == 422
    assert client.get('/notes?limit=101', headers=headers).status_code == 422
    assert client.delete(f'/notes/{note_id}', headers=headers).status_code == 204
    assert client.get(f'/notes/{note_id}', headers=headers).status_code == 404
    assert client.get('/notes', headers={'Authorization': 'Bearer invalid'}).status_code == 401


def test_seed_is_repeatable(api, monkeypatch):
    from app.seed import seed
    _, engine = api
    monkeypatch.setattr('app.seed.get_engine', lambda: engine)
    monkeypatch.setattr('app.seed.get_audit_collection', lambda: MagicMock())
    seed()
    seed()
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Note)) == 20


def test_audit_outage_preserves_note(api, monkeypatch):
    from pymongo.errors import ConnectionFailure
    collection = MagicMock()
    collection.insert_one.side_effect = ConnectionFailure('offline')
    monkeypatch.setattr('app.services.get_audit_collection', lambda: collection)
    client, _ = api
    headers = {'Authorization': 'Bearer ' + create_token(1)}
    assert client.post('/notes', json={'title': 'Saved', 'content': 'Data'}, headers=headers).status_code == 201
    assert len(client.get('/notes', headers=headers).json()) == 1
