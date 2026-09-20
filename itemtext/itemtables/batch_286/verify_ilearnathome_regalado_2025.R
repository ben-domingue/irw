# verify_ilearnathome_regalado_2025.R -- Step 5b, routes 2 (response-range/block
# structure), 7 (marker item) and 1 (a published descriptive statistic).
#
# CLAIM UNDER TEST: the item text shipped for live item code Q<n> is the text the
# deposit's own codebook sheet numbers "No. <n>". DATA.xlsx (Zenodo 15116678,
# CC BY 4.0) has two sheets: "Data", whose QUESTIONS block is headed Q1..Q30, and
# "Questions", which lists 30 numbered questions with their option keys. The tie
# between them is the shared 1..30 numbering, and that is the only inference in
# this extraction (data/ilearnathome_regalado_2025.R keeps the column names
# verbatim -- `select(Q1:Q15)` then `pivot_longer(names_to="item")` -- so the live
# item code IS the Data-sheet column name, with no positional step).
#
# irw::irw_fetch() is deliberately NOT called (200GB/30d export quota). The live
# item/resp sets are confirmed server-side with irw::irw_table_sets(), and the
# live per-item means measured at extraction time (Q1 1.09, Q2 1.17, Q3 1.23,
# Q4 1.33, Q5 1.49, Q6 1.28, Q7 1.48, Q8 1.39, Q9 1.35, Q10 1.42, Q11 1.15,
# Q12 2.04, Q13 1.33, Q14 1.59, Q15 1.68; n = 909 each) equal the DATA.xlsx
# column means this script recomputes, to 2 dp.

suppressMessages({ library(readxl); library(irw) })

TABLE <- "ilearnathome_regalado_2025"
URL   <- "https://zenodo.org/api/records/15116678/files/DATA.xlsx/content"
loc   <- file.path("..", "..", ".cache", TABLE, "DATA.xlsx")
if (!file.exists(loc)) {
  loc <- tempfile(fileext = ".xlsx")
  download.file(URL, loc, quiet = TRUE, mode = "wb")
}

d <- as.data.frame(read_xlsx(loc, sheet = "Data", skip = 4))
qs <- paste0("Q", 1:30)
stopifnot(all(qs %in% names(d)))

nlev <- sapply(qs, function(q) length(unique(na.omit(as.character(d[[q]])))))
cat("--- T1. codebook numbering carries no offset -------------------------\n")
cat("Codebook: questions 1-15 all share ONE 3-level key (Always=1/Sometimes=2/\n")
cat("Never=3); questions 16-30 are the heterogeneous 'Items' block with their own\n")
cat("option lists. Distinct levels per Data-sheet column:\n")
cat(sprintf("  %-4s %s\n", qs, nlev), sep = "")
t1 <- all(nlev[1:15] == 3) && all(nlev[16:30] >= 4)
cat(sprintf("  Q1-Q15 all exactly 3 levels: %s ; Q16-Q30 all >=4 levels: %s\n",
            all(nlev[1:15] == 3), all(nlev[16:30] >= 4)))
cat(sprintf("  => any offset k != 0 would put a >=4-level item inside the 3-level block: T1 %s\n\n",
            if (t1) "PASS" else "FAIL"))

x  <- sapply(paste0("Q", 1:15), function(q) as.numeric(d[[q]]))
m  <- colMeans(x)
p1 <- colMeans(x == 1) * 100
p3 <- colMeans(x == 3) * 100

cat("--- T2. marker item: question 12 is the only radio item ---------------\n")
cat("Radio was the least-used 'Aprendo en casa' delivery channel, so the item\n")
cat("'You give feedback to students who use the radio' must be the least-performed\n")
cat("activity of the 15 (1=Always .. 3=Never, so the HIGHEST mean).\n")
cat(sprintf("  %-5s mean %5.2f   Always%% %5.1f   Never%% %5.1f\n",
            names(m), m, p1, p3), sep = "")
t2 <- names(which.max(m)) == "Q12" && sum(p3 > 30) == 1 && p3["Q12"] > 30
cat(sprintf("  argmax(mean) = %s (expected Q12); columns with Never%% > 30: %s\n",
            names(which.max(m)), paste(names(which(p3 > 30)), collapse = ",")))
cat(sprintf("  => T2 %s\n\n", if (t2) "PASS" else "FAIL"))

cat("--- T3. the deposit's own published statistic -------------------------\n")
cat("Zenodo 15116678 abstract: \"92.1% of the teachers planned their learning\n")
cat("sessions using the 'I learn at home' strategy\" -- codebook question 1 is\n")
cat("'You respect the planning of the \"I learn at home\" strategy'.\n")
PUB <- 92.1
cat(sprintf("  published Always%% for question 1: %.1f ; observed Q1 Always%%: %.1f ; diff %.1f\n",
            PUB, p1["Q1"], p1["Q1"] - PUB))
cat(sprintf("  Q1 is the highest-Always column: %s (next highest %s at %.1f%%)\n",
            names(which.max(p1)) == "Q1",
            names(sort(p1, decreasing = TRUE))[2], sort(p1, decreasing = TRUE)[2]))
t3 <- names(which.max(p1)) == "Q1" && abs(p1["Q1"] - PUB) <= 2
cat(sprintf("  => T3 %s\n\n", if (t3) "PASS" else "FAIL"))

cat("--- live sets (server-side, no export) --------------------------------\n")
ts <- try(irw::irw_table_sets(TABLE), silent = TRUE)
if (!inherits(ts, "try-error")) {
  it <- sort(unique(as.character(ts$item))); rv <- sort(unique(as.numeric(ts$resp)))
  cat(sprintf("  live items (%d): %s\n", length(it), paste(it, collapse = ",")))
  cat(sprintf("  live resp values: %s\n", paste(rv, collapse = ",")))
} else cat("  irw_table_sets() unavailable offline; sets were confirmed by validate_items.R --table-sets\n")

cat("\nWhat this does NOT establish: T1 rules out any shift of the codebook\n")
cat("numbering and T2/T3 pin questions 12 and 1 individually, but nothing here\n")
cat("separates Q2-Q11 and Q13-Q15 from each other -- a permutation within that\n")
cat("group would leave every number above unchanged. Status is PARTIAL, not\n")
cat("VERIFIED; the tie for those 12 items rests on the deposit codebook's own\n")
cat("numbering, not on the data.\n")

cat(if (t1 && t2 && t3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
