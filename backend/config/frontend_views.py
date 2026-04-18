"""
Serves the vanilla JS frontend files directly from Django.

Because this project has no separate frontend server, Django acts as a
static file host for all HTML, CSS, and JS files living in backend/frontend/.

The URL router's catch-all pattern sends every non-API request here.
A path traversal check ensures a crafted URL like '../../etc/passwd' can
never escape the frontend directory.
"""
from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404
import mimetypes


def serve_frontend(request, path="index.html"):
    """
    Locate and stream a file from the backend/frontend/ directory.

    Falls back to index.html for the bare root URL ('/').
    Returns 404 for any path that doesn't exist or tries to escape the directory.
    The correct MIME type (text/html, text/css, application/javascript …) is
    inferred automatically from the file extension.
    """
    # Resolve the absolute path to the frontend folder
    base = (Path(settings.BASE_DIR) / "frontend").resolve()

    # Default to index.html for bare root request
    if not path or path == "/":
        path = "index.html"

    file_path = (base / path).resolve()

    # Security: reject any path that resolves outside the frontend folder
    # e.g. a request for '../../backend/config/settings.py'
    if not str(file_path).startswith(str(base)):
        raise Http404

    # If a directory is requested, look for an index.html inside it
    if file_path.is_dir():
        file_path = file_path / "index.html"

    if not file_path.exists():
        raise Http404

    # Let the browser know what kind of file it's receiving
    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(open(file_path, "rb"), content_type=content_type or "application/octet-stream")
