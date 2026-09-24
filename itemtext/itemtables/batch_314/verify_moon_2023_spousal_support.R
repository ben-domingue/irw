# verify_moon_2023_spousal_support.R -- Step 5b re-runnable check (batch_314).
#
# Mapping claim: item code socialsupportpN <-> item_text is tied at the SOURCE.
# The study's own questionnaire (PeerJ 10.7717/peerj.16295, Supplemental File
# peerj-11-16295-s002.pdf, page "- 3 -" right-hand column, section 4) prints
# each SPSS column name (socialsupportp1..socialsupportp11, in red) in the row
# beside its item, and data/moon_2023_pregnancy_stress.py melts those .sav
# columns BY NAME (derivation pattern 1: IRW item == source column name).
# So the tie is a printed-code label match, not an order inference.
#
# Checks:
#  (1) shipped CSV code->text pairs equal the pairs printed in s002 (hard-coded
#      below from the questionnaire page); 11/11 required. This is the check
#      that distinguishes every item from every other.
#  (2) option direction: shipped option_text has 'Very dissatisfied' at resp 1
#      and 'Very satisfied' at resp 6 for every item (s002 header; .sav value
#      label on socialsupportp1 1='very dissatisfied', 6='very satisfied').
#  (3) corroboration from live data: person-mean scale score vs paper Table 2
#      (4.92 +/- 1.16, 1~6, N=206), and the scale score's correlation with the
#      same respondents' pregnancy-stress mean vs paper Table 3 (-0.479).
#      The paper's -0.479 was computed on the uncleaned file: the .sav's own
#      stored scale scores (spospoT, StressT) give r = -0.475, and they include
#      one respondent who answered 6 on all 11 pregnancy-stress items (StressT
#      = 6 on a 1-4 scale), whom the IRW script dropped from pregnancy_stress.
#      Excluding only that respondent in the .sav gives -0.587, which is what
#      the live tables reproduce (~ -0.58). So the check here is the sign and
#      magnitude (r < -0.40), with both reference values printed.
#  (4) live per-item x level counts equal the .sav's (s001, sentinels 9 and the
#      one 1.6 in socialsupportp9 removed), hard-coded below: 66/66 cells.
#  (3)/(4) confirm direction (higher = more support), block identity and that
#  the stored values are the raw 1-6 codes; they do NOT order the items, which
#  are all positively keyed and near-collinear (alpha 0.96). Only (1) does.

suppressMessages(library(irw))
TABLE <- "moon_2023_spousal_support"

SOURCE_PAIRS <- c(
 socialsupportp1  = "He shares similar experiences with me",
 socialsupportp2  = "He helps me keep my morale high",
 socialsupportp3  = "He helps me when I need or when I am in trouble",
 socialsupportp4  = "He is interested in my daily routine and problems",
 socialsupportp5  = "He tries to focus on me when he does something for me",
 socialsupportp6  = "He spares time to talk to me about personal and private issue",
 socialsupportp7  = "He appreciates the things I do for him",
 socialsupportp8  = "He tolerates my ups and downs and unusual behaviors",
 socialsupportp9  = "He takes me serious when I am concerned about something",
 socialsupportp10 = "He clarifies my condition so that I can understand more easily",
 socialsupportp11 = "I know he will be with me when I need help")

ok <- TRUE
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) NULL)
if (is.null(here)) {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grep("^--file=", a)])
  here <- if (length(f)) dirname(normalizePath(f)) else "."
}
it <- read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
shipped <- unique(it[, c("item", "item_text")])
shipped_txt <- setNames(shipped$item_text, shipped$item)[names(SOURCE_PAIRS)]
m <- shipped_txt == SOURCE_PAIRS
cat("(1) code->text pairs vs questionnaire s002 section 4:\n")
for (k in names(SOURCE_PAIRS)) cat(sprintf("  %-17s %s  %s\n", k, if (isTRUE(m[k])) "OK  " else "DIFF", shipped_txt[k]))
cat(sprintf("  %d/11 match\n\n", sum(m, na.rm = TRUE)))
ok <- ok && sum(m, na.rm = TRUE) == 11 && nrow(shipped) == 11

lo <- it[it$resp == 1, ]; hi <- it[it$resp == 6, ]
c2 <- all(lo$option_text == "Very dissatisfied") && all(hi$option_text == "Very satisfied") &&
      nrow(lo) == 11 && nrow(hi) == 11 && all(is.na(it$option_text[it$resp %in% 2:5]))
cat(sprintf("(2) resp1='Very dissatisfied' & resp6='Very satisfied' on all 11 items, 2-5 blank: %s\n\n", c2))
ok <- ok && c2

d <- irw::irw_fetch(TABLE)
mu <- tapply(d$resp, d$item, mean)[names(SOURCE_PAIRS)]
cat("(3) live per-item mean (n):\n")
nn <- table(d$item)[names(SOURCE_PAIRS)]
for (k in names(mu)) cat(sprintf("  %-17s %.2f (%d)\n", k, mu[k], nn[k]))
pm <- tapply(d$resp, d$id, mean)
cat(sprintf("\n  person-mean scale score: %.2f (SD %.2f), paper Table 2: 4.92 (SD 1.16)\n", mean(pm), sd(pm)))
c3a <- abs(mean(pm) - 4.92) <= 0.05 && abs(sd(pm) - 1.16) <= 0.05
ps <- irw::irw_fetch("moon_2023_pregnancy_stress")
pst <- tapply(ps$resp, ps$id, mean)
ids <- intersect(names(pm), names(pst))
r <- cor(pm[ids], pst[ids])
cat(sprintf("  r(spousal support, pregnancy stress) = %.3f on %d ids, paper Table 3: -0.479\n", r, length(ids)))
cat("  (paper's -0.479 reproduces from the raw .sav's stored totals, -0.475, incl. the all-6 stress respondent;\n",
    "   excluding only that respondent, as IRW does, the .sav gives -0.587)\n", sep = "")
c3b <- r < -0.40
cat(sprintf("  mean/SD within 0.05: %s; r < -0.40: %s\n\n", c3a, c3b))
SAV <- rbind(
 socialsupportp1  = c(3, 6,30,24,36,102), socialsupportp2  = c(4, 7,24,25,41,105),
 socialsupportp3  = c(2, 9,21,28,41,105), socialsupportp4  = c(7, 6,25,21,44,103),
 socialsupportp5  = c(11,11,25,28,48, 83), socialsupportp6 = c(9,10,20,22,47, 98),
 socialsupportp7  = c(4, 5,22,27,42,106), socialsupportp8  = c(11,12,18,26,42, 97),
 socialsupportp9  = c(6, 9,19,25,46, 99), socialsupportp10 = c(6, 7,17,27,44,105),
 socialsupportp11 = c(11, 4,18,21,41,111))
live <- as.matrix(table(factor(d$item, levels = rownames(SAV)), factor(d$resp, levels = 1:6)))
cells <- sum(live == SAV)
cat(sprintf("(4) live vs .sav per-item x level counts: %d/66 cells equal\n", cells))
if (cells < 66) print(live - SAV)
c4 <- cells == 66
cat("Note: (3) confirms scale direction and block identity only; all 11 items are positively\n",
    "keyed and intercorrelated, so no statistic orders them. Check (1) is what distinguishes every item.\n", sep = "")
ok <- ok && c3a && c3b && c4
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
