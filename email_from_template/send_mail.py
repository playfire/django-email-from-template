from django.conf import settings
from django.template import Context
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives

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

    def render(component, fail_silently=False):
        txt = render_fn(template, {
            'email_from_template': 'email_from_template/%s.email' % component,
        }, context).strip()

        if not fail_silently:
            assert txt, "Refusing to send mail with empty %s - did you forget to" \
                " add a {%% block %s %%} to %s?" % (component, component, template)

        return txt

    connection = kwargs.get('connection', get_connection(
        username=kwargs.get('auth_user', None),
        password=kwargs.get('auth_password', None),
        fail_silently=kwargs.get('fail_silently', False),
    ))

    mail = EmailMultiAlternatives(
        render('subject'),
        render('body'),
        from_email,
        recipient_list,
        *args,
        **kwargs
    )

    html_message = render('html', fail_silently=True)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()
