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
##  smith_2023_candidates_brazil 1,817 respondents (federal deputy candidates)
##  smith_2023_candidates_chile  3,732 (diputado)       smith_2023_candidates_peru 3,698
##N = the article's valid N in each country, after the authors' filter (kept here): IP located in
##the country, consent, citizen, resident, aged 18+, finished the survey.
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
##cov_party_sympathy 1 = yes 2 = no (p17).
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
  x <- x[x$ip_country == cc & x$p1 == 1 & x$p2 == 1 & x$p3 == 1 & as.numeric(x$p4) > 1 & x$Finished == 1, ]
  x$rid <- seq_len(nrow(x))
  res <- list()
  for (t in 1:3) for (p in 1:2) {
    l <- letters[2 * (t - 1) + p]; ch <- as.integer(x[[paste0("p2", t)]]); stopifnot(all(ch %in% 1:2))
    d <- data.table(id = x$rid, task = t, profile = p, choice = as.integer(ch == p))
    for (v in names(attrs)) { lv <- trimws(x[[paste0(v, "_", l)]]); stopifnot(all(lv != "")); d[, paste0("attr_", attrs[[v]]) := lv] }
    res[[length(res) + 1]] <- d
  }
  d <- rbindlist(res)
  stopifnot(all(x$p6 %in% 1:2), all(x$p7 %in% c(names(edu[[cc]]), "")))
  r <- data.table(id = x$rid, trial_order = x$order, cov_age = as.integer(x$p4) + 16L, cov_gender = c("male", "female")[as.integer(x$p6)],
                  cov_education = unname(edu[[cc]][x$p7]))
  for (v in names(cv)) r[, paste0("cov_", cv[[v]]) := as.integer(x[[v]])]
  stopifnot(all(r$trial_order %in% c("policy", "traits")), all(r$cov_age >= 18), !anyNA(r$cov_gender))
  d <- merge(d, r, by = "id")
  setcolorder(d, c("id", "task", "profile", "choice", "trial_order"))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(attr_sex)] == 2)
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("smith_2023_candidates_", tolower(cc), ".csv")))
}
