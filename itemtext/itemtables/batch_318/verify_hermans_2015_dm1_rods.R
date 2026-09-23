# verify_hermans_2015_dm1_rods.R -- Step 5b mapping check for hermans_2015_dm1_rods (batch_318).
#
# Basis: item codes r_ods001..r_ods144 are the S1 Appendix .xls's own column names, melted
# unchanged by data/hermans_2015_dm1_rods.py, and the paper's S1 Appendix legend
# (PLOS ONE 10.1371/journal.pone.0139944) labels every one of the 105 codes by name
# ("r_ods089 = eat soup", "r_ods018 = run", ...). The item_text is that legend, so the
# mapping is an explicit code label, not an order inference.
#
# This script tests that the legend's labels are attached to the right COLUMNS, using two
# falsifiable predictions from the data:
#  (A) Paper Table 2 publishes Rasch locations (logits) for the 25 final DM1-Activ C items,
#      named by wording. Mapping those 25 names to codes via the legend, item difficulty in
#      the live data (1 - mean/2) must rank-order like the published locations.
#  (B) Nested tasks in the item bank must be monotone in difficulty: walk up 1 < 2 < 3
#      stairs, walk outdoor <100 m < <1 km < >1 km, stand <15 min < stand for hours,
#      wash face < wash entire body, walk on even < uneven ground, walk indoor < outdoor >1 km.
# Table 2's "carry and put down heavy object (10 kg)" is taken as r_ods053 ("carry/put down a
# heavy object"), not r_ods052 ("lift heavy object (10 kilograms)"); both are printed below.
# What this does NOT establish: route A pins 25 of 105 items by rank and route B a further
# handful by nesting; a swap between two unanchored, similar-difficulty items (e.g. read a
# book / read a newspaper) would pass. The code-label legend is what ties those.

suppressMessages(library(irw))
TABLE <- "hermans_2015_dm1_rods"
d <- irw::irw_fetch(TABLE)
m <- tapply(d$resp, d$item, mean)
diff <- 1 - m / 2   # 0 = everyone able without difficulty

# (A) Table 2 locations, final 25 items -> legend codes. "run" has two age-split
# locations (2.343 <30 y, 3.904 >=30 y); the >=30 group is ~90% of the sample, so use it.
A <- data.frame(
  code = c("r_ods089","r_ods139","r_ods068","r_ods077","r_ods060","r_ods064","r_ods061",
           "r_ods007","r_ods055","r_ods111","r_ods120","r_ods085","r_ods058","r_ods110",
           "r_ods108","r_ods113","r_ods094","r_ods044","r_ods029","r_ods008","r_ods004",
           "r_ods022","r_ods015","r_ods053","r_ods018"),
  name = c("eat soup","visit family or friends","care for hair and body","dress lower body",
           "wash upper body","take a shower","wash lower body","get out of bed","move a chair",
           "do the dusting/cleaning","do the shopping","tie the laces","catch an object",
           "use dustpan and brush","empty dustbin","make up your bed","vacuum clean",
           "serve coffee/tea on a tray","dance","stand up from squatting","stand on one leg",
           "walk uphill","walk 3 flights of stairs","carry/put down heavy object (10 kg)","run"),
  loc = c(-3.305,-2.967,-2.608,-2.314,-2.278,-2.222,-2.150,-1.777,-1.217,-1.071,-0.825,
          -0.569,-0.527,-0.145,-0.013,0.491,0.807,1.408,1.844,2.162,2.287,2.399,2.832,3.509,3.904),
  stringsAsFactors = FALSE)
A$obs <- diff[A$code]
cat("(A) Table 2 Rasch location vs live difficulty (1 - mean/2)\n")
cat(sprintf("%-9s %-38s %7s %7s\n", "code", "Table 2 item", "logit", "diff"))
for (i in seq_len(nrow(A))) cat(sprintf("%-9s %-38s %7.3f %7.3f\n", A$code[i], A$name[i], A$loc[i], A$obs[i]))
rho <- cor(A$loc, A$obs, method = "spearman")
cat(sprintf("Spearman rho = %.3f over %d items\n", rho, nrow(A)))

# Permutation null: how often does a random assignment of the 25 labels to these codes reach rho?
set.seed(1); null <- replicate(5000, cor(A$loc, sample(A$obs), method = "spearman"))
cat(sprintf("random-permutation null: max rho %.3f, 99.9th pct %.3f\n", max(null), quantile(null, .999)))

# (B) nested chains -- each must be strictly increasing in difficulty
chains <- list(
  stairs  = c("r_ods013","r_ods014","r_ods015"),
  outdoor = c("r_ods019","r_ods020","r_ods021"),
  stand   = c("r_ods002","r_ods003"),
  wash    = c("r_ods062","r_ods063"),
  ground  = c("r_ods026","r_ods027"),
  indoor_vs_far = c("r_ods012","r_ods021"))
cat("\n(B) nested-task chains (difficulty must increase left to right)\n")
okB <- TRUE
for (nm in names(chains)) {
  v <- diff[chains[[nm]]]
  ok <- all(diff(v) > 0)
  okB <- okB && ok
  cat(sprintf("%-14s %s  %s  %s\n", nm, paste(chains[[nm]], collapse = " < "),
              paste(sprintf("%.3f", v), collapse = " < "), if (ok) "ok" else "VIOLATED"))
}

cat(sprintf("\nr_ods052 lift heavy object (10 kg) diff %.3f; r_ods053 carry/put down diff %.3f\n", diff["r_ods052"], diff["r_ods053"]))
cat("\nNot established: order among unanchored items of similar difficulty outside A/B.\n")
pass <- rho >= 0.85 && rho > quantile(null, .999) && okB
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
