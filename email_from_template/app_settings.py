from django.conf import settings

# Coffin users should use `coffin.template.loader.render_to_string`.
EMAIL_RENDER_METHOD = getattr(settings, 'EMAIL_RENDER_METHOD',
    'django.template.loader.render_to_string')

EMAIL_CONTEXT_PROCESSORS = getattr(settings, 'EMAIL_CONTEXT_PROCESSORS', (
    'email_from_template.context_processors.debug',
    'email_from_template.context_processors.django_settings',
))
