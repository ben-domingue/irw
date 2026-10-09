##Dynastic-candidate rating conjoint (Japan) from
##Miwa, H., Kasuya, Y., & Ono, Y. (2023). Voters' perceptions and evaluations of dynastic
##politics in Japan. Asian Journal of Comparative Politics, 8(3), 671-688.
##https://doi.org/10.1177/20578911221144101  (design read from the RIETI discussion-paper
##version, DP 22-E-113, pp. 16-17; Online Appendix E.1 is not in the deposit)
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z2P876, CC0 1.0. Files read:
##replication_data_conjoint.csv ("original format" of the .tab) and codebook.pdf;
##replication_code_conjoint.R read as text (not run).
##Usage: Rscript miwa_2023.R <raw dir> <output dir>
##
##Rakuten Insight online panel, 2020, 1,126 respondents (paper: 1,126 respondents, 22,520
##observations; both match). Each task showed ONE candidate profile, in bullet points and full
##sentences in Japanese, with 8 attributes; respondents rated 10 candidates for a House of
##Representatives election and 10 for a House of Councillors election, the order of the two
##elections randomized across respondents.
##  rating = favourability, 8-point, 1 "Not favorable at all" .. 8 "Very favorable" (codebook);
##           higher = more favourable; stored as in the source.
##Levels are the deposit's English short labels (the Japanese sentences shown are in Online
##Appendix E.1, not deposited); the paper gives the legacy levels as "his or her parents had no
##political experience" / "... parent was a local politician" / "... a Diet member" / "... a
##cabinet minister" (data: None / Local politician / Diet member / Cabinet minister). The
##source's typo "Buniness employee" is corrected to "Business employee".
##trial_hoc: 0 = House of Representatives task, 1 = House of Councillors task (codebook `HOC`).
##Task numbering is INFERRED from row order and is NOT the display order: in the deposit every
##respondent's 10 HoR rows come first and the 10 HoC rows second, although the paper says the
##election order was randomized, so the deposit was re-sorted; the order within each block is
##unknown. task = row within respondent (1-10 HoR, 11-20 HoC); profile = 1 (single profile).
##Level weights: legacy levels drawn at 85.3 / 3.6 / 4.2 / 6.9 % (paper fn 20); the other
##marginal distributions were "adjusted to the real-world distributions" (paper p. 17; values in
##Appendix E.1, not deposited). Every pair of levels of two attributes occurs in the data.
##Covariates (codebook): cov_gender (1 Male, 2 Female, 3 Others -> male/female/other),
##cov_age (years), cov_education (codebook text, 7 categories), cov_party_id (partisanship,
##codebook text; code 11 "I don't know, or I refuse to answer." merges don't-know and refusal
##and is kept as its text), cov_knowledge (self-reported political knowledge, codebook text).
##No survey weight in the deposit. The paper dropped respondents failing two attention checks
##before the deposit; no attention variable is deposited.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "replication_data_conjoint.csv"))
stopifnot(nrow(s) == 22520, uniqueN(s$respondent.id) == 1126, s[, .N, respondent.id]$N == 20)
s[, task := seq_len(.N), respondent.id]
stopifnot(s[, all(HOC == as.integer(task > 10))])
stopifnot(all(s$rating %in% 1:8), all(s$gender %in% 1:3), all(s$education %in% 1:7),
          all(s$partisanship %in% 1:11), all(s$knowledge %in% 1:5))
edu <- c("Junior high school", "High school", "Vocational school", "Junior college",
         "College of technology", "College", "Graduate school")
pty <- c("Liberal Democratic Party", "Constitutional Democratic Party", "Democratic Party for the People",
         "Komeito", "Japanese Communist Party", "Japan Innovation Party", "Social Democratic Party",
         "Reiwa Shinsengumi", "Other political organizations", "I don't support any party.",
         "I don't know, or I refuse to answer.")
kno <- c("I think I know well.", "I think I know well, if anything.", "I can't say either.",
         "I think I don't know well, if anything.", "I think I don't know well.")
d <- s[, .(id = as.integer(respondent.id), task, profile = 1L, rating = as.integer(rating),
           attr_legacy = legacy, attr_gender = cand.gender, attr_age = as.character(cand.age),
           attr_education = cand.edu, attr_occupation = occupation, attr_hometown = hometown,
           attr_experience = experience, attr_party = party, trial_hoc = as.integer(HOC),
           cov_gender = c("male", "female", "other")[gender], cov_age = as.integer(age),
           cov_education = edu[education], cov_party_id = pty[partisanship], cov_knowledge = kno[knowledge])]
d[attr_occupation == "Buniness employee", attr_occupation := "Business employee"]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miwa_2023_dynastic_candidates.csv"))
