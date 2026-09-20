# verify_skalka2025_ai_literacy.R -- Step 5b, re-runnable mapping evidence.
#
# mapping_basis = paper_explicit. The claim under test is NOT "the table has 50
# items" (validate_items.R checked that). It is:
#
#   (a) every one of the 50 item codes in the live IRW table is printed, verbatim
#       and uniquely, next to its own wording in the deposit's own questionnaire
#       PDF (figshare 29488523 file 56024522, "AI_Literacy_survey.pdf"), so the
#       shipped item_text for code X is the line the source labels X; and
#   (b) resp ascends from disagreement to agreement, i.e. option_text
#       1 = "strongly disagree" / 5 = "strongly agree" is not reversed.
#
# (a) would break if item_text for any two items were swapped.
# (b) would break if the anchors were flipped.
#
# Run from itemtext/ (or anywhere; paths are resolved relative to this file).

suppressMessages(library(irw))

TABLE   <- "skalka2025_ai_literacy"
PDF_URL <- "https://ndownloader.figshare.com/files/56024522"
PDF_SHA <- "265f8c55417c495c119bbf30648cb2e12f5bc38ce5462042aa4e453066096edc"

args  <- commandArgs(trailingOnly = FALSE)
here  <- dirname(sub("^--file=", "", grep("^--file=", args, value = TRUE)[1]))
if (is.na(here) || !nzchar(here)) here <- "."
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))

ok <- TRUE

## ---- (a) code->text label match against the deposit's questionnaire PDF ----
pdf <- tempfile(fileext = ".pdf")
dl  <- tryCatch({ download.file(PDF_URL, pdf, quiet = TRUE); TRUE },
                error = function(e) FALSE)
if (!dl || !file.exists(pdf) || file.size(pdf) == 0) {
  cat("COULD NOT FETCH", PDF_URL, "-- mapping evidence did not reproduce.\n")
  ok <- FALSE
} else {
  sha <- tryCatch(
    as.character(tools::sha256sum(pdf)),
    error = function(e) {
      as.character(strsplit(system2("sha256sum", pdf, stdout = TRUE), " ")[[1]][1])
    })
  cat(sprintf("questionnaire PDF sha256: %s\n  expected:               %s  [%s]\n",
              sha, PDF_SHA, if (identical(sha, PDF_SHA)) "match" else "DIFFERS"))
  if (!identical(sha, PDF_SHA)) ok <- FALSE

  txt <- system2("pdftotext", c("-layout", pdf, "-"), stdout = TRUE)
  txt <- txt[seq_len(match(TRUE, grepl("Survey source", txt), nomatch = length(txt)) - 1)]
  ent <- character(0)
  for (ln in txt) {
    s <- trimws(gsub("\f", "", ln))
    if (!nzchar(s)) next
    if (grepl("^•", s)) ent <- c(ent, trimws(sub("^•", "", s)))
    else if (length(ent) && grepl("^[a-z(]", s)) ent[length(ent)] <- paste(ent[length(ent)], s)
  }
  m   <- regmatches(ent, regexec("^(?!Q[0-9])([A-Z]{1,2}[0-9])[ ]+(.*)$", ent, perl = TRUE))
  m   <- m[lengths(m) == 3]
  src <- setNames(vapply(m, `[`, "", 3), vapply(m, `[`, "", 2))
  cat(sprintf("item codes labelled in the PDF: %d (unique: %d)\n",
              length(src), length(unique(names(src)))))

  it  <- read.csv(items_csv, stringsAsFactors = FALSE, colClasses = "character")
  shp <- tapply(it$item_text, it$item, function(x) unique(x))
  live <- sort(unique(names(shp)))

  bad <- 0L
  for (code in live) {
    s <- if (code %in% names(src)) src[[code]] else NA_character_
    if (!identical(s, shp[[code]])) {
      bad <- bad + 1L
      cat(sprintf("  MISMATCH %-4s PDF: %s\n           %-4s CSV: %s\n",
                  code, s, "", shp[[code]]))
    }
  }
  cat(sprintf("label match: %d/%d shipped item_text strings are byte-identical to the line the PDF labels with that same code\n",
              length(live) - bad, length(live)))
  # a permutation check: is any wording reused across codes?
  cat(sprintf("distinct shipped item_text strings: %d (must equal %d for a permutation to be detectable)\n",
              length(unique(unlist(shp))), length(live)))
  if (bad > 0L) ok <- FALSE
  cat(sprintf("sample: A3 -> %s\n        L1 -> %s\n", shp[["A3"]], shp[["L1"]]))
}

## ---- (b) direction of the 1..5 anchors, from the live data ----
d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[d$resp > 0, ]                    # 0 is a no-answer code, not a scale point
A <- paste0("A", 1:5)                   # the AI-anxiety block: negatively valenced
w <- reshape(d[, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
oth <- setdiff(colnames(w), c("id", A))

anx  <- rowMeans(w[, A], na.rm = TRUE)
rest <- rowMeans(w[, oth], na.rm = TRUE)
cm   <- cor(w[, setdiff(colnames(w), "id")], use = "pairwise.complete.obs")
rAA  <- mean(cm[A, A][upper.tri(cm[A, A])])
rAO  <- mean(cm[A, oth])

cat(sprintf("\nanxiety-block mean %.3f vs all other items %.3f (diff %.3f)\n",
            mean(anx, na.rm = TRUE), mean(rest, na.rm = TRUE),
            mean(anx, na.rm = TRUE) - mean(rest, na.rm = TRUE)))
cat(sprintf("cor(anxiety mean, other mean) = %.3f\n", cor(anx, rest, use = "complete.obs")))
cat(sprintf("mean r within A block = %.3f ; mean r A vs other items = %.3f\n", rAA, rAO))
dir_ok <- mean(anx, na.rm = TRUE) < mean(rest, na.rm = TRUE) && rAA > rAO && rAO < 0
cat(sprintf("direction check: %s -- worry items sit BELOW the endorsement items, so 5 is the agree end\n",
            if (dir_ok) "consistent with 1=strongly disagree .. 5=strongly agree" else "INCONSISTENT"))
if (!dir_ok) ok <- FALSE

## ---- what this does NOT establish ----
cat("\nNot established by this script: the wording of resp 2, 3 and 4 (the deposit\n",
    "publishes only the two endpoints, so those option_text cells are blank), and the\n",
    "meaning of resp 0 (unlabelled in every source; it appears only in the 19 items of\n",
    "the IM/S/C/BI blocks and is concentrated in respondents reporting 0 hours of\n",
    "AI coursework, but no source states it).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
