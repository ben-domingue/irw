# verify_liu_2025_classroom_interaction.R
#
# CLAIM UNDER TEST. data/liu_2025_classroom_wtc.py assigns the IRW item codes
# POSITIONALLY: it drops the first 4 columns of the study's S2 Data workbook
# (10.1371/journal.pone.0328226.s002) and names columns 0-6 of the remainder
# ci_li_1..ci_li_7 and columns 7-10 ci_ll_1..ci_ll_4. Those workbook columns are
# headed with the item wording itself, and the shipped item_text is the same 11
# items in the same order as the paper's S1 Appendix ("The Complete 44 Items in
# the Questionnaire", items 1-11).
#
# The falsifiable prediction: for each shipped item, the response-level count
# vector (#1,#2,#3,#4,#5) computed from the raw workbook column at that position
# must equal the count vector of the live IRW item of that name, cell for cell.
# If item_text for any two items were swapped, the assignment would break --
# all 11 raw vectors are mutually distinct (smallest L1 distance 20), so this
# route distinguishes every item from every other item.
#
# What it does NOT establish: nothing about the words themselves being the
# administered wording. The study administered a Chinese translation and only
# published English, so item_text is an English substitute (see provenance).

suppressMessages(library(irw))

TABLE <- "liu_2025_classroom_interaction"
ITEMS <- c(paste0("ci_li_", 1:7), paste0("ci_ll_", 1:4))

# Raw per-item response-level counts read from S2 Data columns 5-15 (1-based),
# in workbook order. Hard-coded so the check runs offline; regenerate with
# pandas.read_excel(s002.xlsx).iloc[:, 4:15] if ever needed.
RAW <- rbind(
  ci_li_1 = c(20, 101, 301, 149,  52),
  ci_li_2 = c(28, 161, 296,  96,  42),
  ci_li_3 = c(12,  68, 278, 191,  74),
  ci_li_4 = c(14,  82, 267, 172,  88),
  ci_li_5 = c(15,  63, 161, 263, 121),
  ci_li_6 = c(10,  59, 189, 251, 114),
  ci_li_7 = c( 5,  71, 185, 240, 122),
  ci_ll_1 = c(18,  81, 277, 175,  72),
  ci_ll_2 = c(16,  80, 265, 191,  71),
  ci_ll_3 = c(16,  75, 275, 186,  71),
  ci_ll_4 = c(28, 104, 276, 151,  64))

d <- irw::irw_fetch(TABLE)
LIVE <- t(sapply(ITEMS, function(it) {
  r <- d$resp[d$item == it]
  sapply(1:5, function(k) sum(r == k))
}))

cat(sprintf("%-8s %-22s %-22s %s\n", "item", "raw S2 col (1..5)", "live IRW (1..5)", "match"))
ok <- TRUE
for (it in ITEMS) {
  m <- all(RAW[it, ] == LIVE[it, ])
  ok <- ok && m
  cat(sprintf("%-8s %-22s %-22s %s\n", it,
              paste(RAW[it, ], collapse = "/"),
              paste(LIVE[it, ], collapse = "/"),
              if (m) "yes" else "NO"))
}

# Distinctness: the route is only decisive if no two raw vectors coincide.
D <- as.matrix(dist(RAW, method = "manhattan"))
diag(D) <- NA
cat(sprintf("\nsmallest L1 distance between any two raw vectors: %d\n", as.integer(min(D, na.rm = TRUE))))

# Cross-assignment matrix: how many live items each raw vector matches exactly.
hits <- sum(outer(seq_len(11), seq_len(11), Vectorize(function(i, j) all(RAW[i, ] == LIVE[j, ]))))
cat(sprintf("exact raw-vs-live matches over the full 11x11 grid: %d (expected 11, all on the diagonal)\n", hits))

cat("Note: this pins item<->code for all 11 items. It says nothing about the wording being\n",
    "the administered Chinese text -- only English was ever published (see provenance).\n", sep = "")

cat(if (ok && hits == 11) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
