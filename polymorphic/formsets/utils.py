"""
Internal utils
"""
import django


def add_media(dest, media):
    """
    Optimized version of django.forms.Media.__add__() that doesn't create new objects.

    Only required for Django < 2.0
    """
    if django.VERSION >= (2, 0):
        combined = dest + media
        dest._css = combined._css
        dest._js = combined._js
    else:
        dest.add_css(media._css)
        dest.add_js(media._js)
