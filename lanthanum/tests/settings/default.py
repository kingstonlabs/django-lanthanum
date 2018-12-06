# Database

SECRET_KEY = 'SECRET'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
    }
}

INSTALLED_APPS = (
    'lanthanum',
    'lanthanum.tests.mock_app'
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True
    },
]
