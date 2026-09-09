"""Clear uploaded __items.csv from the batch directories (#1956).

The bookkeeping in BATCH_PROCESS.md deletes a table's items CSV once the table
is uploaded, keeping every sidecar. Doing that by directory glob is how records
get destroyed, so this inverts the test the stamping uses: a file is deleted
ONLY when its batch's provenance row carries a real upload date. Anything else
-- an empty stamp, "unrecorded", or no provenance row at all -- is kept and
listed, whatever the directory listing looks like.

Run from itemtext/. Prints the split; pass --apply to git rm the delete set.
"""

import csv, glob, os, re, subprocess, sys
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


prov = {}
for f in sorted(glob.glob('itemtables/*/provenance.csv')):
    b = os.path.basename(os.path.dirname(f))
    for row in csv.DictReader(open(f)):
        prov[(b, row['table'])] = (row.get('uploaded') or '').strip()

delete, keep = [], []
for p in sorted(glob.glob('itemtables/*/*__items.csv')):
    b = os.path.basename(os.path.dirname(p))
    t = os.path.basename(p).replace('__items.csv', '')
    stamp = prov.get((b, t))
    if stamp is not None and DATE.match(stamp):
        delete.append((p, stamp))
    else:
        keep.append((p, 'no provenance row' if stamp is None else repr(stamp)))

print(f"KEEP ({len(keep)}) -- not provably uploaded:")
for p, why in keep:
    print(f"  {p}  [{why}]")
print(f"\nDELETE ({len(delete)}):")
for p, s in delete:
    print(f"  {p}  [uploaded={s}]")

if '--apply' in sys.argv:
    subprocess.run(['git', 'rm', '--quiet'] + [p for p, _ in delete], check=True)
    print(f"\nremoved {len(delete)} files")
