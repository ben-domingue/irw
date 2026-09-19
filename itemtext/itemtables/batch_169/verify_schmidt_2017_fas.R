# verify_schmidt_2017_fas.R -- mapping check for schmidt_2017_fas (batch_169).
#
# mapping_basis = data_labels: the IRW item codes ses_1_1..ses_4_1 ARE the
# column names of the PLOS S1 Dataset (.s001, SPSS), and item_text/option_text
# are that file's own German variable/value labels. This script checks that the
# live IRW columns really are those label-bearing .sav columns, by matching
# per-item x per-level response counts between the .sav and the live table
# (route 9). A permutation of any two items would break it: the four items
# have different level sets (0-1, 0-2, 0-3, 0-3) and the two 0-3 items have
# different count profiles (17/52/63/95 vs 1/39/80/113).
# It does NOT check the German-to-English translations (machine translation).
suppressMessages({library(irw); library(haven)})
TABLE <- "schmidt_2017_fas"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0182845.s001"
tmp <- tempfile(fileext = ".sav")
download.file(URL, tmp, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "IRW-Finder/1.0"))
sav <- read_sav(tmp)
items <- c("ses_1_1","ses_2_1","ses_3_1","ses_4_1")
d <- irw::irw_fetch(TABLE)
fa <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
here <- if (length(fa)) dirname(fa[1]) else "."
it <- read.csv(file.path(here, "schmidt_2017_fas__items.csv"), stringsAsFactors = FALSE)
ok <- TRUE
for (i in items) {
  x <- as.numeric(sav[[i]]); x <- x[!is.na(x) & x == round(x)]   # script drops the one 1.5
  lab <- attr(sav[[i]], "label")
  src <- table(factor(x, levels = 0:3)); live <- table(factor(d$resp[d$item == i], levels = 0:3))
  shipped <- unique(it$item_text[it$item == i])
  cat(sprintf("%s  sav label: %s\n         shipped: %s\n", i, lab, shipped))
  cat(sprintf("         counts 0..3  sav: %s   live: %s\n",
              paste(src, collapse = "/"), paste(live, collapse = "/")))
  vl <- attr(sav[[i]], "labels")
  lv <- sort(unique(d$resp[d$item == i]))
  opt <- it$option_text[it$item == i][match(lv, it$resp[it$item == i])]
  cat(sprintf("         value labels sav: %s   shipped: %s\n",
              paste(paste0(vl, "=", names(vl)), collapse = "; "),
              paste(paste0(lv, "=", opt), collapse = "; ")))
  if (!identical(as.integer(src), as.integer(live))) ok <- FALSE
  if (!identical(lab, shipped)) ok <- FALSE
  if (!identical(unname(names(vl))[match(lv, vl)], opt)) ok <- FALSE
}
cat("Not established: the English in *_translated (IRW machine translation).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
