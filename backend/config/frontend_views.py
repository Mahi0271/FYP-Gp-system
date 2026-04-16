from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404
import mimetypes


def serve_frontend(request, path="index.html"):
    """Serve static frontend files from backend/frontend/."""
    base = (Path(settings.BASE_DIR) / "frontend").resolve()

    # Default to index.html for bare root request
    if not path or path == "/":
        path = "index.html"

    file_path = (base / path).resolve()

    # Security: block path traversal
    if not str(file_path).startswith(str(base)):
        raise Http404

    if file_path.is_dir():
        file_path = file_path / "index.html"

    if not file_path.exists():
        raise Http404

    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(open(file_path, "rb"), content_type=content_type or "application/octet-stream")
