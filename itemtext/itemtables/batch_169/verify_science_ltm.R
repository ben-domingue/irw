# verify_science_ltm.R -- Step 5b check for science_ltm (batch_169).
#
# CLAIM BEING TESTED. The item codes are the ltm::Science column names and the
# ltm Rd documents each one's statement, so item<->item_text is a label match.
# The inference this table makes is on the OTHER axis, option_text<->resp, and it
# DEPARTS from the table's own documentation: ltm's factor levels (and the live
# table's resp_raw) read 1=strongly disagree .. 4=strongly agree for all seven
# items, while the shipped item text says that for the three negatively worded
# statements (Environment, Technology, Industry) resp runs the other way:
# 1=Strongly agree .. 4=Strongly disagree (i.e. the data are scored so that a high
# value is favourable to science for every item).
#
# FALSIFIABLE PREDICTION. The Eurobarometer 38.1 codebook (GESIS ZA2295_cdb.pdf,
# v1.0.1, doi:10.4232/1.10904) prints per-country marginals for every item. The
# ltm data are 392 Great Britain respondents on a 4-category scale, which is the
# split-ballot-B form (Q.62_B / Q.66_B: 1 Strongly agree, 2 Agree to some extent,
# 3 Disagree to some extent, 4 Strongly disagree). If the shipped orientation is
# right, each live item's resp distribution, read through the shipped option_text,
# must reproduce the GB-GBN ballot-B marginal for the SAME statement -- and must
# fit that statement better than the opposite orientation does, and better than
# any OTHER statement's marginal does.
#
# Hard-coded from the codebook (weighted by v8, GB-GBN row, DK/NA/inap excluded):
gbB <- rbind(   # columns: Strongly agree, Agree to some extent, Disagree to some extent, Strongly disagree
  Comfort     = c(106, 366,  53,  15),  # v249 Q.62a_B
  Environment = c( 45, 124, 197, 151),  # v252 Q.62d_B
  Work        = c( 71, 269, 129,  49),  # v256 Q.62h_B
  Future      = c(117, 280,  96,  26),  # v260 Q.62l_B
  Technology  = c( 20, 120, 203, 147),  # v294 Q.66a_B
  Industry    = c( 15,  62, 229, 196),  # v297 Q.66d_B
  Benefit     = c( 93, 241, 119,  35))  # v304 Q.66k_B
# Ballot A (5-point, neutral dropped) printed for reference only.
gbA <- rbind(
  Comfort     = c( 97, 316,  40,   7),  # v237, neutral 40 dropped
  Environment = c( 34,  97, 169, 135),  # v240, neutral 41
  Work        = c( 53, 203,  92,  36),  # v244, neutral 88
  Future      = c( 99, 219,  64,  28),  # v248, neutral 72
  Technology  = c( 16,  73, 192, 138),  # v283, neutral 42
  Industry    = c( 11,  51, 212, 166),  # v286, neutral 31
  Benefit     = c( 70, 179,  75,  19))  # v293, neutral 124

# Shipped orientation: which resp value carries "Strongly agree" .. "Strongly disagree".
NEG <- c("Environment", "Technology", "Industry")
shipped_order <- function(item) if (item %in% NEG) 1:4 else 4:1   # resp values in SA,A,D,SD order

suppressMessages(library(irw))
d <- irw::irw_fetch("science_ltm")   # 2,744 rows; a negligible export
live <- table(factor(d$item), factor(d$resp, levels = 1:4))
items <- rownames(gbB)
prop <- function(x) x / sum(x)
tvd  <- function(p, q) sum(abs(p - q)) / 2

cat("Per item: live distribution read through shipped option_text vs GB-GBN ballot B\n")
cat(sprintf("%-12s %-27s %-27s %8s %9s %8s\n", "item", "live SA/A/D/SD (shipped)",
            "GB ballot B SA/A/D/SD", "TVD", "TVD_flip", "TVD_A"))
ok <- TRUE
for (it in items) {
  ship <- prop(as.numeric(live[it, shipped_order(it)]))
  flip <- rev(ship)
  b <- prop(gbB[it, ]); a <- prop(gbA[it, ])
  t1 <- tvd(ship, b); t2 <- tvd(flip, b); ta <- tvd(ship, a)
  cat(sprintf("%-12s %-27s %-27s %8.3f %9.3f %8.3f\n", it,
              paste(sprintf("%.3f", ship), collapse = "/"),
              paste(sprintf("%.3f", b), collapse = "/"), t1, t2, ta))
  if (!(t1 < 0.06 && t2 > 0.30)) ok <- FALSE
}

cat("\nNearest statement: TVD of each live item (shipped orientation) to every ballot-B marginal\n")
M <- sapply(items, function(g) sapply(items, function(it)
  tvd(prop(as.numeric(live[it, shipped_order(it)])), prop(gbB[g, ]))))
print(round(M, 3))   # rows = live item, cols = GB statement
nearest <- colnames(M)[apply(M, 1, which.min)]
for (i in seq_along(items))
  cat(sprintf("  %-12s nearest GB statement: %-12s %s\n", items[i], nearest[i],
              if (nearest[i] == items[i]) "ok" else "MISMATCH"))
if (!all(nearest == items)) ok <- FALSE

cat("\nWhat this does NOT establish: the codebook marginals are v8-weighted and cover every\n",
    "GB-GBN ballot respondent, not ltm's 392 complete cases, so the match is proportional,\n",
    "not cell-for-cell. Technology and Environment have similar marginals, so their mutual\n",
    "separation is thin (see the matrix); their item_text rests primarily on the ltm Rd's\n",
    "explicit code->statement listing. It also does not prove the ltm sample is ballot B\n",
    "rather than ballot A with neutral answers dropped (TVD_A is shown for that reason);\n",
    "the item and option wording is identical across the two ballots apart from the\n",
    "neutral point, which the live data do not contain.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
