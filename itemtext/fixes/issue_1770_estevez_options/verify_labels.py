import hashlib, json, sys, urllib.request
import pyreadstat

CASES = [
    ("estevez_2021", "5156068", "BASE_DATOS_PERFILES.sav",
     "/tmp/zenodo_5156068_BASE_DATOS_PERFILES.sav"),
    ("chen_2024", "13855427", "2024929健身教练数据(Peerj).sav",
     "/tmp/zenodo_13855427.sav"),
]

for name, rec, fname, path in CASES:
    print("=" * 70)
    print(name, "|", path)
    raw = open(path, "rb").read()
    md5 = hashlib.md5(raw).hexdigest()
    try:
        import requests
        api = requests.get(f"https://zenodo.org/api/records/{rec}", timeout=60).json()
        entry = [f for f in api["files"] if f["key"] == fname]
        remote = entry[0]["checksum"] if entry else "FILE KEY NOT FOUND: " + str([f["key"] for f in api["files"]])
    except Exception as e:
        remote = f"UNAVAILABLE ({type(e).__name__}: {e})"
    print(f"  local md5   : {md5}  ({len(raw)} bytes)")
    print(f"  zenodo cksum: {remote}")
    print(f"  MATCH       : {remote.endswith(md5)}")

    df, meta = pyreadstat.read_sav(path)
    print(f"  columns: {len(meta.column_names)}   rows: {len(df)}")
    varlab = {k: v for k, v in meta.column_names_to_labels.items()
              if v is not None and str(v).strip() != ""}
    print(f"  --- non-empty VARIABLE labels: {len(varlab)}")
    for k, v in varlab.items():
        print(f"      {k!r}: {v!r}")
    vvl = meta.variable_value_labels
    print(f"  --- columns with VALUE labels: {len(vvl)}")
    for k, v in vvl.items():
        print(f"      {k!r}: {v!r}")
    print(f"  --- value_labels sets defined in file: {len(meta.value_labels)}")
    for k, v in meta.value_labels.items():
        print(f"      {k!r}: {v!r}")
    other = {k: getattr(meta, k, None) for k in
             ("notes", "file_label", "table_name")}
    print("  --- other:", other)
