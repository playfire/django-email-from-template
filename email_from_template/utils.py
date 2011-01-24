from django.utils.functional import memoize

from . import app_settings

def get_render_method():
    return from_dotted_path(app_settings.EMAIL_RENDER_METHOD)
get_render_method = memoize(get_render_method, {}, 0)

def get_context_processors():
    return [from_dotted_path(x) for x in app_settings.EMAIL_CONTEXT_PROCESSORS]
get_context_processors = memoize(get_context_processors, {}, 0)

def from_dotted_path(fullpath):
    """
    Returns the specified attribute of a module, specified by a string.

    ``from_dotted_path('a.b.c.d')`` is roughly equivalent to::

        from a.b.c import d

    except that ``d`` is returned and not entered into the current namespace.
    """

    module, attr = fullpath.rsplit('.', 1)

    return getattr(__import__(module, {}, {}, (attr,)), attr)
