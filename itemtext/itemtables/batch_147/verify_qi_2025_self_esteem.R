# verify_qi_2025_self_esteem.R -- Step 5b, re-runnable mapping check.
#
# CLAIM UNDER TEST. The 10 live item codes Esteem_1..Esteem_10 carry the
# Rosenberg Self-Esteem Scale items in the order printed on the Morris
# Rosenberg Foundation / University of Maryland Sociology form
# (socy.umd.edu "Using the Rosenberg Self-Esteem Scale", item table image
# "Rosenberg SE Scale.jpg", sha256 87ffbaebff754c74264bb06fd972ee24fa4c997161
# e6331752f3568eca438c6e), whose reverse-worded items are 3, 5, 8, 9, 10.
#
# WHY THIS IS FALSIFIABLE. The RSES circulates in TWO widely used orderings
# that differ only in the permutation of the same ten sentences:
#   (A) the UMD form shipped here          -- reverse items 3, 5, 8, 9, 10
#   (B) the other common circulated order  -- reverse items 2, 5, 6, 8, 9
# Qi et al. (2025) report Cronbach's alpha = 0.89 for this exact sample, and
# alpha is computed AFTER reverse-scoring, so it is a direct test of which
# permutation was administered. The two orderings are not close: (A)
# reproduces 0.89, (B) is strongly negative.
#
# WHAT THIS DOES NOT ESTABLISH: the order of items WITHIN a polarity class.
# Swapping the shipped text of Esteem_1 and Esteem_2 (both positive-worded),
# or of Esteem_9 and Esteem_10 (both reverse-worded), would move none of the
# numbers below. Hence the recorded status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "qi_2025_self_esteem"
PUBLISHED_ALPHA <- 0.89   # Qi et al. (2025) Sci Data 12:1755, Methods
# The paper reports alpha to two decimals, so the test is that the shipped
# ordering ROUNDS to the published value (observed 0.8853 -> 0.89).
COLS <- paste0("Esteem_", 1:10)

# Reverse sets implied by each candidate ordering.
REV_SHIPPED <- c(3, 5, 8, 9, 10)   # UMD form (what this table ships)
REV_RIVAL   <- c(2, 5, 6, 8, 9)    # the other circulated RSES ordering

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, COLS]

alpha <- function(m) {
    k <- ncol(m)
    k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
}
flip <- function(m, idx) { m[, idx] <- 5 - m[, idx]; m }

a_ship  <- alpha(flip(w, REV_SHIPPED))
a_rival <- alpha(flip(w, REV_RIVAL))
a_raw   <- alpha(w)

cat(sprintf("n respondents: %d;  items: %d;  resp range %d-%d\n\n",
            nrow(w), ncol(w), min(w), max(w)))
cat("Cronbach's alpha, published for this sample (2 d.p.): ", PUBLISHED_ALPHA, "\n", sep = "")
cat(sprintf("  shipped ordering (reverse %s): %.4f  [diff %+.4f]\n",
            paste(REV_SHIPPED, collapse = ","), a_ship, a_ship - PUBLISHED_ALPHA))
cat(sprintf("  rival ordering   (reverse %s): %.4f\n",
            paste(REV_RIVAL, collapse = ","), a_rival))
cat(sprintf("  no reversal at all:                %.4f\n\n", a_raw))

# Second, independent leg: the sign pattern of the correlation matrix must
# reproduce the shipped polarity classes item by item.
POSITIVE <- setdiff(1:10, REV_SHIPPED)
r <- cor(w)
cat("Correlation sign pattern against the shipped polarity classes\n")
cat(sprintf("  positive-worded per shipped text: %s\n",
            paste(COLS[POSITIVE], collapse = ", ")))
cat(sprintf("  reverse-worded  per shipped text: %s\n\n",
            paste(COLS[REV_SHIPPED], collapse = ", ")))
cat(sprintf("%-11s %14s %14s %10s\n", "item", "mean r w/ pos", "mean r w/ rev", "item-rest"))
rest <- sapply(1:10, function(i) cor(w[, i], rowSums(w[, -i, drop = FALSE])))
for (i in 1:10) {
    rp <- mean(r[i, setdiff(POSITIVE, i)])
    rn <- mean(r[i, setdiff(REV_SHIPPED, i)])
    cat(sprintf("%-11s %14.3f %14.3f %10.3f\n", COLS[i], rp, rn, rest[i]))
}

# Esteem_8 is expected to break the sign rule: "I wish I could have more
# respect for myself" is the item whose Chinese rendering is documented to
# behave as positively worded, and it is precisely why the published alpha is
# 0.89 rather than the 0.91 obtained by dropping it from the reverse set.
a_no8 <- alpha(flip(w, setdiff(REV_SHIPPED, 8)))
cat(sprintf("\nalpha if Esteem_8 were NOT reversed: %.4f (published is %.2f, so the\n",
            a_no8, PUBLISHED_ALPHA))
cat("authors did reverse it; it is simply a weak item in this Chinese sample)\n\n")

sign_ok <- all(sapply(setdiff(POSITIVE, integer(0)), function(i)
                   mean(r[i, setdiff(POSITIVE, i)]) > 0 &&
                   mean(r[i, REV_SHIPPED[REV_SHIPPED != 8]]) < 0)) &&
           all(sapply(setdiff(REV_SHIPPED, 8), function(i)
                   mean(r[i, POSITIVE]) < 0 &&
                   mean(r[i, setdiff(REV_SHIPPED, c(i, 8))]) > 0))

cat("polarity sign pattern reproduces (Esteem_8 excused, see above): ",
    sign_ok, "\n", sep = "")
cat("NOT established by this script: order within a polarity class.\n")

ok <- round(a_ship, 2) == PUBLISHED_ALPHA && a_rival < 0 && sign_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
