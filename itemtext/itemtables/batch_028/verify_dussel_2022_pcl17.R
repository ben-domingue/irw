# verify_dussel_2022_pcl17.R -- Step 5b re-runnable evidence.
#
# CLAIM BEING TESTED (two mapping axes):
#  (a) option_text <-> resp: resp 1..5 = "Not at all" .. "Extremely", i.e. the
#      standard PCL 1-5 anchoring and NOT the 0-4 anchoring printed in the
#      study's own S1 Appendix, and NOT reversed.
#  (b) item_text <-> item: the 17 PCL codes name their own content, and the two
#      codes that do not disambiguate themselves (PCL_defensive / PCL_watchful,
#      both hyperarousal) are assigned by column position in the source file.
#
# Data: the study's S1 Dataset (PLOS ONE 10.1371/journal.pone.0267032, CC BY 4.0),
# which is EXACTLY what data/dussel_2022_hospital_covid.py melts into the live
# table (rename -> melt -> drop NA -> keep 1..5; no recode, no reorder). Using it
# instead of irw_fetch() is deliberate: irw_fetch() exports the whole table and
# the account shares a 200GB/30-day Redivis export cap. The link between the two
# is checked below with irw_table_sets(), which is a server-side aggregate.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "dussel_2022_pcl17"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0267032.s003"
PUBLISHED_PCT_ABOVE_44 <- 14   # paper Results: "PTSD symptoms (PCL > 44) for 14%"
CUTOFF <- 44

f <- tempfile(fileext = ".xlsx")
download.file(URL, f, quiet = TRUE, mode = "wb")
raw <- as.data.frame(read_excel(f))
names(raw) <- trimws(names(raw))
# readxl de-duplicates the file's two HAD_enjoy columns (HADS items 2 and 6);
# keep the first occurrence under its plain name.
names(raw) <- sub("^(HAD_enjoy)\\.\\.\\.[0-9]+$", "\\1", names(raw))
raw <- raw[, !duplicated(names(raw))]
pcl <- grep("^PCL_", names(raw), value = TRUE)

# --- link the source file to the live table (server-side, no export) ----------
s <- irw::irw_table_sets(TABLE, source = "core")
cat("live item set == source PCL_ columns:",
    identical(sort(s$items), sort(pcl)), "\n")
cat("live resp set:", paste(sort(as.numeric(s$resp)), collapse = ","), "\n\n")
ok_link <- identical(sort(s$items), sort(pcl)) &&
           identical(sort(as.numeric(s$resp)), 1:5 + 0)

# --- (a) anchor direction: reproduce the published PCL total ------------------
X <- raw[, pcl]
X <- X[stats::complete.cases(X), ]
tot <- rowSums(X)
pct <- 100 * mean(tot > CUTOFF)
pct_rev <- 100 * mean((6 * length(pcl) - tot) > CUTOFF)
cat("--- (a) option_text <-> resp -------------------------------------------\n")
cat(sprintf("n complete = %d; total score mean %.2f, min %d, max %d\n",
            nrow(X), mean(tot), min(tot), max(tot)))
cat(sprintf("as shipped (1=Not at all .. 5=Extremely): %.1f%% > %d  (paper: %d%%)\n",
            pct, CUTOFF, PUBLISHED_PCT_ABOVE_44))
cat(sprintf("if anchors were reversed:                %.1f%% > %d\n", pct_rev, CUTOFF))
cat(sprintf("min/max %d/%d is the 17-85 range of a 1-5 scale; a 0-4 scale (as the S1 Appendix prints) would give 0-68\n",
            min(tot), max(tot)))
ok_a <- abs(pct - PUBLISHED_PCT_ABOVE_44) < 1 && min(tot) == 17 && max(tot) == 85 && pct_rev > 50

# --- (b) item content: cross-instrument content predictions ------------------
# The HADS in the same file gives independent content anchors. If the PCL codes
# name their own content, then among all 17 PCL items:
#   HAD_enjoy  ("I still enjoy the things I used to enjoy") -> PCL_loss_interest
#   HAD_slow   ("I feel as if I am slowed down")            -> PCL_concentration
#   HAD_jumpy  ("I feel tense or wound up")                 -> hyperarousal block
cat("\n--- (b) item_text <-> item ---------------------------------------------\n")
pred <- list(HAD_enjoy = "PCL_loss_interest", HAD_slow = "PCL_concentration")
ok_b <- TRUE
for (h in names(pred)) {
    d2 <- raw[, c(pcl, h)]
    d2 <- d2[stats::complete.cases(d2), ]
    r <- sapply(pcl, function(c) cor(d2[[c]], d2[[h]]))
    o <- sort(r, decreasing = TRUE)
    cat(sprintf("%-10s top: %s\n", h,
        paste(sprintf("%s %.3f", names(o)[1:3], o[1:3]), collapse = " | ")))
    ok_b <- ok_b && names(o)[1] == pred[[h]]
}
# hyperarousal block (items 13-17) must be each other's nearest neighbours
D <- c("PCL_sleep","PCL_irritability","PCL_concentration","PCL_defensive","PCL_watchful")
C <- cor(X)
for (it in D) {
    w <- mean(C[it, setdiff(D, it)]); b <- mean(C[it, setdiff(pcl, c(D, it))])
    cat(sprintf("%-22s within-hyperarousal %.3f vs rest %.3f\n", it, w, b))
    ok_b <- ok_b && w > b
}
cat("\nNOT ESTABLISHED by any check here: PCL_defensive vs PCL_watchful.\n")
cat(sprintf("Their means are %.3f and %.3f (diff %.3f) and both are hyperarousal;\n",
            mean(X$PCL_defensive), mean(X$PCL_watchful),
            abs(mean(X$PCL_defensive) - mean(X$PCL_watchful))))
cat("they are assigned to appendix items 16 and 17 by source-column position only.\n")
cat("Hence the recorded status is PARTIAL, not VERIFIED.\n\n")

cat(if (ok_link && ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
