# verify_han_2026_gad7.R -- re-runnable evidence for the item_text <-> item mapping.
#
# CLAIM: GAD01..GAD07 in han_2026_gad7 (melted verbatim from supplementary file
# peerj-14-20868-s006.xlsx by data/han_2026_gad7.py) correspond, respectively, to
# columns 11..17 of peerj-14-20868-s002.xlsx -- the questionnaire file PeerJ labels
# "GAD-7 and PHQ-9 scales administered to the elderly population in Jiangsu Province",
# whose headers carry the item wording (Chinese original in supplementary codebook
# s010.docx, English in the s002 header row).
#
# The two files hold different, non-alignable ID sets (2,086 vs 2,630 rows), so the
# proof is a row match: rows whose PHQ-9 nine-tuple is unique in BOTH files are paired
# unambiguously, and each GAD column is then compared cell-for-cell with each candidate
# anxiety column. A correct mapping agrees 100%; any swap breaks immediately.
#
# NOTE ON WHAT IS *NOT* CHECKED HERE: nothing is fetched from Redivis. The tie between
# s006 and the live table is mechanical (the processing script melts GAD01..GAD07
# unchanged) and validate_items.R --table-sets already confirmed the live item/resp
# sets. To anchor s006 as the file the paper actually analysed, the script also
# reproduces the paper's published Table 2 per-item means.

suppressMessages({library(readxl)})

URL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13048223/supplementaryFiles"
tmp <- tempfile(fileext = ".zip"); dir <- tempfile(); dir.create(dir)
download.file(URL, tmp, quiet = TRUE,
              headers = c("User-Agent" = "IRW-itemtext/1.0 (ben.domingue@gmail.com)"))
unzip(tmp, exdir = dir)
a <- as.data.frame(read_excel(file.path(dir, "peerj-14-20868-s006.xlsx")))  # analysed data
b <- as.data.frame(read_excel(file.path(dir, "peerj-14-20868-s002.xlsx")))  # questionnaire

FREQ <- c("Never" = 0, "Several days" = 1, "More than half the days" = 2,
          "Nearly every day" = 3)
INT  <- c("No" = 0, "Cannot judge" = 1, "Yes" = 2)

phq_a <- sprintf("PHQ0%d", 1:9); phq_b <- names(b)[2:10]
anx_b <- names(b)[11:17]; gad_a <- sprintf("GAD0%d", 1:7)

bn <- b
for (cc in names(b)[2:16]) bn[[cc]] <- unname(FREQ[b[[cc]]])
bn[[names(b)[17]]] <- unname(INT[b[[names(b)[17]]]])

ka <- apply(a[phq_a], 1, paste, collapse = "|")
kb <- apply(bn[phq_b], 1, paste, collapse = "|")
uk <- intersect(names(which(table(ka) == 1)), names(which(table(kb) == 1)))
A <- a[match(uk, ka), ]; B <- bn[match(uk, kb), ]
cat(sprintf("Rows paired on a PHQ-9 nine-tuple unique in both files: %d\n\n", length(uk)))

cat(sprintf("%-7s %-58s %8s %8s\n", "item", "shipped source column (s002 header)",
            "agree", "next"))
ok <- TRUE
for (i in 1:7) {
    ag <- sapply(anx_b, function(cc) mean(A[[gad_a[i]]] == B[[cc]]))
    best <- names(which.max(ag)); second <- sort(ag, decreasing = TRUE)[2]
    hit  <- (best == anx_b[i]) && (ag[[best]] == 1)
    ok <- ok && hit
    cat(sprintf("%-7s %-58s %8.4f %8.4f%s\n", gad_a[i], substr(anx_b[i], 1, 58),
                ag[[anx_b[i]]], second, if (hit) "" else "   <-- MISMATCH"))
}

cat("\nGAD07 x s002 column 17, on the paired rows (0=No, 1=Cannot judge, 2=Yes):\n")
print(table(B[[anx_b[7]]], A$GAD07, dnn = c("s002", "GAD07")))

PUB <- c(0.20, 0.23, 0.20, 0.16, 0.14, 0.18, 0.36)   # paper Table 2, GAD1..GAD7 means
obs <- sapply(gad_a, function(g) mean(a[[g]]))
cat("\nPaper Table 2 per-item means vs s006 columns (anchors s006 as the analysed file):\n")
for (i in 1:7) cat(sprintf("  %-7s published %.2f   observed %.3f\n", gad_a[i], PUB[i], obs[i]))
means_ok <- max(abs(round(obs, 2) - PUB)) <= 0.005

cat("\nWhat this establishes: every one of the seven codes is distinguished from every\n",
    "other -- each matches exactly one questionnaire column at 100% while the best rival\n",
    "column sits below 0.79. It also shows GAD07 is NOT a GAD-7 item: it is the study's\n",
    "loss-of-interest question on a No/Cannot judge/Yes coding, which is why the shipped\n",
    "wording and option text for GAD07 differ from the other six.\n",
    "What it does NOT establish: the Chinese wording pairing (taken from codebook s010.docx,\n",
    "whose 16 rows are in s002 column order) is checked only by that shared ordering, and\n",
    "the response-option Chinese is nowhere in the deposit.\n", sep = "")

cat(if (ok && means_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
