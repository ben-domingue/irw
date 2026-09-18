# Verification for teq_novak_2021_scbs (#1945, batch_205).
#
# SOURCE. Novak et al. (2021), IJERPH 18:5343, CC BY; OSF deposit osf.io/z85cv.
# This is the study's SCBCS (Santa Clara Brief Compassion Scale) block. The paper
# states the scale, its length and its anchors -- "five items rated on a
# seven-point Likert scale ranging from 'Not at all true of me' (1) to 'Very true
# of me' (7)" -- but prints no items, and neither does the deposit.
#
# THE MAPPING IS A NUMBER LOOKUP AND THAT IS THE POINT. The live codes are
# SCBCS_1..SCBCS_5, taken straight from the source columns by data/teq_novak_2021.R
# (select(SCBCS_1:SCBCS_5)), and the SCBCS is a numbered five-item scale. The
# wording ships from an independent CC BY reproduction that lists the items
# against the same numbering (PMC8626830, Table 1: "SCBCS_1 Santa Clara Brief
# Compassion Scale, Item 1 ...", through Item 5).
#
# Route 1: five codes, numbered 1-5, nothing else.
# Route 2: the paper's reported reliability reproduced from the live data.
# Route 3: convergent direction -- compassion should track empathy.
suppressWarnings(suppressMessages({library(dplyr); library(tidyr)}))
alpha <- function(m) { m <- m[complete.cases(m), , drop = FALSE]; k <- ncol(m)
    (k / (k - 1)) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
d <- as.data.frame(irw::irw_fetch("teq_novak_2021_scbs"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
w <- d %>% select(id, item, resp) %>% distinct(id, item, .keep_all = TRUE) %>%
     pivot_wider(names_from = item, values_from = resp)

cat("=== Route 1: the code set ===\n")
r1 <- setequal(unique(d$item), paste0("SCBCS_", 1:5))
cat(sprintf("  live codes: %s\n", paste(sort(unique(d$item)), collapse = ", ")))
cat(sprintf("  exactly SCBCS_1..SCBCS_5: %s\n", r1))
lv <- sort(unique(d$resp))
r1b <- identical(as.numeric(lv), as.numeric(1:7))
cat(sprintf("  response levels %s -- matches the paper's 1-7: %s\n",
            paste(lv, collapse = ","), r1b))

cat("\n=== Route 2: the paper's reported reliability reproduced ===\n")
a <- alpha(as.matrix(w[, paste0("SCBCS_", 1:5)]))
cat(sprintf("  Cronbach's alpha from the live data: %.3f; the paper reports 0.84\n", a))
r2 <- abs(a - 0.84) < 0.01
cat(sprintf("  -> agrees to the printed precision: %s\n", r2))
cat("  A five-item scale reproducing its published alpha confirms that these five\n")
cat("  codes are that scale's five items, scored in the stated direction. It says\n")
cat("  nothing about WHICH item is which within the five.\n")

cat("\n=== Route 3: direction, from the study's own convergent claim ===\n")
teq <- tryCatch(as.data.frame(irw::irw_fetch("teq_novak_2021_teq")), error = function(e) NULL)
r3 <- TRUE
if (!is.null(teq) && nrow(teq)) {
    tt <- teq %>% group_by(id) %>% summarise(teq = mean(resp, na.rm = TRUE), .groups = "drop")
    ss <- d %>% group_by(id) %>% summarise(scbs = mean(resp, na.rm = TRUE), .groups = "drop")
    m <- inner_join(tt, ss, by = "id")
    rr <- cor(m$teq, m$scbs, use = "complete.obs")
    cat(sprintf("  TEQ empathy mean vs SCBCS compassion mean: r = %+.3f on %d ids\n", rr, nrow(m)))
    cat("  The paper reports positive associations between empathy and compassion,\n")
    cat("  and both scales are coded with higher = more, so a positive r is expected.\n")
    r3 <- rr > 0
    cat(sprintf("  -> %s\n", if (r3) "as expected" else "UNEXPECTED SIGN"))
} else {
    cat("  teq_novak_2021_teq not reachable; skipped (not load-bearing).\n")
}

cat("\n=== What this does NOT establish ===\n")
cat("  Which of the five printed items is SCBCS_1 versus SCBCS_2, beyond the\n")
cat("  shared numbering. Two cautions on the shipped wording, both disclosed in\n")
cat("  provenance: the source renders item 1 without the trailing 'for him or her'\n")
cat("  that appears elsewhere, and item 5 reads 'when the seem to be in need',\n")
cat("  which is transcribed as printed rather than silently corrected.\n")
cat("\nVERDICT:", if (r1 && r1b && r2 && r3) "PASS" else "FAIL", "\n")
