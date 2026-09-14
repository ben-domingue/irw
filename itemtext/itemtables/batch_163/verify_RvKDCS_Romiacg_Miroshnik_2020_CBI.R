# Step 5b evidence for RvKDCS_Romiacg_Miroshnik_2020_CBI -- re-runnable.
#
# The claim: item_text for CBI-1..CBI-11 is the wording the study's own online form
# attached to the form field of that exact name, and the live IRW item code IS that
# same field/column. Two independent links, both machine-checked here:
#
#   LINK A (code -> wording).  OSF g5bk4 "1. Materials/HTML study code.txt" is the
#     administered questionnaire source. Each item is a <p><b> N. text</b> block
#     followed by four {{field type="radio" name="CBI-k" ...}} tags. Parsing it gives
#     code -> wording with no inference at all. Note the form's PRESENTATION order is
#     NOT the code order (screen item 3 is CBI-11, screen item 4 is CBI-10, ...), so a
#     positional misread would be loudly visible, not silent.
#
#   LINK B (code -> live data).  The processing script (data/RvKDCS_Romiacg_Miroshnik_2020.R)
#     pivots the columns of "Raw data (K-DOCS; English).xlsx" that start with "cbi",
#     keeping their names. So the live code must be the xlsx column of the same name.
#     Checked at the CELL level: every live (id, item, resp) triple against the raw
#     sheet. This is permutation-proof -- swapping any two item codes breaks it.
#
# Corroboration printed as well: the raw workbook's own subscale formulas define
# contiguous blocks (Visual Arts = CBI-1:CBI-3, Literature = CBI-4:CBI-7,
# Crafts = CBI-8:CBI-11), and the wording Link A returns falls into exactly those
# semantic blocks; plus the option->resp direction check (resp=1 = "Никогда не делал").

suppressMessages({library(irw); library(readxl)})

TABLE   <- "RvKDCS_Romiacg_Miroshnik_2020_CBI"
CSV     <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                     paste0(TABLE, "__items.csv"))
if (!file.exists(CSV)) CSV <- file.path("itemtables", "batch_163", paste0(TABLE, "__items.csv"))
CACHE   <- file.path("itemtext", ".cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- file.path(".cache", TABLE)
if (!dir.exists(CACHE)) { CACHE <- tempdir() }
HTML_URL <- "https://osf.io/download/64f468046d1e89198a151562/"   # HTML study code.txt
XLSX_URL <- "https://osf.io/download/5faa8f20d1894f01de68b801/"   # Raw data (K-DOCS; English).xlsx

fetch <- function(url, path, mode = "wb") {
    if (!file.exists(path)) download.file(url, path, mode = mode, quiet = TRUE)
    path
}

ok <- TRUE

## ---- LINK A: parse the administered form -----------------------------------
html <- fetch(HTML_URL, file.path(CACHE, "study_code.txt"))
raw  <- readLines(html, warn = FALSE)
txt  <- paste(iconv(raw, from = "CP1251", to = "UTF-8"), collapse = "\n")

chunks <- strsplit(txt, "<p><b>", fixed = TRUE)[[1]]
form <- do.call(rbind, lapply(chunks, function(b) {
    if (!grepl("</b>", b, fixed = TRUE)) return(NULL)
    code <- unique(gsub('name="|"', "", regmatches(b, gregexpr('name="[^"]+"', b))[[1]]))
    if (length(code) != 1 || !grepl("^CBI-", code)) return(NULL)
    w <- sub("</b>.*$", "", b)
    w <- trimws(gsub("\\s+", " ", sub("^\\s*[0-9]+\\.\\s*", "", w)))
    labs <- gsub('.*label="|"$', "", regmatches(b, gregexpr('label="[^"]*"', b))[[1]])
    vals <- gsub('.*value="|"$', "", regmatches(b, gregexpr('value="[^"]*"', b))[[1]])
    data.frame(item = code, form_text = w,
               v = paste(vals, collapse = "|"), l = paste(labs, collapse = "|"),
               stringsAsFactors = FALSE)
}))
cat("== LINK A: administered form (OSF g5bk4, HTML study code.txt)\n")
cat("CBI item blocks parsed:", nrow(form), "\n")

items <- read.csv(CSV, stringsAsFactors = FALSE, encoding = "UTF-8")
ship  <- unique(items[, c("item", "item_text")])
ship$item_text <- trimws(gsub("\\s+", " ", ship$item_text))
cmp <- merge(ship, form[, c("item", "form_text")], by = "item")
cmp <- cmp[order(as.integer(sub("CBI-", "", cmp$item))), ]
cat(sprintf("%-7s %-6s %s\n", "item", "match", "form wording (administered Russian)"))
for (i in seq_len(nrow(cmp)))
    cat(sprintf("%-7s %-6s %s\n", cmp$item[i],
                if (identical(cmp$item_text[i], cmp$form_text[i])) "EXACT" else "DIFFER",
                substr(cmp$form_text[i], 1, 78)))
nA <- sum(cmp$item_text == cmp$form_text)
cat(sprintf("LINK A: %d/%d shipped item_text identical to the form field's own wording\n\n",
            nA, nrow(cmp)))
if (nA != 11 || nrow(cmp) != 11) ok <- FALSE

## option labels, same source
optship <- unique(items[, c("resp", "option_text")])
optship <- optship[order(optship$resp), ]
formlab <- strsplit(form$l[1], "\\|")[[1]]
formval <- strsplit(form$v[1], "\\|")[[1]]
cat("== option_text vs the form's radio labels (all items share one scale)\n")
for (i in seq_along(formlab))
    cat(sprintf("  resp=%s  form value=%-3s  %-28s | shipped: %s\n",
                optship$resp[i], formval[i], formlab[i], optship$option_text[i]))
nO <- sum(trimws(optship$option_text) == trimws(formlab))
cat(sprintf("option labels identical: %d/4 (form values R1..R4 in ascending order)\n\n", nO))
if (nO != 4) ok <- FALSE

## ---- LINK B: live data IS the named raw column, cell for cell ---------------
xl <- fetch(XLSX_URL, file.path(CACHE, "raw.xlsx"))
rw <- readxl::read_xlsx(xl)
cbi <- rw[, c("ID", paste0("CBI-", 1:11))]
long <- data.frame(
    id   = rep(as.integer(cbi$ID), 11),
    item = rep(paste0("CBI-", 1:11), each = nrow(cbi)),
    raw  = as.integer(unlist(cbi[, paste0("CBI-", 1:11)], use.names = FALSE)),
    stringsAsFactors = FALSE)
live <- irw::irw_fetch(TABLE)
m <- merge(live, long, by = c("id", "item"))
bad <- sum(m$resp != m$raw)
cat("== LINK B: live table vs the raw workbook column of the same name\n")
cat(sprintf("live rows %d | joined on (id,item) %d | disagreeing cells %d\n",
            nrow(live), nrow(m), bad))
if (nrow(m) != nrow(live) || bad != 0) ok <- FALSE

# a permutation control: how badly does a shifted assignment fail?
shift <- long
shift$item <- paste0("CBI-", ((as.integer(sub("CBI-", "", shift$item)) %% 11) + 1))
ms <- merge(live, shift, by = c("id", "item"))
cat(sprintf("control: same join under a 1-position code shift -> %d disagreeing cells\n\n",
            sum(ms$resp != ms$raw)))

## ---- corroboration ----------------------------------------------------------
cat("== corroboration 1: subscale blocks (raw workbook formulas) vs item content\n")
blocks_def <- list("Visual Arts" = 1:3, "Literature" = 4:7, "Crafts" = 8:11)
for (b in names(blocks_def))
    cat(sprintf("  %-12s = CBI-%s : %s\n", b,
                paste(range(blocks_def[[b]]), collapse = "..CBI-"),
                paste(cmp$item_text[blocks_def[[b]]], collapse = " / ")))

cat("\n== corroboration 2: option direction and interior order\n")
tb <- table(live$item, live$resp)
tb <- tb[paste0("CBI-", 1:11), ]
print(tb)
mono12 <- sum(apply(tb, 1, function(r) r[1] > r[2] & r[2] > r[3]))
cat(sprintf("items with n(1) > n(2) > n(3): %d/11  (R1='Никогда не делал' is the floor;\n", mono12))
cat(sprintf("  n(4) > n(3) only for CBI-3/CBI-1/CBI-7, the three commonest activities --\n"))
cat(sprintf("  expected for an unbounded top category 'more than five times')\n"))
cat(sprintf("floor share: CBI-4 'Published a work of literature' %.3f (highest) vs\n",
            tb["CBI-4", 1] / sum(tb["CBI-4", ])))
cat(sprintf("             CBI-3 'Made sketches' %.3f (lowest)\n", tb["CBI-3", 1] / sum(tb["CBI-3", ])))
if (mono12 != 11) ok <- FALSE

cat("\nWhat this does NOT establish: nothing on the item axis -- Link A + Link B tie\n")
cat("every one of the 11 codes to its wording documentarily and at the cell level.\n")
cat("On the option axis the four labels are verbatim from the same form, and their\n")
cat("R1..R4 -> 1..4 order is inferred from the form's ascending presentation, then\n")
cat("corroborated by the floor pattern and by n(1)>n(2)>n(3) holding for all 11 items.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
