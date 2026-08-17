# heekerens2025_bfi_neuroticism — dictionary Description fix (not an itemtext change)

Issue: [ben-domingue/irw#1621](https://github.com/ben-domingue/irw/issues/1621)

**Scope note:** this is a fix to the IRW data dictionary's `Description` field
(produced by the `metadata/` pipeline / `irw-site-update` skill), not to the
itemtext content. `item_text` for this table is already correct — German
BFI-10 Neuroticism items (`NEUROTICISM_1_r`, `NEUROTICISM_2`) — and needs no
change.

**Current (wrong) Description:**
> Assesses openness to experience, imagination, and curiosity using the 2-item Openness subscale of the German BFI-10

**Corrected Description:**
> Assesses neuroticism/emotional stability using the 2-item Neuroticism subscale of the German BFI-10

No itemtext CSV was produced for this table since no itemtext content
changes. Whoever next runs the metadata/dictionary pipeline should apply the
corrected Description text above for `heekerens2025_bfi_neuroticism`.
