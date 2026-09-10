# verify_muir_2025_resilience_behaviours.R
#
# Claim under test (two axes):
#   (A) item_text <-> item.  The IRW item code IS the verbatim column header of the
#       study's raw-data deposit (S5 File, PLOS pone.0338728), and those headers are
#       self-describing AND numbered 12..19, contiguous with the questionnaire's own
#       numbering (S3 File: Q1-Q4 demographics = cols 1-4, Q5 opinions a-g = cols 5-11,
#       Q6 behaviours a-h = cols 12-19).  The falsifiable prediction is that each
#       header's distinguishing keyword appears in exactly ONE of the eight shipped
#       item_text strings, and in the one at the matching questionnaire position.
#   (B) option_text <-> resp.  The deposit stores LABELS ("Sometimes"/"Frequently"/
#       "Always"); the IRW table stores 3/4/5.  Route 9: per item x level counts must
#       match cell for cell under Sometimes=3, Frequently=4, Always=5, and must break
#       under the reversed coding.
#
# NOTE ON EXPORT QUOTA: this table is 501 rows (~25 KB); irw_fetch() here is a
# deliberate, negligible export, needed because per-item x per-level counts are not
# available from irw_table_sets().

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE  <- "muir_2025_resilience_behaviours"
ITEMS  <- c("12_behaviours_collaboration_within_units",
            "13_behaviours_collabortion_between_units",
            "14_behaviours_adjusted_process_and_procedures",
            "15_behaviours_innovation",
            "16_behaviour_effective_communication",
            "17_behaviour_supportive_leadership",
            "18_behaviour_staff_resilience",
            "19_behaviour_staff_adaption")
# Q6 letter in S3 File (Appendix III Questionnaire) at each column position.
LETTERS8 <- c("a","b","c","d","e","f","g","h")
# Distinguishing keyword each header asserts about its item's content.
KEY <- c("collaboration within", "collaboration between",
         "processes and procedures", "Innovative",
         "Communication was effective", "leadership were supportive",
         "staff demonstrated resilience", "willingness to adapt")
LEVELS_LAB <- c("Sometimes", "Frequently", "Always")
CODE_OK    <- c(Sometimes = 3, Frequently = 4, Always = 5)
CODE_REV   <- c(Sometimes = 5, Frequently = 4, Always = 3)

URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0338728.s005")
xl <- file.path(tempdir(), "muir_s005.xlsx")
cached <- "../../.cache/muir_2025_resilience_behaviours/s005.xlsx"
if (file.exists(cached)) xl <- cached else
    download.file(URL, xl, quiet = TRUE, mode = "wb",
                  headers = c("User-Agent" = "IRW-Finder/1.0 (ben.domingue@gmail.com)"))
raw <- readxl::read_excel(xl)

items_csv <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                       paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- paste0(TABLE, "__items.csv")
ship <- read.csv(items_csv, stringsAsFactors = FALSE)
shiptxt <- tapply(ship$item_text, ship$item, function(x) unique(x)[1])[ITEMS]

## ---- (A) header keyword -> shipped item_text, injectivity ------------------
cat("=== (A) item code (= deposit column header) vs shipped item_text ===\n")
hits <- matrix(FALSE, 8, 8, dimnames = list(ITEMS, ITEMS))
for (i in 1:8) for (j in 1:8)
    hits[i, j] <- grepl(KEY[i], shiptxt[j], fixed = TRUE)
okA <- TRUE
for (i in 1:8) {
    n <- sum(hits[i, ])
    diag_ok <- hits[i, i]
    cat(sprintf("%-46s Q6%s  keyword %-30s matches %d of 8 shipped texts; own text: %s\n",
                ITEMS[i], LETTERS8[i], paste0("'", KEY[i], "'"), n,
                if (diag_ok) "YES" else "NO"))
    if (n != 1 || !diag_ok) okA <- FALSE
}
cat(sprintf("(A) each header keyword matches exactly one shipped item_text, its own: %s\n",
            if (okA) "TRUE (8/8)" else "FALSE"))
cat("   Header order also matches questionnaire order: cols 12..19 = Q6 a..h.\n")

## ---- (B) route 9: per item x level counts ----------------------------------
cat("\n=== (B) option_text <-> resp, per item x level counts (route 9) ===\n")
live <- irw::irw_fetch(TABLE)
mis_ok <- 0; mis_rev <- 0
cat(sprintf("%-46s %-10s %6s %6s\n", "item", "label", "raw", "live"))
for (i in 1:8) {
    rv <- raw[[ITEMS[i]]]
    for (lab in LEVELS_LAB) {
        n_raw  <- sum(!is.na(rv) & rv == lab)
        n_ok   <- sum(live$item == ITEMS[i] & live$resp == CODE_OK[[lab]])
        n_rev  <- sum(live$item == ITEMS[i] & live$resp == CODE_REV[[lab]])
        cat(sprintf("%-46s %-10s %6d %6d\n", ITEMS[i], lab, n_raw, n_ok))
        if (n_raw != n_ok)  mis_ok  <- mis_ok + 1
        if (n_raw != n_rev) mis_rev <- mis_rev + 1
    }
}
cat(sprintf("\nmismatched cells under Sometimes=3/Frequently=4/Always=5 : %d of 24\n", mis_ok))
cat(sprintf("mismatched cells under the reversed coding                : %d of 24\n", mis_rev))

cat("\nWhat this does NOT establish: (A) is a keyword tie between the deposit's own\n",
    "column header and the questionnaire statement at the same position -- it rules out\n",
    "any permutation of the eight items, but it is not an independent statistical\n",
    "identification of each item, and the source publishes no per-item M(SD) to give\n",
    "one. It says nothing about the transcribed `instructions`. (B) pins the direction\n",
    "of the frequency scale but only over the three levels respondents used; Never=1 and\n",
    "Rarely=2 were never selected and are absent from the table by design.\n", sep = "")

cat(if (okA && mis_ok == 0 && mis_rev > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
