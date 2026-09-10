# verify_ren_2019_sdq.R
#
# NOTE: ren_2019_sdq is BLOCKED ON RIGHTS and ships NO item text. sdqinfo.org:
#   "Users are not permitted to create or distribute electronic versions for any
#    purpose without prior authorization from youth in mind."
# This script therefore certifies nothing that is published. It exists to bank the
# mapping evidence so that, if youthinmind ever authorizes IRW or Ben rules the
# clause non-blocking, the extraction does not start from zero. It deliberately
# contains NO SDQ item wording -- only item NUMBERS and the instrument's published
# structural facts, which are what the mapping claim rests on.
#
# THE CLAIM UNDER TEST: the live item codes SDQ1..SDQ25 carry the SDQ's own
# canonical item numbering (Goodman 1997), rather than some other order. The
# numbering is a falsifiable prediction about the data because the SDQ fixes
#   - which 10 of the 25 items are positively worded (1,4,9,17,20 prosocial;
#     7,11,14,21,25 the reverse-keyed difficulty items), and
#   - which 5 must be reversed before the 20-item total-difficulties score.
# Neither fact is used to build the mapping; both would break under a relabelling.

suppressMessages(library(irw))

TABLE <- "ren_2019_sdq"

# Published: Ren et al. (2019) Front Psychol 10:2550, Measures section.
PUBLISHED_ALPHA_TOTDIFF <- 0.754
POSITIVE  <- c(1, 4, 9, 17, 20, 7, 11, 14, 21, 25)   # canonical positively-worded
REVERSE   <- c(7, 11, 14, 21, 25)                    # canonical reverse-keyed
DIFF      <- setdiff(1:25, c(1, 4, 9, 17, 20))       # the 20 total-difficulties items

d <- irw::irw_fetch(TABLE)
d$k <- as.integer(sub("^SDQ", "", d$item))

## ---- (1) polarity: do the 10 canonical positive positions take the 10 top means?
m <- tapply(d$resp, d$k, mean)
m <- m[order(as.integer(names(m)))]
top10 <- as.integer(names(sort(m, decreasing = TRUE))[1:10])
cat("per-item means (item: mean)\n")
for (i in 1:25) cat(sprintf("  SDQ%-2d %.3f%s\n", i, m[[as.character(i)]],
                            if (i %in% POSITIVE) "   <- canonically positive" else ""))
cat(sprintf("\npositive-worded positions, canonical: %s\n", paste(sort(POSITIVE), collapse = ",")))
cat(sprintf("top-10 positions by mean:            %s\n", paste(sort(top10), collapse = ",")))
polarity_ok <- setequal(top10, POSITIVE)
cat(sprintf("perfect split: %s   (min positive %.3f vs max negative %.3f; p under random relabelling = 1/C(25,10) = %.2e)\n",
            polarity_ok, min(m[as.character(POSITIVE)]),
            max(m[as.character(setdiff(1:25, POSITIVE))]), 1 / choose(25, 10)))

## ---- (2) reverse-key set: is the canonical quintet the alpha-maximising one?
dd <- as.data.frame(d[, c("id", "item", "resp")])
w  <- reshape(dd, idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
X0 <- w[, paste0("SDQ", DIFF)]
X0 <- X0[complete.cases(X0), ]
alpha <- function(X) {
  k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}
flip <- function(X, items) { for (i in items) X[[paste0("SDQ", i)]] <- 4 - X[[paste0("SDQ", i)]]; X }
combos <- combn(DIFF, 5, simplify = FALSE)
a <- vapply(combos, function(cc) alpha(flip(X0, cc)), numeric(1))
ord <- order(a, decreasing = TRUE)
canon_i <- which(vapply(combos, function(cc) setequal(cc, REVERSE), logical(1)))
rank_canon <- which(ord == canon_i)
cat(sprintf("\nn respondents (listwise, 20 difficulty items): %d; candidate 5-subsets: %d\n", nrow(X0), length(combos)))
cat(sprintf("alpha, no reversal:                 %.4f\n", alpha(X0)))
cat(sprintf("alpha, canonical reverse {%s}: %.4f  -> RANK %d of %d\n",
            paste(REVERSE, collapse = ","), a[canon_i], rank_canon, length(combos)))
for (j in 1:3) cat(sprintf("   runner-up %d {%s}: %.4f\n", j,
                           paste(combos[[ord[j]]], collapse = ","), a[ord[j]]))
cat(sprintf("published total-difficulties alpha: %.3f (observed %.3f)\n",
            PUBLISHED_ALPHA_TOTDIFF, a[canon_i]))
rev_ok <- rank_canon == 1

## ---- (3) marker item: SDQ22 (stealing) must be the most floored item.
floor_pct <- tapply(d$resp == 1, d$k, mean) * 100
marker <- names(sort(floor_pct, decreasing = TRUE))[1]
cat(sprintf("\nmost-floored item: SDQ%s (%.1f%% at resp=1); SDQ22 is %.1f%%\n",
            marker, max(floor_pct), floor_pct[["22"]]))
marker_ok <- marker == "22"

cat(sprintf("\npolarity %s | reverse-key rank-1 %s | marker item 22 %s\n",
            polarity_ok, rev_ok, marker_ok))
cat("NOT established by any of the above: order WITHIN a polarity class or within a\n")
cat("subscale (SDQ3 vs SDQ13, say). This would be PARTIAL, never VERIFIED.\n")
cat("Table is BLOCKED on rights regardless; nothing here is published.\n")
cat(if (polarity_ok && rev_ok && marker_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
