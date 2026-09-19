# verify_EWAS_Sanford_2024.R -- Step 5b check for EWAS_Sanford_2024 (batch_257).
#
# Claim: item_text/option_text for each code come from Sanford's own "SPSS Variable
# Definitions" PDF (OSF osf.io/4td6k), which prints every variable name (Mea1..Prod6)
# beside its stem and coded options. data/EWAS_Sanford_2024.R selects those columns BY
# NAME and tolower()s them, so the IRW code IS the source column name.
#
# Independent checks run here (no whole-table export; live data via irw_table_sets):
#   A. Range signature: per item, the max resp of the SHIPPED option set equals the live
#      max resp, for all 30 items (type 3 = 1..7, type 5 = 1..5, types 1/2/4/6 = 1..6).
#   B. Published final-scale list: the paper's Table 2 prints the 6 final EWAS stems
#      (administered in Study 2). The live items with n = 718 (Study 1 + Study 2) must be
#      exactly the codes whose shipped item_text equals those 6 published stems.
#   C. Study 2 .sav variable labels (a data-level label) equal the shipped item_text for
#      the 6 Study 2 codes, and its value labels equal the shipped option_text.
#   D. Paper Table 1 per-type average item partial r (criterion correlations controlling
#      for PSS) reproduced from the Study 1 .sav with columns grouped by the codebook's
#      suffix -> type assignment.
# What the STATISTICS do not establish: within one domain, types 1 vs 2 (and 1/2 vs 4)
# are not separated by A or D alone; that tie rests on the codebook's explicit
# variable-name labels, which C corroborates at the data-label level for 6 of 30 items.

suppressMessages({library(irw); library(haven)})
TABLE <- "EWAS_Sanford_2024"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_257")
csv <- file.path(here, "EWAS_Sanford_2024__items.csv")
if (!file.exists(csv)) csv <- "itemtables/batch_257/EWAS_Sanford_2024__items.csv"
it <- read.csv(csv, stringsAsFactors = FALSE)
ok <- TRUE

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
cat("== A. per-item resp max: shipped vs live ==\n")
shipmax <- tapply(it$resp, it$item, max)
pi <- pi[match(names(shipmax), pi$item), ]
A <- data.frame(item = names(shipmax), shipped_max = as.integer(shipmax), live_max = pi$resp_max,
                live_min = pi$resp_min, n = pi$n)
print(A, row.names = FALSE)
a_ok <- all(A$shipped_max == A$live_max) && all(A$live_min == 1)
cat("A:", if (a_ok) "PASS" else "FAIL", "\n\n"); ok <- ok && a_ok

cat("== B. paper Table 2 final-scale stems vs live n = 718 items ==\n")
T2 <- c(
 "Think about the most productive things you did this last week (where you accomplished things or made progress toward goals). How productive were you when doing these things?",
 "In the last week, how often did you do an activity that was enriching (where you learned, improved, grew, or experienced something new)?",
 "Doing something engaging means doing something where you are involved, engrossed, and focused on what you were doing. Compared to what an average person typically does, how much did you do things that were engaging during the last week?",
 "Think about the most satisfying things you did this last week (times when you did what you wanted to do and felt good about it). How satisfying were these things?",
 "In the last week, how often did you do an activity that was meaningful (where you did something valuable, important, or worthwhile)?",
 "Doing something enriching means doing something where you learn, improve, grow, or experience something new. Compared to what an average person typically does, how much did you do things that were enriching during the last week?")
stems <- unique(it[, c("item", "item_text")])
codes_by_text <- stems$item[match(T2, stems$item_text)]
live718 <- sort(A$item[A$n == 718])
cat("codes whose shipped text = Table 2 stems:", paste(codes_by_text, collapse = ", "), "\n")
cat("live items with n = 718:               ", paste(live718, collapse = ", "), "\n")
b_ok <- !anyNA(codes_by_text) && setequal(codes_by_text, live718)
cat("B:", if (b_ok) "PASS" else "FAIL", "\n\n"); ok <- ok && b_ok

tmp <- file.path(tempdir(), "ewas"); dir.create(tmp, showWarnings = FALSE)
f1 <- file.path(tmp, "s1.sav"); f2 <- file.path(tmp, "s2.sav")
if (!file.exists(f1)) download.file("https://osf.io/download/kdngt/", f1, mode = "wb", quiet = TRUE)
if (!file.exists(f2)) download.file("https://osf.io/download/yw79x/", f2, mode = "wb", quiet = TRUE)

cat("== C. Study 2 .sav labels vs shipped text ==\n")
d2 <- read_sav(f2); c_ok <- TRUE
for (x in c("prod1", "enri2", "enga3", "sat1", "mea2", "enri3")) {
  lab <- trimws(attr(d2[[x]], "label")); vl <- attr(d2[[x]], "labels")
  sub <- it[it$item == x, ]; sub <- sub[order(sub$resp), ]
  m1 <- identical(lab, sub$item_text[1])
  m2 <- identical(trimws(names(vl))[order(vl)], sub$option_text) && identical(as.integer(sort(vl)), sub$resp)
  cat(sprintf("%-6s varlabel==item_text %s | valuelabels==options %s\n", x, m1, m2))
  c_ok <- c_ok && m1 && m2
}
cat("C:", if (c_ok) "PASS" else "FAIL", "\n\n"); ok <- ok && c_ok

cat("== D. Table 1 average item partial r by type (Study 1 .sav) ==\n")
d1 <- zap_labels(read_sav(f1))
v <- as.vector(t(outer(c("Mea", "Sat", "Enri", "Enga", "Prod"), 1:6, paste0)))
crit <- c("ExerDays", "FBCdiet", "TaaqAct", "TaaqBen")
pr <- sapply(v, function(x) {
  r <- sapply(crit, function(cv) {
    z <- na.omit(data.frame(i = d1[[x]], c = d1[[cv]], s = d1$PSS))
    cor(resid(lm(i ~ s, z)), resid(lm(c ~ s, z)))
  }); sqrt(mean(r^2)) })
obs <- tapply(pr, as.integer(sub("\\D+", "", v)), mean)
PUB <- c(.29, .27, .27, .25, .16, .19)
D <- data.frame(type = 1:6, published = PUB, observed = round(as.numeric(obs), 3))
print(D, row.names = FALSE)
worst <- max(abs(obs - PUB)); cat(sprintf("largest deviation %.3f (tol 0.015)\n", worst))
# the load-bearing contrast: types 5/6 (low) vs 1-4, and 5 < 6 as published
d_ok <- worst <= 0.015 && obs[5] < obs[6] && max(obs[5:6]) < min(obs[1:4])
cat("D:", if (d_ok) "PASS" else "FAIL", "\n\n"); ok <- ok && d_ok

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
