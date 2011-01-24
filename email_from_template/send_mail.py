from django.conf import settings
from django.template import Context
from django.core.mail import send_mail as django_send_mail

from .utils import get_render_method, get_context_processors

def send_mail(recipient_list, template, context=None, from_email=None, *args, **kwargs):
    """
    Wrapper around ``django.core.mail.send_mail`` that generates the subject
    and message body from a template.

    Usage::

        >>> from email_from_template import send_mail
        >>> send_mail([user.email], 'path/to/my_email.email', {
            'a': 1,
            'user': user,
        })

    path/to/my_email.email::

        {% extends email_from_template %}

        {% block subject %}
        Hi {{ user.username }}
        {% endblock %}

        {% block body %}
        Hi {{ user.username }}.
        Did you know that a = {{ a }} ?
        {% endblock %}
    """

    context = Context(context)
    for fn in get_context_processors():
        context.update(fn())

    render_fn = get_render_method()

    def render(component):
        txt = render_fn(template, {
            'email_from_template': 'email_from_template/%s.email' % component,
        }, context).strip()

        assert txt, "Refusing to send mail with empty %s - did you forget to" \
            " add a {%% block %s %%} to %s?" % (component, component, template)

        return txt

    return django_send_mail(
        render('subject'),
        render('body'),
        from_email,
        recipient_list,
        *args,
        **kwargs
    )
