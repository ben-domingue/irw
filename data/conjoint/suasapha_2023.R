##Choice of tourism higher-education institution: rated stimulus cards, Indonesia (Bali)
##Suasapha, A. H. (2023). Conjoint output, descriptive statistics and orthogonal design, THEI research
##(Output Conjoint, Descriptive Statistics dan Orthogonal Design Riset THEI). Dataset with no paper DOI.
##Deposit: figshare doi:10.6084/m9.figshare.29133230, CC BY 4.0 (record licence). Files read:
##"DATASET Kuesioner Stimuli Conjoint EDITED 9 Agustus 2023.xlsx" (sheet Form Responses 1; saved as stim.xlsx)
##and "Output Conjoint Analysis EDUCATION of 238 Subject.spv" (a zip of the SPSS output; its syntax
##header was read as text). Usage: Rscript suasapha_2023.R <dir holding stim.xlsx> <output dir>
##
##238 respondents (students of tourism polytechnics, answers in Indonesian), each rated 16 fixed stimulus
##cards (fixed orthogonal plan, all respondents saw the same 16 cards) that describe a higher-education
##institution by 5 attributes: graduate absorption into the job market (3 levels), academic quality (3),
##campus reputation (2), tuition (3), facilities (3). The cards' text is the column header of the
##stimulus ratings, e.g. "1. Hanya sedikit lulusan yang terserap, Kualitas akademis kampus rendah, Kampus
##tidak terkenal, Biaya kuliah mahal, Fasilitas kampus tidak lengkap." and is split into the five levels (header 7 uses a tab
##instead of a comma). Levels are stored in Indonesian, as displayed.
##Outcome: rating = the 1-4 score of each card. The deposit has no question wording or scale labels. The SPSS
##CONJOINT syntax in the output file uses /SCORE=S1 TO S16, i.e. a preference score in which larger = more
##preferred; stored raw (observed values 1-4). task = card number 1-16 in the file's column order (the order the
##cards were displayed is not documented), profile = 1.
##The sheet has 259 form responses; the 238 with all 16 scores are the authors' analysis set (identical to the
##238 rows of DATASETeducation.xlsx; checked). Others (incomplete) are dropped.
##Covariates: cov_gender (free-typed Indonesian answers mapped to female/male: "laki..." variants -> male,
##"perempuan" and its typo "perrmpuan" -> female; one blank answer -> NA), cov_conf_1..5 (five items answered 1-5,
##"1 very unsure ... 5 very sure": tourism will recover soon, own future in tourism, tourism education gives
##knowledge / skills / attitude), cov_n_campuses_applied (number of campuses applied to).
##Dropped: timestamp, e-mail address (PII FOUND: respondent e-mail addresses in the xlsx), campus name and field of study (free text).
##ids are the order of the complete rows.
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressMessages(read_excel(file.path(raw, "stim.xlsx"), col_names = FALSE, .name_repair = "minimal")))
nm <- as.character(unlist(x[1])); x <- x[-1]
sc <- 13:28
stopifnot(length(nm) == 28, all(grepl("^[0-9]+\\. ", nm[sc])))
r <- suppressWarnings(as.data.frame(lapply(x[, sc, with = FALSE], as.numeric)))
keep <- complete.cases(r)
x <- x[keep]; r <- as.matrix(r[keep, ])
stopifnot(nrow(r) == 238, all(r %in% 1:4))
parts <- lapply(nm[sc], function(h) trimws(strsplit(sub("\\.\\s*$", "", sub("^[0-9]+\\.\\s*", "", h)), "[,\t]")[[1]]))
stopifnot(all(lengths(parts) == 5))
an <- c("graduate_absorption", "academic_quality", "campus_reputation", "tuition", "facilities")
cards <- rbindlist(lapply(seq_along(parts), function(k) { z <- as.list(parts[[k]]); names(z) <- paste0("attr_", an); data.table(task = k, as.data.table(z)) }))
g <- tolower(trimws(x[[3]]))
gender <- ifelse(grepl("^per", g), "female", ifelse(grepl("^laki", g), "male", NA_character_))

cv <- data.table(id = seq_len(nrow(x)), cov_gender = gender, cov_n_campuses_applied = suppressWarnings(as.integer(x[[4]])))
for (j in 1:5) cv[, paste0("cov_conf_", j) := as.integer(x[[7 + j]])]
rt <- data.table(id = rep(seq_len(nrow(x)), each = 16), task = rep(1:16, times = nrow(x)), profile = 1L, rating = as.integer(t(r)))
d <- merge(merge(rt, cards, by = "task"), cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "suasapha_2023_tourism_education.csv"))
