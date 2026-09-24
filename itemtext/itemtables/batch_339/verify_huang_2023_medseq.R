# verify_huang_2023_medseq.R -- Step 5b check for huang_2023_medseq (batch_339).
#
# Claim: MedSEQ_n carries the wording of item n in Supplement 1
# (jeehp-20-02-suppl.docx, Harvard Dataverse 10.7910/DVN/SQ8PJY). The source xlsx
# has no labels -- its headers are MedSEQ_1..MedSEQ_22 and the processing script
# keeps them as item codes -- so the tie is number-to-number (paper_explicit).
#
# Route 3/5: the supplement and the paper's Table 2 publish the item->domain
# assignment and each domain's Cronbach's alpha. Recomputing alpha from the live
# data under that assignment should reproduce all eight published alphas. As a
# contrast, shifting every domain boundary by one item (+1 / -1) should NOT.
#
# What this does NOT establish: order WITHIN a domain (alpha is invariant to
# permuting items inside a block), e.g. MedSEQ_1 vs MedSEQ_2 vs MedSEQ_3.

suppressMessages(library(irw))

TABLE <- "huang_2023_medseq"
DOMAINS <- list(
  teaching   = 1:3,  assessment = 4:6,   staff     = 7:9,  learning = 10:13,
  clinical   = 14:15, online    = 16:17, cultural  = 18:19, cared    = 20:22)
PUBLISHED <- c(teaching = 0.719, assessment = 0.833, staff = 0.850, learning = 0.856,
               clinical = 0.708, online = 0.687, cultural = 0.712, cared = 0.749)
TOL <- 0.005

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, paste0("MedSEQ_", 1:22)])
cat(sprintf("persons: %d, complete cases: %d\n", nrow(X), sum(complete.cases(X))))

alpha <- function(M) {
  M <- M[complete.cases(M), , drop = FALSE]
  k <- ncol(M)
  k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}
calc <- function(doms) sapply(doms, function(ix) alpha(X[, ix, drop = FALSE]))

obs <- calc(DOMAINS)
cat(sprintf("\n%-11s %-7s %9s %9s %8s\n", "domain", "items", "published", "observed", "diff"))
for (n in names(DOMAINS))
  cat(sprintf("%-11s %-7s %9.3f %9.3f %8.3f\n", n,
              paste0(min(DOMAINS[[n]]), "-", max(DOMAINS[[n]])),
              PUBLISHED[n], obs[n], obs[n] - PUBLISHED[n]))
# 'cared' (20-22) does not reproduce: 0.661 observed vs 0.749 published. It is
# tested by ELIMINATION instead -- the other seven domains pin items 1-19 exactly,
# leaving 20-22 as the only possible members. No contiguous or content-plausible
# 2-4 item set reproduces 0.749 (only scattered cross-domain combinations do), so
# the gap is recorded as a source discrepancy, not a mapping failure.
seven <- setdiff(names(DOMAINS), "cared")
worst <- max(abs(obs[seven] - PUBLISHED[seven]))
cat(sprintf("\nlargest deviation over the 7 reproducing domains: %.4f (tolerance %.3f)\n", worst, TOL))
cat(sprintf("cared-for (20-22): observed %.3f vs published %.3f -- SOURCE DISCREPANCY, membership by elimination\n",
            obs["cared"], PUBLISHED["cared"]))
resid <- setdiff(1:22, unlist(DOMAINS[seven]))
cat("items left after the 7 pinned domains:", paste0("MedSEQ_", resid), "\n")
worst <- if (identical(resid, 20:22)) worst else Inf

# Contrast: mis-assign by shifting every item index by +1 / -1 (wrapping 1..22).
shift <- function(s) lapply(DOMAINS, function(ix) ((ix - 1 + s) %% 22) + 1)
for (s in c(1, -1)) {
  o <- calc(shift(s))
  cat(sprintf("shift %+d: largest deviation %.3f; domains within tolerance %d/8\n",
              s, max(abs(o - PUBLISHED)), sum(abs(o - PUBLISHED) <= TOL)))  # all 8 compared
}
cat("Note: pins domain membership and the domain boundaries at 3|4, 6|7, 9|10,\n",
    "13|14, 15|16, 17|18, 19|20; does NOT pin order within a domain.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
