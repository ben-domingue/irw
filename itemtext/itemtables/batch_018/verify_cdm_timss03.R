# verify_cdm_timss03.R -- mapping verification for cdm_timss03.
#
# WHAT THE MAPPING IS
# data/cdm.R does `index <- grep("^M", names(x)); x <- x[,index]` over
# CDM::data.timss03.G8.su$data and emits `item = names(x)[i]`. The IRW code IS
# the source column name -- no rename, no positional assignment. Those column
# names are the IEA's own TIMSS unique item IDs. The shipped item_text was
# transcribed from the page images of the IEA released item sets, and EVERY
# RELEASED PAGE PRINTS THAT UNIQUE ID in its header ("UniqueID M012001" /
# "Item ID M022043"). So each item's wording was read off a page carrying that
# item's own code: an explicit code-label tie, not an order inference.
#
# WHAT THIS SCRIPT RE-CHECKS
# That tie, against two sources neither of which was used to write the CSV:
#   1. the CDM package's own `iteminfo` table (23x9, ships with the data)
#   2. the released PDFs' index tables, re-parsed at run time
# Per item it compares two independent signatures -- the number of response
# options and the printed answer Key -- plus asserts every code is present in a
# released set. A permutation of item_text across items would move option
# counts and keys off their codes and break checks 2 and 3.
#
# No irw_fetch() and no irw:: call: the codes come from the CDM package, which
# is what data/cdm.R itself reads.

suppressMessages(library(CDM))
data(data.timss03.G8.su, package = "CDM")
d  <- data.timss03.G8.su
ii <- as.data.frame(d$iteminfo, stringsAsFactors = FALSE)

here <- dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1]))
csv  <- read.csv(file.path(here, "cdm_timss03__items.csv"), stringsAsFactors = FALSE)

CACHE <- "/home/ben/irw-queue/itemtext/.cache/cdm_timss03"
SRC <- list(
  y03 = list(pdf = file.path(CACHE, "fresh_M8.pdf"),
             url = "https://timssandpirls.bc.edu/PDF/T03_RELEASED_M8.pdf"),
  y07 = list(pdf = file.path(CACHE, "T07_G8_Released_Items_MAT.pdf"),
             url = "https://timssandpirls.bc.edu/timss2007/PDF/T07_G8_Released_Items_MAT.zip"))

ok <- TRUE

## -- 1. item set == the ^M columns of the CDM source data --------------------
src <- grep("^M", names(d$data), value = TRUE)
cat("1. item set vs CDM source columns (the codes data/cdm.R emits verbatim)\n")
same <- setequal(src, unique(csv$item))
cat("   source columns:", length(src), "| shipped items:", length(unique(csv$item)),
    "| identical sets:", same, "\n\n")
ok <- ok && same

## -- 2. option counts vs CDM iteminfo$response_options -----------------------
cat("2. shipped option rows per item vs CDM iteminfo$response_options\n")
FIGURAL <- "M022043"   # five options are pictures of shaded circles; not transcribed
cmp <- data.frame(item = src,
                  shipped  = sapply(src, function(k) sum(csv$item == k & !is.na(csv$option_text))),
                  iteminfo = as.integer(ii$response_options[match(src, ii$item)]),
                  row.names = NULL)
cmp$agree <- cmp$shipped == cmp$iteminfo
cmp$agree[cmp$item %in% FIGURAL] <- NA
print(cmp)
n_ok <- sum(cmp$agree, na.rm = TRUE); n_test <- sum(!is.na(cmp$agree))
cat("   agree:", n_ok, "/", n_test, "  (", FIGURAL, "excluded: figural options)\n\n")
ok <- ok && (n_ok == n_test)

## -- 3. correct_response vs the Key printed in the released PDF index --------
cat("3. shipped correct_response vs the Key printed in the released item sets\n")
have <- all(file.exists(SRC$y03$pdf, SRC$y07$pdf))
if (!have) {
  cat("   PDFs not cached. Fetch them (public, no login):\n")
  cat("     curl -L", SRC$y03$url, "-o", SRC$y03$pdf, "\n")
  cat("     curl -L", SRC$y07$url, "-o /tmp/t07.zip && unzip -o /tmp/t07.zip -d", CACHE, "\n")
  ok <- FALSE
} else {
  t03 <- system2("pdftotext", c("-layout", shQuote(SRC$y03$pdf), "-"), stdout = TRUE)
  t07 <- system2("pdftotext", c("-layout", shQuote(SRC$y07$pdf), "-"), stdout = TRUE)
  # 2003 index row:  M012001  M01  01  MC  A  Yes  Number ...      -> key = field 5
  k03 <- regmatches(t03, regexec("^\\s*(M\\d{6}[A-Z]?)\\s+M\\d{2}\\s+\\d{2}\\s+(MC|CR)\\s+(\\S+)\\s+(Yes|No)\\b", t03))
  k03 <- do.call(rbind, lapply(Filter(length, k03), function(x) data.frame(item=x[2], type=x[3], key=x[4])))
  # 2007 index row:  M022043  M  8  M01  01  Number  Knowing  1  D -> key = last field
  k07 <- regmatches(t07, regexec("^\\s*(M\\d{6}[A-Z]?)\\s+M\\s+8\\s+M\\d{2}\\s+\\d{2}\\s+\\S+.*?\\s(\\S|See scoring guide)\\s*$", t07))
  k07 <- do.call(rbind, lapply(Filter(length, k07), function(x) data.frame(item=x[2], type=NA, key=x[3])))
  idx <- rbind(k03, k07); idx <- idx[!duplicated(idx$item), ]
  res <- data.frame(item = src,
                    shipped_key = sapply(src, function(k) { v <- csv$correct_response[csv$item == k][1]; if (is.na(v)) "" else v }),
                    pdf_key     = idx$key[match(src, idx$item)],
                    in_released = src %in% idx$item, row.names = NULL)
  res$agree <- ifelse(res$shipped_key == "", is.na(res$pdf_key) | !res$pdf_key %in% LETTERS,
                      res$shipped_key == res$pdf_key)
  print(res)
  cat("   all 23 codes found in a released set:", all(res$in_released), "\n")
  cat("   key agreement:", sum(res$agree, na.rm = TRUE), "/", nrow(res), "\n\n")
  ok <- ok && all(res$in_released) && all(res$agree, na.rm = TRUE) && !any(is.na(res$agree))
}

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
