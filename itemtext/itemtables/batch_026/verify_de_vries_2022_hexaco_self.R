# verify_de_vries_2022_hexaco_self.R
#
# This table is BLOCKED on rights (hexaco.org's "free of charge, but only for the
# purpose of non-profit academic research" clause on the only published source of the
# HEXACO-PI-R item wording), so NO item text was shipped and there is no
# item_text<->item mapping to verify. What this script re-runs is the evidence recorded
# in verification_de_vries_2022_hexaco_self.csv, i.e. the facts about the code
# derivation that would have made the mapping inference-free had the wording been
# shippable, plus the check that separates this table from its meta-perception sibling:
#
#   1. The IRW item code IS the PLOS S1 Data .sav column name with the '_1' rater-slot
#      suffix stripped (data/de_vries_2022_hexaco.py). Set equality both ways, 96 codes.
#   2. Every live per-item mean reproduces its _1 (SELF) source column exactly, and NOT
#      the _3 (META-perception) column -- so this table is the self-report slot.
#   3. All 96 self columns carry zero SPSS variable labels and zero value labels, which
#      is why mapping_basis could not have been data_labels and why the wording would
#      have had to come from the NC-restricted hexaco.org form.
#
# It fetches its own data. irw_fetch() is used deliberately here: per-item means are
# needed for check 2 and irw_table_sets() does not supply them; the table is 41,664 rows.

suppressMessages({library(irw); library(haven)})

TABLE   <- "de_vries_2022_hexaco_self"
SI_URL  <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0272095.s007&type=supplementary"
CACHE   <- file.path("..", "..", ".cache", TABLE, "s007.sav")

if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(SI_URL, CACHE, mode = "wb", quiet = TRUE)
}
raw  <- haven::read_sav(CACHE)
nm   <- names(raw)
self <- grep("^P[OCAXEH][a-z]+[0-9]+_1$", nm, value = TRUE)
meta <- grep("^P[OCAXEH][a-z]+[0-9]+_3$", nm, value = TRUE)
cat(sprintf("source .sav: %d self (_1) columns, %d meta (_3) columns\n", length(self), length(meta)))

n_varlab <- sum(vapply(raw[self], function(x) !is.null(attr(x, "label")), logical(1)))
n_vallab <- sum(vapply(raw[self], function(x) length(attr(x, "labels")) > 0, logical(1)))
cat(sprintf("self columns carrying a variable label: %d/96 ; value labels: %d/96\n",
            n_varlab, n_vallab))

d    <- irw::irw_fetch(TABLE)
live <- tapply(d$resp, d$item, mean)
base <- sub("_1$", "", self)
cat(sprintf("live: %d rows, %d distinct items\n", nrow(d), length(live)))
cat(sprintf("codes in live but not in source: %d ; in source but not live: %d\n",
            length(setdiff(names(live), base)), length(setdiff(base, names(live)))))

sm <- vapply(self, function(c) mean(as.numeric(raw[[c]]), na.rm = TRUE), numeric(1))
mm <- vapply(meta, function(c) mean(as.numeric(raw[[c]]), na.rm = TRUE), numeric(1))
names(sm) <- base
names(mm) <- sub("_3$", "", meta)
common <- intersect(names(live), base)

cat(sprintf("\n%-10s %10s %10s %10s\n", "item", "live", "self(_1)", "meta(_3)"))
for (i in head(sort(common), 6))
    cat(sprintf("%-10s %10.4f %10.4f %10.4f\n", i, live[i], sm[i], mm[i]))

d_self <- max(abs(live[common] - sm[common]))
d_meta <- max(abs(live[common] - mm[common]))
cat(sprintf("\nmax |live - self(_1)| = %.6f over %d items\n", d_self, length(common)))
cat(sprintf("max |live - meta(_3)| = %.6f ; mean |diff| = %.4f\n",
            d_meta, mean(abs(live[common] - mm[common]))))

cat("Note: this establishes the code->source-column tie and the self-vs-meta slot only.\n",
    "It says NOTHING about item wording -- none was shipped, the table is blocked on the\n",
    "hexaco.org non-commercial clause -- and nothing about which published HEXACO item\n",
    "each facet code refers to.\n", sep = "")

ok <- length(self) == 96 && length(meta) == 96 &&
      length(setdiff(names(live), base)) == 0 && length(setdiff(base, names(live))) == 0 &&
      n_varlab == 0 && n_vallab == 0 &&
      d_self < 1e-9 && d_meta > 0.1
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
