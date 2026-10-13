##Massage parlor service preference: rated stimulus cards, Indonesia
##Prasetyo, Y. T., Cahigas, M. M. L., Tan, A. P., Kurniawan, L. E., Prawiro, S. N., Nadlifatin, R.,
##Gumasing, M. J. J., & Ayuwati, I. D. (2024). The Indonesian consumer perspective on the massage industry:
##A conjoint analysis approach. PLOS ONE, 19(8), e0308098. https://doi.org/10.1371/journal.pone.0308098
##Raw data: figshare doi:10.6084/m9.figshare.25491376, CC BY 4.0. File read: "Massage Parlor Preference
##(Responses).xlsx", sheet "Form Responses 1" (saved as m.xlsx). Usage: Rscript prasetyo_2024.R <dir holding m.xlsx> <output dir>
##
##212 Indonesian adults with massage experience (convenience sample, Google Forms, Sept-Nov 2022; the paper's
##N = 212 valid respondents), each scoring 27 fixed stimulus cards (a fixed orthogonal plan, all respondents
##saw the same 27 cards) that describe a massage parlor service by 6 attributes: therapist gender, price per
##session, duration, room type, massage type, Google review rating. The card text is the column header, e.g.
##"1. Terapis Wanita, Harga berkisar 200-250k, Durasi 60 menit, Couple Room, Reflexology (Pijat Kering), Google Review
##kurang dari 4", split on commas into the six levels (stored in Indonesian, as displayed; the third review band
##is written "antara 4.3-4" in the form although the paper's band is 4.3-4.0; kept as displayed).
##Outcome: rating = "Kindly rate the following combination of massage parlor services based on your
##preferences" (paper), 7-point, 1 = strongly not preferred, 7 = strongly preferred; stored raw.
##task = card number 1-27 in the file's column order (display order not documented), profile = 1.
##The sheet has 226 rows: 212 complete respondents plus 14 rows without ratings (summary tallies pasted at
##the foot of the sheet and one-off blanks); only the 212 complete rows are kept.
##Covariates: cov_gender (Pria -> male, Wanita -> female, "Tidak ingin menjawab" -> NA), cov_age (whole years
##between 15 and 100, else NA), cov_visits_per_month (answer text), cov_usual_spend (answer text, IDR per massage).
##Dropped: timestamp, e-mail address (PII FOUND: respondent e-mail addresses in the xlsx), occupation (free text).
##ids are the order of the complete rows. The second sheet ("Copy of Form Responses 1") is a working copy and is not read.
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressMessages(read_excel(file.path(raw, "m.xlsx"), sheet = 1, col_names = FALSE, .name_repair = "minimal")))
nm <- as.character(unlist(x[1])); x <- x[-1]
sc <- 8:34
stopifnot(length(nm) == 34, all(grepl("^[0-9]+\\. Terapis", nm[sc])))
r <- suppressWarnings(as.data.frame(lapply(x[, sc, with = FALSE], as.numeric)))
keep <- complete.cases(r)
x <- x[keep]; r <- as.matrix(r[keep, ])
stopifnot(nrow(r) == 212, all(r %in% 1:7))
parts <- lapply(nm[sc], function(h) trimws(strsplit(sub("^[0-9]+\\.\\s*", "", h), ",")[[1]]))
stopifnot(all(lengths(parts) == 6))
an <- c("therapist", "price", "duration", "room", "massage_type", "google_review")
cards <- rbindlist(lapply(seq_along(parts), function(k) { z <- as.list(parts[[k]]); names(z) <- paste0("attr_", an); data.table(task = k, as.data.table(z)) }))
g <- tolower(trimws(x[[3]]))
age <- suppressWarnings(as.numeric(x[[4]]))
cv <- data.table(id = seq_len(nrow(x)), cov_gender = ifelse(g == "pria", "male", ifelse(g == "wanita", "female", NA_character_)),
                 cov_age = ifelse(!is.na(age) & age == round(age) & age >= 15 & age <= 100, as.integer(age), NA_integer_),
                 cov_visits_per_month = trimws(x[[6]]), cov_usual_spend = trimws(x[[7]]))
rt <- data.table(id = rep(seq_len(nrow(x)), each = 27), task = rep(1:27, times = nrow(x)), profile = 1L, rating = as.integer(t(r)))
d <- merge(merge(rt, cards, by = "task"), cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "prasetyo_2024_massage_parlor.csv"))
