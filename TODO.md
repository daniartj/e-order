# TODO - Nixpacks/Django WSGI deployment fix

- [x] Inspect WSGI/Procfile settings.
- [x] Update `Procfile` to force `DJANGO_SETTINGS_MODULE` and use `gunicorn eorder.wsgi:application`.
- [ ] Rebuild/redeploy with Nixpacks to confirm the error is gone.

