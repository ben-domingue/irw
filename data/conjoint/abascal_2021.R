##Neighborhood-diversity conjoint from
##Abascal, M., Xu, J., & Baldassarri, D. (2021). People use both heterogeneity and minority
##representation to evaluate diversity. Science Advances, 7(11), eabf2507.
##https://doi.org/10.1126/sciadv.abf2507
##Replication data: Harvard Dataverse doi:10.7910/DVN/MTH58P, CC0 1.0, no restricted files.
##File read: "02 ConjointData_dec2019.csv" (Dataverse "original format" download, saved as
##conjoint.csv): the raw Qualtrics export, answers as text, two header rows. Level text,
##question wording and covariate codes from "03 Qualtrics_Data_Codebook_dec2019.docx" and
##the export's question-text row.
##Usage: Rscript abascal_2021.R <raw dir> <output dir>
##
##1,999 Qualtrics opt-in panel respondents (US, December 2019), race-balanced quota sample
##(about 500 each White, Black, Latino, Asian). 4 tasks, each a pair of hypothetical
##neighborhoods (A = profile 1, B = profile 2) described as "Neighborhood A, which is 90%
##Asian, 8% Black, and 2% White". The description is the only thing shown; its parts are the
##attributes here: attr_shares = the share pattern (50%/48%/2%, 60%/38%/2%, 70%/28%/2%,
##80%/18%/2%, 90%/8%/2%), attr_largest_group, attr_second_group, attr_third_group (the
##2% group), each White / Black / Latino / Asian. The fourth group is absent. The three groups
##are always distinct (a restriction by construction). The full displayed text is
##"<s1>% <largest>, <s2>% <second>, and 2% <third>" (1,325 of the 4,033 White-largest
##descriptions lack the comma before "and"; that punctuation difference is not kept).
##Profiles A and B were drawn independently: 78 of 7,996 pairs are identical.
##Outcomes:
##  choice = "Which of these two neighborhoods do you think is more racially diverse?"
##           Neighborhood A or B; forced choice, no opt-out.
##  rating = "On a scale from 1 to 7, where 1 indicates that the neighborhood is not racially
##           diverse at all and 7 indicates that the neighborhood is very racially diverse,
##           how would you rate this neighborhood?" Asked for A, then B. Kept 1-7.
##           (Higher = more diverse; the question is about perceived diversity, not liking.)
##STRAIGHTLINERS: Qualtrics flagged 196 respondents who gave the same answer to every choice
##and every rating ("replace_but_keep"); the paper's main sample (N = 1,803) excludes them,
##section S8 adds them back. All 1,999 are kept here with cov_straightliner = 1/0.
##Respondent IDs are Qualtrics ResponseIDs, re-keyed to integers in file order. Dropped:
##start/end/recorded dates and duration.
##Covariates. As answer text (export answer text, checked against the codebook "03 Qualtrics_
##Data_Codebook_dec2019.docx"): cov_gender "What gender do you consider yourself?" female /
##male (codebook gender 1 = Male, 2 = Female, 3 = Something else; no "Something else" in the
##export); cov_education "What is the highest level of education you have completed?" as
##worded in the export: Less than high school / High school/GED / Some college / 2-year
##degree (Associate's) / 4-year degree (Bachelor's) / Graduate or professional degree
##(codebook educ 1-6); cov_party_id (export variable party1; not in the codebook) Democrat /
##Republican / Independent / Something else, as in the export.
##Numeric codes: cov_age years; cov_race 1=White 2=Black 3=Hispanic/Latino 4=Asian; cov_income
##1=<$10k 2=$10-20k ... 10=$90-100k 11=$100-150k 12=$150k+; cov_born 1=US 2=US territory
##3=other country; cov_immigration 1=keep at present level 2=increase 3=decrease;
##cov_aa_1 (race in college admissions) 1=favor 2=oppose 3=neither; cov_aa_2 (if favor)
##1=strongly 2=not strongly; cov_aa_3 (if oppose) 1=strongly 2=not strongly (the codebook
##says "favor" here by mistake). Not in the codebook, coded here from the answer text:
##cov_better_place (more diversity makes the US) 1=better 2=no difference 3=worse;
##cov_white_advantage (being White affects getting ahead) 1=helps a lot 2=helps a little
##3=neither 4=hurts a little 5=hurts a lot; cov_employment 1=full time 2=part time 3=with a
##job but not at work 4=unemployed/looking 5=retired 6=in school 7=keeping house
##8=something else; cov_party_strength 1=strong 2=not very strong; cov_party_lean
##1=closer to Democratic 2=closer to Republican 3=neither; cov_ideology 1=extremely liberal..7=extremely
##conservative, 8=haven't thought much about this; cov_ideology_forced 1=liberal
##2=conservative 3=neither; cov_vote2016 1=Clinton 2=Trump 3=someone else 4=did not vote.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "conjoint.csv"), colClasses = "character", na.strings = "", header = TRUE)
r <- r[-(1:2)]   # question-text and ImportId rows
stopifnot(!anyDuplicated(r$ResponseID))
code <- function(x, lv) { i <- match(x, lv); stopifnot(all(is.na(x) | !is.na(i))); i }
chk <- function(x, lv) { code(x, lv); x }   # keep the answer text, checked against the known options
cv <- data.table(id = seq_len(nrow(r)),
  cov_age = as.integer(r$age),
  cov_gender = tolower(chk(r$gender, c("Male", "Female"))),
  cov_education = chk(r$educ, c("Less than high school", "High school/GED", "Some college", "2-year degree (Associate's)",
                          "4-year degree (Bachelor's)", "Graduate or professional degree")),
  cov_race = code(r$race, c("White", "Black/African American", "Hispanic/Latino(a)", "Asian/Asian American")),
  cov_income = code(r$faminc, c("Less than $10,000", "$10,000 - $19,999", "$20,000 - $29,999", "$30,000 - $39,999",
                                "$40,000 - $49,999", "$50,000 - $59,999", "$60,000 - $69,999", "$70,000 - $79,999",
                                "$80,000 - $89,999", "$90,000 - $99,999", "$100,000 - $149,999", "More than $150,000")),
  cov_born = code(r$born, c("United States", "U.S. territory (e.g., Puerto Rico)", "Some other country")),
  cov_immigration = code(r$immigration, c("Present level", "Increased", "Decreased")),
  cov_aa_1 = code(r$aa_1, c("Favor", "Oppose", "Neither favor nor oppose")),
  cov_aa_2 = code(r$aa_2, c("Strongly favor", "Not strongly favor")),
  cov_aa_3 = code(r$aa_3, c("Strongly oppose", "Not strongly oppose")),
  cov_better_place = code(r$betterplace, c("A better place to live", "Doesn't make much difference either way", "A worse place to live")),
  cov_white_advantage = code(r$whiteadvantage, c("Helps a lot", "Helps a little", "Neither helps nor hurts", "Hurts a little", "Hurts a lot")),
  cov_employment = code(r$empstat, c("Working full time", "Working part time",
                                     "With a job, but not at work for temporary reason (e.g,. illness, vacation, strike)",
                                     "Unemployed, laid off, or looking for work", "Retired", "In school", "Keeping house", "Something else")),
  cov_party_id = chk(r$party1, c("Democrat", "Republican", "Independent", "Something else")),
  cov_party_strength = code(sub(" \\$\\{.*", "", r$party2), c("Strong", "Not very strong")),
  cov_party_lean = code(r$party3, c("Closer to the Democratic Party", "Closer to the Republican Party", "Neither")),
  cov_ideology = code(r$ideo1, c("Extremely liberal", "Liberal", "Slightly liberal", "Moderate, middle of the road",
                                 "Slightly conservative", "Conservative", "Extremely conservative", "Haven't thought much about this")),
  cov_ideology_forced = code(r$ideo2, c("Liberal", "Conservative", "Neither")),
  cov_vote2016 = code(r$vote16, c("Hillary Clinton", "Donald Trump", "I voted for someone else", "I did not vote for president in 2016")),
  cov_straightliner = as.integer(!is.na(r$replace_but_keep) & r$replace_but_keep == "1"))
d <- rbindlist(lapply(1:4, function(t) rbindlist(lapply(1:2, function(p) {
  txt <- r[[sprintf("F-%d-%d-1", t, p)]]
  m <- regmatches(txt, regexec("^(\\d+)% (\\w+), (\\d+)% (\\w+),? and 2% (\\w+)$", txt))
  stopifnot(all(lengths(m) == 6))
  m <- do.call(rbind, m)
  ch <- code(r[[paste0("choice", t)]], c("Neighborhood A", "Neighborhood B"))
  data.table(id = seq_len(nrow(r)), task = t, profile = p, choice = as.integer(ch == p),
             rating = as.integer(substr(r[[sprintf("rating%d_%s", t, c("A", "B")[p])]], 1, 1)),
             attr_shares = paste0(m[, 2], "%/", m[, 4], "%/2%"),
             attr_largest_group = m[, 3], attr_second_group = m[, 5], attr_third_group = m[, 6])
}))))
stopifnot(d[, all(attr_largest_group != attr_second_group & attr_largest_group != attr_third_group & attr_second_group != attr_third_group)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7))
d <- d[!(is.na(choice) & is.na(rating))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "abascal_2021_neighborhood_diversity.csv"))
