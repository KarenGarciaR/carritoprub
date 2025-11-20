#!/usr/bin/env python3
import os
import sys
import django
# Ensure project root is on sys.path so Django can be imported when running this script directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
try:
    django.setup()
except Exception as e:
    print('DJANGO SETUP ERROR:', e)
    raise

from store.models import Branch

candidates = []
for b in Branch.objects.all():
    lat = None
    lon = None
    try:
        lat = float(b.latitude) if b.latitude is not None else None
        lon = float(b.longitude) if b.longitude is not None else None
    except Exception:
        continue
    reason = None
    # Heurística: longitudes positivas en rango 10..100 con lat en rango México (14..33)
    if lon is not None and lon > 0 and 10 < lon < 100 and lat is not None and 14 <= lat <= 33:
        reason = 'negate_lon'
    # Valores fuera de rango
    elif lat is not None and abs(lat) > 90 or lon is not None and abs(lon) > 180:
        reason = 'out_of_range'
    # Tal vez están intercambiados (por ejemplo latitudes > 90)
    elif lat is not None and lon is not None and (abs(lat) <= 90 and abs(lon) <= 180) and (lat > 90 or lon > 90):
        reason = 'maybe_swapped'

    if reason:
        candidates.append({'id': b.id, 'name': b.name, 'lat': lat, 'lon': lon, 'reason': reason})

print('Total branches:', Branch.objects.count())
print('Candidates found:', len(candidates))
for c in candidates:
    print(c)

# Print suggestion summary
if candidates:
    print('\nSuggested automatic correction:')
    for c in candidates:
        if c['reason'] == 'negate_lon':
            print(f"Branch {c['id']} ('{c['name']}'): set longitude = -{c['lon']}")
        else:
            print(f"Branch {c['id']} ('{c['name']}'): reason={c['reason']} - review manually")
