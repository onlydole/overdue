"""Helpers for reading submitted form values."""

from starlette.datastructures import FormData


def form_str(form: FormData, key: str, default: str = "") -> str:
    """Read a form field as a plain string.

    Starlette types form values as ``UploadFile | str``, because a client can
    submit a file part under any field name. Calling ``.strip()`` on the result
    would raise AttributeError for such a request, so anything that isn't a
    string falls back to ``default``.
    """
    value = form.get(key, default)
    return value if isinstance(value, str) else default
