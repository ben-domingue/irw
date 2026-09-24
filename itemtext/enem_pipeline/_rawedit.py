"""Edit one field value in place without reformatting the file.

These CSVs are written by R: character columns quoted, numbers and NA bare.
Python's csv writer cannot reproduce that, so a read-modify-write round trip
rewrites all ~1000 lines of every file it touches -- 24,000 spurious diff
lines across 48 files, hiding the eight that matter.

So: locate with csv, edit the raw bytes. A stem is hundreds of characters and
shared by exactly the item's five rows, which makes the whole old value a
unique, unambiguous anchor. Only the quote doubling inside a quoted field has
to be accounted for.
"""


def _field(v):
    return v.replace('"', '""')


def rewrite_field(path, old, new, expect=None):
    """Replace every occurrence of field value `old` with `new`. Returns count."""
    if old == new:
        return 0
    raw = open(path, encoding="utf-8").read()
    o, n = _field(old), _field(new)
    c = raw.count(o)
    if c == 0:
        raise AssertionError(f"{path}: old value not found verbatim")
    if expect is not None and c != expect:
        raise AssertionError(f"{path}: expected {expect} occurrences, found {c}")
    open(path, "w", encoding="utf-8").write(raw.replace(o, n))
    return c
