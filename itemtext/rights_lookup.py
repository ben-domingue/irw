#!/usr/bin/env python3
"""Ask the rights register what has been ruled about one instrument, by name.

    python3 itemtext/rights_lookup.py MSLQ
    python3 itemtext/rights_lookup.py "need for cognition"

The gate (`irw_validate.rights`, on the upload profile) answers a different
question: does anything in this table match a register pattern? It can discover
a prohibition and never a permission, because a permission has no reason to
carry matchers. On 2026-10-18 that cost a correct table --
`hung_2026c_academic_self_efficacy` is a verbatim MSLQ self-efficacy subscale,
the MSLQ is registered `ship` (public domain, U-Michigan NCRIPTAL, citation
only) with a note saying adaptations ship too, and it was held anyway, because
the row's `^mslq` pattern cannot match codes ASE1-ASE8 and the row has no
`match_item_text` at all.

Step 3.5 of the irw-automated-finding skill requires checking the register BY
NAME once the stems have been read and the instrument identified. This is that
check, instead of a manual read of a 343-row CSV.

Lives beside the register it reads. The logic is `irw_validate/rights.py`;
this is only an entry point, so `python -m` need not re-import the package.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from irw_validate.rights import _cli  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(_cli())
