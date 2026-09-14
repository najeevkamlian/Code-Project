import logging
from pymongo.errors import PyMongoError
from app.database import get_audit_collection
from app.models import utcnow

logger = logging.getLogger(__name__)


def record_event(action: str, admin_id: int, note_id: int):
    # PostgreSQL is authoritative; an audit outage must not undo a saved note.
    try:
        get_audit_collection().insert_one({'action': action, 'admin_id': admin_id,
                                          'note_id': note_id, 'created_at': utcnow()})
    except PyMongoError:
        logger.warning('Audit write failed for note %s', note_id)
