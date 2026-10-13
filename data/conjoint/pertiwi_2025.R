##Children's educational fashion cards rated by millennial parents: fixed rated stimulus cards, Indonesia
##Pertiwi, P. A. M., & Murniati, M. (2025). Industrial Engineering Approach to Analyzing Millennials' Purchase Preferences for
##Sustainable Educational Fashion in Business Using Conjoint Analysis Data [Data set]. Mendeley Data, v1. No paper DOI listed.
##Deposit: doi:10.17632/8bj7b68ddm, CC BY 4.0 (Mendeley data_licence field). File read: the .xlsx, sheet "Form Responses 1"
##(saved as fash.xlsx). Usage: Rscript pertiwi_2025.R <dir holding fash.xlsx> <output dir>
##
##103 respondents (Indonesian-language Google Form; the form concerns the children's clothing brand "LUCU Kids") each rated
##16 stimulus cards, "Kombinasi Level Atribut 1-16", whose text is the column header, e.g. "1. Tema : Planet Explores /
##2. Ukuran : XL / 3. Warna : Pastel / 4. Pembelian : Offline". Attributes: theme (Planet Explores, Penguin Facts, Counting
##Pigs, Humans Organs), size (M, L, XL), colour (Pastel, Neon), purchase channel (Online, Offline). The 16 cards are a fixed
##orthogonal subset of the 48 combinations; all respondents rated the same 16 cards. Levels are stored as in the headers.
##Outcome: rating = the 1-5 score for each card (observed 1-5). The deposit has no question wording or scale labels: direction
##unknown (presumably 5 = most preferred); stored raw. task = card number in column order (display order not documented),
##profile = 1.
##Covariates (Indonesian answer text as recorded): cov_purchase_frequency ("Jarang (1x/bulan)", "Sering (> 1x/bulan)": how often the
##respondent buys children's clothing), cov_purchase_place (usual place of purchase: online marketplace / offline store).
##Dropped: timestamp and the free-text comment/suggestion column. ids are the sheet row order. No PII in this file. No article is
##listed, so N could not be compared (103 respondents; the triage estimate was 103).
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressWarnings(suppressMessages(read_excel(file.path(raw, "fash.xlsx"), sheet = "Form Responses 1", col_names = FALSE, .name_repair = "minimal"))))
h <- as.character(unlist(x[1])); x <- x[-1]
sc <- 4:19
stopifnot(all(grepl("^Kombinasi Level Atribut [0-9]+", h[sc])), nrow(x) == 103)
r <- suppressWarnings(as.matrix(sapply(x[, sc, with = FALSE], as.numeric)))
stopifnot(!anyNA(r), all(r %in% 1:5))
get <- function(hh, key) { l <- strsplit(hh, "\n")[[1]]; trimws(sub("^[0-9]\\. [^:]+: *", "", l[grepl(paste0("^[0-9]\\. ", key, " *:"), l)])) }
cards <- rbindlist(lapply(seq_along(sc), function(k) data.table(task = k,
  attr_theme = get(h[sc[k]], "Tema"), attr_size = get(h[sc[k]], "Ukuran"),
  attr_colour = get(h[sc[k]], "Warna"), attr_purchase_channel = get(h[sc[k]], "Pembelian"))))
stopifnot(!anyNA(cards), nrow(unique(cards[, -1])) == 16)
n <- nrow(x)
cv <- data.table(id = seq_len(n), cov_purchase_frequency = x[[2]], cov_purchase_place = x[[3]])
d <- merge(merge(data.table(id = rep(seq_len(n), each = 16), task = rep(1:16, times = n), profile = 1L, rating = as.integer(t(r))), cards, by = "task"), cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pertiwi_2025_educational_fashion.csv"))
