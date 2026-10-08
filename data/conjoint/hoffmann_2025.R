##Immigrant admission conjoint (US, Prolific, June 2023) from
##Hoffmann, N. I., & Velasco, K. (2025). How sexuality affects evaluations of immigrant deservingness
##and cultural similarity: A conjoint survey experiment. Public Opinion Quarterly, 89(4), 1138-1153.
##https://doi.org/10.1093/poq/nfaf054
##Replication data: Harvard Dataverse doi:10.7910/DVN/3FONBK, CC0 1.0. Files read (Dataverse "original
##format"): qualtrics.csv (Qualtrics export) and prolific.csv (Prolific export). qualtrics_codebook.csv,
##prolific_codebook.csv, readme-1.txt and main_replication.Rmd read as text, not run.
##Usage: Rscript hoffmann_2025.R <dir holding the two .csv files> <output dir>
##
##US Prolific sample, 20-23 June 2023. 4 tasks x 2 immigrants ("Immigrant 1" .. "Immigrant 8" across the
##survey), each described by 7 randomized features: gender, sexuality, country wealth (gdp), skill
##(education and job), English, religion and reason for migrating. The profile is a written
##description with the levels embedded; attr_ keeps each embedded phrase exactly as exported
##("has an MD, and works as a cardiologist", "straight (that is, not lesbian)"). The pronoun and
##possessive fields are display helpers that follow gender and are dropped. 6 of 1,873 raw records
##show gdp "middle-income" (not a codebook level); none is in the analysed sample.
##Sample: the authors' filters (main_replication.Rmd): Prolific status APPROVED or AWAITING REVIEW,
##two Prolific IDs excluded (one failed attention check, one "extra person"), Finished, and Prolific
##age available (29 respondents with expired Prolific data dropped). 1,621 respondents; the article
##reports 1,650 (the count before the age filter).
##task = (immigrant number + 1) %/% 2, profile = 1 for odd, 2 for even immigrant numbers (recorded).
##Outcomes (qualtrics_codebook.csv):
##  choice        = choice_a..d, "Based on their descriptions, which of these two immigrants would you
##                  personally prefer to see admitted to the United States?" (Immigrant k should be
##                  admitted; forced choice, no opt-out; one chosen per task, checked).
##  choice_values = value_a..d, "Based on their descriptions, which of these two immigrants do you think
##                  has greater shared values with the United States?" (blank if unanswered).
##  rating        = rating1..8, "Regarding admission, how would you rate immigrant k? A rating of 1 means
##                  that the U.S. should absolutely not admit immigrant k, and a 7 means that the U.S.
##                  should definitely admit this immigrant." 1-7, 7 = definitely admit.
##  rating_values = value1..8, "To what degree do you think immigrant k has shared values with the U.S.?
##                  Choosing 1 signifies having no shared values, and 7 signifies a great deal of shared
##                  values." 1-7.
##Randomization: the codebook lists sexuality as "gay/lesbian; straight (that is, not gay/lesbian)":
##the word shown follows the immigrant's gender (gay / not gay for a man, lesbian / not lesbian for a
##woman), a conditional level (restrictions = yes); no other rules are documented.
##Covariates (respondent answers as text): cov_gender (resp_gender "What is your gender?", codebook
##options Man, Woman, Other; stored male / female / other), cov_citizen, cov_born_citizen, cov_party_id
##(resp_politics "Do you consider yourself a Democrat, a Republican, an independent, or none of
##these?", text as exported: Democrat, Republican, Independent, None of these), cov_sexuality,
##cov_education (resp_education, as worded), cov_religion, cov_attend, cov_know_lg (lesbian or gay
##friends/family), cov_imm_1 .. cov_imm_11 (the 11 immigration statements, codebook order); from
##Prolific: cov_age, cov_sex_panel (Prolific's "Sex: Male, Female", kept as text; cov_gender is the
##survey's own question), cov_ethnicity. The survey's two attention checks (attention_color,
##attention_number) and "Duration (in seconds)" are not kept. The authors' post-stratification weights (raked to Pew
##ATP wave 112, not deposited) are not built.
##PII in the deposit, not kept: Prolific IDs (prolific_pid, PROLIFIC_PID; Participant id and Submission id
##in prolific.csv), ResponseId, start/end times. IP addresses and locations are already redacted.
##IDs are re-keyed to integers in file order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "qualtrics.csv"), header = TRUE, colClasses = "character")[-(1:2)]
p <- fread(file.path(raw, "prolific.csv"), colClasses = "character")[Status %in% c("APPROVED", "AWAITING REVIEW")]
s <- d[PROLIFIC_PID %in% p$`Participant id` & !PROLIFIC_PID %in% c("644af405d31dd25adf037157", "6048622d518a190008dfbe38") & Finished == "True"]
s[, age := suppressWarnings(as.integer(p$Age[match(PROLIFIC_PID, p$`Participant id`)]))]
s <- s[!is.na(age)]
stopifnot(nrow(s) == 1621L, !anyDuplicated(s$PROLIFIC_PID))
num <- function(x) { y <- as.integer(substr(x, 1, 1)); y[x == ""] <- NA; y }
rows <- list()
for (k in 1:8) {
  t <- (k + 1L) %/% 2L; pr <- 2L - k %% 2L; L <- letters[t]
  ch <- s[[paste0("choice_", L)]]; vc <- s[[paste0("value_", L)]]
  x <- data.table(id = seq_len(nrow(s)), task = t, profile = pr,
                  choice = as.integer(ch == sprintf("Immigrant %d should be admitted.", k)),
                  choice_values = fifelse(vc == "", NA_integer_, as.integer(vc == sprintf("Immigrant %d has greater shared values with the U.S.", k))),
                  rating = num(s[[paste0("rating", k)]]), rating_values = num(s[[paste0("value", k)]]))
  x[ch == "", choice := NA_integer_]
  for (v in c("gender", "sexuality", "gdp", "skill", "lang", "religion", "reason")) x[, paste0("attr_", v) := s[[paste0(v, k)]]]
  rows[[k]] <- x
}
x <- rbindlist(rows)
setnames(x, c("attr_gdp", "attr_lang"), c("attr_country_wealth", "attr_english"))
stopifnot(!anyNA(x$choice), x[, sum(choice), .(id, task)][, all(V1 == 1)],
          x[!is.na(choice_values), sum(choice_values), .(id, task)][, all(V1 == 1)],
          all(x$rating %in% 1:7), !anyNA(x[, .SD, .SDcols = patterns("^attr_")]), all(x$attr_country_wealth %in% c("low-income", "moderately wealthy")))
cv <- c(cov_gender = "resp_gender", cov_citizen = "resp_citizen", cov_born_citizen = "resp_born", cov_party_id = "resp_politics",
        cov_sexuality = "resp_sexuality", cov_education = "resp_education", cov_religion = "resp_religion", cov_attend = "resp_attend",
        cov_know_lg = "resp_knowlg", setNames(paste0("resp_imm_support_", 1:11), paste0("cov_imm_", 1:11)))
c2 <- data.table(id = seq_len(nrow(s)))
for (v in names(cv)) c2[, (v) := { y <- s[[cv[[v]]]]; y[y == ""] <- NA; y }]
stopifnot(all(c2$cov_gender %in% c("Man", "Woman", "Other", NA)))
c2[, cov_gender := c(Man = "male", Woman = "female", Other = "other")[cov_gender]]
c2[, cov_age := s$age]
pm <- match(s$PROLIFIC_PID, p$`Participant id`)
c2[, cov_sex_panel := p$Sex[pm]][, cov_ethnicity := p$`Ethnicity simplified`[pm]]
c2[cov_sex_panel %in% c("DATA_EXPIRED", ""), cov_sex_panel := NA][cov_ethnicity %in% c("DATA_EXPIRED", ""), cov_ethnicity := NA]
x <- merge(x, c2, by = "id")
setorder(x, id, task, profile)
fwrite(x, file.path(out, "hoffmann_2025_immigrant_sexuality.csv"))
