def get_client_ip(request) -> str:
    # If you later add a reverse proxy, you can expand this to check X-Forwarded-For.
    return request.META.get("REMOTE_ADDR", "") if request else ""


def log_event(request, action: str, obj=None, object_type: str = "", metadata: dict | None = None):
    """
    Minimal audit logger. Call from API views after successful actions.
    """
    from .models import AuditLog  # local import avoids circular imports

    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        role = getattr(user, "role", "") or ""
        audit_user = user
    else:
        role = ""
        audit_user = None

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
