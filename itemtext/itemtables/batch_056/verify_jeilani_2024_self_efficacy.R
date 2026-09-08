# verify_jeilani_2024_self_efficacy.R -- Step 5b, re-runnable mapping evidence.
#
# CLAIM UNDER TEST: each live item code SEF1/SEF6/SEF8/SEF9 carries the item text
# that the study's own SPSS file attaches to the column of that same name, and
# SEF4 -- which has NO label anywhere in the deposit -- carries General
# Self-Efficacy Scale item 4.
#
# The chain that is testable, and what each link rules out:
#   (a) the shipped item_text for SEF1/6/8/9 is byte-identical to the .sav's
#       variable label for that column  -> a swap of any two of those four texts
#       breaks this immediately;
#   (b) the .sav column and the .xlsx column of the same name are element-wise
#       identical over all 663 respondents -> rules out the failure mode this
#       deposit actually exhibits elsewhere (in the same .sav, PWB1 is NOT the
#       .xlsx's PWB1, it is SSF1), i.e. that a .sav label describes a different
#       question than the equally-named spreadsheet column the IRW script read;
#   (c) the live table's per-item x per-level counts equal the .xlsx column's
#       value counts, cell for cell, and the five items' count vectors are all
#       distinct -> ties each live code to exactly one spreadsheet column.
#
# NOT established: SEF4's wording. Nothing in the deposit labels it. It is
# assigned canonical GSE item 4 because links (a)-(c) show SEF1/6/8/9 to be GSE
# items 1/6/8/9 verbatim at their canonical numbers, so the numeric suffix is the
# GSE item number -- an inference about the study's numbering, not a measurement.
# The verdict below does not depend on it.

suppressMessages({library(irw); library(haven); library(readxl)})

TABLE <- "jeilani_2024_self_efficacy"
ITEMS <- c("SEF1", "SEF4", "SEF6", "SEF8", "SEF9")
LABELLED <- c("SEF1", "SEF6", "SEF8", "SEF9")

# Shipped text (this batch's __items.csv), hard-coded so the script is standalone.
SHIPPED <- c(
  SEF1 = "I can always manage to solve difficult problems if I try hard  enough.",
  SEF6 = "I can solve most problems if I invest the necessary effort.",
  SEF8 = "When I am confronted with a problem, I can usually find several solutions.",
  SEF9 = "If I am in trouble, I can usually think of a solution")

# --- fetch the deposit (figshare 10.6084/m9.figshare.26820745, CC0) -----------
dir.create("/tmp/jeilani_verify", showWarnings = FALSE)
fl <- jsonlite::fromJSON("https://api.figshare.com/v2/articles/26820745/files")
get <- function(ext) {
  u <- fl$download_url[grepl(ext, fl$name, fixed = TRUE)][1]
  p <- file.path("/tmp/jeilani_verify", basename(sub("\\?.*$", "", u)))
  p <- paste0(p, ext)
  if (!file.exists(p)) download.file(u, p, quiet = TRUE, mode = "wb")
  p
}
sav <- haven::read_sav(get(".sav"))
xls <- readxl::read_excel(get(".xlsx"))

ok <- TRUE

# --- (a) shipped text vs .sav variable labels --------------------------------
cat("(a) shipped item_text vs the .sav's own variable label\n")
for (it in LABELLED) {
  lb <- attr(sav[[it]], "label")
  same <- identical(lb, unname(SHIPPED[it]))
  ok <- ok && same
  cat(sprintf("  %-5s %s\n       label:   %s\n       shipped: %s\n",
              it, if (same) "IDENTICAL" else "DIFFERS", lb, SHIPPED[it]))
}

# --- (b) .sav column == .xlsx column, element-wise ----------------------------
cat("\n(b) .sav column vs .xlsx column of the same name, over all respondents\n")
for (it in LABELLED) {
  a <- as.numeric(sav[[it]]); b <- as.numeric(xls[[it]])
  eq <- sum((a == b) | (is.na(a) & is.na(b)))
  ok <- ok && (eq == length(a)) && (length(a) == nrow(xls))
  cat(sprintf("  %-5s %d / %d rows equal\n", it, eq, length(a)))
}

# --- (c) live per-item x per-level counts vs the .xlsx ------------------------
cat("\n(c) live per-item x resp-level counts vs the .xlsx column value counts\n")
tb  <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source("core"))
liv <- irw:::.irw_query_tibble(sprintf(
  "SELECT CAST(item AS STRING) AS item, CAST(resp AS INT64) AS resp, COUNT(*) AS n
     FROM `%s` GROUP BY 1,2", tb$qualified_reference))
cat(sprintf("  %-5s %-27s %-27s %s\n", "item", "live 1..5", "xlsx 1..5", "match"))
vecs <- list()
for (it in ITEMS) {
  lv <- sapply(1:5, function(k) { v <- liv$n[liv$item == it & liv$resp == k]
                                  if (length(v)) as.integer(v) else 0L })
  xv <- sapply(1:5, function(k) sum(as.numeric(xls[[it]]) == k, na.rm = TRUE))
  vecs[[it]] <- lv
  m <- identical(as.integer(lv), as.integer(xv)); ok <- ok && m
  cat(sprintf("  %-5s %-27s %-27s %s\n", it,
              paste(lv, collapse = "/"), paste(xv, collapse = "/"),
              if (m) "yes" else "NO"))
}
dup <- anyDuplicated(sapply(vecs, paste, collapse = "/"))
cat(sprintf("  distinct count vectors across the 5 items: %s\n",
            if (dup == 0) "yes (each code ties to one column)" else "NO -- ambiguous"))
ok <- ok && dup == 0

cat("\nNot established by any of the above: the wording of SEF4, which the deposit\n",
    "never labels; it is canonical GSE item 4 by numbering inference. Status PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
