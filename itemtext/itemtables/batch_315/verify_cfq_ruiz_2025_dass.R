# verify_cfq_ruiz_2025_dass.R -- Step 5b mapping check (route 5: subscale block structure).
#
# Claim: live item DASSk carries the text of item k of the study's own Spanish DASS-21
# questionnaire (OSF sv9c3, Questionnaires/DASS-21.pdf). The item codes are the source
# column names of Dataset.xlsx unchanged (data/cfq_ruiz_2025.py melts columns starting
# 'DASS'), so the only inferential link is "column DASSk = printed item k".
#
# Falsifiable prediction: the DASS-21 has a fixed, published item-number -> subscale key
# (Lovibond & Lovibond 1995; DASS website scoring key; the Spanish Daza page states "The
# items are in the same order as the English DASS21"):
#   Depression 3,5,10,13,16,17,21 | Anxiety 2,4,7,9,15,19,20 | Stress 1,6,8,11,12,14,18
# If column k really is printed item k, each item should correlate most with its own
# subscale. A shift or permutation across subscales breaks this.
#
# What this does NOT establish: order WITHIN a subscale (e.g. DASS3 vs DASS5 could be
# swapped and still pass). DASS subscales are also strongly correlated (general distress
# factor), so a modest hit rate is expected even for a correct key; the permutation
# null quantifies how far above chance the observed structure is.

suppressMessages(library(irw))
TABLE <- "cfq_ruiz_2025_dass"
KEY <- list(D = c(3,5,10,13,16,17,21), A = c(2,4,7,9,15,19,20), S = c(1,6,8,11,12,14,18))

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, paste0("DASS", 1:21)])
R <- cor(X, use = "pairwise.complete.obs")

score <- function(key) {
  grp <- integer(21); for (g in seq_along(key)) grp[key[[g]]] <- g
  hits <- 0; rows <- list()
  for (i in 1:21) {
    m <- sapply(1:3, function(g) { j <- setdiff(which(grp == g), i); mean(R[i, j]) })
    hits <- hits + (which.max(m) == grp[i])
    rows[[i]] <- c(i, grp[i], m)
  }
  list(hits = hits, rows = do.call(rbind, rows))
}
obs <- score(KEY)
cat(sprintf("%-7s %-4s %7s %7s %7s  own-highest?\n", "item", "key", "r_D", "r_A", "r_S"))
for (i in 1:21) {
  r <- obs$rows[i, ]
  cat(sprintf("DASS%-3d %-4s %7.3f %7.3f %7.3f  %s\n", i, names(KEY)[r[2]], r[3], r[4], r[5],
              if (which.max(r[3:5]) == r[2]) "yes" else "NO"))
}
allpairs <- which(upper.tri(R), arr.ind = TRUE)
grp <- integer(21); for (g in 1:3) grp[KEY[[g]]] <- g
same <- grp[allpairs[,1]] == grp[allpairs[,2]]
cat(sprintf("\nmean within-subscale r = %.3f; mean between-subscale r = %.3f\n",
            mean(R[allpairs][same]), mean(R[allpairs][!same])))
cat(sprintf("items whose own subscale has the highest mean r: %d / 21\n", obs$hits))

set.seed(315)
null <- replicate(2000, { p <- sample(21); score(lapply(KEY, function(k) p[k]))$hits })
pval <- mean(null >= obs$hits)
cat(sprintf("permutation null (2000 random 7/7/7 keys): median %d, 95th pct %d, max %d; p = %.4f\n",
            median(null), quantile(null, .95), max(null), pval))
cat("Not established: order within a subscale.\n")
cat(if (obs$hits >= 15 && pval < 0.01) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
