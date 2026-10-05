# verify_spain_2015_immigration_proximity.R -- Step 5b check for batch_506.
#
# CLAIM (mapping_basis=paper_explicit): the CIS questionnaire cues3119.pdf prints
#   P.27  (col 125) neighbours  'Entre todos sus vecinos y vecinas, ¿cuántos son gitanos o gitanas?'
#   P.27a (col 126) friends     '¿Y entre todos sus amigos y amigas?'
#   P.27b (col 127) co-workers  '¿Y entre sus compañeros/as de trabajo o estudios?'
#   P.27c (col 128) relatives   '¿Y entre sus familiares?'
# while the CIS SPSS syntax ES3119 (and 3119.sav) label P27A 'Compañeros/as de trabajo o
# estudios' and P27B 'Amigos y amigas' -- i.e. the two level-1 sources DISAGREE on p27a/p27b.
# This script decides the dispute with the data, and pins the other two items.
#
# Reference block: the parallel P.26 block (same four groups, asked about immigrants), shipped
# in batch_504 as spain_2015_immigration_contact, where the questionnaire and ES3119 labels
# AGREE: p26 neighbours, p26a friends, p26b co-workers/fellow students, p26c relatives.
#
# Routes (all on live IRW data, no source files needed):
#  1. Filter signature. 'No procede' (code 7, recoded to missing by the .do) on the co-workers
#     question means "no workplace or place of study"; the same respondents should be missing on
#     both co-workers items. The p27x whose missing set overlaps p26b's is the co-workers item.
#  2. Cross-block assignment. Each p27x should correlate most with the p26x asking about the SAME
#     group of people. Over all 24 assignments of p27x -> p26x, the claimed one must be the unique
#     maximum of summed Spearman correlations.
#  3. Marker. Relatives are the group least likely to include Roma (as they are for immigrants in
#     P.26): among the three unfiltered items the relatives item must have the highest 'Ninguno'.

suppressMessages({library(irw); library(tidyr)})

wide <- function(tab) {
  d <- as.data.frame(irw::irw_fetch(tab))[, c("id", "item", "resp")]
  as.data.frame(tidyr::pivot_wider(d, names_from = item, values_from = resp))
}
w <- merge(wide("spain_2015_immigration_proximity"), wide("spain_2015_immigration_contact"),
           by = "id", all = TRUE)
P <- c("p27", "p27a", "p27b", "p27c")
C <- c("p26", "p26a", "p26b", "p26c")   # neighbours, friends, co-workers, relatives
ok <- TRUE

cat("== Route 1: Jaccard overlap of each p27x missing set with p26b's (co-workers) ==\n")
miss_b <- is.na(w$p26b)
jac <- sapply(P, function(p) { m <- is.na(w[[p]]); sum(m & miss_b) / sum(m | miss_b) })
for (p in P) {
  m <- is.na(w[[p]])
  cat(sprintf("%-5s missing %4d   p26b missing %4d   both %4d   Jaccard %.3f\n",
              p, sum(m), sum(miss_b), sum(m & miss_b), jac[p]))
}
if (!(jac["p27b"] > 0.8 && all(jac[c("p27", "p27a", "p27c")] < 0.1))) {
  cat("FAIL: p27b is not the co-workers item\n"); ok <- FALSE
}

cat("\n== Route 2: Spearman p27x (rows) vs p26x (cols) ==\n")
R <- cor(w[, P], w[, C], method = "spearman", use = "pairwise.complete.obs")
print(round(R, 3))
perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
pp <- perms(1:4)
sc <- sapply(pp, function(p) sum(R[cbind(1:4, p)]))
o <- order(sc, decreasing = TRUE)
for (k in o[1:4]) cat(sprintf("  %-26s sum %.3f\n", paste(P, C[pp[[k]]], sep = "->", collapse = " "), sc[k]))
best <- pp[[o[1]]]
cat(sprintf("claimed (identity) sum %.3f; best alternative %.3f; margin %.3f\n",
            sum(diag(R)), sc[o[2]], sum(diag(R)) - sc[o[2]]))
if (!identical(as.integer(best), 1:4)) { cat("FAIL: identity is not the best assignment\n"); ok <- FALSE }

cat("\n== Route 3: share 'Ninguno' (resp 4) ==\n")
nin <- sapply(P, function(p) mean(w[[p]] == 4, na.rm = TRUE))
print(round(nin, 3))
if (names(which.max(nin[c("p27", "p27a", "p27c")])) != "p27c") { cat("FAIL: p27c is not the most-floored unfiltered item\n"); ok <- FALSE }

cat("\nWhat this does NOT establish: route 2 alone does not separate p27c from p27a on p27c's own\n",
    "row (0.125 with p26c vs 0.126 with p26a); p27c is pinned by the assignment maximum over all 24\n",
    "permutations together with route 3. Everything rests on the P.26 reference block's mapping,\n",
    "which is double-sourced (questionnaire and ES3119 labels agree) and filter-confirmed (p26b\n",
    "carries 1036 'No procede').\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
