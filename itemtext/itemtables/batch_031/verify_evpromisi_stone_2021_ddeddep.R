# verify_evpromisi_stone_2021_ddeddep.R
#
# CLAIM UNDER TEST: each IRW item code DDEDDEP04/05/06/17/22/29/36/41 carries the
# item text the deposit's codebooks print against that very variable name, and the
# option labels Never..Always sit on resp 1..5 in that order.
#
# ROUTE 9 (response-frequency matching), run on the item axis. The deposit's three
# daily-diary SAS files that contain the depression block (community, chemotherapy,
# premenstrual) hold one column per item under the SAME name the IRW table uses.
# If the shipped text/level mapping were permuted, the per-item x per-level count
# table computed from those raw columns would no longer reproduce the live table
# cell for cell. Counts are hard-coded from the raw files (Harvard Dataverse
# doi:10.7910/DVN/G4E2SR, files promis_ecolval_{cs,bc,pms}_daily.sas7bdat, pooled)
# so the script needs only the live IRW data.

suppressMessages(library(irw))
TABLE <- "evpromisi_stone_2021_ddeddep"

RAW <- rbind(
  DDEDDEP04 = c(5918,  840,  471, 158, 38),
  DDEDDEP05 = c(5502,  990,  661, 245, 30),
  DDEDDEP06 = c(5207, 1108,  791, 259, 53),
  DDEDDEP17 = c(3586, 1812, 1471, 473, 78),
  DDEDDEP22 = c(5704,  909,  568, 194, 48),
  DDEDDEP29 = c(4336, 1449, 1176, 385, 74),
  DDEDDEP36 = c(3593, 1859, 1436, 441, 84),
  DDEDDEP41 = c(5531, 1003,  636, 205, 47))
colnames(RAW) <- 1:5

d <- irw::irw_fetch(TABLE)
LIVE <- table(factor(d$item, levels = rownames(RAW)), factor(d$resp, levels = 1:5))
LIVE <- matrix(as.integer(LIVE), nrow = nrow(RAW), dimnames = dimnames(RAW))

cat("per-item x per-level counts: raw deposit columns (R) vs live IRW table (L)\n")
cat(sprintf("%-10s %-32s %-32s %s\n", "item", "raw (resp 1..5)", "live (resp 1..5)", "ok"))
for (i in rownames(RAW))
  cat(sprintf("%-10s %-32s %-32s %s\n", i,
      paste(RAW[i, ], collapse = " "), paste(LIVE[i, ], collapse = " "),
      if (all(RAW[i, ] == LIVE[i, ])) "yes" else "NO"))

ndist <- length(unique(apply(RAW, 1, paste, collapse = "-")))
cat(sprintf("\ndistinct count-vectors among the 8 items: %d of 8 (a permutation of any two items would break at least one cell)\n", ndist))
cat("This pins every item against every other item, and the level order Never..Always = 1..5,\n")
cat("because the raw column names ARE the IRW item codes and the codebook keys its text to those names.\n")
cat("What it does NOT establish: the WORDING itself, which rests on the codebook document\n")
cat("(the .sas7bdat files carry no variable labels); it establishes only that code X in IRW is column X in the deposit.\n")

ok <- all(RAW == LIVE) && ndist == 8
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
