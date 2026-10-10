##Car-emission policy-instrument conjoint (Switzerland, December 2017) from
##Huber, R. A., Wicki, M. L., & Bernauer, T. (2020). Public support for environmental policy
##depends on beliefs concerning effectiveness, intrusiveness, and fairness. Environmental
##Politics, 29(4), 649-673. https://doi.org/10.1080/09644016.2019.1629171
##(the Dataverse record gives 10.1080/09644016.2019.1628872, which is not this article).
##Replication data: Harvard Dataverse doi:10.7910/DVN/2V2LGK, CC0 1.0, no restricted files.
##Files read: df_conj_out1.csv (the first conjoint), ri.csv (respondent information). Also read
##as text: README.txt, beliefs_conj1.R, beliefs_descriptives.R, beliefs_regression1.R and
##appendix.pdf (Tables A2-A4: instrument descriptions in English and German, conjoint attributes;
##Figure A3 example task).
##Usage: Rscript huber_2020.R <raw dir> <output dir>
##
##Same IPSOS survey of 2,034 Swiss residents (8-21 December 2017) as wicki_2020_vehicle_emissions
##(that table is the survey's second conjoint, df_conj_out2, with policy packages); this is the
##FIRST conjoint, a separate experiment with its own attributes. 5 tasks (round) x 2 proposals:
##profile 1 = "Initiative" (policy A), profile 2 = "Gegenentwurf"/counter-proposal (policy B), as
##in the authors' script; both recorded.
##Two attributes (appendix Table A4): attr_policy = the instrument (Car tax / Environmental bonus /
##Car ban / Parking spaces / Information campaign / Road pricing / Tightening of energy labels,
##the Table A4 English names; each was shown with a paragraph describing it, Tables A2-A3) and
##attr_implementation_year ("Implementation until ..." 2025-2045). The paragraph wording depended
##on a between-respondent frame, trial_frame: "EV" (promote switching to electric vehicles) or
##"Emission reduction" (switch from highly emitting to low-emission cars) (ri.csv `frame`).
##8.9% of tasks show the same instrument in both proposals (kept as fielded).
##Outcomes (appendix Figure A3 note: the respondent "would have supported road pricing, rejected
##the car tax, and subsequently chosen the initiative vis-a-vis the counter-proposal"):
##  rating = support (1) or reject (0) each proposal: the authors' `rate` (= rate_A/rate_B,
##    _1 = support, _2 = reject; 0/1 judgement of each profile, not a pick, so a rating).
##  choice = the proposal chosen between the two; forced, exactly one per task (checked).
##Wording is paraphrased (the article was not retrieved; the screenshot is an image).
##Respondents saw German, French or Italian (cov_language); labels are the appendix English.
##Level shares are unequal (car ban 16.4% and energy label 15.1% of profiles vs about 13.3% for
##the others; year 2030 22.1% vs 2045 18.2%) although the authors' cjoint models assume a uniform
##design: level weights observed. No restriction documented.
##Covariates (ri.csv, text as stored): cov_gender, cov_age (years), cov_language (de/fr/it),
##cov_region (region7, Latin-1 decoded), cov_urban_rural (uar), cov_education (the authors' four
##groups, as stored), cov_lr (left-right 0-10; -99 -> NA), and the respondent's beliefs about
##each of the seven instruments, asked separately from the conjoint (appendix/script labels):
##cov_<instrument>_effective (1 = Very effective .. 7 = Very ineffective), _intrusive (1 = Not at
##all intrusive .. 7 = Very intrusive), _fair (1 = Very unfair .. 7 = Very fair), _support
##(1 = Fully oppose .. 7 = Fully support); instruments p1..p7 = car tax, env. bonus, car ban,
##parking spaces, information campaign, road pricing, energy label (the authors' Attrib1 _k <->
##pk mapping in beliefs_conj1.R). Dropped: mp (authors' derived score), the belief items'
##display order (p*_order), the authors' recoded eff/int/fai.
##N: 2,034 respondents, 10,170 tasks (= 20,340 rows), as in the deposit and the sibling article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "df_conj_out1.csv"))
r <- fread(file.path(raw, "ri.csv"))
stopifnot(nrow(s) == 20340L, uniqueN(s$id) == 2034L, nrow(r) == 2034L, !anyDuplicated(r$id), all(s$id %in% r$id),
          s[, .N, .(id, round)][, all(N == 2)], s[, sum(choice), .(id, round)][, all(V1 == 1)])
stopifnot(all(s$rate == as.integer(fifelse(s$policy == "A", s$rate_A, s$rate_B) == "_1")))
pol <- c("Car tax", "Environmental bonus", "Car ban", "Parking spaces", "Information campaign", "Road pricing",
         "Tightening of energy labels")
k1 <- as.integer(sub("_", "", s$Attrib1)); k2 <- as.integer(sub("_", "", s$Attrib2))
stopifnot(all(as.integer(substr(s$attrib1_lab, 1, 1)) == k1), all(as.integer(substr(s$attrib2_lab, 1, 1)) == k2))
d <- s[, .(id = as.integer(id), task = as.integer(round), profile = match(policy, c("A", "B")),
           choice = as.integer(choice), rating = as.integer(rate))]
d[, `:=`(attr_policy = pol[k1], attr_implementation_year = as.character(c(2025, 2030, 2035, 2040, 2045))[k2])]
fr <- gsub("\\s+", " ", r$frame)
stopifnot(all(fr %in% c("EV Frame", "Emission Reduction Frame")))
inst <- c("car_tax", "env_bonus", "car_ban", "parking", "info_campaign", "road_pricing", "energy_label")
cv <- r[, .(id = as.integer(id), trial_frame = c("EV Frame" = "EV", "Emission Reduction Frame" = "Emission reduction")[fr],
            cov_gender = gender, cov_age = as.integer(age), cov_language = language, cov_region = iconv(region7, "latin1", "UTF-8"),
            cov_urban_rural = uar, cov_education = edu, cov_lr = fifelse(leftright == -99L, NA_integer_, as.integer(leftright)))]
for (i in 1:7) {
  q <- c(ef = "effective", "in" = "intrusive", fa = "fair", su = "support")
  for (j in names(q)) cv[, paste0("cov_", inst[i], "_", q[[j]]) := as.integer(r[[paste0("p", i, "_", j)]])]
}
stopifnot(all(cv$cov_gender %in% c("female", "male")))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", "attr_policy", "attr_implementation_year", "trial_frame"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "huber_2020_car_policy_instruments.csv"))
