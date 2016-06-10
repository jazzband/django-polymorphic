"""
Internal utils
"""

def add_media(dest, media):
    """
    Optimized version of django.forms.Media.__add__() that doesn't create new objects.
    """
    dest.add_css(media._css)
    dest.add_js(media._js)
