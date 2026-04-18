"""
Helper utilities for writing to the audit log.

Usage — call log_event() from any API view after a successful action:

    log_event(
        request,
        action="APPOINTMENT_CREATE",
        obj=appt,                      # the model instance that was affected
        object_type="appointment",     # optional — inferred from obj.__class__ if omitted
        metadata={"status": appt.status},  # any extra JSON context
    )

The AuditLog model import is deferred to inside log_event() to avoid
circular imports (models importing from utils, utils importing from models).
"""


def get_client_ip(request) -> str:
    """
    Extract the client's IP address from the Django request object.

    Uses REMOTE_ADDR which is the direct connection IP.  If this app is
    later put behind a reverse proxy (nginx, etc.), expand this to check
    the X-Forwarded-For header instead.
    """
    return request.META.get("REMOTE_ADDR", "") if request else ""


def log_event(request, action: str, obj=None, object_type: str = "", metadata: dict | None = None):
    """
    Write one audit log entry for a completed action.

    Parameters:
      request      – the Django HTTP request (used to get user + IP)
      action       – short ALL_CAPS string describing what happened
      obj          – the model instance that was affected (optional)
      object_type  – human-readable type name; inferred from obj class if blank
      metadata     – any extra data worth recording as JSON
    """
    from .models import AuditLog  # local import to break the circular dependency

    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        role = getattr(user, "role", "") or ""
        audit_user = user
    else:
        # Unauthenticated action (e.g. a failed login attempt logged separately)
        role = ""
        audit_user = None

    # Derive the object's id and type from the model instance
    if obj is not None:
        object_id = getattr(obj, "id", None)
        if not object_type:
            object_type = obj.__class__.__name__.lower()
    else:
        object_id = None

    AuditLog.objects.create(
        user=audit_user,
        role=role,
        action=action,
        object_type=object_type or "",
        object_id=object_id,
        metadata=metadata or {},
        ip_address=get_client_ip(request),
    )
