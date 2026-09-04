# verify_cognitive_load_klimova_2023_pwi.R
#
# STATUS: this table is BLOCKED -- no __items.csv was written. There is therefore
# no shipped item_text<->item or option_text<->resp mapping to verify, and the
# recorded verification status is NO_ROUTE.
#
# What this script DOES check is the set of structural claims recorded in
# provenance_cognitive_load_klimova_2023_pwi.csv, so that a future attempt does not
# have to re-derive them, and so "couldn't check" is not mistaken for "checked":
#
#   (A) The table is two BETWEEN-SUBJECTS label conditions of the SAME eight items.
#       PWICONTROLa..h and PWIEXPa..h, 16 codes, and every respondent answers
#       exactly one of the two blocks (83 CONTROL + 87 EXP = 170, the N reported in
#       the deposit description and in Field Methods 38(1):46-61). Consequence for a
#       future extraction: letter a..h identifies one PWI item, and the CONTROL/EXP
#       prefix identifies the fully-labeled vs end-labeled response-scale version --
#       so item_text is shared across the pair and only option_text differs.
#
#   (B) The letterwise item means track across the two conditions (r = 0.76 over the
#       8 letters), which is what (A) predicts and what a letter-permuted pairing
#       would break.
#
#   (C) The a..h -> PWI-domain assignment is NOT determined. Two readings of an
#       8-column PWI block are both standard, and the data do not settle between
#       them; this script prints the numbers that show why.
#         reading 1 -- PWI-A's seven core domains + the optional spirituality/religion
#                      domain (a=standard of living ... h=spirituality)
#         reading 2 -- the "life as a whole" global item first, then the seven core
#                      domains (a=life as a whole, b=standard of living ... h=future
#                      security)  [NB h/g ordering differs between published forms]
#       Under reading 1 the LAST letter is spirituality/religion, which in a secular
#       Russian undergraduate sample should sit at or near the floor. It does not:
#       h sits in the upper half in both conditions (rank 8 of 8 in CONTROL, 5 of 8
#       in EXP; letter g is the minimum in both). That disfavours
#       reading 1 but does not establish reading 2, and neither reading is evidence
#       about the ORDER within the seven domains. Hence NO_ROUTE, not PARTIAL.
#
# The block itself rests on source availability, not on this script: the openICPSR
# deposit (doi:10.3886/E194063V2) contains exactly two files, Aggregated_pupil_data.csv
# and Final_data.csv -- no codebook, no questionnaire -- and the only publication,
# Field Methods 38(1):46-61 (doi:10.1177/1525822X251344709), is closed access with
# zero OA locations in Unpaywall.
#
# VERDICT: PASS here means "the structural claims recorded in provenance reproduce",
# NOT "an item-text mapping was verified". Nothing was shipped to verify.

suppressMessages(library(irw))

TABLE <- "cognitive_load_klimova_2023_pwi"
LETTERS8 <- letters[1:8]

d <- as.data.frame(irw::irw_fetch(TABLE))
d$blk <- ifelse(grepl("^PWICONTROL", d$item), "CONTROL", "EXP")

cat("== (A) item set and between-subjects structure ==\n")
its <- sort(unique(d$item))
cat("distinct items:", length(its), "\n")
cat(paste(its, collapse = ", "), "\n")
tt <- table(d$id, d$blk) > 0
n_ids       <- nrow(tt)
n_ctrl_only <- sum(tt[, "CONTROL"] & !tt[, "EXP"])
n_exp_only  <- sum(!tt[, "CONTROL"] & tt[, "EXP"])
n_both      <- sum(tt[, "CONTROL"] & tt[, "EXP"])
cat(sprintf("respondents: %d   CONTROL-only: %d   EXP-only: %d   BOTH: %d\n",
            n_ids, n_ctrl_only, n_exp_only, n_both))
cat(sprintf("expected (deposit description / paper N): 170 = 83 + 87, BOTH = 0\n"))

n_per <- table(d$item)
cat(sprintf("per-item n: CONTROL block all %s, EXP block all %s\n",
            paste(unique(n_per[paste0("PWICONTROL", LETTERS8)]), collapse = "/"),
            paste(unique(n_per[paste0("PWIEXP", LETTERS8)]), collapse = "/")))

cat("\n== (B) letterwise means, the two conditions side by side ==\n")
m  <- tapply(d$resp, d$item, mean)
a  <- m[paste0("PWICONTROL", LETTERS8)]
b  <- m[paste0("PWIEXP", LETTERS8)]
cat(sprintf("%-8s %10s %10s\n", "letter", "CONTROL", "EXP"))
for (i in seq_along(LETTERS8))
  cat(sprintf("%-8s %10.2f %10.2f\n", LETTERS8[i], a[i], b[i]))
r_pair <- cor(a, b)
cat(sprintf("\nPearson r over the 8 letters: %.3f  (recorded: 0.76)\n", r_pair))

cat("\n== (C) why the letter -> PWI-domain assignment is NOT determined ==\n")
cat(sprintf("lowest letter, CONTROL: %s (%.2f)   lowest letter, EXP: %s (%.2f)\n",
            LETTERS8[which.min(a)], min(a), LETTERS8[which.min(b)], min(b)))
cat(sprintf("letter h (spirituality/religion under reading 1): CONTROL %.2f (rank %d of 8), EXP %.2f (rank %d of 8)\n",
            a[8], rank(a)[8], b[8], rank(b)[8]))
cat("Reading 1 predicts letter h at or near the floor in a secular student sample.\n")
cat("It is not. Reading 1 is disfavoured; reading 2 is not thereby established, and\n")
cat("neither reading fixes the order of the seven domains. No published per-item\n")
cat("statistics, no per-item range structure (all 8 letters share the same 1-6 scale),\n")
cat("no subscale structure (the PWI is scored as one index) -- routes 1, 2, 3, 5 and 9\n")
cat("are all unavailable for this table.\n")

ok <- length(its) == 16 &&
      n_ids == 170 && n_both == 0 &&
      n_ctrl_only == 83 && n_exp_only == 87 &&
      abs(r_pair - 0.76) < 0.02 &&
      rank(a)[8] >= 5 && rank(b)[8] >= 5
cat("\n", if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n", sep = "")
