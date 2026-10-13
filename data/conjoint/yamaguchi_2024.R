##Decision-model x policy vignette experiment (Japan) from
##Yamaguchi, A., Hata, M., & Inoue, A. (2024). How can we accept 'our' decisions?: An experimental
##study on lottocracy, epistocracy, and electoral democracy. Japanese Journal of Political Science,
##25(3), 123-139. https://doi.org/10.1017/s1468109924000094
##Replication data: Harvard Dataverse doi:10.7910/DVN/TTQWMQ, CC0 1.0. Files read:
##replication_yamaguchietal2024.tab (comma/tab export of the survey), Codeook.pdf (codebook, read
##as text) and JJPSreplication_yamaguchietal2024.R (the authors' code, read as text, not run).
##Usage: Rscript yamaguchi_2024.R <dir holding data.tab> <output dir>   (file saved as data.tab)
##
##2,398 Japanese adults from a survey company's panel, ONE text vignette each (id = the file's ID;
##task = profile = 1, inferred: each respondent answered exactly one of eight question blocks).
##Eight experimental groups = 4 x 2 between-subject factorial:
##  attr_decision_model : who decides -- "Electoral democracy" / "Lottocracy (Full)" / "Lottocracy
##                        (Upper only)" / "Epistocracy" (Q9.1..Q16.1 block: groups 1-4 and 5-8)
##  attr_policy         : "Education Policy" (groups 1-4) / "Environmental Tax" (groups 5-8)
##These level names are the AUTHORS' labels in the replication code (decision / policy variables); the
##vignette text respondents read (a bill decided by that body) is not in the deposit. The factor is read
##from which block (Q9.1 ... Q16.1) holds the answer.
##Outcome rating = the block's single acceptance item, stored raw 1-5. In the authors' code
##out = 6 - raw and their figure axis runs "Not Acceptance <- -> Acceptance", so RAW 1 = most
##accepting, 5 = least (LOWER = more favourable in this table). Item wording is not in the codebook
##(paraphrase: how acceptable the decision is to the respondent).
##Covariates: cov_gender (codebook: Male = 1, Female = 2), cov_age (18-79), cov_education (Q2.1,
##codebook text: Middle school / High school / Junior college, technical college, vocational school /
##Four-year university / Graduate school; 6 "Prefer not to say" -> NA), cov_income_band (Q2.2: 21
##bands of 500k yen from under 3,000k to over 20,000k for 2019 household income; 22 prefer not -> NA;
##kept as band number 1-21), cov_know_term / cov_know_turnout / cov_know_party (Q7.2-Q7.4 political
##knowledge quiz answers, codes 1-5 with 5 = "I don't know"; options in the codebook; correct = 4 / 2 / 1),
##cov_attention_pass (the authors' `manu`: Q17.1 names the bill and Q17.2 the legislative body shown in
##the respondent's own arm; 1 = both correct, 1,013 of 2,398; the answer options are not labelled in
##the codebook, the correct codes come from the authors' code).
##No weight; no restrictions (between-subject, all 8 cells filled 279-331). Dropped: nothing else.
##N: 2,398 respondents (the authors' code divides by 2,398).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "data.tab"))
qs <- c("Q9.1", "Q10.1", "Q11.1", "Q12.1", "Q13.1", "Q14.1", "Q15.1", "Q16.1")
stopifnot(nrow(k) == 2398, all(rowSums(!is.na(k[, ..qs])) == 1), uniqueN(k$ID) == 2398)
g <- max.col(!is.na(as.matrix(k[, ..qs])), ties.method = "first")
dm <- c("Electoral democracy", "Lottocracy (Full)", "Lottocracy (Upper only)", "Epistocracy")
d <- data.table(id = as.integer(k$ID), task = 1L, profile = 1L,
  rating = as.integer(unlist(lapply(seq_len(nrow(k)), function(i) k[[qs[g[i]]]][i]))),
  attr_decision_model = dm[(g - 1L) %% 4L + 1L], attr_policy = c("Education Policy", "Environmental Tax")[(g - 1L) %/% 4L + 1L])
d[, cov_gender := c("male", "female")[k$sex]]
d[, cov_age := as.integer(k$age)]
d[, cov_education := c("Middle school", "High school", "Junior college, technical college, vocational school", "Four-year university", "Graduate school", NA)[k$Q2.1]]
d[, cov_income_band := ifelse(k$Q2.2 == 22L, NA_integer_, as.integer(k$Q2.2))]
d[, cov_know_term := as.integer(k$Q7.2)]; d[, cov_know_turnout := as.integer(k$Q7.3)]; d[, cov_know_party := as.integer(k$Q7.4)]
ok <- ((g <= 4 & k$Q17.1 == 1) | (g > 4 & k$Q17.1 == 4)) & k$Q17.2 == c(4, 1, 2, 3)[(g - 1L) %% 4L + 1L]
d[, cov_attention_pass := as.integer(!is.na(ok) & ok)]
cat("attention pass:", sum(d$cov_attention_pass), "\n")
stopifnot(!anyNA(d$rating), d[, .N, .(attr_decision_model, attr_policy)][, .N] == 8)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "yamaguchi_2024_lottocracy.csv"))
