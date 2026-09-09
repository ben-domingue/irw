# verify_han_2026_phq9.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: item codes PHQ01..PHQ09 in the live IRW table carry the
# wording listed, in that order, in the study's Translation Codebook
# (peerj-14-20868-s010.docx, Table "Original text (Chinese) | English
# translation"), whose English column is byte-identical to the column headers
# of the administered questionnaire export S2 (peerj-14-20868-s002.xlsx).
#
# TWO ROUTES, BOTH RUN HERE.
#
# Route 9 (response-frequency / joint-pattern matching) -- PRIMARY.
#   S2 stores LABELS ("Never", "Several days", ...) under English item-wording
#   headers; the live IRW table stores integers 0-3 under PHQ01..PHQ09. If the
#   assumed column order is right, every one of the 2,086 live 9-item response
#   vectors must occur as a row of S2 (S2 holds 2,630 respondents; 532 were
#   dropped for missing ISI, plus 12 others, leaving the analytic 2,086).
#   Any permutation of the wording-to-code assignment breaks that containment.
#
# Route 1 (published per-item means) -- SECONDARY, and weaker here: paper
#   Table 2 gives PHQ1 Anhedonia 0.36 ... PHQ9 Suicide ideation 0.09, but
#   PHQ6 (0.19) and PHQ7 (0.20) sit 0.01 apart, so means alone do not separate
#   that pair. Route 9 does.
#
# NOTE ON THE FETCH: this table is 18,774 rows, so irw_fetch() is a trivial
# export here; the quota rule that bans it for large tables is not in play.

suppressMessages({library(irw); library(readxl)})

TABLE <- "han_2026_phq9"
ITEMS <- sprintf("PHQ%02d", 1:9)

# --- live data, wide ---------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d <- d[, c("id", "item", "resp")]
wide <- reshape(as.data.frame(d), idvar = "id", timevar = "item",
                direction = "wide")
A <- as.matrix(wide[, paste0("resp.", ITEMS)])
storage.mode(A) <- "integer"
cat(sprintf("live: %d respondents x %d items\n", nrow(A), ncol(A)))

# --- Route 1: published per-item means (paper Table 2) ------------------------
PUBLISHED <- c(0.36, 0.25, 0.56, 0.41, 0.24, 0.19, 0.20, 0.22, 0.09)
obs <- colMeans(A)
cat("\n-- Route 1: per-item mean vs paper Table 2 --\n")
cat(sprintf("%-7s %-22s %10s %10s %8s\n", "item", "paper label", "published", "observed", "diff"))
LAB <- c("Anhedonia","Sad Mood","Sleep problems","Fatigue","Appetite",
         "Guilt","Concentration","Motor problems","Suicide ideation")
for (i in 1:9)
    cat(sprintf("%-7s %-22s %10.2f %10.3f %8.3f\n",
                ITEMS[i], LAB[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i]))
worst <- max(abs(obs - PUBLISHED))
cat(sprintf("largest deviation: %.4f (tolerance 0.010)\n", worst))
route1 <- worst <= 0.010

# --- Route 9: joint-pattern containment against S2 ---------------------------
url <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13048223/supplementaryFiles"
zp <- tempfile(fileext = ".zip"); dir <- tempfile(); dir.create(dir)
ok <- tryCatch({
    download.file(url, zp, quiet = TRUE, mode = "wb")
    unzip(zp, files = "peerj-14-20868-s002.xlsx", exdir = dir); TRUE
}, error = function(e) FALSE)

route9 <- NA
if (!ok) {
    cat("\n-- Route 9: SKIPPED, could not fetch Europe PMC supplementary zip --\n")
} else {
    s2 <- readxl::read_excel(file.path(dir, "peerj-14-20868-s002.xlsx"))
    hdr <- names(s2)[2:10]
    MAP <- c("Never" = 0L, "Several days" = 1L,
             "More than half the days" = 2L, "Nearly every day" = 3L)
    B <- sapply(hdr, function(h) unname(MAP[as.character(s2[[h]])]))
    cat(sprintf("\n-- Route 9: S2 questionnaire export, %d respondents --\n", nrow(B)))
    cat("S2 column order (first 9 item columns), as shipped in item_text_translated:\n")
    for (i in 1:9) cat(sprintf("  %s  %s\n", ITEMS[i], substr(hdr[i], 1, 60)))

    key <- function(M) apply(M, 1, paste, collapse = "-")
    contain <- function(perm) {
        ta <- table(key(A)); tb <- table(key(B[, perm, drop = FALSE]))
        sum(pmin(ta, tb[match(names(ta), names(tb))]), na.rm = TRUE)
    }
    id <- 1:9
    n_id <- contain(id)
    cat(sprintf("\nlive response vectors found in S2 under the SHIPPED order: %d of %d (%.1f%%)\n",
                n_id, nrow(A), 100 * n_id / nrow(A)))
    best <- 0; bestp <- ""
    for (i in 1:8) for (j in (i + 1):9) {
        p <- id; p[c(i, j)] <- p[c(j, i)]
        v <- contain(p)
        if (v > best) { best <- v; bestp <- sprintf("swap %s<->%s", ITEMS[i], ITEMS[j]) }
    }
    cat(sprintf("best of the 36 pairwise swaps: %d (%.1f%%)  [%s]\n",
                best, 100 * best / nrow(A), bestp))
    # reversed option coding must also fail
    Brev <- 3L - B
    tb <- table(key(Brev)); ta <- table(key(A))
    n_rev <- sum(pmin(ta, tb[match(names(ta), names(tb))]), na.rm = TRUE)
    cat(sprintf("reversed option coding (Never=3 .. Nearly every day=0): %d (%.1f%%)\n",
                n_rev, 100 * n_rev / nrow(A)))
    route9 <- (n_id == nrow(A)) && (best < nrow(A)) && (n_rev < nrow(A))
}

cat("\nWhat this does NOT establish: nothing about the instructions or a recall\n",
    "window (the deposit publishes none), and nothing about the Chinese wording of\n",
    "the response anchors (only the English labels were published). It DOES\n",
    "separate every item from every other item, and it fixes Never=0 .. Nearly\n",
    "every day=3 rather than the reverse.\n", sep = "")

pass <- route1 && isTRUE(route9)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
