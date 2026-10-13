##Single-profile rated-person conjoint, 9 randomized attributes + a value statement, from
##Jung, J.-H., & Clifford, S. (2024). Varieties of values: Moral values are uniquely divisive. American Political
##Science Review. https://doi.org/10.1017/S0003055424000443
##Replication data: Harvard Dataverse doi:10.7910/DVN/MLJQQN, CC0 1.0. File read: "9089.119_TESS 119 Clifford.tab"
##(the raw TESS file, Dataverse "original format" .dta, saved here as tess.dta); SM_OnlineAppendix.pdf (pdftotext,
##saved as sm.txt; the completed strings are embedded below) for the full text of 37 value statements whose Stata value labels are cut at 80 characters;
##analysis_tess.do and analysis_R.R read as text for the outcome and attribute coding.
##Usage: Rscript jung_2024_value_conjoint.R <dir holding tess.dta> <output dir>
##
##863 respondents (NORC AmeriSpeak probability panel, TESS 119). Each rated SIX hypothetical people, one at a time
##(task = 1..6, profile = 1): wide columns *_1 ... *_6 are the six profiles. Attributes as labelled in the .dta:
##gender (Man/Woman), age (28/37/46/55/63), ethnicity (White/Hispanic/African-American/Asian), partisanship
##(Democrat/Republican/Independent), career (8), religion (7), education (4), favorite hobby (9), and the person's
##stance on a value statement: attr_value_stance ("Agrees that "Statement"" / "Disagrees that "Statement"", the
##labelled wording) and attr_value_statement (one of 102 statements measuring 21 values, StatementsToShowRandomQ1_k,
##value-label text; 37 are completed from the online appendix list). Level probabilities are not stated and the table shares are
##unequal (e.g. ethnicity White ~60%, religion, partisanship), so level_weights = observed. Level text is as in
##the value labels (the questionnaire screens are not deposited).
##Outcomes (ratings, three questions per profile, stored raw; 98 = "SKIPPED ON WEB" -> NA):
##  rating_favorability = Q7A..Q12A "How positive or negative are your feelings toward [this person]"
##    1 Very positive ... 4 Neutral ... 7 Very negative (LOWER = more favourable);
##  rating_neighbor = Q7B.. "How happy or unhappy would you be to have [this person] as a neighbor" (paraphrase
##    from the 80-char variable label and analysis_tess.do), 1 Very happy, 2 Somewhat happy, 3 Neither, 4 Somewhat
##    unhappy, 5 Very unhappy (LOWER = more favourable; the authors reverse it in the .do file);
##  rating_house = Q7C.. "Imagine that you need someone to look a[fter your house ...]" (variable label cut at 80
##    characters; trust to look after the respondent's house, paraphrase) 1 Not comfortable at all ... 5 Completely
##    comfortable (HIGHER = more favourable).
##No choice, no opt-out. Covariates: cov_gender (GENDER 1 Male, 2 Female), cov_age (AGE), cov_education (EDUC5 label
##text), cov_party_id7 (PartyID7 label text, "Unknown" -> NA), cov_race_ethnicity (RACETHNICITY label text),
##cov_survey_weight (WEIGHT, post-stratification weight, 18+ general population). Dropped: the respondent's own
##agreement with the 102 statements and all derived value/quota/flag columns, state/region/household fields, dates,
##device. The MTurk and Lucid pilots (xlsx) are separate pilots and are not built.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "tess.dta")))
stopifnot(nrow(s) == 863, !anyDuplicated(s$CaseId))
fix <- c(
  "It is important to me to think up new ideas, be creative, and do things in my ow" = "It is important to me to think up new ideas, be creative, and do things in my own original way.",
  "It is important to me to make my own decisions and to be free to plan and choose" = "It is important to me to make my own decisions and to be free to plan and choose activities for myself.",
  "It is important to me to be interested, curious, and to try to understand all so" = "It is important to me to be interested, curious, and to try to understand all sorts of things.",
  "It is important to me to seek every chance to have fun and to do things that giv" = "It is important to me to seek every chance to have fun and to do things that give me pleasure.",
  "It is important to me to help the people around me and to care for other people." = "It is important to me to help the people around me and to care for other people.",
  "It is important to me to be loyal to my friends and to devote myself to people c" = "It is important to me to be loyal to my friends and to devote myself to people close to me.",
  "It is important to me to respond to the needs of others and support those I know" = "It is important to me to respond to the needs of others and support those I know.",
  "It is important to me to always be the one who makes decisions and to be the lea" = "It is important to me to always be the one who makes decisions and to be the leader.",
  "It is important to me that every person in the world is treated equally and rece" = "It is important to me that every person in the world is treated equally and receives justice.",
  "It is important to me to listen to people who are different from me and understa" = "It is important to me to listen to people who are different from me and understand them, even when I disagree with them.",
  "It is important to me to promote peace and harmony among all groups in the world" = "It is important to me to promote peace and harmony among all groups in the world.",
  "It is important to me to adapt to nature and fit in to it, rather than try to ch" = "It is important to me to adapt to nature and fit in to it, rather than try to change nature.",
  "It is important to me that my country is safe from threats within and without an" = "It is important to me that my country is safe from threats within and without and that social order is protected.",
  "It is important to me to have a stable government and that social order is prote" = "It is important to me to have a stable government and that social order is protected.",
  "It is important to me to do lots of different things in life and to look for new" = "It is important to me to do lots of different things in life and to look for new things to try.",
  "It is important to me that people follow the rules and do what they're told, eve" = "It is important to me that people follow the rules and do what they're told, even when no one is watching.",
  "It is important to me to be obedient and to show respect for my parents and to o" = "It is important to me to be obedient and to show respect for my parents and to older people.",
  "It is important to me to always be polite to other people and to never disturb o" = "It is important to me to always be polite to other people and to never disturb or irritate others.",
  "It is important to me that people are satisfied with what they have and that the" = "It is important to me that people are satisfied with what they have and that they not ask for more.",
  "My religious beliefs are important to me, and I try to do what my religion requi" = "My religious beliefs are important to me, and I try to do what my religion requires.",
  "It is important to me to do things in traditional ways and follow the customs I'" = "It is important to me to do things in traditional ways and follow the customs I've learned.",
  "It is important to me to be humble and modest, and not to draw attention to myse" = "It is important to me to be humble and modest, and not to draw attention to myself.",
  "When the government makes laws, the number one principle should be ensuring that" = "When the government makes laws, the number one principle should be ensuring that everyone is treated fairly.",
  "People should be loyal to their family members, even when they have done somethi" = "People should be loyal to their family members, even when they have done something wrong.",
  "If I were a soldier and disagreed with my commanding officer’s orders, I would o" = "If I were a soldier and disagreed with my commanding officer’s orders, I would obey anyway because that is my duty.",
  "Incomes should be more equal because every family’s needs for food, housing, and" = "Incomes should be more equal because every family’s needs for food, housing, and so on, are the same.",
  "Incomes cannot be made more equal since people’s abilities and talents are unequ" = "Incomes cannot be made more equal since people’s abilities and talents are unequal.",
  "The dignity and welfare of people should be the most important concern in any so" = "The dignity and welfare of people should be the most important concern in any society.",
  "All people who are unable to provide for their basic needs should be helped by o" = "All people who are unable to provide for their basic needs should be helped by others.",
  "One of the problems of today’s society is that we are often too kind to people w" = "One of the problems of today’s society is that we are often too kind to people who don’t deserve it.",
  "This country would have many fewer problems if there were more emphasis on tradi" = "This country would have many fewer problems if there were more emphasis on traditional family ties.",
  "The world is always changing and we should adjust our views of moral behavior to" = "The world is always changing and we should adjust our views of moral behavior to those changes.",
  "We should be more tolerant of people who choose to live according to their own m" = "We should be more tolerant of people who choose to live according to their own moral standards, even if they are very different from our own.",
  "Most people who don't get ahead should not blame the system; they only have them" = "Most people who don't get ahead should not blame the system; they only have themselves to blame.",
  "The free market can handle today's economic problems without government being in" = "The free market can handle today's economic problems without government being involved.",
  "The main reason government has become bigger over the years is because it has go" = "The main reason government has become bigger over the years is because it has gotten involved in things that people should do for themselves.",
  "Government has become bigger because the problems we face today have become bigg" = "Government has become bigger because the problems we face today have become bigger."
)
lab <- function(v) as.character(as_factor(v, levels = "labels"))
stmt_labs <- names(attr(s$StatementsToShowRandomQ1_1, "labels"))
stmt_full <- ifelse(stmt_labs %in% names(fix), fix[stmt_labs], stmt_labs)
stmt <- function(v) stmt_full[match(as.character(lab(v)), stmt_labs)]
lst <- lapply(1:6, function(k) {
  g <- function(n) s[[paste0(n, "_", k)]]
  data.table(id = s$CaseId, task = k, profile = 1L,
    rating_favorability = as.integer(s[[paste0("Q", 6 + k, "A")]]), rating_neighbor = as.integer(s[[paste0("Q", 6 + k, "B")]]),
    rating_house = as.integer(s[[paste0("Q", 6 + k, "C")]]),
    attr_gender = lab(g("GENDER")), attr_age = lab(g("AGE")), attr_ethnicity = lab(g("ETHNICITY")),
    attr_partisanship = lab(g("PARTISANSHIP")), attr_career = lab(g("CAREER")), attr_religion = lab(g("RELIGION")),
    attr_education = lab(g("EDUCATION")), attr_hobby = lab(g("FAVORITEHOBBY")),
    attr_value_stance = lab(g("VALUETOSHOW")), attr_value_statement = stmt(s[[paste0("StatementsToShowRandomQ1_", k)]]))
})
d <- rbindlist(lst)
for (v in c("rating_favorability", "rating_neighbor", "rating_house")) d[get(v) == 98L, (v) := NA_integer_]
cov <- data.table(id = s$CaseId, cov_gender = c("male", "female")[as.integer(s$GENDER)], cov_age = as.integer(s$AGE),
  cov_education = lab(s$EDUC5), cov_party_id7 = fifelse(as.integer(s$PartyID7) < 0, NA_character_, lab(s$PartyID7)),
  cov_race_ethnicity = lab(s$RACETHNICITY), cov_survey_weight = as.numeric(s$WEIGHT))
d <- merge(d, cov, by = "id")
stopifnot(!anyNA(d[, .(attr_gender, attr_age, attr_ethnicity, attr_partisanship, attr_career, attr_religion, attr_education, attr_hobby, attr_value_stance, attr_value_statement)]))
d <- d[!(is.na(rating_favorability) & is.na(rating_neighbor) & is.na(rating_house))]
d[, id := match(id, sort(unique(id)))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jung_2024_value_conjoint.csv"))
