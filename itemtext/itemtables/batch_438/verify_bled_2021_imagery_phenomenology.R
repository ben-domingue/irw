# verify_bled_2021_imagery_phenomenology.R -- Step 5b check, batch_438.
#
# Claim: item codes are the S1 Data column names (self-describing), and on the
# option axis resp 3 = the "positive" pole of every item: detailed (pheno_detail),
# persistent (pheno_duration), always (pheno_manipulation). For pheno_detail this
# OVERRIDES the S1 CSV header, which reads "[1=detailed; 2=detailed/blurry; 3=blurry]".
#
# Falsifiable prediction: Bled et al. (2021, PLOS ONE 10.1371/journal.pone.0255039),
# Results section 2, report % autistic vs % control reporting
#   detailed images 66.7 vs 43.8; persistent 35.9 vs 20; always manipulate 56.4 vs 46.3.
# Each published pair must be reproduced by resp == 3 of its own item and by no other
# (item, level) cell. Group: cov_group 1 = autism, 0 = control.
#
# Does NOT establish: the order of levels 1 vs 2 within an item (the paper pools the
# two non-positive answers). That rests on the S1 header's middle label (2 = the mixed
# answer for all three items), which a pure endpoint reversal leaves in place.

suppressMessages(library(irw))
TABLE <- "bled_2021_imagery_phenomenology"
PUB <- list(pheno_detail = c(66.7, 43.8), pheno_duration = c(35.9, 20.0),
            pheno_manipulation = c(56.4, 46.3))
TOL <- 0.06  # published values are rounded to 1 dp (46.25 prints as 46.3)

d <- irw::irw_fetch(TABLE)
pct <- function(it, lv, g) { s <- d[d$item == it & d$cov_group == g, ]; 100 * mean(s$resp == lv) }

cat(sprintf("%-20s %4s %9s %9s\n", "item", "resp", "autism%", "control%"))
cells <- expand.grid(item = names(PUB), lv = 1:3, stringsAsFactors = FALSE)
cells$aut <- mapply(pct, cells$item, cells$lv, 1)
cells$con <- mapply(pct, cells$item, cells$lv, 0)
for (i in seq_len(nrow(cells)))
  cat(sprintf("%-20s %4d %9.2f %9.2f\n", cells$item[i], cells$lv[i], cells$aut[i], cells$con[i]))

ok <- TRUE
cat("\nPublished pair -> matching (item, resp) cells:\n")
for (it in names(PUB)) {
  p <- PUB[[it]]
  hit <- cells[abs(cells$aut - p[1]) <= TOL & abs(cells$con - p[2]) <= TOL, ]
  cat(sprintf("  %-20s published %.1f / %.1f -> %s\n", it, p[1], p[2],
              if (nrow(hit)) paste0(hit$item, "=", hit$lv, collapse = ", ") else "NONE"))
  if (!(nrow(hit) == 1 && hit$item == it && hit$lv == 3)) ok <- FALSE
}
cat(sprintf("\npheno_detail under the S1 header coding (1=detailed): %.1f / %.1f vs published 66.7 / 43.8\n",
            pct("pheno_detail", 1, 1), pct("pheno_detail", 1, 0)))
cat("Not established: level 1 vs level 2 order within items (paper pools them).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
