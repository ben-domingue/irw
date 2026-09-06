#!/usr/bin/env Rscript
# Mapping verification for fisher_2019_belonging.
#
# What is being verified: that item code `accepted` carries the "I feel accepted"
# wording and `insignificant` carries the "I feel insignificant" wording -- i.e.
# that the two item texts are not swapped.
#
# Route 9 (response-frequency matching): the live table's per-item x per-level
# counts are compared cell-for-cell against the study's own S1 Data columns of
# the same names (PLOS 10.1371/journal.pone.0209279.s001, sheet "newdat").
# Route 6/8 support: the direction of each column's correlates in S1 is checked
# against the paper's own findings (women feel less accepted / more insignificant;
# accepted mitigates distress, insignificant raises it), which fixes which column
# is the positively-valenced item independently of the column names.

suppressMessages({library(irw); library(readxl)})

url <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0209279.s001"
tmp <- file.path(tempdir(), "fisher2019_s001.xlsx")
if (!file.exists(tmp)) download.file(url, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp, sheet = "newdat"))

live <- irw::irw_fetch("fisher_2019_belonging")   # 706 rows -- negligible export
live_tab <- table(live$item, live$resp)

src_tab <- rbind(
  accepted      = as.integer(table(factor(raw$accepted,      levels = 1:6))),
  insignificant = as.integer(table(factor(raw$insignificant, levels = 1:6))))
colnames(src_tab) <- 1:6

cat("--- live per-item x resp counts ---\n"); print(live_tab)
cat("\n--- S1 Data per-column x value counts ---\n"); print(src_tab)

live_m <- matrix(as.integer(live_tab[c("accepted","insignificant"), as.character(1:6)]),
                 nrow = 2, byrow = FALSE,
                 dimnames = list(c("accepted","insignificant"), 1:6))
live_m[] <- as.integer(live_tab[c("accepted","insignificant"), as.character(1:6)])
counts_match <- identical(as.integer(live_m), as.integer(src_tab))
cat("\nAll 12 item x level cells identical: ", counts_match, "\n", sep = "")

# Cross-item check: the two columns' distributions are far apart, so the match is
# not satisfiable by a swap.
cat("means  live: accepted=", round(mean(live$resp[live$item=="accepted"]),3),
    " insignificant=", round(mean(live$resp[live$item=="insignificant"]),3), "\n", sep = "")
swapped_match <- identical(as.integer(live_m[c(2,1), ]), as.integer(src_tab))
cat("swapped assignment would also match: ", swapped_match, "\n", sep = "")

# Direction check against the paper's reported findings.
cr <- function(a, b) round(cor(as.numeric(raw[[a]]), as.numeric(raw[[b]]), use = "complete.obs"), 3)
cat("\ncor(accepted, female)      = ", cr("accepted","female"),
    "   [paper: women feel LESS accepted -> expect < 0]\n", sep = "")
cat("cor(insignificant, female) = ", cr("insignificant","female"),
    "   [paper: women feel MORE insignificant -> expect > 0]\n", sep = "")
cat("cor(accepted, distress)      = ", cr("accepted","distress"),
    "   [paper: acceptance mitigates distress -> expect < 0]\n", sep = "")
cat("cor(insignificant, distress) = ", cr("insignificant","distress"),
    "   [paper: insignificance lowers well-being -> expect > 0]\n", sep = "")

dir_ok <- cr("accepted","female") < 0 && cr("insignificant","female") > 0 &&
          cr("accepted","distress") < 0 && cr("insignificant","distress") > 0

cat("\nVERDICT: ", if (counts_match && !swapped_match && dir_ok) "PASS" else "FAIL", "\n", sep = "")
