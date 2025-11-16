import sys
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from importlib import import_module
import hashlib
import json

load_dotenv()

# Ensure FLASK_CONFIG default is set (not required but consistent)
os.environ.get('FLASK_CONFIG', 'base')

from MainApp.wsgi import app


def runserver(host: str = '127.0.0.1', port: int = 5000, debug: bool = None):
    """Run the development server.

    host: host IP to bind to (default 127.0.0.1)
    port: port number (default 5000)
    debug: if None, use app.debug; otherwise honor the boolean value
    """
    if debug is None:
        debug = app.config.get('DEBUG', False)
    # Ensure port is an int
    try:
        port = int(port)
    except Exception:
        raise ValueError(f'port must be an integer, got {port!r}')

    app.run(host=host, port=port, debug=debug)


def collectstatic(dest: str = None, fingerprint: bool = False):
    """Collect static files from INSTALLED_APPS into a single directory.

    By default this will create `FlaskTest/static_collected/` and copy each
    app's `static/` into `static_collected/<AppName>/...`.

    If `fingerprint` is True the function will append a short hash to file
    names (before the extension) and write a `manifest.json` mapping
    original paths to fingerprinted paths. This is useful for cache-busting
    in production deployments.
    """
    # Determine destination
    if dest is None:
        dest = os.environ.get('STATIC_ROOT') or os.path.join(os.getcwd(), 'MainApp', 'static_collected')
    dest_path = Path(dest).resolve()
    dest_path.mkdir(parents=True, exist_ok=True)

    # Try to read INSTALLED_APPS from app config first, then fallback to settings
    installed = []
    try:
        installed = app.config.get('INSTALLED_APPS') or []
    except Exception:
        installed = []

    # Fallback: try to import MainApp.settings.base and read INSTALLED_APPS
    if not installed:
        try:
            settings = import_module('MainApp.settings.base')
            installed = getattr(settings.base, 'INSTALLED_APPS', []) or []
        except Exception:
            installed = []

    if not installed:
        print('No INSTALLED_APPS found; nothing to collect.')
        return

    total = 0
    manifest = {}
    for entry in installed:
        # entry can be 'App' or ('App','/prefix')
        app_name = entry[0] if isinstance(entry, (list, tuple)) else entry

        # Candidate static locations
        candidates = [
            Path(os.getcwd()) / app_name / 'static',
            Path(os.getcwd()) / 'MainApp' / app_name / 'static',
        ]

        found = False
        for src in candidates:
            if src.exists() and src.is_dir():
                found = True
                # copy files preserving relative paths under dest/<AppName>/...
                for root, dirs, files in os.walk(src):
                    rel = Path(root).relative_to(src)
                    target_dir = dest_path / app_name / rel
                    target_dir.mkdir(parents=True, exist_ok=True)
                    for fn in files:
                        src_file = Path(root) / fn
                        # Determine destination filename (optionally fingerprinted)
                        if fingerprint:
                            # compute a short hash of the file contents
                            h = hashlib.sha256()
                            with src_file.open('rb') as f:
                                while True:
                                    chunk = f.read(8192)
                                    if not chunk:
                                        break
                                    h.update(chunk)
                            digest = h.hexdigest()[:8]
                            # preserve extension; insert hash before extension
                            if src_file.suffix:
                                name = src_file.stem
                                ext = src_file.suffix
                                new_name = f"{name}.{digest}{ext}"
                            else:
                                new_name = f"{src_file.name}.{digest}"
                            dst_file = target_dir / new_name
                            # record mapping in manifest using app-relative path
                            orig_rel = (Path(app_name) / rel / fn).as_posix()
                            new_rel = (Path(app_name) / rel / new_name).as_posix()
                            manifest[orig_rel] = new_rel
                        else:
                            dst_file = target_dir / fn

                        shutil.copy2(src_file, dst_file)
                        total += 1
                print(f'Collected static for {app_name} from {src} -> {dest_path / app_name}')
                break

        if not found:
            print(f'No static folder found for app: {app_name} (looked in {candidates})')

    print(f'Collected total {total} files into {dest_path}')
    # If fingerprinting was used, write a manifest.json at the destination
    if fingerprint and manifest:
        manifest_path = dest_path / 'manifest.json'
        try:
            with manifest_path.open('w', encoding='utf-8') as mf:
                json.dump(manifest, mf, indent=2, ensure_ascii=False)
            print(f'Wrote manifest with {len(manifest)} entries to {manifest_path}')
        except Exception as exc:
            print(f'Failed to write manifest.json: {exc}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'runserver':
            # parse: python manage.py runserver [--host HOST] [--port PORT] [--debug]
            args = sys.argv[2:]
            host = '127.0.0.1'
            port = 5000
            debug_flag = None
            # allow shorthand like host:port as single positional
            for a in args:
                if a.startswith('--'):
                    if a == '--debug':
                        debug_flag = True
                    elif a.startswith('--host='):
                        host = a.split('=', 1)[1]
                    elif a.startswith('--port='):
                        port = a.split('=', 1)[1]
                    elif a == '--no-debug':
                        debug_flag = False
                    # unknown flags ignored
                else:
                    # positional: allow HOST:PORT or PORT
                    if ':' in a:
                        h, p = a.split(':', 1)
                        host = h
                        port = p
                    else:
                        # if numeric, interpret as port
                        if a.isdigit():
                            port = a
                        else:
                            host = a

            runserver(host=host, port=port, debug=debug_flag)
        elif cmd == 'collectstatic':
            # Support: python manage.py collectstatic [dest_dir] [--fingerprint]
            args = sys.argv[2:]
            dest = None
            fingerprint = False
            for a in args:
                if a == '--fingerprint':
                    fingerprint = True
                elif a.startswith('--'):
                    # unknown flag - ignore for now
                    continue
                else:
                    # first non-flag argument is treated as destination
                    if dest is None:
                        dest = a

            collectstatic(dest, fingerprint=fingerprint)
        else:
            print('Usage: python manage.py [runserver|collectstatic [dest_dir]]')
    else:
        print('Usage: python manage.py [runserver|collectstatic [dest_dir]]')
