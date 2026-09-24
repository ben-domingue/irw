"""Write a CSV the way R's write.csv wrote this one, so a rewrite touches
only the content that changed.

These tables come from R: it quotes CHARACTER columns and leaves numeric
columns and NA bare. Python's csv writer has no dialect that reproduces that
-- QUOTE_MINIMAL drops quotes R keeps, QUOTE_ALL adds quotes R omits -- and
either one rewrites every line of every file it touches. A three-cell fix
once became a 24,000-line diff across 48 files that way.

Crucially the decision is per COLUMN, not per value: option_text is a
character column, so R quotes "4" there while leaving resp's 4 bare. So the
dialect is read back off the file rather than guessed.
"""
import csv


def quoted_columns(path):
    """Indices of columns R quoted, inferred from the file itself."""
    quoted = set()
    with open(path, encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh))
    ncol = len(header)
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    # Skip the header line. R quotes EVERY column name, so scanning it would
    # mark every column as a character column and re-quote the numeric ones.
    raw = raw[raw.index("\n") + 1:]
    # walk the raw text field by field, tracking quotes
    i, col, inq, fresh, n = 0, 0, False, True, len(raw)
    while i < n:
        c = raw[i]
        if fresh and c == '"':
            quoted.add(col)
            inq = True; fresh = False; i += 1
            continue
        fresh = False
        if inq:
            if c == '"':
                if i + 1 < n and raw[i + 1] == '"':
                    i += 2; continue
                inq = False
            i += 1
            continue
        if c == ',':
            col += 1; fresh = True
        elif c == '\n':
            col = 0; fresh = True
        i += 1
    return {c for c in quoted if c < ncol}


def write_r_csv(path, cols, rows, quoted):
    def f(v, idx):
        v = "" if v is None else v
        if idx in quoted and v != "NA":
            return '"' + v.replace('"', '""') + '"'
        return v
    with open(path, "w", encoding="utf-8", newline="") as fh:
        # R quotes EVERY column name, whatever the column's type.
        fh.write(",".join('"' + c.replace('"', '""') + '"' for c in cols) + "\n")
        for r in rows:
            fh.write(",".join(f(r.get(c, ""), i) for i, c in enumerate(cols)) + "\n")
