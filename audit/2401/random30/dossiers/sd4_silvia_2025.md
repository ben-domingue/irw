# sd4_silvia_2025 (slot 5, agent a)

**Current state.** Live in `item_response_warehouse_2` (v26_0), 14,840 rows = 530 x 28, matching metadata. No item text. It appears in the 09-06/07 string-NA sweeps: live resp is now float, so that is already remedied. 44 NA resp, scattered.

**Data (full read).** All 28 SD4 items (mach/narc/psyc/sadi x 7) are 1-5, with no sentinels and no dup id+item. `cov_age` 18-95, `cov_gender` Male/Female, `cov_edu` 0-5. Upload profile: conforms, passes. The warnings (resp_na, column_order, `imputed_values` on sd4_psyc_3 with 61% at 1, which is a normal floor on a dark-trait item) are all below the bar.

**Rights.** No item text is live. The `sd4_*` codes are opaque.

**Source caveat.** `data/shorttripm_hexaco_sd4_silvia_2025.R` keeps `dataset=="Vulgar_Humor"` from a pooled OSF file. The header states no defect, mean-fill or id fallback.

**Outcome.** Clean, `no_action` (high).
