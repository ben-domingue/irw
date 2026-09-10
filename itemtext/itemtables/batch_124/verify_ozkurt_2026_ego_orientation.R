# verify_ozkurt_2026_ego_orientation.R
#
# What is being verified: item <-> item_text for EGOQ1..EGOQ10.
#
# The wording ships from S6 File (the study's "Measurement Instruments Used in
# the Study" DOCX), whose Table 2 lists all 10 EGOQ items against an "Original
# item no." column, 1..10. The live item codes are EGOQ1..EGOQ10, taken verbatim
# from the S2 File .sav column names by data/ozkurt_2026_wrestlers.py (it melts
# columns matching r"EGOQ\d+$" and renames nothing). So the claim under test is:
# EGOQ<k> is the item S6 numbers <k>.
#
# Four falsifiable links, none of which is an item count:
#
#   Link A (route 9, response-frequency matching). S1 File .xlsx holds the same
#     374 respondents under DIFFERENT headers that NUMBER the goal-orientation
#     columns "2.Ego Orientation" .. "10.Task Orientation". Rows are ordered
#     differently between the two deposits, so the columns are tied by their
#     5-level response-count vectors. For each k in 2..10, the count vector of
#     S1 header "k.<Subdim>" must equal that of .sav column EGOQ<k> and must
#     match NO OTHER EGOQ column -- a unique bijection, which is what rules out
#     a permutation. (S1 File has no column for item 1; EGOQ1 falls out by
#     elimination and is covered by links C and D.)
#   Link B. The live IRW table's per-item count vectors must equal the .sav's,
#     so the bijection reaches the shipped codes and not just the source file.
#   Link C. The .sav variable label for EGOQ<k> ("Task orientation G1" ..
#     "Ego orientation E5") must name the same subdimension S6 Table 2 gives for
#     item k, AND the same one the S1 header spells.
#   Link D (external, not written by these authors). The GOEM's published
#     scoring key at the instrument's own site (Bangor University, Markland &
#     Petherick) assigns items 1,3,4,6,9 to Task and 2,5,7,8,10 to Ego. The
#     study's numbering must reproduce that exactly, otherwise S6's numbering is
#     the authors' own invention rather than the instrument's.
#
# Anchor direction (route 8) is checked too: S6 states 1 = Strongly Disagree ..
# 5 = Strongly Agree, and the five task items should sit at the ceiling in a
# sample of national-team wrestlers while the ego items sit lower -- the
# reversed reading inverts both.
#
# What this does NOT establish: within each polarity block, links A-C rest on
# the authors' own two files agreeing. Link D is what makes the numbering
# external, and it pins subscale membership for all 10 -- but the canonical GOEM
# key cannot separate two items inside the same subscale. The remaining
# separation comes from the item wording itself pairing one-for-one and IN ORDER
# with the canonical GOEM form (item 1 "exercise to the best of my ability",
# 2 "Other exercisers don't do as well as me", 3 "I make progress", 4 "achieve
# the exercise goal I set for myself", 5 "show other exercisers that I'm better
# than everyone else", 6 "I feel like I've improved", 7 "prove to myself that I
# am the only one who can do a certain exercise task", 8 "more capable than
# other exercisers", 9 "a level that reflects personal improvement", 10 "prove
# to others that I'm the best"), which is checked by eye in provenance rather
# than by this script.
#
# The live table is 374 x 10 = 3740 rows, so irw_fetch() here is a negligible
# export.

suppressMessages(library(irw))

TABLE <- "ozkurt_2026_ego_orientation"
BASE  <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0353067."

ITEMS <- paste0("EGOQ", 1:10)

# S6 File Table 2: subdimension per "Original item no."
S6_SUB <- c("Task", "Ego", "Task", "Task", "Ego", "Task", "Ego", "Ego", "Task", "Ego")

# Link D: canonical GOEM scoring key, exercise-motivation.bangor.ac.uk/goem/goemmain.php
GOEM_TASK <- c(1, 3, 4, 6, 9)
GOEM_EGO  <- c(2, 5, 7, 8, 10)

ok <- TRUE

## ---- fetch the two deposits -------------------------------------------------
tmp_x <- tempfile(fileext = ".xlsx"); tmp_s <- tempfile(fileext = ".sav")
download.file(paste0(BASE, "s001"), tmp_x, quiet = TRUE, mode = "wb")
download.file(paste0(BASE, "s002"), tmp_s, quiet = TRUE, mode = "wb")

x   <- as.data.frame(readxl::read_excel(tmp_x))
sav <- haven::read_sav(tmp_s)
stopifnot(all(ITEMS %in% names(sav)))

cnt <- function(v) as.integer(table(factor(as.integer(v), levels = 1:5)))
sav_cnt <- sapply(ITEMS, function(c) cnt(sav[[c]]))

## ---- Link B: live table vs the .sav ----------------------------------------
d <- irw::irw_fetch(TABLE)
live_cnt <- sapply(ITEMS, function(i) cnt(d$resp[d$item == i]))
cat("Link B -- live per-item response counts vs S2 File .sav column counts\n")
cat(sprintf("%-8s %-22s %-22s %s\n", "item", "live 1..5", ".sav 1..5", "match"))
for (i in seq_along(ITEMS)) {
    m <- identical(live_cnt[, i], sav_cnt[, i]); ok <- ok && m
    cat(sprintf("%-8s %-22s %-22s %s\n", ITEMS[i],
                paste(live_cnt[, i], collapse = " "),
                paste(sav_cnt[, i],  collapse = " "), ifelse(m, "yes", "NO")))
}

## ---- Link A: S1 numbered header -> .sav column, uniquely --------------------
hdr <- paste0(2:10, ".", ifelse(S6_SUB[2:10] == "Task", "Task", "Ego"), " Orientation")
stopifnot(all(hdr %in% names(x)))
cat("\nLink A -- S1 File numbered header vs .sav column, by 5-level count vector\n")
cat(sprintf("%-22s %-22s %-10s %s\n", "S1 header", "counts 1..5", "expected",
            "unique match among EGOQ1-10"))
for (i in seq_along(hdr)) {
    cc <- cnt(x[[hdr[i]]])
    hits <- ITEMS[apply(sav_cnt, 2, function(z) identical(z, cc))]
    want <- ITEMS[i + 1]
    good <- length(hits) == 1 && hits == want; ok <- ok && good
    cat(sprintf("%-22s %-22s %-10s %s\n", hdr[i], paste(cc, collapse = " "), want,
                paste(hits, collapse = ",")))
}
cat("EGOQ1 has no S1 File column (that deposit omits item 1); it is the single\n",
    "remaining code after the 9 above are pinned.\n", sep = "")

## ---- Link C + D: subdimension agreement, three files + the instrument -------
lab <- sapply(ITEMS, function(c) {
    l <- attr(sav[[c]], "label"); if (is.null(l)) NA_character_ else l
})
cat("\nLink C/D -- .sav variable label vs S6 Table 2 vs canonical GOEM scoring key\n")
cat(sprintf("%-8s %-24s %-8s %-8s %s\n", "item", ".sav label", "S6", "GOEM", "agree"))
for (i in seq_along(ITEMS)) {
    lab_sub <- if (grepl("^Task", lab[i])) "Task" else if (grepl("^Ego", lab[i])) "Ego" else "?"
    goem <- if (i %in% GOEM_TASK) "Task" else if (i %in% GOEM_EGO) "Ego" else "?"
    agree <- identical(lab_sub, S6_SUB[i]) && identical(goem, S6_SUB[i])
    ok <- ok && agree
    cat(sprintf("%-8s %-24s %-8s %-8s %s\n", ITEMS[i], lab[i], S6_SUB[i], goem,
                ifelse(agree, "yes", "NO")))
}

## ---- anchor direction (route 8) --------------------------------------------
mu <- tapply(d$resp, factor(d$item, levels = ITEMS), mean)
task_mu <- mean(mu[GOEM_TASK]); ego_mu <- mean(mu[GOEM_EGO])
cat("\nAnchor direction -- item means on the shipped 1 = Strongly Disagree .. 5 = Strongly Agree\n")
cat(paste(sprintf("%s=%.2f", ITEMS, mu), collapse = "  "), "\n")
cat(sprintf("task block mean %.2f (items 1,3,4,6,9); ego block mean %.2f (items 2,5,7,8,10)\n",
            task_mu, ego_mu))
dir_ok <- min(mu[GOEM_TASK]) > 4.0 && task_mu > ego_mu; ok <- ok && dir_ok
cat("Reversed anchors would read as elite wrestlers disagreeing that they feel good\n")
cat("when they do their best or improve; and the task/ego gap would invert.\n")

cat("\nNot established here: the canonical GOEM key separates the two subscales but\n")
cat("not two items inside one subscale; the within-block order rests on S6's\n")
cat("wording pairing one-for-one and in order with the canonical GOEM item list,\n")
cat("which is recorded in provenance rather than tested here.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
