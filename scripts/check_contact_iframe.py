import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ecommerce.settings')
import django
django.setup()
from django.test import Client
c = Client()
resp = c.get('/contacto/')
text = resp.content.decode('utf-8')
start = text.find('iframe')
if start!=-1:
    i = text.find('src="', start)
    if i!=-1:
        j = text.find('"', i+5)
        src = text[i+5:j]
        print('IFRAME SRC:', src)
    else:
        print('iframe tag present but no src attribute found')
else:
    print('No iframe found in rendered contacto page')
