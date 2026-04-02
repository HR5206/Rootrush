from __future__ import annotations

from typing import Any, Dict, List
import json
import os
from datetime import datetime
from pathlib import Path

from flask import session


SESSION_KEY_FACTORIES = "factories"
SESSION_KEY_LOCATIONS = "locations"
SESSION_KEY_PLAN_RESULTS = "plan_results"
SESSION_KEY_SETTINGS = "settings"

# Server-side storage for large plan data (bypasses session cookie size limits)
PLAN_STORAGE_DIR = Path(__file__).parent / ".plan_storage"


def _ensure_storage_dir() -> Path:
    """Ensure the plan storage directory exists."""
    PLAN_STORAGE_DIR.mkdir(exist_ok=True)
    return PLAN_STORAGE_DIR


def _default_factories() -> List[Dict[str, Any]]:
    """Return default factory definitions around Salem, Tamil Nadu, India.

    Each factory has: name, lat, lng, weekly_rate.
    """

    return [
        {"name": "Factory 1", "lat": 11.6643, "lng": 78.1460, "weekly_rate": 12},
        {"name": "Factory 2", "lat": 11.6850, "lng": 78.1200, "weekly_rate": 10},
        {"name": "Factory 3", "lat": 11.6500, "lng": 78.1700, "weekly_rate": 8},
    ]


def _default_locations() -> List[Dict[str, Any]]:
    """Return a small set of sample project locations around Salem."""

    return [
        {"name": "Site A", "lat": 11.6640, "lng": 78.1465},
        {"name": "Site B", "lat": 11.6700, "lng": 78.1400},
        {"name": "Site C", "lat": 11.6580, "lng": 78.1500},
    ]


def ensure_factories() -> List[Dict[str, Any]]:
    """Get factories from session, initialising with defaults if missing.

    This keeps a consistent place for factory state and ensures later
    clustering/scheduling logic always sees a non-empty list.
    """

    factories = session.get(SESSION_KEY_FACTORIES)
    if not factories:
        factories = _default_factories()
        session[SESSION_KEY_FACTORIES] = factories
    return factories


def save_factories(factories: List[Dict[str, Any]]) -> None:
    session[SESSION_KEY_FACTORIES] = factories
    session.modified = True


def ensure_locations() -> List[Dict[str, Any]]:
    """Get project locations from session, initialising with defaults if missing."""

    locations = session.get(SESSION_KEY_LOCATIONS)
    if not locations:
        locations = _default_locations()
        session[SESSION_KEY_LOCATIONS] = locations
    return locations


def save_locations(locations: List[Dict[str, Any]]) -> None:
    session[SESSION_KEY_LOCATIONS] = locations
    session.modified = True


def get_current_inputs() -> Dict[str, Any]:
    """Return a snapshot of the current input state.

    Structure is stable so later parts (clustering, routing, scheduling,
    AI insights) can rely on it.
    """

    return {
        "factories": ensure_factories(),
        "locations": ensure_locations(),
    }


def get_settings() -> Dict[str, Any]:
    """Return user-level settings (e.g. AI toggle, HF token).

    This prepares for later Hugging Face integration.
    """

    settings = session.get(SESSION_KEY_SETTINGS)
    if not settings:
        settings = {
            "enable_ai_insights": True,
            "hf_api_token": "",
        }
        session[SESSION_KEY_SETTINGS] = settings
    return settings


def save_settings(settings: Dict[str, Any]) -> None:
    session[SESSION_KEY_SETTINGS] = settings
    session.modified = True


def get_plan_results() -> Dict[str, Any] | None:
    """Return the last generated plan from file storage.
    
    Uses file-based storage to avoid session cookie size limits for large datasets.
    """
    
    storage_dir = _ensure_storage_dir()
    plan_file = storage_dir / "latest_plan.json"
    
    if not plan_file.exists():
        return None
    
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def save_plan_results(results: Dict[str, Any]) -> None:
    """Persist the latest plan results structure in file storage.
    
    Uses file-based storage to handle large datasets (600+ locations)
    that exceed Flask session cookie size limits (~4KB).
    """
    
    storage_dir = _ensure_storage_dir()
    plan_file = storage_dir / "latest_plan.json"
    
    try:
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, default=str)
    except Exception as e:
        print(f"Warning: Could not save plan results to file: {e}")
