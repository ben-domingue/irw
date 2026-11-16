##Legislative-candidate conjoints in Brazil, Chile and Peru from
##Smith, A. E., & Boas, T. C. (2023). Religion, sexuality politics, and the transformation of Latin
##American electorates. British Journal of Political Science, 54, 816-835.
##https://doi.org/10.1017/S0007123423000613
##Replication data: Harvard Dataverse doi:10.7910/DVN/7GIJPI, CC0 1.0, no restricted files.
##Files read (from replication.zip): replication/{Brazil,Chile,Peru}_results_final.csv (Qualtrics
##exports with numeric codes for questions and level TEXT for the conjoint attributes). The
##deposit's Qualtrics Questionnaire {Brazil,Chile,Peru}.docx give question wording and codes;
##9_analyze_conjoint.R (read as text, not run) gives the authors' sample filter.
##Usage: Rscript smith_2023.R <raw dir holding replication/> <output dir>
##
##Online surveys recruited through Facebook ads stratified by age, sex and region, 7-22 May 2019.
##THREE TABLES, one per country: separate fieldings in Portuguese (Brazil) and Spanish (Chile,
##Peru), with different level text, and the authors estimate every effect country by country:
##  smith_2023_candidates_brazil 1,857 respondents (federal deputy candidates)
##  smith_2023_candidates_chile  3,810 (diputado)       smith_2023_candidates_peru 3,800
##Sample: the authors' eligibility conditions are kept (IP located in the country, p1 consent, p2
##citizen, p3 resident, p4 aged 18+), and every eligible respondent with at least one answered task is
##kept, finished or not (IRW conjoint ruling, Ben 2026-11-10: no author sample exclusions); unanswered
##tasks are omitted. The authors' analysis sample (9_analyze_conjoint.R) also excludes respondents who did
##not finish the survey; reproduce it with cov_finished == 1 (the article's valid N: 1,817 / 3,732 /
##3,698, all of whom answered all three tasks). Added: 40 / 78 / 102 unfinished respondents.
##Design: 3 tasks of two candidates (Candidato A/B, C/D, E/F -> task 1-3, profile 1-2), 9 binary
##attributes each independently randomized: sex, age (39/56), education, occupation, political
##experience (former mayor / none), religion (Catholic/Evangelical), abortion policy (keep current
##laws / complete ban: full legalization deliberately not offered), economic policy, security
##policy. Outcome: choice = "Em qual dos candidatos você votaria?" / "¿Por cuál de los candidatos
##votaría usted?" (Candidato A/B), forced, no opt-out. trial_order = source `order`: "policy" =
##the three policy attributes shown first, "traits" = shown last (article: "randomly shown first
##or last"); attribute order within each block was also randomized but is not recorded.
##Covariates (Qualtrics codes; labels in the country's questionnaire .docx; the categories of
##education, religion and party differ by country): cov_age = p4 code + 16 (code 2 = 18,
##83 = 99; questionnaire p4 "Menos de 18 (1) ... 99 (83)"); cov_gender (p6: Masculino (1) /
##Feminino or Femenino (2) -> male / female); cov_education (p7, as the questionnaire's answer
##text in Portuguese or Spanish: Brazil codes 11-20 "Nenhum" ... "Mestrado / doutorado /
##pós-graduação", Chile and Peru codes 11, 30-38 "Ninguna" ... "Postgrado, master, o
##doctorado"; the deposit's {country}_results_final_text.csv export agrees on every row);
##cov_religion (p9);
##cov_religious_attendance (p10); cov_political_interest (p11); cov_left_right 1 = left .. 10 =
##right (p12); cov_abortion_position 1 = legalize 2 = keep current laws 3 = complete ban (p14);
##cov_economy_position 1 = stimulate private initiative 2 = increase the state's role (p15);
##cov_security_position 1 = more prisons and harsher sentences 2 = social development (p16);
##cov_party_sympathy 1 = yes 2 = no (p17); cov_finished (Qualtrics Finished, 1/0). Covariates a respondent
##did not reach are NA.
##Spot check: among tasks whose two candidates differ on abortion, a choice ~ agree-with-own-
##position LPM gives 0.41 (Brazil), 0.49 (Chile), 0.32 (Peru), the article's Figure 5 values.
##Dropped: Qualtrics ResponseId (re-keyed to integers in file order), dates, duration, IP country,
##ethnicity/race (p8), region/state (p5), priority ranking (p13), party named (p18), 2017/2018
##vote (p19-p20), raffle question (p24), page-timing columns (i2*).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c(sex = "sex", age = "age", edu = "education", occ = "occupation", exp = "experience", rel = "religion",
           abo = "abortion_policy", eco = "economic_policy", seg = "security_policy")
edu <- list(Brazil = setNames(c("Nenhum", "Ensino fundamental incompleto", "Ensino fundamental completo", "Ensino médio incompleto",
                                "Ensino médio completo", "Técnico / Tecnológico incompleto", "Técnico / Tecnológico completo",
                                "Superior incompleto", "Superior completo", "Mestrado / doutorado / pós-graduação"), 11:20),
            Chile = setNames(c("Ninguna", "Básica incompleta", "Básica completa", "Media incompleta", "Media completa",
                               "Superior no universitaria incompleta", "Superior no universitaria completa", "Universitaria incompleta",
                               "Universitaria completa", "Postgrado, master, o doctorado"), c(11, 30:38)))
edu$Peru <- edu$Chile
cv <- c(p9 = "religion", p10 = "religious_attendance", p11 = "political_interest", p12 = "left_right",
        p14 = "abortion_position", p15 = "economy_position", p16 = "security_position", p17 = "party_sympathy")
for (cc in c("Brazil", "Chile", "Peru")) {
  x <- read.csv(file.path(raw, "replication", paste0(cc, "_results_final.csv")), as.is = TRUE, encoding = "UTF-8")[-(1:2), ]
  if (cc != "Brazil") names(x)[which(names(x) %in% c("p2", "p2.1"))] <- c("p1", "p2")  # duplicate 'p2' header (authors' fix)
  ans <- (x$p21 %in% 1:2) + (x$p22 %in% 1:2) + (x$p23 %in% 1:2)
  x <- x[x$ip_country == cc & x$p1 == 1 & x$p2 == 1 & x$p3 == 1 & as.numeric(x$p4) > 1 & ans > 0, ]
  stopifnot(all(x$Finished %in% 0:1), all(x$p21[x$Finished == 1] %in% 1:2), all(x$p22[x$Finished == 1] %in% 1:2),
            all(x$p23[x$Finished == 1] %in% 1:2),
            sum(x$Finished == 1) == c(Brazil = 1817, Chile = 3732, Peru = 3698)[[cc]], nrow(x) == c(Brazil = 1857, Chile = 3810, Peru = 3800)[[cc]])
  x$rid <- seq_len(nrow(x))
  res <- list()
  for (t in 1:3) for (p in 1:2) {
    l <- letters[2 * (t - 1) + p]; ch <- suppressWarnings(as.integer(x[[paste0("p2", t)]])); stopifnot(all(ch %in% c(1:2, NA)))
    d <- data.table(id = x$rid, task = t, profile = p, choice = as.integer(ch == p))
    for (v in names(attrs)) { lv <- trimws(x[[paste0(v, "_", l)]]); d[, paste0("attr_", attrs[[v]]) := lv] }
    d <- d[!is.na(ch)]
    for (v in names(attrs)) stopifnot(all(d[[paste0("attr_", attrs[[v]])]] != ""))
    res[[length(res) + 1]] <- d
  }
  d <- rbindlist(res)
  stopifnot(all(x$p6[x$Finished == 1] %in% 1:2), all(x$p6 %in% c("1", "2", "")), all(x$p7 %in% c(names(edu[[cc]]), "")))
  r <- data.table(id = x$rid, trial_order = x$order, cov_age = as.integer(x$p4) + 16L, cov_gender = c("male", "female")[suppressWarnings(as.integer(x$p6))],
                  cov_education = unname(edu[[cc]][x$p7]))
  for (v in names(cv)) r[, paste0("cov_", cv[[v]]) := suppressWarnings(as.integer(x[[v]]))]
  r[, cov_finished := as.integer(x$Finished)]
  stopifnot(all(r$trial_order %in% c("policy", "traits")), all(r$cov_age >= 18), !anyNA(r$cov_gender[r$cov_finished == 1]))
  d <- merge(d, r, by = "id")
  setcolorder(d, c("id", "task", "profile", "choice", "trial_order"))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(attr_sex)] == 2)
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("smith_2023_candidates_", tolower(cc), ".csv")))
}
