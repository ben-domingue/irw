# verify_dalichaouche_2026_covid_attitudes.R -- Step 5b, re-runnable.
#
# Claim: live items A1..A5 are the xlsx score columns of the same name, each score
# column is coded from the French response-label column immediately to its left
# (whose header is that question's de-spaced French stem), and every non-blank
# option_text row shipped for (item, resp) is the label the source respondents at
# that score actually chose. A swap of any two items' text breaks check 2, because
# each item's shipped option labels match exactly one label column.
# Also prints the A1 crosstab that justifies leaving A1 resp 0/1 option_text blank.

suppressMessages({library(irw); library(readxl)})
TABLE <- "dalichaouche_2026_covid_attitudes"
here <- tryCatch(dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))),
                 error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
ok <- TRUE

xl <- tempfile(fileext = ".xlsx")
download.file("https://ndownloader.figshare.com/files/63116881", xl, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "Mozilla/5.0 (IRW-research)"))
src <- as.data.frame(read_excel(xl))
live <- irw::irw_fetch(TABLE)
it <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
A <- paste0("A", 1:5)
labcol <- setNames(names(src)[match(A, names(src)) - 1], A)

# 1. live per-item x level counts vs the source score columns
cat("== 1. live vs source score-column counts (resp 0/1/2) ==\n")
for (a in A) {
  lv <- table(factor(live$resp[live$item == a], 0:2)); sv <- table(factor(src[[a]], 0:2))
  cat(sprintf("%s live %s | source %s\n", a, paste(lv, collapse = "/"), paste(sv, collapse = "/")))
  if (!all(lv == sv)) ok <- FALSE
}

# 2. item <-> text: which source label column carries each item's shipped option labels
cat("\n== 2. shipped option labels vs each source label column (share of shipped labels found) ==\n")
cat(sprintf("%-4s %s\n", "item", paste(sprintf("%8s", paste0("L(", A, ")")), collapse = "")))
for (a in A) {
  shipped <- unique(na.omit(it$option_text[it$item == a]))
  # the one deliberate edit: A2's trailing " t" artifact stripped
  share <- sapply(A, function(b) {
    lv <- sub(" t$", "", unique(na.omit(src[[labcol[b]]])))
    mean(shipped %in% lv) * (length(setdiff(lv, shipped)) == 0 || a == "A1")
  })
  cat(sprintf("%-4s %s\n", a, paste(sprintf("%8.2f", share), collapse = "")))
  if (share[a] != 1 || sum(share == 1) != 1) { ok <- FALSE; cat("   -> not uniquely matched\n") }
}
cat("(A1 ships one label of three, so its row tests containment only; the other four must match their own column's full label set and no other.)\n")

# 3. option <-> resp: for each non-blank shipped option, agreement among labelled source rows at that score
cat("\n== 3. option_text vs resp: share of labelled source respondents at that score who chose the shipped label ==\n")
for (i in which(!is.na(it$option_text))) {
  a <- it$item[i]; r <- it$resp[i]
  lab <- sub(" t$", "", src[[labcol[a]]][src[[a]] == r])
  n_na <- sum(is.na(lab)); lab <- lab[!is.na(lab)]
  sh <- mean(lab == it$option_text[i])
  cat(sprintf("%s resp=%d  %3d/%3d = %.3f  (+%d unlabelled rows scored %d)  '%s'\n",
              a, r, sum(lab == it$option_text[i]), length(lab), sh, n_na, r, it$option_text[i]))
  if (sh < 0.9) ok <- FALSE
}

# 4. A1: why resp 0/1 are blank
cat("\n== 4. A1 source label x score (why A1 resp 0 and 1 ship no option_text) ==\n")
print(table(label = addNA(src[[labcol["A1"]]]), A1 = src$A1))
cat("Questionnaire key: Negative(panic)=0, Neutral(not worried)=1, Positive(rational)=2.\n")
cat("Does NOT establish: the correct A1 coding for 0/1 -- the data contradict the key, so those rows stay blank.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
