#!/usr/bin/env python3
"""Item text for rogers_2026_bees_feedback (figshare 29874713). The five variable labels share one lead-in
("Filling out the Brief Emotional Wellbeing Survey over the course of term helped me:"), shipped once as
`instructions`; the item_text is the remainder. Anchors = value labels. English administration."""
from _itemtext_writer_c import load_script, row, write

mod = load_script("rogers_2026_bees_feedback")
LEAD = "Filling out the Brief Emotional Wellbeing Survey over the course of term helped me:"


def main():
    labels, vlabels = mod.labels()
    table = "rogers_2026_bees_feedback"
    rows = []
    for c in mod.ITEMS:
        lab = labels[c].strip()
        assert lab.startswith(LEAD), lab
        stem = lab[len(LEAD):].strip()
        for r, opt in sorted(vlabels[c].items()):
            rows.append(row(table, f"{table}_1", c, "Feedback on term-long mood monitoring with the BEES, 5 items", "",
                            int(r), stem, option_text=opt, instructions=LEAD))
    write(table, rows)


if __name__ == "__main__":
    main()
