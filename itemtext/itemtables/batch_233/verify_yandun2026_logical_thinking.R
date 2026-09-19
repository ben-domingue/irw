# verify_yandun2026_logical_thinking.R
#
# CLAIM UNDER TEST: data/yandun2026_cognitive.py assigns the item codes
# log1..log4 POSITIONALLY to columns 19..22 (1-based) of each sheet of
# DATA_MATRIX_TRANSLATED.xlsx, i.e. to the four "Logical Thinking" indicator
# headers on row 3 of that sheet, in order:
#     log1 = "Relates numbers with clues"
#     log2 = "Relates images with words"
#     log3 = "Associates colors in sequences"
#     log4 = "Associates geometric shapes with similar objects"
# A positional assignment leaves no trace of the source column in the code, so
# the mapping is checked by REPRODUCING the live responses from the source
# columns, and by showing that no other assignment of the four columns to the
# four codes reproduces them.
#
# The test is falsifiable: if item_text for, say, log1 and log3 were swapped,
# the identity permutation would stop reproducing and a different one would.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "yandun2026_logical_thinking"
URL   <- "https://ndownloader.figshare.com/files/64067737"   # figshare 32114668 v1
COLS  <- 19:22          # 1-based source columns for the Logical Thinking block
ITEMS <- paste0("log", 1:4)

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, mode = "wb", quiet = TRUE)

read_wave <- function(sheet, wave) {
  raw <- readxl::read_excel(tmp, sheet = sheet, col_names = FALSE,
                            .name_repair = "minimal")
  dat <- raw[4:nrow(raw), ]                       # rows 1-3 are title/headers
  ids <- suppressWarnings(as.numeric(unlist(dat[[1]])))
  m   <- sapply(COLS, function(k) suppressWarnings(as.numeric(unlist(dat[[k]]))))
  keep <- !is.na(ids)
  list(id = ids[keep], wave = wave, m = m[keep, , drop = FALSE])
}

hdr <- readxl::read_excel(tmp, sheet = "Pre-Intervention", col_names = FALSE,
                          n_max = 3, .name_repair = "minimal")
cat("Source header row 3 at columns", paste(COLS, collapse = ","), ":\n")
for (k in seq_along(COLS)) cat(sprintf("  col %2d -> %-50s (claimed %s)\n",
                                       COLS[k], as.character(hdr[3, COLS[k]]), ITEMS[k]))
cat("\n")

src <- list(read_wave("Pre-Intervention", 1), read_wave("Post-Intervention", 2))

live <- irw::irw_fetch(TABLE)
live$key <- paste(live$id, live$wave, sep = "|")

# Build a lookup of live resp for (id, wave, item)
lookup <- function(id, wave, item) {
  i <- which(live$id == id & live$wave == wave & live$item == item)
  if (length(i) != 1) return(NA_real_)
  as.numeric(live$resp[i])
}

score_perm <- function(perm) {          # perm: which source column feeds logK
  ok <- 0; tot <- 0
  for (w in src) {
    for (k in seq_along(ITEMS)) {
      v <- w$m[, perm[k]]
      for (r in seq_along(w$id)) {
        lv <- lookup(w$id[r], w$wave, ITEMS[k])
        if (is.na(lv) && is.na(v[r])) next
        tot <- tot + 1
        if (!is.na(lv) && !is.na(v[r]) && lv == v[r]) ok <- ok + 1
      }
    }
  }
  c(ok = ok, tot = tot)
}

perms <- as.matrix(expand.grid(1:4, 1:4, 1:4, 1:4))
perms <- perms[apply(perms, 1, function(p) length(unique(p)) == 4), , drop = FALSE]

cat(sprintf("%-22s %8s %8s\n", "column->item mapping", "matched", "of"))
best <- NULL
for (i in seq_len(nrow(perms))) {
  p <- as.integer(perms[i, ])
  s <- score_perm(p)
  lab <- paste(COLS[p], collapse = ",")
  if (identical(p, 1:4) || s[["ok"]] == s[["tot"]])
    cat(sprintf("%-22s %8d %8d%s\n", lab, s[["ok"]], s[["tot"]],
                if (identical(p, 1:4)) "   <- claimed" else ""))
  if (s[["ok"]] == s[["tot"]]) best <- c(best, lab)
}

claimed <- score_perm(1:4)
cat("\nclaimed mapping reproduces", claimed[["ok"]], "of", claimed[["tot"]],
    "live responses\n")
cat("permutations of the 4 columns that reproduce the live data exactly:",
    paste(best, collapse = " / "), "\n")

pass <- claimed[["ok"]] == claimed[["tot"]] && length(best) == 1 &&
        identical(best, paste(COLS, collapse = ","))
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
