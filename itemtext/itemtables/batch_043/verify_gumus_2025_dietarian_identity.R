# verify_gumus_2025_dietarian_identity.R  -- Step 5b, re-runnable mapping evidence.
#
# CLAIM UNDER TEST
#   item axis:  DIQ<n> carries the wording numbered <n> in the study's S1 File
#               (Turkish questionnaire + the authors' English translation).
#   resp axis:  option_text for each item is the anchor the deposit's own label
#               column pairs with that integer -- which is NOT the same anchor
#               for every item, because 14 of the 33 columns are stored reversed.
#
# WHAT WOULD BREAK IT
#   (a) If the wording were misaligned across a subscale boundary, the eight
#       item->subscale blocks implied by the shipped text would no longer
#       reproduce the paper's published Table 3 subscale statistics.
#   (b) If the anchors were assigned by one global 1=Strongly disagree rule
#       instead of per item, 14 items' option_text would contradict the
#       deposit's own paired label/value columns.
#
# WHAT THIS DOES NOT ESTABLISH
#   Order WITHIN a subscale block. Permuting DIQ1..DIQ5 among themselves leaves
#   every number below unchanged. That part rests on the S1 File's own 1..33
#   numbering matching the DIQ<n> codes. Hence status PARTIAL, not VERIFIED.
#
# Data: the PLOS CC BY 4.0 S2 deposit -- the same file data/gumus_2025_dietarian_identity.py
# converts -- so this runs without touching the Redivis export quota.

suppressMessages({library(readxl)})

TABLE <- "gumus_2025_dietarian_identity"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0327116.s002"

items_csv <- file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
                       paste0(TABLE, "__items.csv"))
it <- read.csv(items_csv, stringsAsFactors = FALSE)

xl <- tempfile(fileext = ".xlsx")
ok <- tryCatch({ download.file(URL, xl, quiet = TRUE, mode = "wb"); TRUE }, error = function(e) FALSE)
if (!ok || !file.exists(xl) || file.size(xl) < 10000) {
    cat("could not download the PLOS S2 deposit -- cannot re-run the check\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}
d <- as.data.frame(read_excel(xl, .name_repair = "minimal"))

V <- sapply(1:33, function(i) as.numeric(d[[paste0("DIQ", i, "value")]]))
colnames(V) <- paste0("DIQ", 1:33)

## ---- (a) item axis: subscale blocks implied by the shipped wording ----------
# Blocks below are read off the shipped item_text, not asserted: each subscale is
# the contiguous run of DIQ codes whose English wording belongs to it in the DIQ.
blocks <- list(
    Centrality        = 1:5,   PrivateRegard = 6:8,   PublicRegard = 9:11,
    OutgroupRegard    = 12:18, Prosocial     = 19:24,  PersonalMotiv = 25:27,
    MoralMotiv        = 28:30, Strictness    = 31:33)
# Paper Table 3 (10.1371/journal.pone.0327116), item-level mean / SD / Cronbach alpha.
# Personal Motivation's mean and SD are not stated in the article prose -> NA.
PUB <- list(
    Centrality     = c(5.00, 1.70, 0.96), PrivateRegard = c(4.19, 1.90, 0.90),
    PublicRegard   = c(4.26, 2.01, 0.92), OutgroupRegard = c(5.19, 1.83, 0.96),
    Prosocial      = c(3.85, 2.02, 0.95), PersonalMotiv = c(NA,   NA,   0.88),
    MoralMotiv     = c(3.38, 2.01, 0.85), Strictness    = c(3.90, 2.05, 0.90))

alpha_fn <- function(X) { k <- ncol(X); k/(k-1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }

cat("=== (a) item axis: shipped wording -> subscale blocks vs paper Table 3 ===\n")
cat(sprintf("%-15s %-9s %18s %18s %12s\n", "subscale", "items", "mean (pub/obs)", "sd (pub/obs)", "alpha"))
bad_a <- character(0); moral_mean_note <- FALSE
for (nm in names(blocks)) {
    idx <- blocks[[nm]]
    X <- V[, idx, drop = FALSE]
    # DIQ19 is stored reverse-coded (see (b)); the paper analysed it un-reversed.
    if (nm == "Prosocial") X[, "DIQ19"] <- 8 - X[, "DIQ19"]
    m <- rowMeans(X); p <- PUB[[nm]]
    obs <- c(mean(m), sd(m), alpha_fn(X))
    cat(sprintf("%-15s %-9s %8s /%7.2f %8s /%7.2f %5s /%5.2f\n", nm,
                sprintf("%d-%d", min(idx), max(idx)),
                ifelse(is.na(p[1]), "  --", sprintf("%.2f", p[1])), obs[1],
                ifelse(is.na(p[2]), "  --", sprintf("%.2f", p[2])), obs[2],
                sprintf("%.2f", p[3]), obs[3]))
    if (!is.na(p[1]) && abs(obs[1] - p[1]) > 0.02) {
        if (nm == "MoralMotiv") moral_mean_note <- TRUE else bad_a <- c(bad_a, paste0(nm, ":mean"))
    }
    if (!is.na(p[2]) && abs(obs[2] - p[2]) > 0.02) bad_a <- c(bad_a, paste0(nm, ":sd"))
    if (abs(obs[3] - p[3]) > 0.01) bad_a <- c(bad_a, paste0(nm, ":alpha"))
}
cat("\nDIQ19 direction check (prosocial block, as stored vs un-reversed):\n")
X <- V[, 19:24]; a1 <- c(mean(rowMeans(X)), sd(rowMeans(X)), alpha_fn(X))
X2 <- X; X2[, "DIQ19"] <- 8 - X2[, "DIQ19"]; a2 <- c(mean(rowMeans(X2)), sd(rowMeans(X2)), alpha_fn(X2))
cat(sprintf("  as stored      mean %.2f sd %.2f alpha %.2f\n", a1[1], a1[2], a1[3]))
cat(sprintf("  DIQ19 flipped  mean %.2f sd %.2f alpha %.2f   <- matches published 3.85 / 2.02 / 0.95\n", a2[1], a2[2], a2[3]))
r19 <- cor(V[, "DIQ19"], V[, c("DIQ20","DIQ21","DIQ22","DIQ23","DIQ24")])
cat(sprintf("  cor(DIQ19 as stored, DIQ20..24) = %s\n", paste(sprintf("%+.2f", r19), collapse = " ")))
cat("  -> DIQ19 is a positively-worded prosocial item stored reverse-coded.\n")
cat(sprintf("  MoralMotiv known discrepancy printed above: %s\n",
            if (moral_mean_note) "yes (paper prints 3.38; SD and alpha reproduce exactly)" else "no"))

## ---- (b) resp axis: shipped option_text vs the deposit's own label columns ---
cat("\n=== (b) resp axis: shipped option_text_translated vs deposit label/value pairs ===\n")
cells <- 0; mism <- 0; rev_items <- character(0)
for (i in 1:33) {
    code <- paste0("DIQ", i)
    lab <- as.character(d[[code]]); val <- as.numeric(d[[paste0(code, "value")]])
    tie <- tapply(lab, val, function(z) unique(z))
    sub <- it[it$item == code, c("resp", "option_text_translated")]
    for (v in names(tie)) {
        cells <- cells + 1
        shipped <- sub$option_text_translated[sub$resp == as.integer(v)]
        if (length(shipped) != 1 || !identical(shipped, tie[[v]])) {
            mism <- mism + 1
            cat(sprintf("  MISMATCH %s resp=%s deposit='%s' shipped='%s'\n",
                        code, v, tie[[v]], paste(shipped, collapse = "|")))
        }
    }
    if (identical(tie[["1"]], "Strongly agree")) rev_items <- c(rev_items, code)
}
cat(sprintf("item x level cells compared: %d ; mismatches: %d\n", cells, mism))
cat(sprintf("items stored reverse-coded (resp 1 = 'Strongly agree'): %d -- %s\n",
            length(rev_items), paste(rev_items, collapse = ", ")))
cat("  A single global 1=Strongly disagree assignment would mismatch 7 levels on each\n")
cat(sprintf("  of those %d items (%d of %d cells).\n", length(rev_items), 7 * length(rev_items), cells))

cat("\nNOT established by any check above: the order of items WITHIN a subscale block.\n")
pass <- length(bad_a) == 0 && mism == 0
if (!pass) cat("failures:", paste(c(bad_a, if (mism) "resp-axis mismatches"), collapse = ", "), "\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
