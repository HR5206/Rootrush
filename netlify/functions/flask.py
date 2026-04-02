"""Netlify Function entrypoint for the Flask app."""

from __future__ import annotations

import awsgi

from app import create_app


flask_app = create_app()


def handler(event, context):
    """Adapt API Gateway-style event to Flask via awsgi."""

    return awsgi.response(flask_app, event, context)
