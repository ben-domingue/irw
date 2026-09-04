# concretewords — parked, NOT for upload (batch_016, 2026-09-03)

`concretewords__items.PARKED.csv` (9155 rows = 1831 items x 5 resp) was built and
gated but deliberately **not** promoted to `itemtables/batch_016/`.

Reason: the IRW `item` axis is the **rater**, not the rated expression.
`data/concretewords.R` sets `item <- x$Participant` and `id <- x$Expression`, and all
1831 live item values match the Qualtrics ResponseID pattern `^R_[A-Za-z0-9]{15,17}$`
with zero containing a space — impossible for a corpus of 62,000 English *multiword*
expressions. So `item_text` is blank for every row and no future pass can fill it: an
anonymous respondent ID has no stem.

What the file does carry, all of it identical across the 1831 items:
- `instructions` — verbatim from OSF `ksypa` / *Multiword expression rating instructions
  Final.docx* (the only file at that node's root).
- `option_text` — `1 = Abstract (language based)`, `5 = Concrete (experience based)`;
  2–4 are unlabelled in the source and are left blank, not padded with their own number.
- `instrument` — Muraki, Abdalla, Brysbaert & Pexman (2023), *Behavior Research Methods*
  55(5):2522–2531.

By the #1770 test ("does a row we ship carry the item's referent?") the answer is no for
every row, so shipping it would make `concretewords` count as "has item text" in the
corpus figures while carrying no item-level information at all.

Also of note: the source's rating scale had a sixth option, "I don't know the meaning of
this expression"; `data/concretewords.R` drops it (`x$Rating %in% 1:5`, plus `x$Filter==1`).

See `itemtables/batch_016/notes_concretewords.csv` and `verify_concretewords.R`.
