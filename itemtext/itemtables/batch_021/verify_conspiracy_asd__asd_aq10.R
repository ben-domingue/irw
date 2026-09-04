# verify_conspiracy_asd__asd_aq10.R -- Step 5b evidence, re-runnable.
#
# Two claims are checked, both falsifiable:
#
# A) ITEM MAPPING. data/conspiracy_belief_schizotypy_asd.py assigns item codes
#    POSITIONALLY: aq10_1..aq10_10 <- columns 53..62 (0-based) of the Figshare
#    coded workbook, whose row 1 carries the item wording. The claim is that the
#    column range is right and unshifted. Prediction: the per-item mean of each
#    source column equals the live IRW mean for the code we attached that
#    column's wording to. All ten means are distinct at 2 d.p., so this
#    separates every item from every other item.
#
# B) OPTION MAPPING (resp <-> option_text). The workbook carries the study's own
#    AQ-10 total in column 63. AQ-10 scoring (Allison et al. 2012) gives 1 point
#    for agreement on items 1,7,8,10 and 1 point for disagreement on items
#    2,3,4,5,6,9. That total is reproducible only under ONE reading of the 1-4
#    coding. Prediction: 1=Definitely disagree .. 4=Definitely agree reproduces
#    the stored total for every respondent; the reversed reading does not.
#    (The anchors themselves are printed in the deposit's own survey docx.)

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "conspiracy_asd__asd_aq10"
URL   <- "https://ndownloader.figshare.com/files/60452459"

f <- tempfile(fileext = ".xlsx")
curl::curl_download(URL, f, quiet = TRUE)
raw <- as.data.frame(read_excel(f, col_names = FALSE, .name_repair = "minimal"))
dat <- raw[-(1:2), , drop = FALSE]

aq  <- sapply(54:63, function(j) as.numeric(dat[[j]]))   # R 1-based = py 53..62
colnames(aq) <- paste0("aq10_", 1:10)
tot <- as.numeric(dat[[64]])

live <- irw::irw_fetch(TABLE)
obs  <- tapply(as.numeric(live$resp), live$item, mean)

cat("-- A) positional item mapping: source column mean vs live per-item mean --\n")
cat(sprintf("%-9s %12s %12s %9s\n", "item", "source col", "live IRW", "diff"))
src <- colMeans(aq, na.rm = TRUE)
for (nm in colnames(aq))
    cat(sprintf("%-9s %12.4f %12.4f %9.2e\n", nm, src[[nm]], obs[[nm]], obs[[nm]] - src[[nm]]))
worstA <- max(abs(obs[colnames(aq)] - src))
cat(sprintf("largest deviation: %.2e\n", worstA))
cat(sprintf("distinct live means at 2 d.p.: %d of 10\n",
            length(unique(round(obs, 2)))))

cat("\n-- B) option/resp direction vs the study's own AQ-10 total (col 63) --\n")
agr <- c(1, 7, 8, 10); dis <- c(2, 3, 4, 5, 6, 9)
score <- function(hi_is_agree) {
    a <- if (hi_is_agree) aq[, agr] >= 3 else aq[, agr] <= 2
    d <- if (hi_is_agree) aq[, dis] <= 2 else aq[, dis] >= 3
    rowSums(a) + rowSums(d)
}
h_agree_hi <- score(TRUE)    # 1=Definitely disagree .. 4=Definitely agree
h_agree_lo <- score(FALSE)   # reversed
n <- length(tot)
mA <- sum(h_agree_hi == tot); mB <- sum(h_agree_lo == tot)
cat(sprintf("1=Def.disagree..4=Def.agree : %d/%d respondents reproduced exactly (mean %.4f vs stored %.4f)\n",
            mA, n, mean(h_agree_hi), mean(tot)))
cat(sprintf("reversed (1=Def.agree..4=Def.disagree): %d/%d reproduced (mean %.4f)\n",
            mB, n, mean(h_agree_lo)))

cat("\nWhat B does NOT establish: it pins the 1-4 direction and the agree-/disagree-\n",
    "keyed CLASS of each item, not the order within a class -- (A) is what does that.\n", sep = "")

ok <- worstA < 1e-6 && length(unique(round(obs, 2))) == 10 && mA == n && mB < n
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
