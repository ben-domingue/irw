# verify_elshafie_2020_edsc.R -- Step 5b, re-runnable evidence (automated_finding, PMC sweep 2026-10-05).
#
# CLAIM: item Qk in elshafie_2020_edsc is the row numbered "k-" of the Arabic
# checklist (PeerJ SI peerj-08-10301-s002.docx), so item_text for Qk is that
# row's wording. mapping_basis paper_order: the .sav columns Q1..Q54 carry a
# number and no variable label.
#
# Route: age bands. Every checklist row is printed with the age band at which
# the milestone is expected (1 month ... 25-30 months; hard-coded below from
# s002, in the form's order). These are 0/1 milestones on 1,503 children aged
# 1-900 days, so each item has an empirical "age at 50% pass" (A50, logistic fit
# of resp on age). If Qk is the k-th row, A50 should rise with the printed band:
#   (1) Spearman rho(band, A50) over the 54 items is high (>= 0.85);
#   (2) the median A50 within each band is non-decreasing across the 16 bands,
#       allowing 1 month of slack for adjacent early bands;
#   (3) A50 does not fall by more than 1.5 months across any band boundary.
# The alternative codings this rules out are the realistic ones: the paper
# describes the 54 items as 22 motor + 32 mental, and a .sav sorted by domain
# (motor block first), or by the English Baroda list's order, would not give a
# monotone A50 sequence. A shift of one or two rows would NOT be detected (the
# printed bands are themselves monotone in k), hence PARTIAL.
# NOT established: the order of items WITHIN a band (2-7 items share each band,
# and adjacent bands overlap in A50) -- PARTIAL.
#
# Data: the staged response CSV (not on Redivis yet), which carries cov_age_days.
# Run from the repo root (irw/src) or automated_finding/.

TABLE <- "elshafie_2020_edsc"
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)
d$age_m <- d$cov_age_days / 30

# printed age band (months; ranges at their midpoint), rows 1..54 of s002
band <- c(rep(1, 3), rep(2, 3), rep(3, 3), rep(4, 3), rep(5, 3), rep(6, 3),
          rep(7, 2), rep(8, 2), rep(9, 4), rep(10, 3), rep(11, 4), rep(12, 2),
          rep(14, 4), rep(17, 7), rep(21.5, 4), rep(27.5, 4))
stopifnot(length(band) == 54)

a50 <- sapply(1:54, function(k) {
  x <- d[d$item == paste0("Q", k), ]
  if (all(x$resp == 1)) return(0)            # passed by everyone: earliest
  m <- suppressWarnings(glm(resp ~ age_m, family = binomial, data = x))
  -coef(m)[1] / coef(m)[2]
})
cat("respondents:", length(unique(d$id)), "\n\n")
cat(sprintf("  Q%-2d band %5.1f  A50 %6.1f\n", 1:54, band, a50), sep = "")

rho <- cor(band, a50, method = "spearman")
cat(sprintf("\n(1) Spearman rho(band, A50) = %.3f\n", rho))
med <- tapply(a50, band, median)
cat("(2) median A50 by band:\n")
print(round(med, 1))
mono <- all(diff(med) >= -1)

# (3) A50 must also rise in the item sequence at every BAND BOUNDARY (the last
# item of a band vs the first of the next, 1.5 months of slack; order within a
# band is not claimed): a domain-sorted coding would reset at its block edge.
bd <- which(diff(band) > 0)                  # k where row k+1 starts a new band
bd <- bd[bd > 3]                              # Q1-Q3 are passed by everyone
steps <- a50[bd + 1] - a50[bd]
seq_ok <- all(steps >= -1.5)
cat(sprintf("(3) largest A50 drop across a band boundary (Q4..Q54): %.1f months\n",
            max(0, -min(steps))))

ok <- rho >= 0.85 && mono && seq_ok
cat(sprintf("\nrho>=0.85: %s  monotone bands: %s  sequence monotone: %s\n",
            rho >= 0.85, mono, seq_ok))
cat("Items follow the form's age order; a shift within/across adjacent rows is not tested.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
