from django.conf import settings

def debug():
    return {'debug': settings.DEBUG}

def site():
    from django.contrib.sites.models import Site
    return {'site': Site.objects.get_current()}

def django_settings():
    return {'settings': settings}

def i18n():
    from django.utils import translation

    return {
        'LANGUAGES': settings.LANGUAGES,
        'LANGUAGE_CODE': translation.get_language(),
        'LANGUAGE_BIDI': translation.get_language_bidi(),
    }
