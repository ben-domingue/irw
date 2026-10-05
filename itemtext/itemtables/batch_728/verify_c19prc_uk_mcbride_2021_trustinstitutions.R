# verify_c19prc_uk_mcbride_2021_trustinstitutions.R  (copied from references/verify_template.R)
#
# Claim: item codes Trust_Body_<institution> are assigned POSITIONALLY per wave by
# data/c19prc_uk_mcbride_2021_crosswalk.py (W1 Trust_Body1..7, W2/W3 Trust_Body1..8,
# W4 Trust_Body1..12, W5 Trust_Body_1..12 -> institution names), and resp is harmonised
# to 1 = "Do not trust at all" .. 5 = "Completely trust" (W1/W2/W4/W5 recoded 6 - raw,
# W3 kept raw). Three checks, all of which break under a swapped item or flipped anchor:
#   A. header diff: the .sav variable label at each source position names the institution
#      the crosswalk assigns to it (47 item-wave positions);
#   B. route 9: .sav per item x wave x level counts, after the build's reversal, equal the
#      live table's counts cell for cell;
#   C. direction: raw codes of the same respondents correlate NEGATIVELY across exactly the
#      wave boundaries where the .sav value labels flip (W2->W3, W3->W4) and positively
#      elsewhere, so the labels (not the measures docx) describe the stored coding.
# Source .sav files are read in place from itemtext/.cache (OSF v2zur, CC BY 4.0).
suppressMessages({ library(irw); library(haven) })
TABLE <- "c19prc_uk_mcbride_2021_trustinstitutions"
C <- "/home/ben/irw-queue-runner/itemtext/.cache/"
F <- list(`1` = "c19prc_uk_mcbride_2021_childimpact/C19PRC_UKW1W2_archive_final.sav",
          `3` = "c19prc_uk_mcbride_2021_comfort/w3/C19PRC_UK_W3_archive_final.sav",
          `4` = "c19prc_uk_mcbride_2021_cmq/w4/C19PRC_UK_W4_archive_final.sav",
          `5` = "c19prc_uk_mcbride_2021_shared/w5/C19PRC_UKW5_archive_final.sav")
F$`2` <- F$`1`
S <- lapply(F[c("1", "3", "4", "5")], function(p) read_sav(paste0(C, p)))
S$`2` <- S$`1`
I8  <- c("parliament","government","police","legal_system","political_parties","scientists","doctors","pharmaceutical_companies")
I12 <- c("parliament","government","devolved_wales","devolved_scotland","devolved_ni","local_government","police","legal_system","political_parties","scientists","doctors","pharmaceutical_companies")
# exact label suffixes allowed at each assigned position (W1-W3 form | W4-W5 form)
KEY <- list(parliament=c("Parliament","The UK Parliament"), government=c("The government","The UK Government"),
         devolved_wales="The devolved government in Wales", devolved_scotland="The devolved government in Scotland",
         devolved_ni="The devolved government in Northern Ireland",
         local_government="Your local government (Council or Local Authority)", police="The police",
         legal_system="The legal system", political_parties="Political parties", scientists="Scientists",
         doctors="Doctors and other health professionals", pharmaceutical_companies="Pharmaceutical companies")
POS <- list(`1` = setNames(paste0("W1_Trust_Body", 1:7), I8[1:7]),
            `2` = setNames(paste0("W2_Trust_Body", 1:8), I8),
            `3` = setNames(paste0("W3_Trust_Body", 1:8), I8),
            `4` = setNames(paste0("W4_Trust_Body", 1:12), I12),
            `5` = setNames(paste0("W5_Trust_Body_", 1:12), I12))
REV <- c("1", "2", "4", "5")

d <- irw::irw_fetch(TABLE)
okA <- 0; okB <- 0; n <- 0
cat("A = header label names the assigned institution; B = counts match after reversal\n")
for (w in names(POS)) for (inst in names(POS[[w]])) {
  col <- POS[[w]][[inst]]; x <- S[[w]][[col]]
  lab <- attr(x, "label")
  a <- trimws(sub(".* - ", "", lab)) %in% KEY[[inst]]
  v <- as.integer(zap_labels(x)); v <- v[!is.na(v)]
  if (w %in% REV) v <- 6L - v
  src <- tabulate(v, 5)
  live <- tabulate(d$resp[d$item == paste0("Trust_Body_", inst) & d$wave == as.integer(w)], 5)
  b <- identical(src, live)
  n <- n + 1; okA <- okA + a; okB <- okB + b
  cat(sprintf("W%s %-26s %-18s A=%s B=%s src=%s live=%s\n", w, inst, col, a, b,
              paste(src, collapse = "/"), paste(live, collapse = "/")))
}
cat(sprintf("\nA header diff: %d/%d   B count match: %d/%d\n", okA, n, okB, n))

cat("\nC raw cross-wave correlations (doctors), same respondents:\n")
raw <- function(w, inst) { x <- S[[w]]; setNames(as.numeric(zap_labels(x[[POS[[w]][[inst]]]])), as.character(x$pid)) }
signs <- c()
for (pr in list(c("1","2"), c("2","3"), c("3","4"), c("4","5"))) {
  a <- raw(pr[1], "doctors"); b <- raw(pr[2], "doctors"); k <- intersect(names(a)[!is.na(a)], names(b)[!is.na(b)])
  r <- cor(a[k], b[k]); expect <- if (identical(pr, c("2","3")) || identical(pr, c("3","4"))) -1 else 1
  signs <- c(signs, sign(r) == expect)
  cat(sprintf("  W%s vs W%s  r=%+.2f n=%d  expected sign %+d\n", pr[1], pr[2], r, length(k), expect))
}
m <- tapply(d$resp, d$item, mean)
cat(sprintf("\nlive means: doctors %.2f (highest=%s), political_parties %.2f (lowest=%s)\n",
            m[["Trust_Body_doctors"]], names(which.max(m)) == "Trust_Body_doctors",
            m[["Trust_Body_political_parties"]], names(which.min(m)) == "Trust_Body_political_parties"))
cat("Does NOT establish: which of the W1-W3 vs W4-W5 wordings of parliament/government a given row saw\n",
    "(that is recorded by wave in the live table, and disclosed in provenance).\n", sep = "")
cat(if (okA == n && okB == n && all(signs)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
