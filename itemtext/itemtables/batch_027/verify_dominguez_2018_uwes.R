# verify_dominguez_2018_uwes.R
#
# This table is BLOCKED on rights, so NO item text was shipped and there is no
# item_text<->item mapping in the corpus to verify. The instrument is the Spanish
# UWES-17 (Encuesta de Bienestar y Trabajo, UWES Preliminary Manual v1.1 pp.54-55),
# whose every page carries the rights holders' own clause:
#   "(c) Schaufeli & Bakker (2003). The Utrecht Work Engagement Scale is free for use
#    for non-commercial scientific research. Commercial and/or non-scientific use is
#    prohibited, unless previous written permission is granted by the authors."
#
# What this script re-runs is the evidence recorded in
# verification_dominguez_2018_uwes.csv: the mapping that WOULD have been shipped is
# fully established, so an unblock (relicensing, or a ruling that this clause does not
# fire) needs no further investigation. Two checks, neither of which is plumbing:
#
#   1. POSITIONAL TIE. data/dominguez_2018_job_crafting.py assigns item_1..item_17 to
#      S1 File (XLSX) columns 32..48 by position. Those columns are headed "Item 1" ..
#      "Item 17" in the sheet's own header row, and each live per-item mean/n must
#      reproduce its source column exactly. A one-column shift breaks this.
#   2. SUBSCALE FINGERPRINT. Sheet row 1 tags each of cols 32..48 VIG/DED/ABS. That
#      17-long sequence must equal the canonical UWES-17 subscale assignment
#      (vigour 1,4,8,12,15,17; dedication 2,5,7,10,13; absorption 3,6,9,11,14,16),
#      which is how the numbering is tied to the manual's printed item numbers.
#      Corroborated in the live data: same-subscale correlations should exceed
#      cross-subscale ones.
#
# irw_fetch() is used deliberately: per-item means are needed for check 1 and
# irw_table_sets() does not supply them. The table is 3,434 rows.

suppressMessages({library(irw); library(readxl)})

TABLE  <- "dominguez_2018_uwes"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?id=10.1371/journal.pone.0197276.s001&type=supplementary")

cands <- c(file.path(".cache", TABLE, "s001.xlsx"),
           file.path("..", "..", ".cache", TABLE, "s001.xlsx"))
CACHE <- cands[file.exists(cands)][1]
if (is.na(CACHE)) {
    CACHE <- cands[1]
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(SI_URL, CACHE, mode = "wb", quiet = TRUE)
}

raw <- suppressMessages(readxl::read_excel(CACHE, sheet = "Hoja1", col_names = FALSE))
raw <- as.data.frame(raw)
COLS <- 33:49                      # 0-based 32..48 in the python script
hdr  <- as.character(unlist(raw[3, COLS]))
sub  <- as.character(unlist(raw[2, COLS]))
cat("source header row (cols 32-48, 0-based):\n  ", paste(hdr, collapse = " | "), "\n", sep = "")
cat("source subscale row:\n  ", paste(sub, collapse = " | "), "\n\n", sep = "")

hdr_ok <- identical(hdr, paste("Item", 1:17))

# canonical UWES-17 subscale assignment (Schaufeli & Bakker, UWES Preliminary Manual)
CANON <- c("VIG","DED","ABS","VIG","DED","ABS","DED","VIG","ABS",
           "DED","ABS","VIG","DED","ABS","VIG","ABS","VIG")
n_sub_match <- sum(sub == CANON)
cat(sprintf("subscale fingerprint: %d/17 positions agree with canonical UWES-17\n", n_sub_match))
cat("  canonical: ", paste(CANON, collapse = " "), "\n", sep = "")

# ---- check 1: live per-item mean/n vs the source column at that position ----
d <- irw::irw_fetch(TABLE)
live_m <- tapply(d$resp, d$item, mean)
live_n <- tapply(d$resp, d$item, length)
items  <- paste0("item_", 1:17)

srcv <- lapply(COLS, function(j) {
    v <- suppressWarnings(as.numeric(unlist(raw[4:nrow(raw), j])))
    v[!is.na(v) & v >= 0 & v <= 6]
})
src_m <- vapply(srcv, mean,   numeric(1))
src_n <- vapply(srcv, length, integer(1))

cat(sprintf("\n%-9s %-8s %10s %10s %9s %5s %5s\n",
            "item", "hdr", "live mean", "src mean", "diff", "liveN", "srcN"))
for (i in 1:17)
    cat(sprintf("%-9s %-8s %10.4f %10.4f %9.2e %5d %5d\n",
                items[i], hdr[i], live_m[items[i]], src_m[i],
                live_m[items[i]] - src_m[i], live_n[items[i]], src_n[i]))

worst_m <- max(abs(live_m[items] - src_m))
n_ok    <- all(live_n[items] == src_n)
cat(sprintf("\nmax |live mean - source column mean| = %.3e over 17 items ; n matches: %s\n",
            worst_m, n_ok))

# shift control: the same comparison one column to the left must NOT match
shift <- lapply(COLS - 1, function(j) {
    v <- suppressWarnings(as.numeric(unlist(raw[4:nrow(raw), j])))
    v[!is.na(v) & v >= 0 & v <= 6]
})
shift_m <- vapply(shift, function(v) if (length(v)) mean(v) else NA_real_, numeric(1))
worst_shift <- max(abs(live_m[items] - shift_m), na.rm = TRUE)
cat(sprintf("control, columns shifted by one: max |diff| = %.4f (must be large)\n", worst_shift))

# ---- check 2 corroboration: subscale block structure in the live data ----
dd <- as.data.frame(d)[, c("id","item","resp")]
w <- reshape(dd, idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
R <- cor(w[, items], use = "pairwise.complete.obs")
same <- outer(CANON, CANON, "==") & upper.tri(R)
diff <- outer(CANON, CANON, "!=") & upper.tri(R)
cat(sprintf("\nlive correlations: mean same-subscale r = %.3f (%d pairs), cross-subscale r = %.3f (%d pairs)\n",
            mean(R[same]), sum(same), mean(R[diff]), sum(diff)))

cat("\nNote: this establishes the positional code->source-column tie and the tie from the\n",
    "item numbering to the manual's printed UWES-17 item numbers. It says NOTHING about\n",
    "any shipped wording -- none was shipped. The block is on the UWES rights clause,\n",
    "not on the mapping. The correlation figure is corroboration only: UWES subscales\n",
    "are known to overlap heavily, so it cannot separate items within a subscale.\n", sep = "")

ok <- hdr_ok && n_sub_match == 17 && worst_m < 1e-9 && n_ok && worst_shift > 0.2
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
