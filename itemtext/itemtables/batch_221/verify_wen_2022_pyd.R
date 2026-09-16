# Step 5b mapping verification for wen_2022_pyd.
#
# CLAIM: the 26 IRW item codes (compe1-4, confi1-7, character1-4, care1-5,
# connect1-6) correspond, in numeric order within each subscale, to the items
# listed in that subscale's block of Table 1 of Wen et al. 2022
# (PLOS ONE 17(7): e0270974, doi:10.1371/journal.pone.0270974).
#
# Table 1 prints a factor loading beside every item and no code. Those 26
# loadings are therefore the falsifiable prediction: they came from the paper's
# phase-1 (EFA) sample, which is the IRW table's cov_study == "s2" subsample
# (n = 471; Table 1's stated N = 472 is off by one). Reproducing them item by
# item, and then asking by exhaustive permutation search which OTHER within-
# subscale orderings would also fit, is what would break if two items' texts
# were swapped.
#
# This does NOT re-check item counts or the item/resp sets -- validate_items.R
# already did that, and a count is not evidence about a mapping.

suppressMessages(library(irw))

TABLE <- "wen_2022_pyd"
TOL   <- 0.01   # published loadings are rounded to 2 dp

SUBS <- list(
  compe     = c(0.69, 0.69, 0.79, 0.81),
  confi     = c(0.68, 0.71, 0.70, 0.72, 0.63, 0.76, 0.75),
  character = c(0.77, 0.76, 0.73, 0.69),
  care      = c(0.70, 0.72, 0.83, 0.80, 0.84),
  connect   = c(0.72, 0.73, 0.71, 0.68, 0.70, 0.75)
)

d <- irw::irw_fetch(TABLE)
d <- d[d$cov_study == "s2", ]
cat(sprintf("phase-1 (EFA) subsample cov_study=='s2': %d respondents, paper N = 472\n\n",
            length(unique(d$id))))

d <- as.data.frame(d)
wide <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
                direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))

perms <- function(v) {
  if (length(v) == 1) return(list(v))
  out <- list()
  for (i in seq_along(v))
    for (p in perms(v[-i])) out[[length(out) + 1]] <- c(v[i], p)
  out
}

ok_all <- TRUE
n_unique <- 0
for (s in names(SUBS)) {
  pub  <- SUBS[[s]]
  cols <- paste0(s, seq_along(pub))
  X    <- wide[, cols]
  X    <- X[complete.cases(X), ]
  # First unrotated common-factor loading, the quantity an EFA of a
  # one-dimensional subscale reports.
  C  <- cor(X)
  e  <- eigen(C)
  l  <- e$vectors[, 1] * sqrt(e$values[1])
  if (sum(l) < 0) l <- -l

  cat(sprintf("--- %s (n = %d)\n", s, nrow(X)))
  cat(sprintf("%-12s %10s %10s %8s\n", "item", "published", "observed", "diff"))
  for (i in seq_along(pub))
    cat(sprintf("%-12s %10.2f %10.3f %8.3f\n", cols[i], pub[i], l[i], l[i] - pub[i]))
  dev <- max(abs(l - pub))

  alt <- Filter(function(p) max(abs(l[p] - pub)) <= TOL, perms(seq_along(pub)))
  cat(sprintf("max deviation in code order: %.4f ; within-subscale orderings fitting <= %.2f: %d\n",
              dev, TOL, length(alt)))
  for (p in alt)
    if (!identical(p, seq_along(pub)))
      cat("   indistinguishable alternative: ", paste0(s, p, collapse = " "), "\n", sep = "")
  cat("\n")
  if (dev > TOL) ok_all <- FALSE
  # An item is pinned uniquely when it occupies the same position in EVERY
  # ordering that fits, not merely when the whole subscale has one solution.
  fixed <- sapply(seq_along(pub),
                  function(i) length(unique(sapply(alt, function(p) p[i]))) == 1)
  n_unique <- n_unique + sum(fixed)
}

cat(sprintf("items pinned uniquely by this route (same position in every fitting ordering): %d of 26\n", n_unique))
cat("Note: this route does NOT separate the three near-tied adjacent pairs\n",
    "compe1/compe2, confi2/confi3 and character1/character2, whose published\n",
    "loadings differ by <= 0.01. Those rest on the .sav variable labels, which\n",
    "carry the original questionnaire codes (compe1=P1Q5, compe2=P1Q6;\n",
    "confi2=P2Q4S02, confi3=P2Q4S03; character1=P2Q5S03, character2=P2Q5S04) --\n",
    "i.e. on Table 1 listing each subscale in ascending questionnaire order,\n",
    "which the uniquely-pinned care (S10-S14) and connect (S15-S18,S21,S22)\n",
    "blocks independently confirm.\n", sep = "")

cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
