# verify_ajlan_2025_stemcell_knowledge.R -- Step 5b, route 9 (response matching), both axes.
#
# Claim: live item qX_Y is the .sav column whose name starts "QX.Y_" (variable label =
# the questionnaire wording shipped as item_text), and live resp maps to that column's
# value labels per item as the __items.csv states:
#   Likert q11_*, q14_*        : Strongly agree=3, Agree=2, Disagree=1, Strongly disagree=0
#   yes/no default             : Yes=2, Not sure=1, No=0
#   q20, q22_4 (reversed)      : Yes=0, Not sure=1, No=2
#   q23_1, q23_3 (1..3 offset) : Yes=1, Not sure=2, No=3
# Live ids are the .sav's own Fsno (data/ajlan_2025_stemcell_knowledge.py renames it and
# drops one duplicated Fsno), so the check is row-aligned: every id x item cell of the
# live table is compared with the label the respondent ticked in the source file.
# Source: PeerJ 10.7717/peerj.19127 Supplemental Information 4 (peerj-13-19127-s004.sav,
# sha256 41ba94f8abdb2519bad77e7f3c3a6a84fdaf7414bee0174928a73f4d9e1f009f), fetched
# from the Europe PMC supplementaryFiles endpoint.
suppressMessages({library(irw); library(haven)})
TABLE <- "ajlan_2025_stemcell_knowledge"

zip <- tempfile(fileext = ".zip")
download.file("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11967409/supplementaryFiles",
              zip, mode = "wb", quiet = TRUE)
sav <- unzip(zip, files = "peerj-13-19127-s004.sav", exdir = tempdir())
raw <- read_sav(sav)
raw <- raw[!duplicated(raw$Fsno), ]

LIK <- c("Strongly agree" = 3, "Agree" = 2, "Disagree" = 1, "Strongly disagree" = 0)
YN  <- c("Yes" = 2, "Not sure" = 1, "No" = 0)
YNR <- c("Yes" = 0, "Not sure" = 1, "No" = 2)
YN3 <- c("Yes" = 1, "Not sure" = 2, "No" = 3)
items <- c(paste0("q11_", 1:3), paste0("q14_", 1:9), paste0("q", 15:21),
           paste0("q22_", 1:6), paste0("q23_", 1:5))
keymap <- function(i) {
  if (grepl("^q1[14]_", i)) LIK else if (i %in% c("q20", "q22_4")) YNR
  else if (i %in% c("q23_1", "q23_3")) YN3 else YN
}
src_col <- function(i) {
  pre <- paste0("Q", sub("_", ".", sub("^q", "", i), fixed = TRUE), "_")
  n <- grep(pre, names(raw), fixed = TRUE, value = TRUE)
  n[startsWith(n, pre)][1]
}

d <- irw::irw_fetch(TABLE)
cat(sprintf("live rows %d, ids %d; source rows after dedupe %d\n",
            nrow(d), length(unique(d$id)), nrow(raw)))

# expected resp per id for each item, from the source's value labels
EXP <- sapply(items, function(i) {
  lab <- as.character(as_factor(raw[[src_col(i)]], levels = "labels"))
  unname(keymap(i)[lab])
})
rownames(EXP) <- as.character(raw$Fsno)

agree <- function(i, j) {             # live item i vs expected from source item j
  li <- d[d$item == i, ]
  e <- EXP[as.character(li$id), j]
  c(sum(li$resp == e, na.rm = TRUE), nrow(li))
}
cat(sprintf("\n%-6s %-58s %10s %14s\n", "item", "source column (variable label basis)", "diag", "best off-diag"))
ok <- logical(length(items)); names(ok) <- items
for (i in items) {
  dg <- agree(i, i)
  off <- max(sapply(setdiff(items, i), function(j) agree(i, j)[1]))
  ok[i] <- dg[1] == dg[2] && off < dg[2]
  cat(sprintf("%-6s %-58s %4d/%-5d %8d/%d\n", i, substr(src_col(i), 1, 58), dg[1], dg[2], off, dg[2]))
}
# How the alternative (un-reversed / un-offset) coding would fare, for the 4 odd items
alt <- sapply(c("q20", "q22_4", "q23_1", "q23_3"), function(i) {
  li <- d[d$item == i, ]
  lab <- as.character(as_factor(raw[[src_col(i)]], levels = "labels"))
  names(lab) <- as.character(raw$Fsno)
  sum(li$resp == unname(YN[lab[as.character(li$id)]]), na.rm = TRUE)
})
cat("\nagreement of q20/q22_4/q23_1/q23_3 under the DEFAULT Yes=2/NotSure=1/No=0 coding instead:",
    paste(names(alt), alt, sep = "=", collapse = ", "), "\n")
cat(sprintf("items reproduced cell-for-cell and distinguished from every other item: %d/%d\n",
            sum(ok), length(ok)))
cat("Not established: nothing about the wording beyond the tie of code -> .sav variable label ->\n",
    "questionnaire row; shipped item_text (S2 questionnaire) is contained in the .sav variable label\n",
    "for 29/30 items (letters-only compare); q17 differs only by 'treatments' (S2) vs 'treatment' (label).\n", sep = "")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
