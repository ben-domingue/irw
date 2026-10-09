##COVID-19 vaccination conjoints (Austria and Italy) from
##Stamm, T. A., Partheymüller, J., Mosor, E., Ritschl, V., Kritzinger, S., Alunno, A., &
##Eberl, J.-M. (2023). Determinants of COVID-19 vaccine fatigue. Nature Medicine, 29,
##1164-1171. https://doi.org/10.1038/s41591-023-02282-y (open access, CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/3R2CMT, CC0 1.0, no restricted files.
##Files read: Data_AT_Pub.xlsx, Data_IT_Pub.xlsx (one row per respondent), Experiment1.xlsx,
##Experiment2.xlsx (profile id -> level codes). Codebook_2023_01_31.docx and the authors'
##Conjoint_2_Pub_2023_01_31.R read as text. Level text and question wording: the article's
##Supplementary Files 3 and 4 (English version, Tables S3.1 and S4.1; German S3.2/S4.2 and
##Italian S3.3/S4.3 are the versions respondents saw).
##Usage: Rscript stamm_2023.R <raw dir> <output dir>
##
##6,357 respondents aged 14+ (Austria 3,187, Italy 3,170; Marketagent online access panel,
##population quotas, 19 July - 8 August 2022), matching the article. TWO experiments with
##different attribute sets -> two tables. Countries are pooled in each (the authors rbind AT
##and IT and estimate with by = ~Country; the English design text is shared), with cov_country.
##In each experiment respondents saw 2 tasks of 2 text scenarios side by side (Scenario /
##Media report 1 = profile 1 and 2 = profile 2), chose one and rated both 0-10. Supplement:
##"Levels were randomly assigned with equal probabilities ... with all combinations being
##plausible"; the Experiment*.xlsx files list the full factorial (768 and 384 profiles).
##stamm_2023_vaccine_campaign (experiment 1, "hypothetical vaccination campaign"): profiles
##Q18A1/Q18A2 (task 1) and Q21A1/Q21A2 (task 2), ratings Q20A1/A2 and Q23A1/A2, choice from
##Ex1A/Ex1B (the preferred profile id; Ex1A0/Ex1B0 the other; verified to be exactly the two
##profiles shown). Vignette: "Virus variants are emerging, <variant> and infection rates are
##increasing. ... Available vaccines: <vaccines> Versions of the vaccines adapted to Omicron
##are <omicron>. <incentive> <Name, age>: "<motivation>. That's why I'm going to get
##vaccinated. And what's your plan for the fall?"". Attributes (code -> Table S3.1 English
##text): attr_variant, attr_vaccines, attr_omicron_adapted, attr_incentive, attr_motivation,
##plus the testimonial: attr_testimonial_gender (Gender1-4, codebook "Gender of the
##testimonials", one per profile in display order) and attr_testimonial_age (Target:
##"same age group as respondent" / "different age group from respondent"). The testimonial
##was shown as a first name and age (e.g. "Maria (49 years)"); the name and the age drawn
##were NOT saved, only the gender and the age-group condition, so these two columns hold the
##design condition, not displayed text.
##  choice: "In which of these two scenarios does the vaccination call appeal to you more? If
##    you find neither or both calls equally appealing, please decide spontaneously." Forced.
##  rating: "On a scale of 0 to 10, how likely is it that you would heed these calls for
##    vaccination and get vaccinated against COVID-19?" 0 "would definitely not get
##    vaccinated" .. 10 "would definitely get vaccinated".
##stamm_2023_vaccine_media (experiment 2, "media communication"): profiles Q27A1/A2 (task 1),
##Q30A1/A2 (task 2), ratings Q29A1/A2, Q32A1/A2, choice from Ex2A/Ex2B. Report text: "TV
##discussion: The talk show on the topic "Should we vaccinate ourselves (again)?" featured
##guests <consensus>. Celebrity Newsflash: <celebrity> Science: A new study has investigated
##the incidence of Long Covid. According to the study, <long covid> suffer from Long Covid
##symptoms ... Current Corona Rules: A valid vaccination certificate will <green pass>.
##Mandatory vaccination: <mandate>". Attributes: attr_consensus, attr_celebrity,
##attr_long_covid, attr_green_pass, attr_mandate (Table S4.1 English text, verbatim including
##its "per cent"/"percent" inconsistency).
##  choice: "Based on which media report would you be more likely to trust vaccination against
##    COVID-19? Please spontaneously choose one if neither or both media reports give an
##    equally trustworthy impression." Forced.
##  rating: "On a scale of 0 to 10, how likely is it that you would get vaccinated against
##    COVID-19 given these media reports?" 0 .. 10 as above.
##Covariates (codebook): cov_country (AT/IT), cov_gender (Q1: female, male; "other" kept as
##"other" although the codebook says it "includes non-binary and people who chose not to
##answer"), cov_age_group (Q3 codebook text "14 to 24 years" .. "65+ years"), cov_education
##(Edu as stored: low / medium / high; 45 missing), cov_vaccinated (Vaccinated: "Not", "1 or
##2", ">=3" doses; codebook), cov_trust_media / _parliament / _healthcare / _government /
##_science / _schools / _pharma (Q15A1-7, 0 "no trust at all" .. 10 "very much trust"),
##cov_feel_hopeful / _worried / _angry / _tired / _frustrated (Q16A1-5, 0 "not at all" .. 10
##"very much"), cov_vacc_att_1..11 (Q13A1-11, 1 "fully agree" .. 5 "fully disagree"; items in
##the codebook, e.g. 1 "I am concerned about unanticipated side effects of the vaccination.").
##In all Q13/Q15/Q16 items 88 = "I do not know" is kept as stored and 99 (missing) -> NA.
##Spot check: OLS of the media-table rating on its attributes among the triple vaccinated
##reproduces the article's AMCEs (celebrity vaccinated 0.169 and falls ill 0.134 vs refuses;
##dissensus physicians -0.161 and scientists -0.132 [article -0.133] vs scientists' consensus).
##Dropped: U0 (panel respondent number, re-keyed to integers), Attitude (the authors' derived
##pro/anti grouping), Vaccinated1 (numeric duplicate of Vaccinated). No survey weight deposited.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- rbind(as.data.table(read_excel(file.path(raw, "Data_AT_Pub.xlsx"))),
           as.data.table(read_excel(file.path(raw, "Data_IT_Pub.xlsx"))))
stopifnot(nrow(x) == 6357, uniqueN(x$U0) == 6357)
x[, id := match(U0, sort(U0))]
e1 <- as.data.table(read_excel(file.path(raw, "Experiment1.xlsx")))
e2 <- as.data.table(read_excel(file.path(raw, "Experiment2.xlsx")))
stopifnot(nrow(e1) == 768, uniqueN(e1$Profile) == 768, nrow(e2) == 384, uniqueN(e2$Profile) == 384)
mp <- function(v, m) { r <- unname(m[as.character(v)]); stopifnot(!anyNA(r)); r }
## respondent covariates
na99 <- function(v) { v <- as.integer(v); v[v == 99L] <- NA_integer_; v }
cv <- x[, .(id, cov_country = country, cov_gender = mp(Q1, c(female = "female", male = "male", other = "other")),
            cov_age_group = mp(Q3, c(`1` = "14 to 24 years", `2` = "25 to 34 years", `3` = "35 to 44 years",
                                     `4` = "45 to 54 years", `5` = "55 to 64 years", `6` = "65+ years")),
            cov_education = Edu,
            cov_vaccinated = mp(Vaccinated, c(Not = "Not", One_or_two = "1 or 2", Three_or_more = ">=3")))]
tr <- c("media", "parliament", "healthcare", "government", "science", "schools", "pharma")
for (i in 1:7) cv[, paste0("cov_trust_", tr[i]) := na99(x[[paste0("Q15A", i)]])]
fe <- c("hopeful", "worried", "angry", "tired", "frustrated")
for (i in 1:5) cv[, paste0("cov_feel_", fe[i]) := na99(x[[paste0("Q16A", i)]])]
for (i in 1:11) cv[, paste0("cov_vacc_att_", i) := na99(x[[paste0("Q13A", i)]])]
## stack the two tasks x two profiles of an experiment
stackx <- function(prof, rate, pref, gend = NULL) {
  rbindlist(lapply(1:2, function(t) rbindlist(lapply(1:2, function(p) {
    k <- (t - 1) * 2 + p
    d <- x[, .(id, task = t, profile = p, pid = as.integer(get(prof[k])), rating = as.integer(get(rate[k])),
               pref = as.integer(get(pref[t])))]
    if (!is.null(gend)) d[, g := x[[gend[k]]]]
    d
  }))))
}
## ---- experiment 1
d <- stackx(c("Q18A1", "Q18A2", "Q21A1", "Q21A2"), c("Q20A1", "Q20A2", "Q23A1", "Q23A2"), c("Ex1A", "Ex1B"),
            paste0("Gender", 1:4))
d[, choice := as.integer(pid == pref)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 0:10))
p <- e1[match(d$pid, e1$Profile)]
d[, `:=`(attr_variant = mp(p$Variante, c(Decline = "which are less dangerous than the current virus variant.",
                                          `No change` = "similar to the current virus variant.",
                                          Escalation = "more dangerous than the current virus variant.")),
         attr_vaccines = mp(p$Vacc, c(mRNA_only = "mRNA vaccines: BioNtech-Pfizer, Moderna",
                                      `mRNA+Inactive` = "mRNA vaccines: BioNtech-Pfizer, Moderna; Inactivated vaccines: Novavax, Valneva")),
         attr_omicron_adapted = mp(p$Omic, c(adap = "available", not_adap = "not available")),
         attr_incentive = mp(p$Incen, c(Free = "The vaccination is free of charge.",
                                        Not_free = "The vaccination costs 20 Euros.",
                                        Voucher = "For the vaccination, you will receive a shopping voucher for 500 Euros as an expense allowance.",
                                        Cash = "For the vaccination you will receive 500 Euros as an expense allowance.")),
         attr_motivation = mp(p$Motiv, c(Econ_Socio = "I don't want any more lockdowns! The shops and restaurants must stay open.",
                                         Econ_Ego = "I can't afford financially to get sick with Long Covid and not be able to work.",
                                         Infect_Ego = "I already had Corona and I don't want to have it again.",
                                         Serious_Ego = "I am afraid of a severe course of the disease. It can affect anyone.",
                                         Serious_Friend = "A friend of mine is a high-risk patient. I want to protect those around me.",
                                         Health_System = "I want to protect the health system. The workload of health workers must be reduced.",
                                         Community = "We should all stick together to overcome the crisis.",
                                         Efficacy_Ego = "We are not powerless in the face of the pandemic. Everyone can do something!")),
         attr_testimonial_gender = mp(d$g, c(female = "female", male = "male")),
         attr_testimonial_age = mp(p$Target, c(Same_age = "same age group as respondent", Diff_age = "different age group from respondent")))]
d[, c("pid", "pref", "g") := NULL]
d <- merge(d, cv, by = "id"); setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "stamm_2023_vaccine_campaign.csv"))
## ---- experiment 2
d <- stackx(c("Q27A1", "Q27A2", "Q30A1", "Q30A2"), c("Q29A1", "Q29A2", "Q32A1", "Q32A2"), c("Ex2A", "Ex2B"))
d[, choice := as.integer(pid == pref)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 0:10))
p <- e2[match(d$pid, e2$Profile)]
d[, `:=`(attr_consensus = mp(p$Cons, c(
  Cons_phys = "Doctors A and B., both physicians. They agreed that the vaccines are safe and effective and called on the population to vaccinate. A representative survey by the Medical Association with more than 10,000 respondents shows that 90% of doctors trust the approved vaccines.",
  Cons_scie = "The immunologist Prof. Dr. E and the infectiologist Prof. Dr. F. Both scientists, agreed that the vaccines are safe and effective and called on the population to vaccinate. A representative survey of the professional societies for immunology and infectiology with over 1000 respondents shows that 99% of the scientists trust the approved vaccines.",
  False_bal_phys = "Doctors C and D. Dr. C was of the opinion that the vaccines were safe and effective and called for vaccination. Dr. D, on the other hand, expressed doubts about the safety and effectiveness of the vaccines and did not recommend vaccination. The debate was controversial and ended without a clear outcome.",
  False_bal_scie = "The infectiologist Prof. Dr. G and the microbiologist Prof. Dr. H. Prof. Dr. G was of the opinion that the vaccines were safe and effective and called for vaccination. Prof. Dr. H, on the other hand, expressed doubts about the safety and effectiveness of the vaccines and did not recommend vaccination. The debate was controversial and ended without a clear result.")),
  attr_celebrity = mp(p$Celeb, c(
  Celeb_ill = "Tennis player J: \"It would have been better to have had me vaccinated earlier\". Due to infiltrations in the lungs after a COVID infection, J is out for the rest of the year.",
  Celeb_not_vacc = "Football player K: \"I stand by the no to vaccination\". K renounces participation in the tournament because entry into the host country is currently not possible without a vaccination certificate.",
  Celeb_vacc = "Singer L: \"I am already vaccinated and appeal to all my fans to do the same\". L is planning a big tour all over Europe in autumn.",
  Celeb_waits = "Actress M: \"I'm waiting for the new vaccines\". The shooting of M's new film is postponed until next year.")),
  attr_long_covid = mp(p$LongCo, c(`1Percent` = "1 percent of the infected", `5Percent` = "5 percent of the infected",
                                   `10Percent` = "10 per cent of the infected", `20Percent` = "20 per cent of those infected")),
  attr_green_pass = mp(p$GreenPa, c(Not_need = "no longer needed.", Needed = "needed again in many areas.")),
  attr_mandate = mp(p$Mand, c(None = "There is no compulsory vaccination.",
                              `50 Years-100 Euro` = "Compulsory vaccination applies from the age of 50 with a fine of 100 euros.",
                              `18 Years-1500 Euro` = "Vaccination is compulsory from the age of 18 with a fine of 1500 euros.")))]
d[, c("pid", "pref") := NULL]
d <- merge(d, cv, by = "id"); setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "stamm_2023_vaccine_media.csv"))
