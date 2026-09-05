# verify_de_vries_2022_bat_burnout_core.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order):
#   Each IRW item code carries BAT-23 core-symptom wording assigned by subscale
#   prefix + within-subscale position of the official Dutch work-related BAT
#   questionnaire (burnoutassessmenttool.be, BAT-Nederlands.pdf):
#     batuit01_1..batuit08_1   -> Uitputting / Exhaustion, questionnaire items 1-8
#     batmen01_1..batmen05_1   -> Mentale distantie / Mental distance, items 9-13
#     batcog01_1..batcog05_1   -> Cognitieve ontregeling / Cognitive impairment, items 14-18
#     batemoo01_1..batemoo05_1 -> Emotionele ontregeling / Emotional impairment, items 19-23
#
# WHAT THIS SCRIPT CHECKS
#   (A) Subscale membership, decisively. The study's own SPSS deposit (PLOS S1
#       Data, .s007) contains four PRE-COMPUTED subscale scores whose variable
#       names are the Dutch subscale headings themselves -- BATuitputting,
#       BATmentaal, BATcognitief, BATemo. Those columns are NOT in the IRW table,
#       so they are an external key. The row-mean of the live IRW items I assigned
#       to a subscale must reproduce that subscale's stored score exactly, and must
#       NOT reproduce any of the other three.
#   (B) Semantic coherence of the block-level response distributions against the
#       BAT Test Manual v2.0 (Schaufeli, De Witte & Desart 2020, p. "Score
#       distribution of the items", Dutch sample N=1,500): "the items that tap
#       exhaustion and cognitive impairment are fairly normally distributed, with
#       the score of 2 occurring the most ... The score distribution of the items
#       that refer to mental distance and emotional impairment ... the lowest score
#       (1) occurs most frequently".
#
# WHAT IT DOES NOT ESTABLISH: the order of items WITHIN a subscale. Nothing in the
#   deposit or in any published source keys an individual BAT item number to a
#   statistic, so positions 1..8 within exhaustion (etc.) rest on the questionnaire's
#   presentation order. Hence status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "de_vries_2022_bat_burnout_core"
SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?id=10.1371/journal.pone.0272095.s007&type=supplementary")

GROUPS <- list(
  BATuitputting = sprintf("batuit%02d_1",  1:8),
  BATmentaal    = sprintf("batmen%02d_1",  1:5),
  BATcognitief  = sprintf("batcog%02d_1",  1:5),
  BATemo        = sprintf("batemoo%02d_1", 1:5)
)

## ---- live IRW data, wide ----
d <- irw::irw_fetch(TABLE)
d$id <- as.integer(as.character(d$id))
d$resp <- as.numeric(d$resp)
wide <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
                timevar = "item", direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
wide <- wide[order(wide$id), ]

## ---- study's own SPSS deposit: the pre-computed subscale scores ----
sav <- tempfile(fileext = ".sav")
utils::download.file(SAV_URL, sav, quiet = TRUE, mode = "wb")
sp <- haven::read_sav(sav)
sp$id <- seq_len(nrow(sp))            # data/de_vries_2022_hexaco.py: id = row index + 1
key <- merge(wide, as.data.frame(sp[, c("id", names(GROUPS))]), by = "id")
cat(sprintf("live rows joined to deposit: %d ids\n\n", nrow(key)))

cat("(A) max |row-mean of assigned items  -  stored subscale score|\n")
cat(sprintf("%-16s %14s %14s %14s %14s\n", "assigned block", names(GROUPS)[1],
            names(GROUPS)[2], names(GROUPS)[3], names(GROUPS)[4]))
diffs <- matrix(NA_real_, 4, 4, dimnames = list(names(GROUPS), names(GROUPS)))
for (g in names(GROUPS)) {
  m <- rowMeans(key[, GROUPS[[g]]])
  for (s in names(GROUPS)) diffs[g, s] <- max(abs(as.numeric(key[[s]]) - m))
  cat(sprintf("%-16s %14.4f %14.4f %14.4f %14.4f\n", g, diffs[g, 1], diffs[g, 2],
              diffs[g, 3], diffs[g, 4]))
}
diag_ok <- all(diag(diffs) < 1e-9)
off <- diffs; diag(off) <- NA
off_ok <- all(off > 0.5, na.rm = TRUE)
cat(sprintf("\n  diagonal max diff = %.2e (need < 1e-9): %s\n", max(diag(diffs)),
            ifelse(diag_ok, "OK", "FAIL")))
cat(sprintf("  smallest off-diagonal = %.3f (need > 0.5): %s\n",
            min(off, na.rm = TRUE), ifelse(off_ok, "OK", "FAIL")))

cat("\n(B) per-item modal response and %% at 1, by assigned block\n")
blockstat <- list()
for (g in names(GROUPS)) {
  for (it in GROUPS[[g]]) {
    v <- key[[it]]; v <- v[!is.na(v)]
    md <- as.integer(names(sort(table(v), decreasing = TRUE))[1])
    cat(sprintf("  %-12s %-14s M=%.2f  mode=%d  %%at1=%.1f\n", g, it, mean(v), md,
                100 * mean(v == 1)))
    blockstat[[g]] <- c(blockstat[[g]], 100 * mean(v == 1))
  }
}
p1_norm <- mean(c(blockstat$BATuitputting, blockstat$BATcognitief))
p1_low  <- mean(c(blockstat$BATmentaal,    blockstat$BATemo))
mode_norm <- all(sapply(c(GROUPS$BATuitputting, GROUPS$BATcognitief), function(it) {
  v <- key[[it]]; v <- v[!is.na(v)]
  as.integer(names(sort(table(v), decreasing = TRUE))[1]) >= 2
}))
cat(sprintf("\n  mean %%-at-1, exhaustion+cognitive blocks = %.1f\n", p1_norm))
cat(sprintf("  mean %%-at-1, mental-distance+emotional blocks = %.1f\n", p1_low))
cat("  manual (Dutch N=1,500) predicts: score 2 modal in the first pair,\n")
cat("  score 1 most frequent in the second pair.\n")
sem_ok <- (p1_low > p1_norm + 10) && mode_norm
cat(sprintf("  prediction holds: %s\n", ifelse(sem_ok, "OK", "FAIL")))

cat("\n")
if (diag_ok && off_ok && sem_ok) cat("VERDICT: PASS\n") else cat("VERDICT: FAIL\n")
