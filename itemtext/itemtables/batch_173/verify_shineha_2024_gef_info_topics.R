# verify_shineha_2024_gef_info_topics.R -- Step 5b mapping check (batch_173).
#
# Claim: Fig3_1..Fig3_17 carry the topics named by the S2 .sav variable labels,
# with the shipped item_text taken from the S1 questionnaire's Q7 list matched
# to those labels by content. Two independent routes, both on the live table:
#
#  A. Fig 3 of Shineha et al. (2024) PLOS ONE 19(4):e0300107 prints, per topic,
#     the % of the public (N=4000) and of experts (N=398) selecting it, for 15
#     named topics. Observed live % by cov_category must reproduce each bar pair.
#     With two independent percentages per topic no two topics are confusable.
#  B. The two topics absent from Fig 3 ("Other", "Nothing in particular that I
#     need to know.") are separated by behaviour: a "nothing" respondent must
#     select nothing else, while "Other" is one choice among several. The
#     questionnaire prints "Nothing" BEFORE "Other", the .sav codes Other=16 and
#     Nothing=17 -- this check is what decides between them.
#
# The table is 74,766 rows (~1 MB); the one export here is a deliberate decision,
# because per-category proportions and per-respondent co-selection cannot be had
# from irw_table_sets().

suppressMessages(library(irw))
TABLE <- "shineha_2024_gef_info_topics"

# Fig 3 bar labels -> item code, public %, expert % (read from the figure image).
PUB <- data.frame(
  item   = c("Fig3_3","Fig3_7","Fig3_1","Fig3_5","Fig3_2","Fig3_9","Fig3_12","Fig3_4",
             "Fig3_13","Fig3_8","Fig3_15","Fig3_11","Fig3_6","Fig3_14","Fig3_10"),
  label  = c("Risk","Measures for safety","Mechanism","Necessity","Benefit","The way of Labeling",
             "Measures for negative effects","Cost","National policy or regulations",
             "Ethical issues of genome editing","Current status of international regulation",
             "Measures for cases of harmful rumors","Industrial possibilities",
             "Schedule for regulatory development","Schedule for R&D of genome editing"),
  public = c(66.4,47.8,41.4,41.1,34.5,24.6,24.1,23.2,22.2,20.6,18.1,12.3,11.2,10.0,4.6),
  expert = c(60.3,54.0,60.3,50.0,77.9,22.4,26.6, 6.5,24.9,25.1,27.9, 8.0,41.7, 6.5,3.3),
  stringsAsFactors = FALSE)
TOL <- 0.051   # figure prints one decimal; allow half-up rounding

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
stopifnot("cov_category" %in% names(d))
pct <- function(cat) tapply(d$resp[d$cov_category == cat], d$item[d$cov_category == cat], mean) * 100
op <- pct("general_public"); oe <- pct("expert")
cat(sprintf("N ids: public %d, expert %d\n",
            length(unique(d$id[d$cov_category == "general_public"])),
            length(unique(d$id[d$cov_category == "expert"]))))

cat("\nRoute A: Fig 3 published % vs live % (public | expert)\n")
cat(sprintf("%-8s %-44s %6s %7s %6s %7s\n", "item", "Fig 3 label", "pubF", "pubObs", "expF", "expObs"))
okA <- TRUE
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]
  a <- op[[it]]; b <- oe[[it]]
  good <- abs(a - PUB$public[i]) <= TOL && abs(b - PUB$expert[i]) <= TOL
  okA <- okA && good
  cat(sprintf("%-8s %-44s %6.1f %7.3f %6.1f %7.3f %s\n", it, PUB$label[i],
              PUB$public[i], a, PUB$expert[i], b, if (good) "" else "<-- MISMATCH"))
}
# Would any permutation of the 15 also fit? Count alternative code matches per bar.
alt <- sapply(seq_len(nrow(PUB)), function(i)
  sum(abs(op[PUB$item] - PUB$public[i]) <= TOL & abs(oe[PUB$item] - PUB$expert[i]) <= TOL))
cat(sprintf("codes fitting each bar pair (must all be 1): %s\n", paste(alt, collapse = " ")))
okA <- okA && all(alt == 1)

cat("\nRoute B: exclusivity of 'Nothing' vs 'Other'\n")
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
topics <- paste0("Fig3_", 1:17)
nsel <- rowSums(w[, topics])
n17 <- sum(w$Fig3_17 == 1); n16 <- sum(w$Fig3_16 == 1)
others17 <- table(nsel[w$Fig3_17 == 1]); others16 <- table(nsel[w$Fig3_16 == 1])
cat(sprintf("Fig3_17 selected by %d; total selections among them: %s\n", n17,
            paste(names(others17), others17, sep = "x", collapse = ", ")))
cat(sprintf("Fig3_16 selected by %d; total selections among them: %s\n", n16,
            paste(names(others16), others16, sep = "x", collapse = ", ")))
cat(sprintf("all respondents' selection totals: %s\n",
            paste(names(table(nsel)), table(nsel), sep = "x", collapse = ", ")))
okB <- n17 > 0 && all(nsel[w$Fig3_17 == 1] == 1) && n16 > 0 && all(nsel[w$Fig3_16 == 1] > 1)
cat(if (okB) "Fig3_17 is exclusive (=Nothing), Fig3_16 co-occurs with other topics (=Other)\n"
    else "exclusivity pattern NOT as claimed\n")

cat("\nDoes NOT establish: the wording itself (the administered Japanese is not in the deposit;\n",
    "the English is the study's tentative translation), nor the 'choose three' instruction --\n",
    "the data show 5 selections per non-'nothing' respondent (see totals above).\n", sep = "")
cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
