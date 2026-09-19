# verify_liu_2022_fragreading_frq.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: live item code N8_k carries the responses to questionnaire
# item "8.k" of the Fragmented Reading Questionnaire, whose Chinese/English
# wording is shipped in liu_2022_fragreading_frq__items.csv.
#
# Two falsifiable predictions, neither of which is an item-count check:
#
# (1) Column-identity. The CC BY deposit (PeerJ 10.7717/peerj.13861, Supplemental
#     Information 1, peerj-10-13861-s001.xls) names its columns N8_1..N8_22, and
#     data/liu_2022_fragmented_reading.py melts them with var_name="item", i.e.
#     the live code IS the source column name. The per-item x level response
#     count vectors below are read off that .xls and hard-coded. All 22 vectors
#     are pairwise DISTINCT, so any permutation of item codes between source and
#     live data breaks the match.
#
# (2) Position of the two counter-worded items. The questionnaire supplement
#     (peerj-10-13861-s002.docx) marks exactly two FRQ items "**Deleted items
#     based on CFA": 8.6 ("...I do a lot of searching and reading about it") and
#     8.10 ("...I carry on later and make sure I finish it"). Both run against
#     the fragmentation construct every other item measures, so they must be the
#     two weakest item-rest correlations in the live data. An offset or shift in
#     the 8.k -> N8_k numbering would move that pair off positions 6 and 10.
#
# What this does NOT establish: the response-option ordering. That is taken from
# the paper's own explicit statement, "all responses were recorded on a
# five-point Likert scale (1 = Strongly disagree; 5 = Strongly agree)".

suppressMessages(library(irw))

TABLE <- "liu_2022_fragreading_frq"

# Counts of 1..5 per column, from the deposit's own s001.xls (N=916).
SRC <- list(
  "N8_1" = c(39, 112, 104, 408, 253),   "N8_2" = c(121, 325, 219, 214, 37),
  "N8_3" = c(73, 225, 220, 330, 68),    "N8_4" = c(150, 264, 213, 246, 43),
  "N8_5" = c(49, 152, 243, 418, 54),    "N8_6" = c(28, 64, 126, 495, 203),
  "N8_7" = c(129, 242, 105, 317, 123),  "N8_8" = c(35, 129, 165, 441, 146),
  "N8_9" = c(26, 110, 248, 442, 90),    "N8_10" = c(62, 227, 242, 288, 97),
  "N8_11" = c(56, 249, 212, 325, 74),   "N8_12" = c(122, 334, 213, 192, 55),
  "N8_13" = c(71, 254, 226, 306, 59),   "N8_14" = c(65, 224, 193, 356, 78),
  "N8_15" = c(27, 82, 122, 523, 162),   "N8_16" = c(48, 126, 140, 434, 168),
  "N8_17" = c(85, 297, 234, 251, 49),   "N8_18" = c(70, 252, 260, 281, 53),
  "N8_19" = c(22, 122, 193, 494, 85),   "N8_20" = c(26, 134, 226, 458, 72),
  "N8_21" = c(59, 191, 208, 346, 112),  "N8_22" = c(46, 199, 211, 374, 86))

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

# --- (1) per-item x level count match, source column vs live item code --------
cat("(1) response-count vectors: deposit column vs live item code\n")
cat(sprintf("%-8s %-26s %-26s %s\n", "item", "deposit .xls (1..5)", "live (1..5)", "ok"))
bad1 <- 0
for (it in names(SRC)) {
    live <- as.integer(table(factor(d$resp[d$item == it], levels = 1:5)))
    ok <- identical(as.integer(SRC[[it]]), live)
    if (!ok) bad1 <- bad1 + 1
    cat(sprintf("%-8s %-26s %-26s %s\n", it,
                paste(SRC[[it]], collapse = ","), paste(live, collapse = ","),
                if (ok) "MATCH" else "MISMATCH"))
}
nd <- length(unique(sapply(SRC, paste, collapse = ",")))
cat(sprintf("\n%d/22 vectors matched; %d/22 deposit vectors are distinct (a permutation could not hide)\n",
            22 - bad1, nd))

# --- (2) the two "**" CFA-deleted counter-worded items ------------------------
ids <- sort(unique(d$id))
m <- matrix(NA_real_, nrow = length(ids), ncol = length(SRC),
            dimnames = list(NULL, names(SRC)))
for (it in names(SRC)) {
    s <- d[d$item == it, ]
    m[, it] <- s$resp[match(ids, s$id)]
}
r_rest <- sapply(colnames(m), function(it) {
    rest <- rowMeans(m[, setdiff(colnames(m), it), drop = FALSE], na.rm = TRUE)
    cor(m[, it], rest, use = "complete.obs")
})
ord <- order(r_rest)
cat("\n(2) item-rest correlations, ascending:\n")
for (i in ord) cat(sprintf("  %-7s %.3f%s\n", names(r_rest)[i], r_rest[i],
                           if (names(r_rest)[i] %in% c("N8_6", "N8_10")) "   <- '**' CFA-deleted in the supplement" else ""))
two_lowest <- names(r_rest)[ord][1:2]
cat(sprintf("two lowest = %s; expected {N8_6, N8_10}\n",
            paste(sort(two_lowest), collapse = ", ")))
bad2 <- !setequal(two_lowest, c("N8_6", "N8_10"))

cat(if (bad1 == 0 && nd == 22 && !bad2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
