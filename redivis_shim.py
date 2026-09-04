"""Make full-table reads work again against redivis 0.20.11 + urllib3 2.x.

    import redivis_shim; redivis_shim.install()

Every whole-table read -- `table.to_arrow_table()`, `query(...).to_dataframe()`,
`irw_fetch`, anything that streams rows rather than aggregating -- currently
dies on this machine with

    OSError: Expected to be able to read 116432 bytes for message body, got 12110

regardless of table, size, shard or query. Aggregate queries are unaffected,
which is why the server-side measuring in `live_dup.py` and `live_cov_range.py`
kept working while nothing could be downloaded.

The cause is not Redivis and not the export allowance. `fetch_rows.py` hands
`requests`' undecoded `response.raw` straight to
`pyarrow.ipc.RecordBatchStreamReader`. Under urllib3 2.x that stream returns
*short reads* -- fewer bytes than asked for, with more still to come -- and
pyarrow's reader treats a short read as a truncated message instead of looping.
The bytes are all there: fetching the same read stream by hand returns the full
payload, ending in the end-of-stream sentinel.

Wrapping the stream in an `io.BufferedReader` restores the loop, because
`BufferedReader.read(n)` is defined to keep reading until it has n bytes or hits
EOF. Everything else about the client is left alone.

Remove this once redivis ships a version that buffers the stream itself.
"""
from __future__ import annotations

import io

_installed = False


def install() -> bool:
    """Patch pyarrow's stream reader to buffer its source. Idempotent."""
    global _installed
    if _installed:
        return False
    import pyarrow.ipc

    original = pyarrow.ipc.RecordBatchStreamReader

    class _BufferedRecordBatchStreamReader(original):
        def __init__(self, source, *args, **kwargs):
            if hasattr(source, "read") and not isinstance(
                    source, (io.BufferedReader, io.BytesIO)):
                try:
                    source = io.BufferedReader(source, buffer_size=1 << 20)
                except Exception:
                    pass          # not wrappable; let pyarrow have it as-is
            super().__init__(source, *args, **kwargs)

    pyarrow.ipc.RecordBatchStreamReader = _BufferedRecordBatchStreamReader
    _installed = True
    return True
