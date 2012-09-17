"""
:mod:`django-email-from-template` --- send emails generated entirely from Django templates
===========================================================================================

``email_from_template`` generates and sends mail defined in Django templates to
avoid presentation layer violations. It has the following features:

 * HTML email support
 * Context processor system
 * Support for non-Django template rendering systems

Whilst Django  provides a comprehensive mail framework that simplifies the
sending mechanics of email, the typical use of it is often ugly and results in
unnecessary and complicated string formatting inside views::

    from django.core.mail import send_mail
    from django.core.urlresolvers import reverse
    from django.contrib.sites.models import Site

    # Shouldn't be in views.py
    send_mail(
        'Hi %s, %d %s written on your wall' % (
            user.username,
            num_posts > 1 and 'people have' or 'person has',
        ),
        'Hi %s\\n\\nCheck out what they wrote here:\\n\\n %s%s\\n\\n' % (
            user.username,
            Site.objects.get_current(),url,
            reverse('profile:view', args=(user.username,)),
        ),
        'from@example.com',
        [user.email],
        fail_silently=False,
    )

With :mod:`django-email-from-template`, you can relegate all this formatting to
the presentation layer as well as leverage any existing templatetags and
filters. First we define our template::

    {% extends email_from_template %}

    {% block subject %}
    Hi {{ user.username }}, {{ num_posts }} {{ num_posts|pluralize:"person has,people have" }} written on your wall
    {% endblock %}

    {% block body %}
    Hi {{ user.username }}.

    Check out what they wrote here:

      {{ site.url }}{% url profile:view user.username %}
    {% endblock %}

We then simply call our template-aware version of ``send_mail`` with the
appropriate context::

    from email_from_template import send_mail

    send_mail([user.email], 'path/to/my_email.email', {
        'user': user,
        'num_posts': num_posts,
    }, 'from@email.com')

Now your views are not cluttered with unnecessary presentation logic.

For HTML-enabled mail readers, we can optionally include suitable content
within a "html" block::

    {% block html %}
    <p>Hi <strong>{{ user.username }}</strong></p>
    <p>Check out what they wrote here:</p>
    <a href="{{ site.url }}{% url profile:view user.username %}">
        {{ site.url }}{% url profile:view user.username %}
    </a>
    {% endblock %}

Context processors
------------------

The ``EMAIL_CONTEXT_PROCESSORS`` setting is a tuple of callables that return a
dictionary of items to merged into the email context. It is identical to the
functionality of Django's regular ``TEMPLATE_CONTEXT_PROCESSORS`` support
except that the callables do not take a request object.

By default, ``EMAIL_CONTEXT_PROCESSORS`` is set to::

    (
        'email_from_template.context_processors.debug',
        'email_from_template.context_processors.django_settings',
    )

``debug``
~~~~~~~~~

Module: ``email_from_template.context_processors.debug``
Enabled by default: ``True``

Sets ``debug`` in the template context to the value of ``settings.DEBUG``::

    def debug():
        from django.conf import settings
        return {'debug': settings.DEBUG}

``django_settings``
~~~~~~~~~~~~~~~~~~~

Module: ``email_from_template.context_processors.django_settings``
Enabled by default: ``True``

Sets ``settings`` in the template context to the value of Django's settings
object, ``django.conf.settings``::

    def django_settings():
        from django.conf import settings
        return {'settings': settings}

``site``
~~~~~~~~

Module: ``email_from_template.context_processors.site``
Enabled by default: ``False``

Sets ``site`` in the template context to the value of the current
``django.contrib.sites`` ``Site`` instance::

    def site():
        from django.contrib.sites.models import Site
        return {'site': Site.objects.get_current()}


``i18n``
~~~~~~~~

Module: ``email_from_template.context_processors.i18n``
Enabled by default: ``False``

Includes ``LANGUAGES``, ``LANGUAGE_CODE`` and ``LANGUAGE_BIDI`` in the template
context. This email context processor is parallel to the
``django.core.context_processors.i18n`` template context processor::

    def i18n():
        from django.utils import translation
        return {
            'LANGUAGES': settings.LANGUAGES,
            'LANGUAGE_CODE': translation.get_language(),
            'LANGUAGE_BIDI': translation.get_language_bidi(),
        }

Configuration
-------------

``EMAIL_CONTEXT_PROCESSORS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A tuple of callables that return a dictionary of items to merged into the email
context. See the `Context processors` section for more details.

``EMAIL_RENDER_METHOD``
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``django.template.loader.render_to_string``

Method to use to actually render templates. If you are using the
`Coffin <github.com/cdleary/coffin>`_ Jinja2 adaptor for Django,
you should set this ``coffin.template.loader.render_to_string``.

Installation
------------

Add ``email_from_template`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'email_from_template',
        ...
    )

Links
-----

View/download code
  https://github.com/playfire/django-email-from-template

File a bug
  https://github.com/playfire/django-email-from-template/issues
"""

from django.conf import settings
from django.template import Context
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives

from .utils import get_render_method, get_context_processors

def send_mail(recipient_list, template, context=None, from_email=None, send_mail=True, *args, **kwargs):
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
        render('subject').split('\n')[0],
        render('body'),
        from_email,
        recipient_list,
        *args,
        **kwargs
    )

    html_message = render('html', fail_silently=True)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    if not send_mail:
        return mail

    return mail.send()

def mail_admins(template, context=None, from_email=None, *args, **kwargs):
    if from_email is None:
        from_email = settings.SERVER_EMAIL

    return send_mail(
        [x[1] for x in settings.ADMINS],
        template,
        context,
        from_email,
        *args,
        **kwargs
    )
