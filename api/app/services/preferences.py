"""The user's preferences (Settings › Preferences)."""

from sqlalchemy.orm import Session

from app.models import UserPreferences


def get_preferences(user_id: int, db: Session) -> UserPreferences:
    """The user's saved preferences, or the defaults (not saved) when they haven't changed any."""
    return db.get(UserPreferences, user_id) or UserPreferences.defaults(user_id)
