# verify_cucchi_2018_scoff.R
#
# mapping_basis = data_labels, so the item_text <-> item axis needs no statistical
# route: the IRW item codes SCOFF1..SCOFF5 ARE the .sav column names
# (data/cucchi_2018_rfq.py melts them unchanged), and each column's SPSS variable
# label carries its own wording prefixed with its own code
# ("SCOFF1: Do you make yourself sick because you feel uncomfortably full?").
# A permutation is impossible without being self-evident.
#
# What this script checks is the OTHER axis -- option_text <-> resp. The
# processing script remaps the .sav's 1=YES / 2=NO coding to 1/0, so the shipped
# anchors depend on that remap being the direction actually stored. Two checks:
#
#   (a) The .sav carries its own SCOFF total score column. SCOFF is scored as the
#       COUNT OF YES ANSWERS (Morgan, Reid & Lacey 1999; the paper: "indicates the
#       possible presence of an eating disorder when more than 2 yes responses are
#       given"). Recoding YES->1 must reproduce that total; recoding NO->1 must not.
#   (b) Per-item non-missing counts in the .sav must equal the live per-item n
#       from irw::irw_table_sets() -- confirming the live table is these columns.
#
# This does NOT re-check item or resp SETS; validate_items.R did that.

suppressMessages({library(irw); library(haven)})

TABLE <- "cucchi_2018_scoff"
SUPPL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6211265/supplementaryFiles"
MEMBER <- "peerj-06-5756-s003.sav"

zf <- tempfile(fileext = ".zip"); sav <- tempfile(fileext = ".sav")
download.file(SUPPL, zf, quiet = TRUE, headers = c("User-Agent" = "IRW-Finder/1.0"))
writeBin(unzip(zf, MEMBER, exdir = tempdir()) |> readBin(what = "raw", n = 1e8), sav)
d <- haven::read_sav(sav)

its <- paste0("SCOFF", 1:5)
raw <- as.data.frame(lapply(d[its], as.numeric))

yes1 <- rowSums(replace(raw, raw == 2, 0))                       # YES=1, NO=0 (shipped)
no1  <- rowSums(replace(replace(raw, raw == 1, 0), raw == 2, 1))  # flipped
score <- as.numeric(d$SCOFF)
ok <- !is.na(score) & complete.cases(raw)

cat("(a) reconstruct the .sav's own SCOFF total score, n =", sum(ok), "\n")
cat(sprintf("    YES=1 (shipped)  agrees on %d / %d\n", sum(score[ok] == yes1[ok]), sum(ok)))
cat(sprintf("    NO=1  (flipped)  agrees on %d / %d\n", sum(score[ok] == no1[ok]),  sum(ok)))

cat("\n(b) per-item n, .sav non-missing vs live irw_table_sets()\n")
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live <- setNames(as.numeric(pi$n), pi$item)[its]
src  <- colSums(!is.na(raw))
cat(sprintf("%-8s %8s %8s\n", "item", ".sav", "live"))
for (i in its) cat(sprintf("%-8s %8d %8d\n", i, src[[i]], live[[i]]))

pass_a <- sum(score[ok] == yes1[ok]) == sum(ok) && sum(score[ok] == no1[ok]) == 0
pass_b <- all(src[its] == live[its])

cat("\nNote: this pins the option_text<->resp direction (YES=1, NO=0) and confirms the\n",
    "live table is these five .sav columns. It establishes nothing about item_text<->item\n",
    "ordering, which needs nothing: the codes are the source column names and each\n",
    "variable label is self-identifying.\n", sep = "")

cat(if (pass_a && pass_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
