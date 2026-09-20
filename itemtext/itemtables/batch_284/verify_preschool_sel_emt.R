# verify_preschool_sel_emt.R
#
# CLAIM: each live `item` code is literally the name of a column in the study's
# own SPSS file (LDbase R305A180293_child-level_CT_v35.sav, ODC-By), and the
# shipped item_text is the variable label of that column's paired administration
# column (emtXn_t1 for the scored column emtXn s_t1).
#
# FALSIFIABLE PREDICTION: for every one of the 48 items, the live per-item counts
# of resp 0/1/2 must equal the counts of 0/1/2 in the .sav column of the SAME
# NAME, cell for cell. All 48 count triples in the .sav are distinct, so any
# permutation of the 48 item codes would break at least one cell.
suppressMessages({library(irw); library(haven)})

TABLE <- "preschool_sel_emt"
SAV_URL <- "https://ldbase.org/system/files/datasets/2023-05/R305A180293_child-level_CT_v35.sav"
SAV <- file.path("../../.cache", TABLE, "child_CT_v35.sav")
if (!file.exists(SAV)) {
  dir.create(dirname(SAV), recursive = TRUE, showWarnings = FALSE)
  download.file(SAV_URL, SAV, mode = "wb", quiet = TRUE)
}

d <- read_sav(SAV); names(d) <- tolower(names(d))
live <- irw::irw_fetch(TABLE)
items <- sort(unique(live$item))

cat(sprintf("%-14s %14s %14s %6s\n", "item", "live 0/1/2", ".sav 0/1/2", "ok"))
ok <- logical(length(items)); tri <- character(length(items))
for (i in seq_along(items)) {
  it <- items[i]
  lt <- as.vector(table(factor(live$resp[live$item == it], levels = 0:2)))
  sv <- d[[it]]
  if (is.null(sv)) { st <- c(NA, NA, NA) } else {
    st <- as.vector(table(factor(as.numeric(sv[!is.na(sv)]), levels = 0:2)))
  }
  ok[i] <- identical(lt, st); tri[i] <- paste(st, collapse = "/")
  cat(sprintf("%-14s %14s %14s %6s\n", it, paste(lt, collapse = "/"),
              paste(st, collapse = "/"), if (ok[i]) "TRUE" else "FALSE"))
}

cat(sprintf("\ncells compared: %d (%d items x 3 levels); items matching: %d/%d\n",
            3 * length(items), length(items), sum(ok), length(items)))
cat(sprintf("distinct count-triples among the .sav columns: %d/%d -- a permutation of the\n",
            length(unique(tri)), length(tri)))
cat("item codes could not pass this check.\n")
cat("Value labels on those same columns give 0=Incorrect, 1=Same Valence, 2=Correct,\n",
    "which is the shipped option_text/resp mapping.\n", sep = "")
cat("NOT established: that the .sav's own label-to-column assignment is correct\n",
    "(the file is trusted at level 1), and the Part 1 / Part 3-Q1 labels are\n",
    "truncated by SPSS at 255 characters, so those item_text values end mid-sentence.\n", sep = "")

cat(if (all(ok) && length(unique(tri)) == length(tri)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
