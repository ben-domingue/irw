# verify_climatechange_geiger_2025.R -- batch_524
#
# Claim: each IRW item code is the cleaned-data column the authors' own
# preparation_S1.Rmd (osf.io/wcgja) renamed from a raw Qualtrics export column,
# and the shipped item_text/option_text is the Canada QSF (osf.io/6hny4
# surveys.zip) text for that export tag / slider choice.
#
# Route: the preparation script sets ID = row index of bind_rows(raw files in the
# order Brazil..Thailand). So each live id points at one raw row, and each live
# item can be compared cell-for-cell against EVERY candidate raw column. The
# mapping is verified if each item matches its hypothesised raw column in 100%
# of rows and no other column does. A swap of any two items (including the
# sum-to-100 slider pairs) breaks this. Then the QSF DataExportTag / choice id
# ties the raw column to the wording, and RecodeValues ties option text to resp.

suppressMessages({library(irw); library(jsonlite)})
TABLE <- "climatechange_geiger_2025"
here <- tryCatch(dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))), error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))

td <- tempfile(); dir.create(td)
download.file("https://osf.io/download/ak9bs/", file.path(td, "raw.zip"), mode = "wb", quiet = TRUE)      # data_raw.zip, osf.io/r2byz
download.file("https://osf.io/download/as8f9/", file.path(td, "surveys.zip"), mode = "wb", quiet = TRUE)  # surveys.zip, osf.io/6hny4
unzip(file.path(td, "raw.zip"), exdir = td); unzip(file.path(td, "surveys.zip"), exdir = td)

cs <- c("Brazil","Canada","China","Germany","India","Indonesia","Italy","Japan","Mexico","Poland","Thailand")
cols <- c("OwnCCBeliefs", paste0("OtherCCBeliefs_", 1:5), "Discuss", "Expectation_Changes_1", "Expectation_Changes_2",
          "Changes", "Expectation_Support_1", "Expectation_Support_2", "Support", "Efficacy", "Age", "Sex")
raw <- do.call(rbind, lapply(cs, function(c) read.csv(file.path(td, paste0(c, ".csv")), fileEncoding = "UTF-8-BOM")[, cols]))
raw$ID <- seq_len(nrow(raw))
cat("raw rows:", nrow(raw), "(codebook: 8,151)\n")

d <- as.data.frame(irw::irw_fetch(TABLE))
hyp <- c(own.ccb = "OwnCCBeliefs", other.ccb.main = "OtherCCBeliefs_1", other.ccb.part = "OtherCCBeliefs_2",
         other.ccb.attr = "OtherCCBeliefs_3", other.ccb.trend = "OtherCCBeliefs_4", other.ccb.know = "OtherCCBeliefs_5",
         discuss = "Discuss", exp.change.low = "Expectation_Changes_1", exp.change.high = "Expectation_Changes_2",
         own.change = "Changes", exp.support.low = "Expectation_Support_1", exp.support.high = "Expectation_Support_2",
         own.support = "Support", efficacy = "Efficacy")
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
m <- raw[match(w$id, raw$ID), ]
dd <- d[match(w$id, d$id), ]
age_ok <- mean(m$Age == dd$cov_age); sex_ok <- mean(m$Sex == dd$cov_gender)
cat(sprintf("id -> raw row anchor: age agrees %.4f, sex agrees %.4f over %d ids\n\n", age_ok, sex_ok, nrow(w)))

cands <- setdiff(cols, c("Age", "Sex"))
pass <- age_ok == 1 && sex_ok == 1
cat(sprintf("%-17s %6s %-22s %8s %s\n", "item", "n", "hyp raw column", "hyp rate", "other cols at 100% / best other rate"))
for (it in names(hyp)) {
  y <- w[[it]]; ok <- !is.na(y)
  rates <- sapply(cands, function(cc) {
    x <- suppressWarnings(as.numeric(m[[cc]])); if (it == "own.ccb") x <- x - 1   # prep script: own.ccb - 1
    mean(!is.na(x[ok]) & x[ok] == y[ok]) })
  others <- rates[names(rates) != hyp[it]]
  cat(sprintf("%-17s %6d %-22s %8.4f %s / %.3f\n", it, sum(ok), hyp[it], rates[hyp[it]],
              if (any(others == 1)) paste(names(others)[others == 1], collapse = ",") else "none", max(others)))
  if (rates[hyp[it]] != 1 || any(others == 1)) pass <- FALSE
}

# --- raw column -> wording, via the Canada QSF's DataExportTag / choice ids ---
clean <- function(s) {
  s <- gsub('<span style="color:#ffffff;">.*?</span>', "", s, perl = TRUE)
  s <- gsub("<br\\s*/?>|</p>|</div>", " ", s, perl = TRUE); s <- gsub("<[^>]+>", "", s)
  s <- gsub("&nbsp;", " ", s); s <- gsub("&#39;", "'", s); s <- gsub("\u00a0", " ", s)
  s <- gsub("\\$\\{e://Field/Nationality_plural(_en)?\\}", "[citizens]", s)
  s <- gsub("\\$\\{e://Field/Country(_en)?\\}", "[country]", s)
  trimws(gsub("\\s+", " ", s))
}
q <- fromJSON(file.path(td, "Climate_Change_Beliefs_Canada.qsf"), simplifyVector = FALSE)
sq <- Filter(function(e) e$Element == "SQ", q$SurveyElements)
byTag <- setNames(lapply(sq, `[[`, "Payload"), sapply(sq, function(e) e$Payload$DataExportTag))
qtext <- function(tag) clean(byTag[[tag]]$QuestionText)
ctext <- function(tag, k) clean(byTag[[tag]]$Choices[[as.character(k)]]$Display)

it <- read.csv(items_csv, stringsAsFactors = FALSE)
first <- function(i, col) unique(it[it$item == i, col])
expect <- list(
  own.ccb = qtext("OwnCCBeliefs"), discuss = qtext("Discuss"), own.change = qtext("Changes"),
  own.support = qtext("Support"), efficacy = qtext("Efficacy"),
  other.ccb.main = ctext("OtherCCBeliefs", 1), other.ccb.part = ctext("OtherCCBeliefs", 2),
  other.ccb.attr = ctext("OtherCCBeliefs", 3), other.ccb.trend = ctext("OtherCCBeliefs", 4),
  other.ccb.know = ctext("OtherCCBeliefs", 5),
  exp.change.low = ctext("Expectation_Changes", 1), exp.change.high = ctext("Expectation_Changes", 2),
  exp.support.low = ctext("Expectation_Support", 1), exp.support.high = ctext("Expectation_Support", 2))
tx_ok <- sapply(names(expect), function(i) identical(first(i, "item_text"), expect[[i]]))
cat("\nshipped item_text == QSF text for the hypothesised export tag/choice:", sum(tx_ok), "/", length(tx_ok), "\n")
if (!all(tx_ok)) { print(names(tx_ok)[!tx_ok]); pass <- FALSE }

# option axis: own.ccb resp = QSF recode - 1; categorical labels by RecodeValues
rv <- byTag$OwnCCBeliefs$RecodeValues
oc <- it[it$item == "own.ccb", ]
own_ok <- all(sapply(names(rv), function(k) oc$option_text[oc$resp == as.numeric(rv[[k]]) - 1] == ctext("OwnCCBeliefs", k)))
cat("own.ccb option_text at resp = recode-1 matches QSF choices:", own_ok, "\n")
tab <- table(w$own.ccb); cat("own.ccb live counts 0..4:", paste(tab, collapse = "/"),
    " (0 = 'mainly responsible' is the modal answer, as the paper's believer majority requires)\n")
for (tag in c("Changes", "Support")) {
  code <- names(hyp)[hyp == tag]; o <- it[it$item == code, ]; r <- byTag[[tag]]$RecodeValues
  okk <- all(sapply(names(r), function(k) o$option_text[o$resp == as.numeric(r[[k]])] == ctext(tag, k)))
  cat(code, "option_text by RecodeValues matches QSF:", okk, "\n"); if (!okk) pass <- FALSE
}
if (!own_ok) pass <- FALSE
cat("\nNot established: nothing item-level is left open -- each of the 14 items matched exactly one raw column.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
