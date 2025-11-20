#!/usr/bin/env python3
import os
import sys
import argparse
# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
import django
django.setup()

from store.models import Branch

parser = argparse.ArgumentParser(description='Preview or apply coordinate fixes for Branch records')
parser.add_argument('--apply', action='store_true', help='Apply the suggested fixes')
parser.add_argument('--aggressive', action='store_true', help='Apply an aggressive rule: negate any longitude > 0')
parser.add_argument('--backup-file', type=str, default=None, help='Path to backup file (JSON). If omitted, auto-named file will be created.')
args = parser.parse_args()

candidates = []
for b in Branch.objects.all():
    try:
        lat = float(b.latitude) if b.latitude is not None else None
        lon = float(b.longitude) if b.longitude is not None else None
    except Exception:
        continue
    if lat is None or lon is None:
        continue
    # Heuristic: if longitude positive and likely within range of Mexico latitudes
    if lon > 0 and 10 < lon < 100 and 14 <= lat <= 33:
        candidates.append((b, 'negate_lon'))
    # Out of numeric range
    elif abs(lat) > 90 or abs(lon) > 180:
        candidates.append((b, 'out_of_range'))
    # Maybe swapped (rare): lat inside lon range and lon inside lat range swapped
    elif lat > 90 or lon > 90:
        candidates.append((b, 'maybe_swapped'))

print('Total branches:', Branch.objects.count())
print('Candidates found:', len(candidates))
if not candidates:
    sys.exit(0)

for b, reason in candidates:
    print(f"ID={b.id}, name='{b.name}', lat={b.latitude}, lon={b.longitude}, reason={reason}")

if not args.apply:
    print('\nRun with --apply to perform the suggested safe fixes (only negating longitude for reason=negate_lon).')
    sys.exit(0)

# Determine which candidates to modify based on mode
to_modify = []
if args.aggressive:
    # Aggressive: any branch with longitude > 0
    to_modify = [b for b in Branch.objects.all() if (b.longitude is not None and float(b.longitude) > 0)]
else:
    # Conservative: only those flagged as negate_lon in candidates
    to_modify = [b for b, reason in candidates if reason == 'negate_lon']

if not to_modify:
    print('\nNo rows matched the chosen modification rule. No changes applied.')
    sys.exit(0)

import json
from datetime import datetime

# Backup affected rows
backup_file = args.backup_file
if not backup_file:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'scripts/branch_coord_backup_{ts}.json'

backup_data = []
for b in to_modify:
    backup_data.append({'id': b.id, 'name': b.name, 'latitude': str(b.latitude), 'longitude': str(b.longitude)})

with open(backup_file, 'w', encoding='utf-8') as fh:
    json.dump({'generated_at': datetime.now().isoformat(), 'count': len(backup_data), 'rows': backup_data}, fh, ensure_ascii=False, indent=2)

print(f'Backup of {len(backup_data)} rows written to: {backup_file}')

# Apply changes: negate longitude for each row in to_modify
modified = []
for b in to_modify:
    try:
        old = float(b.longitude)
    except Exception:
        continue
    b.longitude = -old
    b.save()
    modified.append((b.id, b.name, old, b.longitude))

print('\nApplied changes:')
for m in modified:
    print(f'ID={m[0]}, name={m[1]}, old_lon={m[2]}, new_lon={m[3]}')

if not modified:
    print('No modifications were applied after processing (unexpected).')
