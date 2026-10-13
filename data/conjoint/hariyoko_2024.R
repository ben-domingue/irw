##Tea drink product cards rated by consumers: 3x2x2 full factorial of rated stimulus cards, Indonesia ("We Need Tea")
##Hariyoko, C., & Murniati, M. (2024). Strategic Implications of Consumer Preferences on Product Development: A Conjoint
##Analysis of the We Need Tea Market in Indonesia Data [Data set]. Mendeley Data, v1. No paper DOI listed.
##Deposit: doi:10.17632/t3b628s7w4, CC BY 4.0 (Mendeley data_licence field). File read: the .xlsx, sheet "Form Responses 1"
##(saved as tea.xlsx). Usage: Rscript hariyoko_2024.R <dir holding tea.xlsx> <output dir>
##
##100 respondents (Google Form, questions partly in English, cards in Indonesian) each rated 12 stimulus cards, "Kombinasi level
##atribut 1-12", whose text is the column header, e.g. "1. Rasa: Peach of Eternity / 2. Intensitas Rasa: Ringan / 3. Varian
##Kemasan: Tea Bags". Attributes: flavour (Peach of Eternity, Tropical Summer, Memory of Paris), flavour intensity (Ringan =
##light, Kuat = strong), pack (Tea Bags, Loose Leaf). The 12 cards are the complete 3x2x2 factorial; all respondents rated all
##12. Levels stored as in the headers (trailing spaces trimmed).
##Outcome: rating = the 1-5 score for each card (observed 1-5). The deposit has no question wording or scale labels:
##direction unknown (presumably 5 = most preferred); stored raw. task = card number in column order (display order not
##documented), profile = 1.
##Covariate: cov_purchase_frequency = answer to "How often do you buy tea drinks? (Ready-to-drink tea, cafes/restaurants, etc.)"
##("Jarang (< 15x/bulan)" = rarely, "Sering (> 15x/bulan)" = often), as recorded.
##Dropped: timestamp, the constant "Name" column (value "Respondent"), two free-text columns (preferences, comments).
##ids are the sheet row order. No PII. No article listed, so N could not be compared (100 respondents = exactly the 100-respondent minimum).
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressWarnings(suppressMessages(read_excel(file.path(raw, "tea.xlsx"), sheet = "Form Responses 1", col_names = FALSE, .name_repair = "minimal"))))
h <- as.character(unlist(x[1])); x <- x[-1]
sc <- 4:15
stopifnot(all(grepl("^Kombinasi level atribut [0-9]+", h[sc])), nrow(x) == 100)
r <- suppressWarnings(as.matrix(sapply(x[, sc, with = FALSE], as.numeric)))
stopifnot(!anyNA(r), all(r %in% 1:5))
get <- function(hh, key) { l <- strsplit(hh, "\n")[[1]]; trimws(sub("^[0-9]\\. [^:]+: *", "", l[grepl(paste0("^[0-9]\\. ", key, " *:"), l)])) }
cards <- rbindlist(lapply(seq_along(sc), function(k) data.table(task = k,
  attr_flavour = get(h[sc[k]], "Rasa"), attr_flavour_intensity = get(h[sc[k]], "Intensitas Rasa"),
  attr_pack = get(h[sc[k]], "Varian Kemasan"))))
stopifnot(!anyNA(cards), nrow(unique(cards[, -1])) == 12, nrow(cards) == 12)
n <- nrow(x)
cv <- data.table(id = seq_len(n), cov_purchase_frequency = x[[3]])
d <- merge(merge(data.table(id = rep(seq_len(n), each = 12), task = rep(1:12, times = n), profile = 1L, rating = as.integer(t(r))), cards, by = "task"), cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hariyoko_2024_tea_preferences.csv"))
