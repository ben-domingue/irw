# verify_yandun2026_attention.R
#
# CLAIM UNDER TEST: data/yandun2026_cognitive.py assigns the item codes
# att1..att5 POSITIONALLY to columns 10..14 (1-based) of each sheet of
# DATA_MATRIX_TRANSLATED.xlsx, i.e. to the five "Memory" indicator headers on
# row 3 of that sheet, in order:
#     mem1 = "Remembers answers and numerical sequences"
#     mem2 = "Remembers tongue twisters/rhymes"
#     mem3 = "Retains patterns and sequences"
#     mem4 = "Remembers names and location of body parts"
#     mem5 = "Memorizes shapes and colors"
# A positional assignment leaves no trace of the source column in the code, so
# the mapping is checked by REPRODUCING the live responses from the source
# columns, and by showing that no OTHER assignment of the five columns to the
# five codes reproduces them. If item_text for mem2 and mem4 were swapped, the
# identity permutation would stop reproducing and a different one would.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "yandun2026_attention"
URL   <- "https://ndownloader.figshare.com/files/64067737"   # figshare 32114668 v1
COLS  <- 5:9            # 1-based source columns for the Attention block
ITEMS <- paste0("att", 1:5)

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, mode = "wb", quiet = TRUE)

hdr <- readxl::read_excel(tmp, sheet = "Pre-Intervention", col_names = FALSE,
                          n_max = 3, .name_repair = "minimal")
cat("Source header row 3 at columns", paste(COLS, collapse = ","), ":\n")
for (k in seq_along(COLS))
  cat(sprintf("  col %2d -> %-45s (claimed %s)\n",
              COLS[k], as.character(hdr[3, COLS[k]]), ITEMS[k]))
cat("\n")

read_wave <- function(sheet, wave) {
  raw <- readxl::read_excel(tmp, sheet = sheet, col_names = FALSE,
                            .name_repair = "minimal")
  dat  <- raw[4:nrow(raw), ]                      # rows 1-3 are title/headers
  ids  <- suppressWarnings(as.numeric(unlist(dat[[1]])))
  m    <- sapply(COLS, function(k) suppressWarnings(as.numeric(unlist(dat[[k]]))))
  keep <- !is.na(ids)
  list(id = ids[keep], wave = wave, m = m[keep, , drop = FALSE])
}
src <- list(read_wave("Pre-Intervention", 1), read_wave("Post-Intervention", 2))

live <- irw::irw_fetch(TABLE)
key  <- paste(live$id, live$wave, live$item, sep = "|")
lv   <- setNames(as.numeric(live$resp), key)
cat("live cells:", length(lv), "\n\n")

score_perm <- function(perm) {          # perm[k] = which of COLS feeds ITEMS[k]
  ok <- 0; tot <- 0
  for (w in src) {
    for (k in seq_along(ITEMS)) {
      v <- w$m[, perm[k]]
      kk <- paste(w$id, w$wave, ITEMS[k], sep = "|")
      have <- kk %in% names(lv)
      tot <- tot + sum(have)
      ok  <- ok + sum(!is.na(v[have]) & v[have] == lv[kk[have]])
    }
  }
  c(ok = ok, tot = tot)
}

perms <- as.matrix(expand.grid(rep(list(1:5), 5)))
perms <- perms[apply(perms, 1, function(p) length(unique(p)) == 5), , drop = FALSE]

cat(sprintf("%-24s %8s %8s\n", "column->item mapping", "matched", "of"))
best <- character(0)
for (i in seq_len(nrow(perms))) {
  p <- as.integer(perms[i, ])
  s <- score_perm(p)
  lab <- paste(COLS[p], collapse = ",")
  if (identical(p, 1:5) || s[["ok"]] == s[["tot"]])
    cat(sprintf("%-24s %8d %8d%s\n", lab, s[["ok"]], s[["tot"]],
                if (identical(p, 1:5)) "   <- claimed" else ""))
  if (s[["ok"]] == s[["tot"]]) best <- c(best, lab)
}

claimed <- score_perm(1:5)
cat("\nclaimed mapping reproduces", claimed[["ok"]], "of", claimed[["tot"]],
    "live responses\n")
cat("permutations of the 5 columns (of 120) that reproduce the live data exactly:",
    paste(best, collapse = " / "), "\n")
cat("Note: this pins item<->text for all 5 items. It does NOT verify the\n",
    "option_text<->resp mapping (1=Never .. 5=Always), which comes from the\n",
    "figshare description and is unlabelled at points 2-4.\n", sep = "")

pass <- claimed[["ok"]] == claimed[["tot"]] && length(best) == 1 &&
        identical(best, paste(COLS, collapse = ","))
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
