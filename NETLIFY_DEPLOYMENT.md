# Netlify Deployment Guide for Rootrush

This project uses Flask, so Netlify runs it through a Python serverless function.

## What is configured

- `netlify.toml` routes all requests to a Python function.
- `netlify/functions/flask.py` adapts Flask to Netlify runtime.
- `requirements.txt` includes `awsgi`.

## Deploy steps

1. Push this repository to GitHub.
2. In Netlify, click **Add new site** -> **Import from Git**.
3. Select this repository and branch.
4. Build settings:
- Build command: `pip install -r requirements.txt`
- Publish directory: `static`
- Functions directory: `netlify/functions`
5. Add environment variables in Netlify Site Settings -> Environment Variables:
- `FLASK_ENV=production`
- `FLASK_SECRET_KEY=<strong-secret-key>`
- `HUGGINGFACE_API_TOKEN=<your-token>`
6. Deploy the site.

## Verify routes

- `/`
- `/inputs`
- `/generate`
- `/results`

## Important limitation

`data_layer.py` currently saves generated plan data to local filesystem (`.plan_storage/latest_plan.json`). Netlify Functions have ephemeral filesystem, so this data may not persist between invocations.

For reliable production behavior, move plan result storage to a persistent store (database or object storage).
