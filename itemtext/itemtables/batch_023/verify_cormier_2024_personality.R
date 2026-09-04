# verify_cormier_2024_personality.R -- Step 5b, route 9 (response-frequency matching).
#
# CLAIM UNDER TEST: the option_text <-> resp mapping shipped for this table
# (1=Disagree strongly, 2=Disagree a little, 3="Neutral: no opinion",
# 4=Agree a little, 5=Agree strongly) is the mapping that actually produced the
# live integers. The item <-> item_text axis needs no statistical route: the IRW
# item codes ARE the Qualtrics column names (Q20_1..Q20_16) and the item text is
# each column's own Qualtrics question label, so there is no positional step to
# get wrong. What COULD be wrong is the label->integer direction, which comes
# from RESP_MAP in data/cormier_2024_hearing_battery.py, not from the paper.
#
# The falsifiable prediction: counting each label per column in the raw PLOS S2
# Qualtrics export and each integer per item in the live IRW table must agree
# cell for cell across all 16 items x 5 levels. A reversed or permuted mapping
# breaks it immediately, because the 16 items' distributions are all different.

suppressMessages(library(irw))

TABLE  <- "cormier_2024_personality"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0304428.s002")
MAP <- c("Disagree strongly" = 1, "Disagree a little" = 2, "Neutral: no opinion" = 3,
         "Agree a little" = 4, "Agree strongly" = 5)

raw <- read.csv(SI_URL, check.names = FALSE, colClasses = "character")
raw <- raw[-c(1, 2), ]                       # 2 Qualtrics header rows
cols <- paste0("Q20_", 1:16)

live <- irw::irw_fetch(TABLE)
live$resp <- as.integer(as.character(live$resp))

cat(sprintf("%-8s %-22s %8s %8s\n", "item", "label", "raw_n", "live_n"))
bad <- 0
for (cl in cols) {
    v <- raw[[cl]]
    for (lb in names(MAP)) {
        k  <- unname(MAP[[lb]])
        nr <- sum(v == lb, na.rm = TRUE)
        nl <- sum(live$item == cl & live$resp == k)
        flag <- if (nr == nl) "" else "  <-- MISMATCH"
        if (nr != nl) bad <- bad + 1
        cat(sprintf("%-8s %-22s %8d %8d%s\n", cl, lb, nr, nl, flag))
    }
}

cat(sprintf("\ncells compared: %d   mismatched: %d\n", length(cols) * length(MAP), bad))
cat("What this does NOT establish: nothing about item identity beyond the column-name\n",
    "identity already in the source (this route would pass even if two items' TEXT were\n",
    "swapped, since it only reads the codes) -- that axis rests on the Qualtrics labels,\n",
    "which name their own column. It also cannot detect a level permutation that happened\n",
    "to preserve every count, which does not occur here (all 80 cell counts differ widely).\n",
    sep = "")

cat(if (bad == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
