# verify_test_taking_much_2025_cm.R -- Step 5b mapping check (batch_415).
#
# Claim: CMii_tt = the ii-th Current Motivation item (codebook: "Response to the
# <ii-th> item at <tt-th> measurement point"), and the ii-th item is row E<ii> of
# efcm_ItemOverview.pdf (https://osf.io/hnr93), whose Current Motivation column is
# the prospective rewording of the SAME TTMI Effort item as the Effort column
# (EF0ii). So each CM item has exactly one parallel Effort item sharing its wording.
#
# Falsifiable prediction: CMii measured right after a block (t2, t3) correlates
# more with its parallel retrospective Effort item EFii from that same block
# (EFii_01, EFii_02) than with any non-parallel Effort item -- strict diagonal
# dominance in every row AND column of the two 3x3 matrices. A permutation of CM
# text relative to the overview's rows breaks the diagonal.
#
# Data: both CM and EF come from live IRW (irw_fetch). An earlier version read EF
# from the OSF source file tte_data.csv, which OSF rate-limited (HTTP 429) at the
# batch_415 orchestrator re-run; the ef table is itself live, so the check no
# longer depends on OSF. (The agent also confirmed live CM == OSF CM cell for cell,
# n=1244 per item, at extraction time.)
#
# NOT established: this ties CM numbering to EF numbering. If CM and EF were BOTH
# permuted identically against the overview's rows, the diagonal would survive.
suppressMessages(library(irw))
TABLE <- "test_taking_much_2025_cm"

wide <- function(d) { w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar="id",
  timevar="item", direction="wide"); names(w) <- sub("^resp\\.", "", names(w)); w }
src <- merge(wide(irw::irw_fetch(TABLE)), wide(irw::irw_fetch("test_taking_much_2025_ef")), by = "id")
cat("merged n =", nrow(src), "\n")
ok_live <- nrow(src) > 0

# 2. diagonal dominance, CM (next block) x EF (just-completed block)
ok_diag <- TRUE
for (p in list(c("_02", "_01"), c("_03", "_02"))) {
  cm <- sapply(1:3, function(i) as.numeric(src[[sprintf("CM%02d%s", i, p[1])]]))
  ef <- sapply(1:3, function(i) as.numeric(src[[sprintf("EF%02d%s", i, p[2])]]))
  r <- cor(cm, ef, use = "pairwise")
  dimnames(r) <- list(sprintf("CM%02d%s", 1:3, p[1]), sprintf("EF%02d%s", 1:3, p[2]))
  print(round(r, 3))
  for (k in 1:3) {
    rowok <- all(r[k, k] > r[k, -k]); colok <- all(r[k, k] > r[-k, k])
    cat(sprintf("  diag %d: r=%.3f  row-max=%s col-max=%s\n", k, r[k, k], rowok, colok))
    ok_diag <- ok_diag && rowok && colok
  }
}
cat("Note: pins CM item k to EF item k (parallel wording); does not rule out an\n",
    "identical permutation of both scales against the item overview's rows.\n", sep = "")
cat(if (ok_live && ok_diag) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
