from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404
import mimetypes

def demo_frontend(request, path="index.html"):
    # Serve files from backend/frontend/
    base = Path(settings.BASE_DIR) / "frontend"
    file_path = (base / path).resolve()

    # Security: prevent ../ path traversal
    if not str(file_path).startswith(str(base.resolve())):
        raise Http404("Not found")

    if file_path.is_dir():
        file_path = file_path / "index.html"

    if not file_path.exists():
        raise Http404("Not found")

    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(open(file_path, "rb"), content_type=content_type or "application/octet-stream")
