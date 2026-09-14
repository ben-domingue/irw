# verify_makowska_2023_pdts.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: item_text is tied to the codes PDTS1..PDTS6 by the deposit's
# own SPSS variable labels (S2 Data, pone.0287223.s003.sav), NOT by the item
# numbering the paper uses in Table 2 -- the two disagree for items 2 and 3.
#   .sav:   PDTS2 = "no control over ICT implemented changes",  PDTS3 = "irritated"
#   paper:  Item 2 = "irritated",                               Item 3 = "no control"
# The shipped table follows the .sav. This script re-runs the two checks that
# decision rests on.
#
# CHECK A (label tie, mechanical): each PDTS column's variable label in the
#   deposit begins with that column's own code, in BOTH deposited samples.
# CHECK B (data signal, falsifiable): PDTS1 is the undisputed "upset" item.
#   If our mapping is right, PDTS3 (labelled "irritated", a near synonym) must
#   correlate MORE with PDTS1 than PDTS2 ("no control") does -- and must do so
#   in both independent samples. If the paper's numbering were the true one the
#   inequality would be expected to reverse.
# CHECK C (live data ties to the source columns): the live IRW per-item means
#   must reproduce the s003 column means exactly (the processing script melts on
#   the column names, so a permutation anywhere would show here).
#
# What this does NOT establish: check B's margin is ~0.05 in each sample, which
# is suggestive, not decisive. PDTS2 and PDTS3 remain the only two codes this
# round could not separate outright. Items 1, 4, 5 and 6 are pinned by content
# (upset / annoyed / overload / competences) and are agreed by both sources.

suppressMessages({library(haven); library(irw)})

S1_URL <- "https://doi.org/10.1371/journal.pone.0287223.s002"   # Study 1, N=229
S2_URL <- "https://doi.org/10.1371/journal.pone.0287223.s003"   # Study 2, N=558 -> IRW
ITEMS  <- paste0("PDTS", 1:6)

get_sav <- function(url) {
    f <- tempfile(fileext = ".sav")
    utils::download.file(url, f, quiet = TRUE, mode = "wb")
    haven::read_sav(f)
}
num <- function(x) { x <- as.character(x); as.numeric(sub("^\\s*(\\d+).*$", "\\1", x)) }

s1 <- get_sav(S1_URL); s2 <- get_sav(S2_URL)

cat("=== CHECK A: deposit variable labels, code prefix vs column name ===\n")
okA <- TRUE
for (nm in ITEMS) {
    for (tag in c("S1", "S2")) {
        d <- if (tag == "S1") s1 else s2
        lab <- attr(d[[nm]], "label"); if (is.null(lab)) lab <- ""
        hit <- grepl(paste0("^", nm, "[. ]"), lab)
        okA <- okA && hit
        cat(sprintf("%-3s %-6s prefix_ok=%-5s %s\n", tag, nm, hit, substr(lab, 1, 92)))
    }
}

cat("\n=== CHECK B: r(PDTS1, PDTS3) vs r(PDTS1, PDTS2), both samples ===\n")
okB <- TRUE
for (tag in c("S1", "S2")) {
    d <- if (tag == "S1") s1 else s2
    m <- sapply(ITEMS, function(nm) num(d[[nm]]))
    r13 <- cor(m[, "PDTS1"], m[, "PDTS3"], use = "pairwise.complete.obs")
    r12 <- cor(m[, "PDTS1"], m[, "PDTS2"], use = "pairwise.complete.obs")
    cat(sprintf("%-3s r(upset PDTS1, irritated PDTS3) = %.3f   r(upset PDTS1, no-control PDTS2) = %.3f   diff = %+.3f\n",
                tag, r13, r12, r13 - r12))
    okB <- okB && (r13 > r12)
}

cat("\n=== CHECK C: live IRW per-item means vs s003 column means ===\n")
live <- irw::irw_fetch("makowska_2023_pdts")
obs  <- tapply(as.numeric(live$resp), live$item, mean)[ITEMS]
src  <- sapply(ITEMS, function(nm) mean(num(s2[[nm]]), na.rm = TRUE))
cat(sprintf("%-8s %12s %12s %10s\n", "item", "s003", "live", "diff"))
for (nm in ITEMS)
    cat(sprintf("%-8s %12.6f %12.6f %10.2e\n", nm, src[[nm]], obs[[nm]], obs[[nm]] - src[[nm]]))
okC <- max(abs(obs - src)) < 1e-9

cat(sprintf("\nA (label prefixes 12/12): %s | B (both samples): %s | C (max |diff| %.2e): %s\n",
            okA, okB, max(abs(obs - src)), okC))
cat("Note: B's margin is ~0.05 in each sample -- consistent, but it does not\n",
    "conclusively separate PDTS2 from PDTS3. That ambiguity is disclosed in\n",
    "provenance and in the table's public_note.\n", sep = "")
cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
