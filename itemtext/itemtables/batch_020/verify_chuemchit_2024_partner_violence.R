# Mapping verification for chuemchit_2024_partner_violence.
#
# CLAIM under test: each live item code names a specific violence TYPE, and the
# item_text shipped for it is the set of questionnaire questions for that type.
#   peco12 = economic (Q75/Q78/Q81)   pcyb12 = cyber (Q86/Q89)
#   ppsy12 = psychological (Q93/Q96/Q99)
#   pphy12 = physical (Q103/Q106/Q109/Q112)
#   psex12 = sexual (Q116/Q119/Q122)
# Each act question is followed by a "did this happen in the last 12 months
# (March 2020 until now) or before the past 12 months or both?" question coded
# 1=only last 12 months, 2=only before, 3=both. The derived "*12" indicator
# should therefore be: any of that type's timing questions in {1,3}.
#
# This is falsifiable: if item_text for, say, pcyb12 and ppsy12 were swapped,
# the reconstruction would disagree on hundreds of rows and the positive counts
# (26 vs 46) would cross.

suppressMessages(library(irw))

TABLE <- "chuemchit_2024_partner_violence"
S2 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0300388.s002")

tf <- tempfile(fileext = ".xlsx")
utils::download.file(S2, tf, quiet = TRUE,
                     headers = c("User-Agent" = "IRW-itemtext/1.0"))
suppressMessages(library(readxl))
d <- as.data.frame(readxl::read_excel(tf))

# Timing questions per violence type, read off the S1 questionnaire's own
# block structure (its routing lines name the types: "If you have never
# experienced economic violence, skip to Q85", "...harassment or cyber
# bullying, please skip to Q93", "...any of psychological violence, please
# skip to Question Q103", "...physical violence, please skip to Q116").
GROUPS <- list(
  peco12 = c("q77","q80","q83"),
  pcyb12 = c("q88","q91"),
  ppsy12 = c("q95","q98","q101"),
  pphy12 = c("q105","q108","q111","q114"),
  psex12 = c("q118","q121","q124"))

base <- !is.na(d$peco12)          # 405 partnered respondents
cat(sprintf("respondents in S2: %d ; with partner-violence module: %d\n",
            nrow(d), sum(base)))

cat("\n-- A. derived indicator reproduced from the type's own timing questions --\n")
cat(sprintf("%-8s %10s %10s %12s\n", "item", "recon n1", "S2 n1", "row agree"))
okA <- TRUE
for (it in names(GROUPS)) {
    g <- d[, GROUPS[[it]], drop = FALSE]
    pred <- as.numeric(apply(g, 1, function(r) any(r %in% c(1, 3))))
    pred[!base] <- NA
    act <- d[[it]]
    agree <- sum((pred == act) | (is.na(pred) & is.na(act)), na.rm = TRUE)
    cat(sprintf("%-8s %10d %10d %7d/%d\n", it, sum(pred, na.rm = TRUE),
                sum(act, na.rm = TRUE), agree, nrow(d)))
    if (agree != nrow(d)) okA <- FALSE
}

cat("\n-- B. cross-type check: does each type's reconstruction fit ONLY its own code? --\n")
recon <- sapply(names(GROUPS), function(it) {
    g <- d[, GROUPS[[it]], drop = FALSE]
    p <- as.numeric(apply(g, 1, function(r) any(r %in% c(1, 3))))
    p[!base] <- NA; p })
M <- outer(seq_along(GROUPS), seq_along(GROUPS), Vectorize(function(i, j)
    sum(recon[base, i] == d[base, names(GROUPS)[j]])))
dimnames(M) <- list(paste0("recon_", names(GROUPS)), names(GROUPS))
print(M)
okB <- all(diag(M) == sum(base)) && all(M[row(M) != col(M)] < sum(base))

cat("\n-- C. live IRW table agrees with the S2 columns, per item --\n")
live <- tryCatch(irw::irw_fetch(TABLE), error = function(e) NULL)
okC <- NA
if (!is.null(live)) {
    cat(sprintf("%-8s %8s %8s %8s %8s\n", "item", "live n", "S2 n", "live n1", "S2 n1"))
    okC <- TRUE
    for (it in names(GROUPS)) {
        lv <- live$resp[live$item == it]
        if (length(lv) != sum(base) || sum(lv) != sum(d[[it]], na.rm = TRUE)) okC <- FALSE
        cat(sprintf("%-8s %8d %8d %8d %8d\n", it, length(lv), sum(base),
                    sum(lv), sum(d[[it]], na.rm = TRUE)))
    }
} else {
    cat("live fetch unavailable; A+B alone still test the mapping in the source file\n")
}

cat("\nWhat this does NOT establish: it pins each item code to a violence TYPE and\n",
    "to that type's question block exactly, but it cannot order the questions\n",
    "WITHIN a block (the block is collapsed into one binary indicator anyway), and\n",
    "it says nothing about the English wording being what respondents heard --\n",
    "the survey was interpreted orally into Lao/Burmese/Khmer.\n", sep = "")

pass <- okA && okB && (is.na(okC) || okC)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
