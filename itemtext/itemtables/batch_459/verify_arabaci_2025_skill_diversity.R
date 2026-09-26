# verify_arabaci_2025_skill_diversity.R -- Step 5b check, batch_459.
#
# Claim: SkillDiversity1..4 carry the four Skill Diversity statements of the
# deposit's "Supplementary Data 2 - Appendix A.docx" in the order the appendix
# lists them (mapping_basis = paper_order).
#
# What CAN be checked, and is checked here:
#   (a) the live codes are the workbook's own columns "Skill Diversity1..4"
#       (space stripped): per-item frequency tables of the live data reproduce
#       the Dataverse .xlsx column-for-column, and a column permutation would
#       break this (the four items' distributions are all distinct);
#   (b) the four items are the paper's skill-diversity scale, stored raw in the
#       1 = strongly disagree .. 5 = strongly agree direction: the SD of the
#       4-item mean reproduces the paper's Table 4 value .93217.
# What this does NOT establish: that the workbook's column numbering follows the
# appendix's (unnumbered) listing order. The paper publishes no per-item
# statistics, so nothing distinguishes the four statements from one another.
# (b) is invariant to item order. Hence verification status NO_ROUTE for the
# item_text <-> item axis; this script can only FAIL if (a) or (b) breaks.

suppressMessages(library(irw))
TABLE <- "arabaci_2025_skill_diversity"
PUB_SD <- 0.93217   # Arabaci & Akca (2025) RBGN 27(3), Table 4, Skill Diversity SD

d <- as.data.frame(irw::irw_fetch(TABLE))
codes <- paste0("SkillDiversity", 1:4)

# source workbook, fetched fresh from Dataverse (CC0)
tmp <- tempfile(fileext = ".xlsx")
download.file("https://dataverse.harvard.edu/api/access/datafile/12030780?format=original",
              tmp, mode = "wb", quiet = TRUE)
w <- as.data.frame(readxl::read_excel(tmp))
w <- w[-nrow(w), ]                      # trailing codebook-legend row
ok_a <- TRUE
for (i in 1:4) {
  src <- table(factor(as.integer(w[[paste0("Skill Diversity", i)]]), levels = 1:5))
  liv <- table(factor(d$resp[d$item == codes[i]], levels = 1:5))
  same <- all(src == liv)
  ok_a <- ok_a && same
  cat(sprintf("%-16s source %-22s live %-22s %s\n", codes[i],
              paste(src, collapse = "/"), paste(liv, collapse = "/"),
              if (same) "match" else "MISMATCH"))
}

wide <- reshape(d[d$item %in% codes, c("id", "item", "resp")],
                idvar = "id", timevar = "item", direction = "wide")
sc <- rowMeans(wide[, paste0("resp.", codes)])
obs_sd <- sd(sc)
ok_b <- abs(obs_sd - PUB_SD) < 5e-4
cat(sprintf("\nscale-mean SD: observed %.5f, published %.5f -> %s\n",
            obs_sd, PUB_SD, if (ok_b) "match" else "MISMATCH"))
cat("NOT established: which appendix statement each column number carries --\n",
    "no per-item statistics are published; status NO_ROUTE for item order.\n", sep = "")
cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
