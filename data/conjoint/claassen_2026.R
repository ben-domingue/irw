##Candidate-choice conjoint with anti-democratic positions (US, South Korea, Poland), from
##Claassen, C. (2026). Voting for democracy? Testing political-cultural constraints on democratic backsliding. Public Opinion
##Quarterly. https://doi.org/10.1093/poq/nfag066 (author/journal/year from Crossref; first author per the questionnaire and
##Crossref; the paper lists further authors not checked here)
##Replication data: Harvard Dataverse doi:10.7910/DVN/N9BFTG, CC0 1.0. File read: voting_for_democracy_replication_materials.zip
##(datafile 14100303; unzipped into its own directory): data/democ_cultures_us.csv (2,016 respondents), democ_cultures_sk.csv (2,028),
##democ_cultures_pl.csv (2,010); questionnaire "democratic cultures questionnaire 190825.docx" (text read) and
##"dem cultures code 2 conjoint v2.R" (the authors' recode) and "code 1 measures v2.R" (as text). The pooled file
##democ_cultures_pool.csv (5,945) is the authors' analytic data (below) and is used only for the count check.
##Usage: Rscript claassen_2026.R <dir that holds the unzipped `data` folder> <output dir>
##
##Design (questionnaire, "Conjoint voting experiment"): each respondent compared TWELVE pairs of candidates and chose one in each
##(CJ_Task_k_choice, 1 or 2; no opt-out). Preamble: "Imagine the following two candidates run in the next presidential election
##[US, South Korea] / in your constituency in the next election for the Sejm [Poland]. Please read their profiles and tell us how
##likely you would be to vote for them at the election." The recorded outcome is "Which candidate do you prefer?" (Candidate 1 /
##Candidate 2). Seven attributes (levels from the questionnaire; the data store integer codes mapped by the authors' recode, which
##agrees with the questionnaire order):
##  age: 35, 44, 51, 59, 64, 68;  gender: Male, Female;
##  background: Lawyer, Political career, Journalist, Company director/founder, Military career, Professional sportsperson, Scientist;
##  party: US Democratic / Republican; South Korea Democratic Party of Korea / People Power Party; Poland Prawo i Sprawiedliwosc (PiS) /
##    Koalicja Obywatelska (KO) / Konfederacja Wolnosc i Niepodleglosc (Kon) / Lewica (code 3 = Kon, 4 = Lewica per the authors' map);
##  views on tax and spending (4), views on gender policy (4), views on changes to the political system (6): the full sentences of the
##  questionnaire, with [executive] = "president" (US, South Korea) or "prime minister" (Poland) as the questionnaire's programming
##  notes define.
##Poland party codes 3 and 4 are mapped Kon and Lewica as in the authors' recode (the questionnaire order; both have probability 0.15, so frequencies cannot confirm it).
##Randomization (questionnaire programming notes): age, background, tax/spending and gender policy uniform; gender Male 0.8 / Female 0.2;
##  party US 0.5/0.5, South Korea 0.5/0.5, Poland PiS 0.35, KO 0.35, Kon 0.15, Lewica 0.15; political system attribute CONSTRAINED:
##  one candidate of each pair gets an anti-democratic level (1, 3 or 5: cut polling stations; ignore court rulings; prosecute
##  journalists) and the other a pro-democratic level (2, 4 or 6: keep polling stations; respect rulings; do not prosecute), which candidate
##  is anti-democratic being a coin flip. Verified here that every task has exactly one odd and one even code.
##  restrictions = yes, level_weights = nonuniform.
##Countries pooled in ONE table (cov_country US/KR/PL) as the authors do (their `pool` file): the attribute set and the English master
##text are shared; the party attribute holds the country's own parties (so party levels differ by country) and the wording of the
##executive differs. Language: US English, South Korea Korean, Poland Polish; label_language is the English master text.
##Samples: online panel survey, fielded 2025 (the files date from October 2025). Exclusion: the authors drop "speedsters" (duration <
##40% of the country median) and their pooled analytic file has 5,945 respondents (US 1,979, KR 2,000, PL 1,966) against 6,054 in the
##three files (US 2,016, KR 2,028, PL 2,010): 109 dropped. Applying the stated rule to the files gives 103 (33, 27, 43), so 6 further
##exclusions are not reproduced. This table keeps all 6,054 respondents and gives cov_duration_sec, so users can apply the rule.
##Attribute order: the questionnaire lists a fixed order and mentions no order randomization; no position variable in the data.
##No survey weights in the deposit.
##Covariates: cov_country; cov_gender (gender question: 1 man -> male, 2 woman -> female, 9 other -> other, 98 prefer not to say -> NA);
##cov_age (slider 18-100, as recorded); cov_education (the questionnaire's eight answer options, from the codes 1-8); cov_duration_sec.
##Dropped: RespondentID and ResponseID (platform/respondent identifiers, re-keyed to integers), state/region, income (country-specific
##scales), the attitude and values batteries, party-evaluation items, free text. Gender "Other" (write-in text) not present in the data.
##Count check: 6,054 respondents x 12 tasks x 2 = 145,296 rows (the paper's N not checked; 5,945 in the authors' pool file, see above).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv <- list(
  age = c("35", "44", "51", "59", "64", "68"),
  gender = c("Male", "Female"),
  background = c("Lawyer", "Political career", "Journalist", "Company director/founder", "Military career", "Professional sportsperson", "Scientist"),
  tax = c("Increase spending on public services and social programs", "Decrease spending on public services and social programs",
          "Increase income tax on the richest 10%", "Decrease income tax on the richest 10%"),
  gpol = c("Companies should be required to give preference to women when hiring for jobs where men are overrepresented.",
           "Companies should not be required to give preference to women when hiring even for jobs where men are overrepresented.",
           "Political parties should be required to have gender quotas to ensure equal numbers of male and female candidates.",
           "Political parties should not be required to have gender quotas to ensure equal numbers of male and female candidates."))
sysl <- function(ex) c("Cut the number of polling stations in areas that support opposing parties.",
  "Keep all polling stations, even in areas that support opposing parties.",
  "Ignore court rulings by judges who were appointed by opposing parties.",
  "Respect all court rulings, even if judges were appointed by opposing parties.",
  paste0("Prosecute journalists who accuse the ", ex, " of misconduct without revealing their sources."),
  paste0("Do not prosecute journalists who accuse the ", ex, " of misconduct, even if they do not reveal their sources."))
party <- list(US = c("Democratic", "Republican"), KR = c("Democratic Party of Korea", "People Power Party"),
  PL = c("Prawo i Sprawiedliwosc (PiS)", "Koalicja Obywatelska (KO)", "Konfederacja Wolnosc i Niepodleglosc (Kon)", "Lewica"))
ex <- c(US = "president", KR = "president", PL = "prime minister")
edu <- c("Did not attend school", "Elementary or primary school completed", "Middle school (if applicable) completed",
         "Some high school but not completed", "High school completed", "Some university or college but no bachelor's degree",
         "Bachelor's degree completed", "Graduate or postgraduate degree completed")
fl <- c(US = "democ_cultures_us.csv", KR = "democ_cultures_sk.csv", PL = "democ_cultures_pl.csv")
res <- list()
for (cn in names(fl)) {
  d <- fread(file.path(raw, "data", fl[cn]), encoding = "UTF-8")
  stopifnot(uniqueN(d$RespondentID) == nrow(d))
  d[, id := paste0(cn, ".", .I)]
  for (k in 1:12) for (p in 1:2) {
    g <- function(j) d[[sprintf("CJ_Task_%d_Cand_%d_Att%d", k, p, j)]]
    x <- data.table(src = d$id, task = k, profile = p, choice = as.integer(d[[sprintf("CJ_Task_%d_choice", k)]] == p),
      attr_age = lv$age[g(1)], attr_gender = lv$gender[g(2)], attr_background = lv$background[g(3)], attr_party = party[[cn]][g(4)],
      attr_tax_spending = lv$tax[g(5)], attr_gender_policy = lv$gpol[g(6)], attr_system_change = sysl(ex[cn])[g(7)],
      sys_code = g(7), cov_country = cn,
      cov_gender = c("male", "female", "other", NA)[match(d$gender, c(1, 2, 9, 98))], cov_age = d$age_1,
      cov_education = edu[d$education], cov_duration_sec = d$Response_duration_seconds)
    res[[length(res) + 1L]] <- x
  }
}
t <- rbindlist(res)
stopifnot(nrow(t) == (2016 + 2028 + 2010) * 24)
ac <- grep("^attr_", names(t), value = TRUE); stopifnot(!anyNA(t[, ..ac]), !anyNA(t$choice))
chk <- t[, .(s = sum(choice), odd = sum(sys_code %% 2)), .(src, task)]
stopifnot(all(chk$s == 1), all(chk$odd == 1))
t[, sys_code := NULL]
t[, id := match(src, unique(src))][, src := NULL]
setcolorder(t, c("id", "task", "profile", "choice"))
setorder(t, id, task, profile)
fwrite(t, file.path(out, "claassen_2026_democratic_backsliding.csv"))
