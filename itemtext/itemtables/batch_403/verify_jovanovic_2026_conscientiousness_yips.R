# verify_jovanovic_2026_conscientiousness_yips.R -- Step 5b mapping evidence, re-runnable.
# Run from itemtext/.
#
# CLAIM UNDER TEST: live codes yips1..yips10 carry the English YIPS wording in the
# numbering of the originator's form (Renshaw 2020, YIEPS measure + user guide,
# https://osf.io/download/ets7c/, items 1-10 = Internalizing), and resp 1..4 =
# Almost Never .. Almost Always.
#
# How the code is derived: data/jovanovic_2026_conscientiousness.py melts the
# Sample 3 .sav columns YIPS1..YIPS10 by name and lower-cases them (code IS the
# column name). The .sav carries NO variable labels and NO value labels, so what
# is inferred is what each column NAME's number means: that the Serbian form kept
# the originator's item order.
#
# Checks:
#   (P) plumbing, not evidence: live cells == the deposit's cells.
#   (D) option axis, direction: YIPS mean correlates POSITIVELY with the same
#       respondents' SPANE negative-affect mean (deposit, same .sav). Under the
#       claimed direction (4 = Almost Always = more problems) this must be > 0;
#       a reversed anchor set would make it negative.
#   (K) keying: the user guide says "No reverse-scoring necessary", so every
#       corrected item-total correlation must be positive.
#   (S) semantic coherence (route 8), POST HOC -- read after seeing the numbers,
#       so it is description, not a test: the two highest-severity items
#       (9 worthless/lonely, 7 panic) are among the three lowest means, and the
#       two most common adolescent complaints (2 tired, 6 moody) are the two
#       highest.
#
# WHAT THIS DOES NOT ESTABLISH: nothing here distinguishes item k from item j.
# No per-item statistics are published for this sample (the paper, JID 47(1),
# is closed-access and 403s; the Serbian validation paper, JPA 105(6), is
# paywalled), the scale has one 1-4 range, no subscales and no reverse items.
# Item identity is NO_ROUTE; the mapping rests on the originator's numbering.
# VERDICT: PASS means (P), (D) and (K) hold -- the option direction is verified,
# the item order is not.

suppressMessages(library(irw))
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")
TABLE <- "jovanovic_2026_conscientiousness_yips"
sav <- cached_source(".cache/jovanovic_2026_conscientiousness_yips/s3.sav",
                     "https://osf.io/download/6616d64b943bee3e9bdfed54/")

d <- as.data.frame(irw::irw_fetch(TABLE))
x <- as.data.frame(haven::read_sav(sav))
x[] <- lapply(x, function(v) as.numeric(v))
Y <- paste0("YIPS", 1:10); S <- paste0("SPANE_NA", 1:6)

# (P) processing script ids are 1..n over samples 1,2,3; sample 3 starts after
# samples 1 and 2, so match on the per-cell multiset per item instead of id.
same <- sapply(1:10, function(i) {
  live <- sort(d$resp[d$item == paste0("yips", i)])
  v    <- x[[Y[i]]]
  src  <- sort(v[!is.na(v) & v == round(v)])   # script drops the deposit's
                                               # imputed fractional cells
  identical(as.numeric(live), as.numeric(src))
})
cat(sprintf("(P) plumbing: per-item live resp multiset == deposit YIPS integer cells: %d / 10\n", sum(same)))
cat(sprintf("    deposit fractional (imputed) cells dropped by the script: %d\n\n",
            sum(sapply(Y, function(v) sum(x[[v]] != round(x[[v]]), na.rm = TRUE)))))

# (D)
ym <- rowMeans(x[, Y], na.rm = TRUE); sm <- rowMeans(x[, S], na.rm = TRUE)
rD <- cor(ym, sm, use = "complete.obs")
cat(sprintf("(D) corr(YIPS mean, SPANE-NA mean) = %+.3f  (n = %d)\n\n", rD,
            sum(complete.cases(ym, sm))))

# (K)
tot <- rowSums(x[, Y])
itc <- sapply(Y, function(v) cor(x[[v]], tot - x[[v]], use = "complete.obs"))
cat("(K) corrected item-total r:\n")
print(round(itc, 3))

# (S)
mn <- sapply(1:10, function(i) mean(d$resp[d$item == paste0("yips", i)]))
names(mn) <- paste0("yips", 1:10)
cat("\n(S) per-item means (post hoc description only):\n")
print(round(sort(mn, decreasing = TRUE), 2))

cat("\nNOT ESTABLISHED: item identity (order within the scale). NO_ROUTE.\n")
ok <- all(same) && rD > 0 && all(itc > 0)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
