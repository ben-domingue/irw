# verify_teicher_2015_mace_sexual.R -- copied from references/verify_template.R
#
# Claim: the 12 item codes (S9 File column names, used verbatim by
# data/teicher_2015_mace_items.py) carry the MACE-X (S3 File) wording of items
# 13-17 (familial adults), 26-30 (adults NOT living in the house) and 49-50 (peers),
# and resp 1 = "Yes", 0 = "No".
#
# Route 1 (7 of 12 items): Teicher & Parigger (2015) PLOS ONE Table 9 (image,
# doi:10.1371/journal.pone.0117423.t009) prints "% Yes" for the seven sexual-abuse
# items retained in the final MACE, Observations = 967. The live table reproduces
# those to the printed decimal on the 967 respondents with all seven items present.
# NOTE: Table 9 labels row 19 "Other adults touched or fondled you in sexual way",
# but its 5.6 is the o_touch_them column (o_fondled is 10.6 on the same 967); the
# S2 MACE form (item 19), the S3 MACE-X form (item 28) and the authors' MACE-X scoring
# template (S6, formula references o_touch_them_*) all word/score it as
# "Had you touch their body in a sexual way". Checks 2-3 below test which reading the
# data support.
#
# Checks 2-3 (structural, cover the 5 items Table 9 does not print: Attemp_sex,
# Intercourse, o_sex_com, o_fondled, o_attempt_sex): the familial and extra-familial
# blocks carry the same five stems in the same order, so the same severity ladder
# (comments > fondled > made to touch > attempted > actual intercourse) and the same
# nesting asymmetries (being made to touch nested within being fondled; actual
# intercourse nested within attempted) must appear in BOTH blocks. A swap of
# o_fondled/o_touch_them (the Table 9 reading) or of attempt/intercourse breaks them.
# These are coherence checks: they do not by themselves prove an item's identity.

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_sexual"

PUBLISHED <- c(                      # Table 9 % Yes, MACE-52 numbering in comments
    Sex_comment       = 4.0,  # 12 Parents inappropriate sexual comments to you
    Fondled           = 2.8,  # 13 Parents touched or fondled you in sexual way
    Touch_them        = 1.4,  # 14 Parents had you touch them in sexual way
    o_touch_them      = 5.6,  # 19 "Other adults touched or fondled you in sexual way" (see note)
    o_intercourse     = 3.7,  # 20 Other adults had sexual intercourse with you
    Peer_forced_sex   = 8.2,  # 36 Peer(s) forced you to engage in sexual activity against your will
    Peer_sex_not_want = 9.5   # 37 Peer(s) forced you to do things sexually you did not want to do
)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
ok <- TRUE

cat("== Route 1: Table 9 % Yes (n = 967) ==\n")
cc <- complete.cases(w[, names(PUBLISHED)])
cat(sprintf("respondents with all 7 Table 9 items present: %d (Table 9: 967)\n", sum(cc)))
if (sum(cc) != 967) ok <- FALSE
all12 <- setdiff(names(w), "id")
pct967 <- sapply(all12, function(i) 100 * mean(w[cc, i] == 1, na.rm = TRUE))
cat(sprintf("%-18s %9s %9s %9s  %s\n", "item", "published", "live967", "rounded", "nearest published"))
for (it in names(PUBLISHED)) {
    nearest <- names(PUBLISHED)[which.min(abs(PUBLISHED - pct967[[it]]))]
    r <- round(pct967[[it]], 1)
    cat(sprintf("%-18s %9.1f %9.3f %9.1f  %s\n", it, PUBLISHED[[it]], pct967[[it]], r, nearest))
    if (abs(r - PUBLISHED[[it]]) > 1e-9 || nearest != it) ok <- FALSE
}
cat("items NOT in Table 9, same 967:\n")
for (it in setdiff(all12, names(PUBLISHED))) cat(sprintf("  %-18s %9.3f\n", it, pct967[[it]]))
cat(sprintf("o_fondled on the 967 = %.1f, not 5.6 -> Table 9 row 19 is the o_touch_them column\n",
            pct967[["o_fondled"]]))

pct <- sapply(all12, function(i) 100 * mean(w[[i]] == 1, na.rm = TRUE))
cat("\n== Check 2: parallel severity ladder (all live respondents) ==\n")
fam <- c("Sex_comment", "Fondled", "Touch_them", "Attemp_sex", "Intercourse")
ext <- c("o_sex_com", "o_fondled", "o_touch_them", "o_attempt_sex", "o_intercourse")
cat("familial:       ", paste(sprintf("%s %.2f", fam, pct[fam]), collapse = " > "), "\n")
cat("extra-familial: ", paste(sprintf("%s %.2f", ext, pct[ext]), collapse = " > "), "\n")
lad <- all(diff(pct[fam]) < 0) && all(diff(pct[ext]) < 0)
cat("strictly decreasing in both blocks:", lad, "\n")
if (!lad) ok <- FALSE
cat("extra-familial > familial for every stem:", all(pct[ext] > pct[fam]), "\n")
if (!all(pct[ext] > pct[fam])) ok <- FALSE

cat("\n== Check 3: nesting asymmetry, same direction in both blocks ==\n")
cond <- function(a, b) { k <- !is.na(w[[a]]) & !is.na(w[[b]]); mean(w[[a]][k & w[[b]] == 1] == 1) }
pairs <- list(c("Fondled", "Touch_them"), c("o_fondled", "o_touch_them"),
              c("Attemp_sex", "Intercourse"), c("o_attempt_sex", "o_intercourse"))
for (p in pairs) {
    a <- cond(p[1], p[2]); b <- cond(p[2], p[1])
    cat(sprintf("P(%s=1 | %s=1) = %.2f   vs   P(%s=1 | %s=1) = %.2f\n", p[1], p[2], a, p[2], p[1], b))
    if (!(a > b)) ok <- FALSE
}

cat("\nresp values present:", paste(sort(unique(d$resp)), collapse = ", "), "\n")
cat("Route 1 distinguishes the 7 Table 9 items from each other and fixes resp=1 as Yes\n",
    "(a flip would put Peer_sex_not_want at 90.5). Checks 2-3 are coherence evidence for the\n",
    "other 5 items and for o_fondled vs o_touch_them; they do NOT establish those items'\n",
    "identity against a published statistic -- that rests on the self-describing S9 column\n",
    "names and MACEscore mace_x_names.R order (positions 13-17, 26-30, 49-50).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
