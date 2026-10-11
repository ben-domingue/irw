##AI-disclosure news-trust conjoint (Netherlands) from
##Mattis, N. M., Kieslich, K., & de Vreese, C. (2025). Feeling iffy about generative AI: When journalists
##disclose AI use, trust in news is lower [Preprint]. OSF Preprints. https://doi.org/10.31219/osf.io/tmzq4_v1
##(the deposit's files are anonymised; authors from the OSF node's contributor list).
##Deposit: OSF 76n2d, doi:10.17605/osf.io/76n2d, node licence
##CC-BY 4.0 International. Files read: data analysis/data_anonymised.csv (683 respondents, Qualtrics
##export without ResponseId/panel id) and data analysis/data_analysis_osf.Rmd (read as text: design,
##coding, wording of the task). No codebook or questionnaire ships; the AI Monitor tables themselves
##(the displayed attribute grid) are not in the deposit, only the news-article stimulus images.
##Usage: Rscript mattis_2025.R <dir holding data_anonymised.csv> <output dir>
##Sample: 683 Dutch respondents (Dutch-language items; a panel company, fielded Jan 2025, filtered by
##the authors to attention-check passers, no straightliners, plausible duration: data_anonymised.csv is
##already the filtered sample, flags shorter_than_24 / straigtliner_* all 0).
##Design: each respondent rates 24 single profiles (8 per topic x 3 topics: housing policy, the logistics
##sector, vaccination). A profile is a news article (image + title + teaser, topic) plus an "AI Monitor"
##table saying who did seven journalistic tasks: idea generation, image generation, background research,
##article writing, proofreading, fact checking (each human or AI) and human in the loop (yes or no).
##The 8 profile columns t<topic>_profile<j>_measure carry the design row j of a FIXED fractional factorial
##(8 runs of 2^7, generated with radiant::doe, seed 123; the authors' code assigns the levels by row j
##below), identical for every respondent; the respondent-level randomisation is the order of topics, the
##order of profiles within a topic and which article of the topic is attached to which row. So
##restrictions = yes (only 8 of 128 combinations occur, orthogonal to the topic and the article).
##Level text: the authors' own codes "human" / "AI" and "yes" / "no" (data_analysis_osf.Rmd, section 2.4);
##the Dutch wording the respondents saw is not in the deposit, so the stored text is the authors' English
##code, not necessarily the displayed words.
##Outcome (rating only, no choice, no opt-out): perceived trustworthiness of the article, 1 = not at all
##trustworthy ... 7 = extremely trustworthy (Rmd section 1; exact Dutch wording not in the deposit).
##task = (position of the topic block among the 3 as shown, from first/second/third_topic) * 8 + design row;
##the order within a topic block is randomised but NOT recorded, so within a block task numbers follow the
##design row, not the display order (task_source: unknown). profile = 1 (one profile per task).
##trial_topic: housing / logistics / vaccination. trial_article_image: the article image id attached to the
##row (t<k>_RandomImage<j>, named by the authors' url mapping, e.g. housing11).
##Covariates: cov_age (age in years, 16-83), cov_gender (1 -> male, 2 -> female, 3 -> other, from the
##authors' wording in the Rmd, L801: "male", "female", "non-binary"; the deposit has no value labels),
##cov_education_code (education 1-7, codes only: no labels in the deposit), cov_political_position_code (political position,
##1-10 scale, left to right per the authors' use; kept raw).
##Dropped: all attitude / knowledge scales, news use, timers, open_end, image URLs, record date (datetime).
##Respondent id = user_id (an integer sequence added by the authors).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data_anonymised.csv"))
stopifnot(nrow(s) == 683, uniqueN(s$user_id) == 683)
des <- data.table(j = 1:8,
  attr_idea_generation = c("human","human","human","human","AI","AI","AI","AI"),
  attr_image_generation = c("human","human","AI","AI","human","human","AI","AI"),
  attr_background_research = c("AI","AI","human","human","human","human","AI","AI"),
  attr_article_writing = c("human","AI","human","AI","human","AI","human","AI"),
  attr_proofreading = c("AI","human","human","AI","human","AI","AI","human"),
  attr_fact_checking = c("human","AI","AI","human","human","AI","AI","human"),
  attr_human_in_the_loop = c("yes","no","yes","no","no","yes","no","yes"))
topics <- c("housing", "logistics", "vaccination")
L <- list()
for (k in 1:3) for (j in 1:8) {
  r <- data.table(id = s$user_id, topic = topics[k], j = j, rating = as.integer(s[[sprintf("t%d_profile%d_measure", k, j)]]),
                  trial_article_image = s[[sprintf("t%d_RandomImage%d", k, j)]])
  L[[length(L) + 1]] <- r
}
d <- rbindlist(L)
stopifnot(!anyNA(d$rating), d[, all(rating %in% 1:7)], d[, all(startsWith(trial_article_image, topic))])
pos <- melt(s[, .(id = user_id, housing = 0L, logistics = 0L, vaccination = 0L, f = first_topic, g = second_topic, h = third_topic)],
            id.vars = c("id", "housing", "logistics", "vaccination"), variable.name = "p", value.name = "topic")
pos[, pos := match(p, c("f", "g", "h"))]
stopifnot(pos[, uniqueN(topic), id][, all(V1 == 3)])
d <- merge(d, pos[, .(id, topic, pos)], by = c("id", "topic"))
d <- merge(d, des, by = "j")
d[, `:=`(task = (pos - 1L) * 8L + j, profile = 1L, trial_topic = topic)]
cv <- s[, .(id = user_id, cov_age = as.integer(age),
            cov_gender = c("male", "female", "other")[gender], cov_education_code = as.integer(education),
            cov_political_position_code = as.integer(pol_pos))]
d <- merge(d, cv, by = "id")
cols <- c("id", "task", "profile", "rating", names(des)[-1], "cov_age", "cov_gender", "cov_education_code",
          "cov_political_position_code", "trial_topic", "trial_article_image")
d <- d[, ..cols]; setorder(d, id, task, profile)
stopifnot(d[, .N, id][, all(N == 24)], d[, uniqueN(task), id][, all(V1 == 24)])
fwrite(d, file.path(out, "mattis_2025_ai_disclosure.csv"))
