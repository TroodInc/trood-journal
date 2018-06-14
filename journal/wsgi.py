
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "journal.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

from configurations.wsgi import get_wsgi_application

application = get_wsgi_application()
