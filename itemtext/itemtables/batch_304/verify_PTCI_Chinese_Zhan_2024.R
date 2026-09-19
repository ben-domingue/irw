# Verification for PTCI_Chinese_Zhan_2024 (#2228, batch_304).
#
# THE ITEM CODES ARE RENUMBERED, so the whole question is whether the shipped
# renumbering is right. SOURCES: the deposit's README.txt (osf.io/tj8rh, CC BY)
# states the rule -- original items 13, 32 and 34 were dropped as experimental
# and the remaining 33 renumbered in order -- and Foa et al. (1999) Appendix B
# gives the subscale each ORIGINAL item belongs to.
#
# Route 1: apply the README's rule and predict, for each renumbered code, which
#   subscale it should carry. Compare against the .sav's own variable labels,
#   which record exactly that and nothing else. 33 independent checks.
# Route 2: the nine codes the .sav prefixes 'b-' should be nine, i.e. the
#   PTCI-9 brief form the paper introduces.
# Route 3: shipped item_text is Foa et al.'s Appendix A wording for the
#   ORIGINAL number that maps to each code.
sav <- ".cache/batch_304/PTCI_data.sav"
rme <- ".cache/batch_304/ptci_README.txt"
for (p in c(sav, rme)) if (!file.exists(p)) stop("missing cached deposit file: ", p)
if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven")

d <- as.data.frame(irw::irw_fetch("PTCI_Chinese_Zhan_2024"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_304/PTCI_Chinese_Zhan_2024__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
s <- haven::read_sav(sav)

SELF  <- c(2,3,4,5,6,9,12,14,16,17,20,21,24,25,26,28,29,30,33,35,36)
WORLD <- c(7,8,10,11,18,23,27)
BLAME <- c(1,15,19,22,31)
DROP  <- c(13, 32, 34)
orig  <- setdiff(1:36, DROP)
stopifnot(length(orig) == 33, setequal(c(SELF, WORLD, BLAME), orig))
newcode <- setNames(seq_along(orig), orig)     # the README's rule
sub_of  <- function(o) if (o %in% SELF) "self" else if (o %in% WORLD) "world" else "blame"

cat("=== Route 1: predicted subscale vs the .sav's variable labels ===\n")
rl <- readLines(rme, warn = FALSE)
cat(sprintf("  README states the dropped items are: %s\n",
            paste(DROP, collapse = ", ")))
cat(sprintf("  README text confirms: %s\n",
            grepl("item 13, item 32, and item 34", paste(rl, collapse = " "), fixed = TRUE)))
ok <- logical(0)
for (o in orig) {
    n <- newcode[[as.character(o)]]
    lab <- trimws(attr(s[[sprintf("ptci%d", n)]], "label"))
    got <- sub("^b-", "", lab)
    ok  <- c(ok, got == sub_of(o))
    cat(sprintf("  orig %2d -> ptci%-2d  predicted %-5s  .sav label %-8s %s\n",
                o, n, sub_of(o), lab, if (tail(ok, 1)) "" else "   <-- MISMATCH"))
}
r1 <- all(ok)
cat(sprintf("  -> %d of 33 agree: %s\n", sum(ok), r1))
cat("  A wrong renumbering would put at least one code in the wrong subscale;\n")
cat("  the three dropped items are precisely the three Foa et al. exclude.\n")

cat("\n=== Route 2: the 'b-' prefix is the brief form ===\n")
brief <- grep("^b-", sapply(sprintf("ptci%d", 1:33), function(c) trimws(attr(s[[c]], "label"))))
cat(sprintf("  codes labelled 'b-...': %s\n", paste(sprintf("ptci%d", brief), collapse = ", ")))
r2 <- length(brief) == 9
cat(sprintf("  -> exactly nine, matching the PTCI-9 the paper introduces: %s\n", r2))

cat("\n=== Route 3: the wording follows the mapping ===\n")
sh <- unique(items[, c("item", "section_prompt", "item_text")])
n_from_prompt <- as.integer(sub(".*original item ([0-9]+);.*", "\\1", sh$section_prompt))
names(n_from_prompt) <- sh$item
r3 <- all(sapply(orig, function(o)
    n_from_prompt[[sprintf("ptci%d", newcode[[as.character(o)]])]] == o)) &&
      setequal(sprintf("ptci%d", 1:33), unique(d$item)) &&
      length(unique(sh$item_text)) == 33
cat(sprintf("  every shipped section_prompt names the original number the\n"))
cat(sprintf("  README's rule gives, and all 33 item_texts are distinct: %s\n", r3))
for (o in c(1, 12, 14, 33, 35, 36))
    cat(sprintf("    orig %2d -> ptci%-2d  %s\n", o, newcode[[as.character(o)]],
                substr(sh$item_text[sh$item == sprintf("ptci%d", newcode[[as.character(o)]])], 1, 58)))

cat("\n=== What this does NOT establish ===\n")
cat("  The administered Chinese. Neither the deposit nor the paper's\n")
cat("  supplements carry it, so Foa et al.'s English ships in the base fields\n")
cat("  with language=Chinese -- the documented fallback.\n")
cat("  Also noted: the README's own mapping table has a typo, line 32 reading\n")
cat("  'ptci35 -> ptci21' where the sequence requires ptci32; ptci21 is\n")
cat("  already taken by original item 22 two lines earlier.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
