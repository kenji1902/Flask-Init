"""Central blueprint registry.

This reads an `INSTALLED_APPS` list from the Flask config and attempts to
import and register a blueprint for each app. Entry forms supported:

- 'AppName'  -> imports FlaskTest.AppName and looks for common blueprint
                attributes (e.g. `about_bp`, `bp`, `blueprint`).
- ('AppName', '/prefix') -> same as above, but registers with a URL prefix.

This mirrors Django's INSTALLED_APPS idea: you only list app names in the
config and the registry wires them up.
"""
from importlib import import_module
import logging
from typing import Iterable

logger = logging.getLogger(__name__)


def _find_blueprint_in_module(module, app_name: str):
    """Search common attribute names for a blueprint in a module."""
    candidates = [f"{app_name.lower()}_bp", "bp", "blueprint", "app_bp", "main"]
    for attr in candidates:
        bp = getattr(module, attr, None)
        if bp is not None:
            return bp
    return None


def register_blueprints(app) -> None:
    """Register blueprints listed in app.config['INSTALLED_APPS'].

    INSTALLED_APPS can be a list of strings or (string, prefix) tuples.
    """
    installed = app.config.get("INSTALLED_APPS") or []
    if not isinstance(installed, Iterable):
        raise TypeError("INSTALLED_APPS must be an iterable of app names or (app, prefix) tuples")

    for entry in installed:
        url_prefix = None
        if isinstance(entry, (list, tuple)):
            if len(entry) == 0:
                continue
            app_name = entry[0]
            if len(entry) > 1:
                url_prefix = entry[1]
        else:
            app_name = entry

        # Try to import the app package first, then fall back to common submodules
        mod = None
        tried = []
        # Build import candidates at project root
        candidates = [app_name, f"{app_name}.urls", f"{app_name}.views"]
        for module_name in candidates:
            try:
                mod = import_module(module_name)
                break
            except Exception as exc:  # import failure; try next
                tried.append((module_name, str(exc)))

        if mod is None:
            logger.warning("Could not import app module for %s; tried: %s", app_name, tried)
            continue

        bp = _find_blueprint_in_module(mod, app_name)
        if bp is None:
            # As a last resort, try importing the package and searching that module
            try:
                pkg = import_module(app_name)
                bp = _find_blueprint_in_module(pkg, app_name)
            except Exception:
                bp = None

        if bp is None:
            logger.warning("No blueprint found for app %s (looked for common attributes)", app_name)
            continue

        # Register the blueprint
        try:
            if url_prefix:
                app.register_blueprint(bp, url_prefix=url_prefix)
            else:
                app.register_blueprint(bp)
            logger.info("Registered blueprint for %s (prefix=%s)", app_name, url_prefix)
        except Exception:
            logger.exception("Failed to register blueprint for %s", app_name)
