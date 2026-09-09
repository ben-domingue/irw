# verify_merlo2025_eet.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (two axes):
#
#  (A) item axis. merlo2025_eet's item codes EET_01..EET_29 are the literal column
#      names of the figshare deposit's Final-dataset.csv (data/merlo2025_engagement.py
#      melts them by name -- core-model derivation pattern 1), and the deposit's own
#      data dictionary Final-dataset-grid.csv maps each of those names to its item
#      wording. This script checks the one link in that chain that could silently be
#      wrong: that live item EET_nn really carries deposit column EET_nn's responses.
#      Per-item means are compared EXACTLY (tol 1e-9). The 29 deposit means are
#      pairwise distinct -- the closest pair, EET_12 vs EET_14, differ by 0.00094 --
#      so any permutation of the 29 codes breaks this test for every permuted item.
#
#  (B) option axis. The shipped anchors run 1 = Never ... 6 = Always (Merlo et al.
#      2026, Formazione & insegnamento 24(2):114-129, sec. 3.2.2: "coded on a 6-point
#      scale from 1 = Never to 6 = Always"). The deposit publishes no value labels, so
#      this is checked against the questionnaire's own attention-check item, EET_17,
#      whose wording IS the instruction "Seleziona la risposta Mai" (select the answer
#      "Never"). Under the shipped direction the compliant answer is resp == 1; under
#      the reversed direction it would be resp == 6.
#
# WHAT THIS DOES NOT ESTABLISH: nothing here checks the WORDS. That an item labelled
# "Anacardi" means cashews, and that the English in the *_translated columns is a
# faithful translation, are outside any numeric route. It also pins only the two
# ENDS of the response scale, not the four interior anchors (Rarely/Sometimes/Often/
# Almost always), which are taken from the paper's own ordered list.

suppressMessages(library(irw))

TABLE <- "merlo2025_eet"
TOL   <- 1e-9
GRID  <- "https://ndownloader.figshare.com/files/58188718"  # Final-dataset-grid.csv
DATA  <- "https://ndownloader.figshare.com/files/58188073"  # Final-dataset.csv

raw  <- read.csv2(DATA,  fileEncoding = "UTF-8-BOM", check.names = FALSE)
grid <- read.csv2(GRID,  fileEncoding = "UTF-8-BOM", check.names = FALSE)

cols <- grep("^EET_", names(raw), value = TRUE)
dep  <- sapply(cols, function(c) mean(as.numeric(raw[[c]]), na.rm = TRUE))

d    <- irw::irw_fetch(TABLE)          # 30,885 rows; a trivial export
live <- tapply(as.numeric(d$resp), d$item, mean)[cols]

food <- setNames(sub("^[^:]*:\\s*", "", trimws(grid$ITEM)), trimws(grid$VARIABLE))[cols]

cat("--- (A) item axis: deposit column mean vs live item mean ---\n")
cat(sprintf("%-7s %-34s %10s %10s %12s\n", "item", "dictionary wording", "deposit", "live", "diff"))
for (i in seq_along(cols))
    cat(sprintf("%-7s %-34s %10.6f %10.6f %12.2e\n",
                cols[i], substr(food[i], 1, 34), dep[i], live[i], live[i] - dep[i]))
worst <- max(abs(live - dep))
gaps  <- as.matrix(dist(dep)); diag(gaps) <- NA
cat(sprintf("\nlargest |live - deposit| : %.2e (tolerance %.0e)\n", worst, TOL))
cat(sprintf("closest pair of deposit means: %.5f -- any code permutation moves an item\n",
            min(gaps, na.rm = TRUE)))
okA <- worst <= TOL

cat("\n--- (B) option axis: attention-check item EET_17 ---\n")
cat("EET_17 wording (deposit dictionary): ", food[["EET_17"]], "\n", sep = "")
r17 <- as.numeric(d$resp[d$item == "EET_17"])
tab <- table(factor(r17, levels = 1:6))
cat("live EET_17 response counts 1..6: ", paste(tab, collapse = " / "), "\n", sep = "")
cat(sprintf("compliant under shipped 1=Never : %d/%d (%.1f%%)\n",
            tab[["1"]], length(r17), 100 * tab[["1"]] / length(r17)))
cat(sprintf("compliant under reversed 6=Never: %d/%d (%.1f%%)\n",
            tab[["6"]], length(r17), 100 * tab[["6"]] / length(r17)))
okB <- tab[["1"]] > 10 * max(tab[c("2","3","4","5","6")])

cat("\n--- (B, corroborating) semantic ordering of the food items ---\n")
o <- order(live, decreasing = TRUE)
cat("most frequently eaten: ",
    paste(sprintf("%s %.2f", food[o[1:3]], live[o[1:3]]), collapse = ", "), "\n", sep = "")
cat("least frequently eaten: ",
    paste(sprintf("%s %.2f", food[rev(o)[1:3]], live[rev(o)[1:3]]), collapse = ", "), "\n", sep = "")
cat("(everyday Italian staples at the top and rare foods at the bottom is only\n",
    " consistent with higher resp = more often, i.e. 6 = Always.)\n", sep = "")

cat("\n", if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n", sep = "")
