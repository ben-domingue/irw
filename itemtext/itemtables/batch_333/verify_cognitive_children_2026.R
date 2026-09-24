# verify_cognitive_children_2026.R
#
# CLAIM UNDER TEST: automated_finding/process_1570.py assigns the 18 item codes
#   att_1..att_5, mem_1..mem_5, lang_1..lang_4, log_1..log_4
# POSITIONALLY (matrix.columns = item_codes) to 1-based columns 5..22 (E..V) of
# both sheets of DATA_MATRIX_ANONYMIZED.xlsx (figshare 32519529 v1), and the
# shipped item_text for each code is the row-3 indicator header at that column
# (hard-coded below as CLAIMED, exactly as shipped).
#
# A positional assignment leaves no trace of the source column in the code, so
# the mapping is checked by REPRODUCING the live responses: for every code, each
# of the 18 source columns is scored against that code's live cells (50 children
# x 2 waves, keyed on id P001..P050 and wave 0/1). The claim holds only if each
# code is reproduced exactly by its claimed column AND by no other column, which
# distinguishes every item from every other item. Swapping item_text for any two
# codes would break the diagonal.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "cognitive_children_2026"
URL   <- "https://ndownloader.figshare.com/files/65116518"   # figshare 32519529 v1
COLS  <- 5:22
ITEMS <- c(paste0("att_",1:5), paste0("mem_",1:5), paste0("lang_",1:4), paste0("log_",1:4))
CLAIMED <- c(
  "Maintains attention during riddles", "Follows oral and visual instructions",
  "Concentrates on color patterns", "Correctly identifies body parts",
  "Focuses on correctly matching figures",
  "Remembers answers and numerical sequences", "Remembers tongue twisters/rhymes",
  "Retains patterns and sequences", "Remembers names and location of body parts",
  "Memorizes shapes and colors",
  "Explains numerical answers clearly", "Pronounces words and repeats phrases correctly",
  "Verbalizes color patterns", "Names body parts",
  "Relates numbers with clues", "Relates images with words",
  "Associates colors in sequences", "Associates geometric shapes with similar objects")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, mode = "wb", quiet = TRUE)

# 1. header diff: shipped text vs the source header at each claimed position, both sheets
hdr_ok <- TRUE
for (s in c("Pre-Intervention", "Post-Intervention")) {
  h <- readxl::read_excel(tmp, sheet = s, col_names = FALSE, n_max = 3, .name_repair = "minimal")
  grp <- as.character(unlist(h[2, COLS]))
  txt <- as.character(unlist(h[3, COLS]))
  n_eq <- sum(txt == CLAIMED)
  cat(sprintf("%s: header row 3 cols 5-22 equal shipped item_text for %d/18\n", s, n_eq))
  cat("  row-2 group labels start at cols:",
      paste(COLS[!is.na(grp)], grp[!is.na(grp)], sep = "=", collapse = "; "), "\n")
  hdr_ok <- hdr_ok && n_eq == 18
}
cat("\n")

# 2. reproduce live responses column by column
read_wave <- function(sheet, wave) {
  raw <- readxl::read_excel(tmp, sheet = sheet, col_names = FALSE, .name_repair = "minimal")
  dat <- raw[4:53, ]                               # 50 participant rows, as the script
  list(id = as.character(unlist(dat[[3]])), wave = wave,
       m = sapply(COLS, function(k) suppressWarnings(as.numeric(unlist(dat[[k]])))))
}
src <- list(read_wave("Pre-Intervention", 0), read_wave("Post-Intervention", 1))

live <- irw::irw_fetch(TABLE)
lv <- setNames(as.numeric(live$resp), paste(live$id, live$wave, live$item, sep = "|"))
cat("live cells:", length(lv), "\n\n")

M <- matrix(0, length(ITEMS), length(COLS), dimnames = list(ITEMS, COLS))
tot <- setNames(numeric(length(ITEMS)), ITEMS)
for (i in seq_along(ITEMS)) for (j in seq_along(COLS)) {
  ok <- 0; n <- 0
  for (w in src) {
    kk <- paste(w$id, w$wave, ITEMS[i], sep = "|")
    have <- kk %in% names(lv)
    n <- n + sum(have)
    ok <- ok + sum(w$m[have, j] == lv[kk[have]], na.rm = TRUE)
  }
  M[i, j] <- ok; tot[i] <- n
}
cat(sprintf("%-7s %5s %9s %-10s %s\n", "item", "n", "claimed", "exact-cols", "best other col (matches)"))
diag_ok <- TRUE
for (i in seq_along(ITEMS)) {
  exact <- COLS[M[i, ] == tot[i]]
  oth <- M[i, -i]; jb <- which.max(oth)
  cat(sprintf("%-7s %5d %9d %-10s col %d (%d)\n", ITEMS[i], tot[i], M[i, i],
              paste(exact, collapse = ","), COLS[-i][jb], oth[jb]))
  diag_ok <- diag_ok && tot[i] == 100 && identical(exact, COLS[i])
}
cat("\nclaimed mapping reproduces", sum(diag(M)), "of", sum(tot), "live responses;",
    "max off-diagonal agreement", max(M[row(M) != col(M)]), "of 100\n")
cat("Note: this pins item<->text for all 18 items. It does NOT verify the\n",
    "option_text<->resp axis (1=Never .. 5=Always), which rests on the companion\n",
    "figshare 32114668 description and is unlabelled at points 2-4.\n", sep = "")

cat(if (hdr_ok && diag_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
