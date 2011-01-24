from . import app_settings

_render_method = None
def get_render_method():
    global _render_method

    if _render_method is None:
        _render_method = from_dotted_path(app_settings.EMAIL_RENDER_METHOD)

    return _render_method

_context_processors = None
def get_context_processors():
    global _context_processors

    if _context_processors is None:
        _context_processors = [
            from_dotted_path(x) for x in app_settings.EMAIL_CONTEXT_PROCESSORS
        ]

    return _context_processors

def from_dotted_path(fullpath):
    """
    Returns the specified attribute of a module, specified by a string.

    ``from_dotted_path('a.b.c.d')`` is roughly equivalent to::

        from a.b.c import d

    except that ``d`` is returned and not entered into the current namespace.
    """

    module, attr = fullpath.rsplit('.', 1)

    return getattr(__import__(module, {}, {}, (attr,)), attr)
