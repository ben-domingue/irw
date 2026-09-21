# verify_offlinefriend_ofaq.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: item code T1_OFAQ_k carries the k-th statement of the O-FAQ as
# numbered in the study's own materials (Satchell et al. 2021 postprint Table 1, and
# the OSF file "Offline Friend Addiction Questionnaire.docx", which number the 37
# statements 1..37; the administered questionnaire lists them in that same order).
# Nothing in the IRW table's own codes carries the wording, so the numbering is the
# only tie -- if the shipped item_text for, say, items 21 and 22 were swapped, every
# other gate in this pipeline would still pass.
#
# THE FALSIFIABLE PREDICTION: the postprint's Table 1 publishes M (SD) per numbered
# item for the EXPLORATORY sample. The IRW table pools the whole Time-1 sample
# (802 respondents), whose means run ~0.1 higher, so the comparison is made on the
# exploratory subsample. Participants 1-417 except 397 (n = 416) are the rows the
# study flagged Used_Time1_EFA == 1 in OFAQData.xlsx, and `id` in the IRW table is
# that Participant number (data/offline_friend.R: `id <- x$Participant`).
#
# PART A (item axis)  -- per-item M/SD vs published, plus a nearest-neighbour
#                        assignment test: each item's own published pair must be the
#                        CLOSEST of all 37, which is what makes this a mapping check
#                        rather than a goodness-of-fit check.
# PART B (resp axis)  -- the raw OSF workbook stores label strings while IRW stores
#                        1..5; every item x level count must agree cell for cell.
#                        Needs network + readxl; skipped (not failed) without them.

suppressMessages(library(irw))

TABLE <- "offlinefriend_ofaq"
EFA_IDS <- setdiff(1:417, 397)          # Used_Time1_EFA == 1, n = 416

# Satchell et al. (2021) Behav Res Methods, postprint Table 1: M (SD), 1-5 scale.
PUB_M  <- c(3.25,3.03,3.88,2.86,3.27,2.53,2.98,3.06,3.16,2.64,2.61,3.29,1.97,
            2.28,1.99,3.29,3.19,1.83,2.53,3.75,3.18,2.94,2.45,3.81,2.11,3.88,
            3.20,3.31,1.88,3.78,3.46,2.08,3.15,3.23,2.82,2.26,2.82)
PUB_SD <- c(1.08,1.08,0.89,1.15,1.14,1.07,1.25,1.26,1.20,1.11,1.13,1.10,1.05,
            1.14,1.02,0.97,1.12,0.91,1.02,0.88,1.17,1.16,1.08,0.98,0.96,1.00,
            1.09,1.08,0.78,0.92,1.01,1.08,1.08,1.15,1.28,1.06,1.12)
# Item 37's published MEAN is excluded: 2.82 is a verbatim repeat of item 35's
# printed mean and is a misprint in the paper's table. Its published SD (1.12) does
# reproduce (observed 1.123). Item 37 is pinned by exclusion -- see the note below.
SKIP_MEAN <- 37L
TOL <- 0.02

items <- paste0("T1_OFAQ_", 1:37)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
sub <- d[as.numeric(d$id) %in% EFA_IDS, ]
cat(sprintf("exploratory subsample: %d respondents, %d rows\n",
            length(unique(sub$id)), nrow(sub)))

obs_m  <- sapply(items, function(it) mean(sub$resp[sub$item == it], na.rm = TRUE))
obs_sd <- sapply(items, function(it) sd(  sub$resp[sub$item == it], na.rm = TRUE))

cat("\n-- PART A: per-item M (SD), live exploratory subsample vs postprint Table 1 --\n")
cat(sprintf("%-12s %8s %8s %8s %8s %8s  %s\n",
            "item", "pub_M", "obs_M", "pub_SD", "obs_SD", "dist", "nearest published item"))
fail_a <- 0L
for (k in 1:37) {
    dist <- sqrt((obs_m[k] - PUB_M)^2 + (obs_sd[k] - PUB_SD)^2)
    near <- order(dist)[1]
    own  <- dist[k]
    flag <- ""
    if (k == SKIP_MEAN) {
        # mean excluded; check SD only, and require every other item to have been
        # claimed by itself so that 37 is the one left over.
        if (abs(obs_sd[k] - PUB_SD[k]) > TOL) { flag <- "  <-- SD MISMATCH"; fail_a <- fail_a + 1L }
        else flag <- "  (mean misprinted in source; SD matches; pinned by exclusion)"
    } else {
        if (near != k || own > TOL) { flag <- "  <-- FAIL"; fail_a <- fail_a + 1L }
    }
    cat(sprintf("%-12s %8.2f %8.3f %8.2f %8.3f %8.4f  %-12s%s\n",
                items[k], PUB_M[k], obs_m[k], PUB_SD[k], obs_sd[k], own,
                items[near], flag))
}
cat(sprintf("\nPART A: %d of 37 items failed; max deviation over the 36 checked items = %.4f\n",
            fail_a, max(sqrt((obs_m[-SKIP_MEAN] - PUB_M[-SKIP_MEAN])^2 +
                             (obs_sd[-SKIP_MEAN] - PUB_SD[-SKIP_MEAN])^2))))

cat("\n-- PART B: option_text <-> resp, raw OSF labels vs live integers --\n")
fail_b <- 0L
ok_b <- FALSE
try({
    suppressMessages(library(readxl))
    f <- file.path(tempdir(), "OFAQData.xlsx")
    if (!file.exists(f))
        utils::download.file("https://osf.io/download/tq9en/", f, quiet = TRUE, mode = "wb")
    raw <- as.data.frame(readxl::read_excel(f, sheet = "All Responses (anon)"))
    raw <- raw[!duplicated(raw$Participant), ]
    lev <- c("Strongly Disagree", "Disagree", "Neither Agree nor Disagree",
             "Agree", "Strongly Agree")          # data/offline_friend.R's match() order
    cells <- 0L
    for (k in 1:37) {
        r <- factor(match(raw[[items[k]]], lev), levels = 1:5)
        l <- factor(d$resp[d$item == items[k]],  levels = 1:5)
        a <- as.integer(table(r)); b <- as.integer(table(l))
        cells <- cells + 5L
        if (!identical(a, b)) {
            fail_b <- fail_b + 1L
            cat(sprintf("  %s raw %s vs live %s  <-- MISMATCH\n", items[k],
                        paste(a, collapse = "/"), paste(b, collapse = "/")))
        }
        if (k %in% c(1L, 37L))
            cat(sprintf("  %s raw %s | live %s\n", items[k],
                        paste(a, collapse = "/"), paste(b, collapse = "/")))
    }
    cat(sprintf("  %d item x level cells compared, %d items mismatched\n", cells, fail_b))
    ok_b <- TRUE
}, silent = TRUE)
if (!ok_b) cat("  SKIPPED (no network or readxl) -- Part A alone decides the verdict\n")

cat("\nWhat this does NOT establish: Part A pins each code to a NUMBER in the study's\n",
    "own item list; it cannot detect an error inside that list itself (i.e. if the\n",
    "postprint table and the questionnaire agreed on a wrong statement for a number).\n",
    "Item 37's mean is a source misprint, so item 37 rests on its SD plus the fact\n",
    "that the other 36 items each claim themselves, leaving 37 as the only residue.\n", sep = "")

cat(if (fail_a == 0L && fail_b == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
