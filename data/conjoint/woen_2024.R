##Tofu snack product cards rated by consumers: 2^4 full factorial of rated stimulus cards, Indonesia
##Woen, K., & Murniati, M. (2024). Optimizing Product Offerings: A Conjoint Analysis of Tofu Attributes and Consumer
##Preferences for Market Success Data [Data set]. Mendeley Data, v1. No paper DOI listed.
##Deposit: doi:10.17632/c9rv63v8w3, CC BY 4.0 (Mendeley data_licence field). File read: the .xls, sheet "Form Responses 1"
##(saved as tofu.xls). The second sheet "NEW" was NOT read (it holds respondents' names, e-mail addresses and other personal
##data: PII FOUND). Usage: Rscript woen_2024.R <dir holding tofu.xls> <output dir>
##
##105 respondents (Indonesian-language Google Form) each rated 16 stimulus cards (a fixed full factorial of 4 binary attributes,
##all respondents rated all 16 cards). The text of each card is the column header, e.g. "Stimulus 1 / 1. Varian: Lumpia Kulit Tahu /
##2. Rasa: Pedas / 3. Kategori: Ready-to-Eat / 4. Porsi: Kecil (5 pcs)", split into: variant (Lumpia Kulit Tahu, Tahu Bakso),
##flavour (Pedas, Original), category (Ready-to-Eat, Frozen Food), portion (Kecil (5 pcs), Besar (10 pcs)). Levels are stored
##in Indonesian as displayed in the header. Fixed design, all respondents rated the same 16 cards.
##Outcome: rating = the 1-5 score of each card (observed 1-5; 666 fives). The deposit has no question wording or scale labels:
##direction unknown (presumably 5 = most preferred); stored raw. task = stimulus number 1-16 in column order (the order in which
##cards were displayed is not documented), profile = 1.
##Dropped: timestamp, the constant "Name" column (value "Respondent"), TOTAL (sum of the 16 ratings; checked equal), the
##free-text feedback column, and the empty education column. No covariates are kept (the demographics sit in sheet NEW, not used).
##ids are the sheet row order. No article is listed, so N could not be compared.
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressWarnings(suppressMessages(read_excel(file.path(raw, "tofu.xls"), sheet = "Form Responses 1", col_names = FALSE, .name_repair = "minimal"))))
h <- as.character(unlist(x[1])); x <- x[-1]
sc <- 3:18
stopifnot(length(h) >= 19, all(grepl("^Stimulus [0-9]+\n", h[sc])), nrow(x) == 105)
r <- suppressWarnings(as.matrix(sapply(x[, sc, with = FALSE], as.numeric)))
stopifnot(!anyNA(r), all(r %in% 1:5), all(rowSums(r) == as.numeric(x[[19]])))
get <- function(hh, key) { l <- strsplit(hh, "\n")[[1]]; trimws(sub("^[0-9]\\. [^:]+: *", "", l[grepl(paste0("^[0-9]\\. ", key, ":"), l)])) }
cards <- rbindlist(lapply(seq_along(sc), function(k) data.table(task = k,
  attr_variant = get(h[sc[k]], "Varian"), attr_flavour = get(h[sc[k]], "Rasa"),
  attr_category = get(h[sc[k]], "Kategori"), attr_portion = get(h[sc[k]], "Porsi"))))
stopifnot(!anyNA(cards), nrow(unique(cards[, -1])) == 16)
n <- nrow(x)
d <- merge(data.table(id = rep(seq_len(n), each = 16), task = rep(1:16, times = n), profile = 1L, rating = as.integer(t(r))), cards, by = "task")
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "woen_2024_tofu_preferences.csv"))
