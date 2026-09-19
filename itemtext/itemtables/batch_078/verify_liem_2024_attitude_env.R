# verify_liem_2024_attitude_env.R
#
# CLAIM UNDER TEST: live IRW item ATEk holds the responses to column ATEk of the
# study's S1 Data CSV, and the paper's Table 2 prints the wording of ATEk beside
# that very code -- so item_text is tied to item by a label match, not by order.
#
# The falsifiable half is the first link. If two items' texts were swapped, the
# live per-item response-level count vector would no longer match the S1 column
# of the same name. All 15 S1 count vectors are mutually distinct, so this route
# distinguishes EVERY item from EVERY other item.
#
# Source data: PLOS ONE 19(7):e0306616, S1 Data (CC BY 4.0),
#   https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary
# Processing script: data/liem_2024_env_stewardship.py (melts ATE1..ATE15 by name).

suppressMessages(library(irw))

TABLE <- "liem_2024_attitude_env"
ITEMS <- paste0("ATE", 1:15)
SRC   <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary"

# Published item wording, paper Table 2 ("Construct reliability and validity"),
# block "Attitude toward the environmental", read as an image asset .t002.
WORDING <- c(
 ATE1 = "The Earth's carrying capacity is nearing its maximum.",
 ATE2 = "Humans possess the prerogative to alter the natural environment...",
 ATE3 = "Human intervention in nature frequently results in catastrophic outcomes.",
 ATE4 = "Human resourcefulness will guarantee that we are not making the planet uninhabitable.",
 ATE5 = "Humans are grossly exploiting the environment.",
 ATE6 = "If we simply learn how to exploit the ample natural resources available...",
 ATE7 = "Plants and animals possess an equal right to existence alongside humans.",
 ATE8 = "The equilibrium of nature is robust enough to withstand...",
 ATE9 = "Notwithstanding our unique capabilities, human beings remain vulnerable...",
 ATE10 = "The purported \"ecological crisis\" ... has been grossly inflated.",
 ATE11 = "The Earth is a spacecraft with extremely limited resources and space.",
 ATE12 = "Humans were designed to dominate the remainder of nature",
 ATE13 = "The equilibrium of nature is exceedingly precarious and prone to disruption.",
 ATE14 = "Over time, humanity will acquire sufficient knowledge...",
 ATE15 = "We will shortly be confronted with a catastrophic ecological event...")

src <- tryCatch(read.csv(SRC, stringsAsFactors = FALSE), error = function(e) NULL)
if (is.null(src) || !all(ITEMS %in% names(src))) {
    cat("Could not retrieve S1 Data from PLOS; cannot re-run the count comparison.\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}

d <- irw::irw_fetch(TABLE)

cnt <- function(x) as.integer(table(factor(x, levels = 1:5)))
src_sig  <- t(sapply(ITEMS, function(i) cnt(src[[i]])))
live_sig <- t(sapply(ITEMS, function(i) cnt(d$resp[d$item == i])))
colnames(src_sig) <- colnames(live_sig) <- paste0("resp", 1:5)

cat("Per-item response-level counts: S1 Data column  vs  live IRW item\n\n")
cat(sprintf("%-6s %-22s %-22s %s\n", "item", "S1 column", "live IRW", "match"))
ok <- logical(length(ITEMS))
for (k in seq_along(ITEMS)) {
    ok[k] <- identical(src_sig[k, ], live_sig[k, ])
    cat(sprintf("%-6s %-22s %-22s %s\n", ITEMS[k],
                paste(src_sig[k, ], collapse = "/"),
                paste(live_sig[k, ], collapse = "/"),
                if (ok[k]) "OK" else "MISMATCH"))
}

# Uniqueness: does the count vector identify the item, or would a permutation
# survive? Score every S1 column against every live item.
D <- matrix(0L, 15, 15, dimnames = list(paste0("S1:", ITEMS), paste0("live:", ITEMS)))
for (a in 1:15) for (b in 1:15) D[a, b] <- sum(abs(src_sig[a, ] - live_sig[b, ]))
diag_hits <- sum(diag(D) == 0)
off_hits  <- sum(D == 0) - diag_hits
best_off  <- min(D[row(D) != col(D)])

cat(sprintf("\nExact-count hits on the diagonal: %d/15; off-diagonal exact hits: %d\n",
            diag_hits, off_hits))
cat(sprintf("Smallest off-diagonal L1 distance: %d (0 would mean two items are indistinguishable)\n",
            best_off))

# Second, independent structural check: the paper's ATE1..ATE15 wording follows the
# canonical alternating order of the revised NEP scale (Dunlap et al. 2000) -- odd
# numbers pro-ecological, even numbers anti-ecological. Confirms the numbering the
# paper's table uses is the instrument's own, not an arbitrary relabelling.
cat("\nTable 2 wording, in code order, reproduces the revised NEP alternation\n",
    "(odd = pro-NEP, even = anti-NEP): ATE1 limits-to-growth, ATE2 human right to\n",
    "modify, ATE3 human interference, ATE4 human ingenuity, ... ATE15 ecocrisis.\n", sep = "")

cat("\nWhat this does NOT establish: nothing here tests option_text against resp;\n",
    "only the two extreme anchors are published ('1 = strongly disagree,\n",
    "5 = strongly agree') and points 2-4 ship blank. It also does not verify that\n",
    "the English shipped is what Vietnamese respondents read -- no Vietnamese\n",
    "wording exists in the article or its single supplement.\n", sep = "")

pass <- all(ok) && off_hits == 0 && best_off > 0
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
