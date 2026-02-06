"""
Internal utils
"""

from django.forms import Media


def add_media(dest: Media, media: Media) -> None:
    """
    Optimized version of django.forms.Media.__add__() that doesn't create new objects.
    """
    dest._css_lists.extend(media._css_lists)  # type: ignore[attr-defined]
    dest._js_lists.extend(media._js_lists)  # type: ignore[attr-defined]
