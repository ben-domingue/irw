# verify_extremera_2016_ei.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item codes ei1..ei16 are the source SPSS column names (ei1..ei15 plus
# ie16 renamed to ei16 by data/extremera_2016_unemployment_wellbeing.py), so the
# code carries no positional component. What IS inferred is which of the 16
# WLEIS-S sentences each number names, and the authors published the scale under
# TWO different numberings:
#
#   A) UMA administration form ("Adaptación al castellano del WLEIS", Extremera,
#      Rey & Sanchez-Alvarez, Univ. de Malaga 2019) -- INTERLEAVED / round-robin:
#      SEA = 1,5,9,13   OEA = 2,6,10,14   UOE = 3,7,11,15   ROE = 4,8,12,16
#   B) Psicothema 31(1):94-100 Table 1 -- BLOCKED:
#      SEA = 1-4   OEA = 5-8   UOE = 9-12   ROE = 13-16
#
# The shipped __items.csv uses (A). (A) and (B) are permutations of the same 16
# sentences, so ONLY the data can choose between them. The WLEIS's four-factor
# structure is a falsifiable prediction: same-subscale items must intercorrelate
# more than cross-subscale ones. If the shipped mapping were (B), that prediction
# would fail.
#
# DATA SOURCE ----------------------------------------------------------------
# The PLOS S1 SPSS file the IRW table is built from (public, no Redivis export;
# the corpus is against a 200GB/30-day cap and item-level correlations would need
# a full-table export). irw::irw_table_sets() is used to confirm the live item set
# is the same 16 codes, server-side.

suppressMessages({library(irw); library(haven)})

TABLE <- "extremera_2016_ei"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0163656.s001")

tmp <- tempfile(fileext = ".sav")
utils::download.file(SI, tmp, quiet = TRUE, mode = "wb",
                     headers = c("User-Agent" = "IRW-itemtext/1.0"))
d <- haven::read_sav(tmp)
names(d)[names(d) == "ie16"] <- "ei16"
cols <- paste0("ei", 1:16)
X <- na.omit(as.data.frame(lapply(d[cols], as.numeric)))
cat(sprintf("source .sav complete cases: %d\n", nrow(X)))

ts <- tryCatch(irw::irw_table_sets(TABLE), error = function(e) NULL)
if (!is.null(ts)) {
    live <- sort(unique(as.character(ts$item)))
    cat(sprintf("live item set == source columns: %s\n",
                identical(live, sort(cols))))
}

C <- cor(X)

score <- function(groups, label) {
    g <- integer(16); for (k in seq_along(groups)) g[groups[[k]]] <- k
    w <- b <- c()
    for (i in 1:15) for (j in (i + 1):16)
        if (g[i] == g[j]) w <- c(w, C[i, j]) else b <- c(b, C[i, j])
    hits <- 0
    for (i in 1:16) {
        o <- sort(C[i, -i], decreasing = TRUE)
        hits <- hits + sum(as.integer(sub("ei", "", names(o)[1:3])) %in%
                           which(g == g[i]))
    }
    cat(sprintf("%-38s within r=%.3f  between r=%.3f  gap=%+.3f  top3-in-subscale %d/48\n",
                label, mean(w), mean(b), mean(w) - mean(b), hits))
    c(gap = mean(w) - mean(b), hits = hits)
}

A <- score(list(c(1,5,9,13), c(2,6,10,14), c(3,7,11,15), c(4,8,12,16)),
           "A) SHIPPED, UMA form (interleaved)")
B <- score(list(1:4, 5:8, 9:12, 13:16),
           "B) rival, Psicothema Tab.1 (blocked)")

# Administration-order corroboration: if ei1..ei16 IS the printed sequence of the
# UMA form, cross-subscale neighbours (i, i+1) should show a small proximity
# excess over cross-subscale non-neighbours.
blk <- function(i) (i - 1) %% 4
adj <- non <- c()
for (i in 1:15) for (j in (i + 1):16) if (blk(i) != blk(j)) {
    if (j - i == 1) adj <- c(adj, C[i, j]) else non <- c(non, C[i, j])
}
cat(sprintf("cross-subscale neighbours r=%.3f (n=%d) vs non-neighbours r=%.3f (n=%d)\n",
            mean(adj), length(adj), mean(non), length(non)))

cat("\nWhat this does NOT establish: the test pins each item's SUBSCALE, and so\n",
    "rules out numbering B outright, but it cannot order the four items WITHIN a\n",
    "subscale -- swapping ei1 with ei9 would leave every number above unchanged.\n",
    "That ordering rests on the UMA form's printed sequence, weakly corroborated\n",
    "by the neighbour excess. Status is PARTIAL, not VERIFIED.\n", sep = "")

pass <- A["gap"] > B["gap"] + 0.05 && A["hits"] > B["hits"]
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
