##High-level radioactive waste disposal site conjoint (Japan) from
##Hayashi, R., Asano, T., Morikawa, S., & Komatsuzaki, S. (2024). Public service motivation and
##not-in-my-backyard: The case of high-level radioactive waste disposal sites in Japan. International
##Public Management Journal, 26(6), 948-971. https://doi.org/10.1080/10967494.2024.2322150
##Replication data: Harvard Dataverse doi:10.7910/DVN/24TY4T, CC0 1.0. Files read:
##HLWconjoint20210330.tab (Dataverse "original format", CSV) and HLWconjoint20210330_codebook.xlsx
##(English codebook: question wording, attribute level text, covariate value labels). The authors'
##analysis scripts 01-05_*.R were read as text, not run.
##Usage: Rscript hayashi_2024.R <dir holding the two files> <output dir>
##
##1,800 respondents (source `no` 1-1800; urban/rural x three groups, 300 each, codebook `group`),
##4 tasks (`time`) x 2 hypothetical construction plans (`rl`: 1 = Plan A, 2 = Plan B; recorded),
##6 attributes, all shown in every task. The survey was in Japanese; only the English codebook
##survives, so attribute and question text are the codebook's English (translated).
##Outcomes (both asked about the same pair):
##  choice = hlw_fsu, "Between Construction Plan A and Construction Plan B, which plan would you
##           accept? Please select one of them." Forced, no opt-out. The source stores the chosen
##           plan (1/2) on both rows; choice = (hlw_fsu == rl), as in the authors' code.
##  rating = hlw_su, "To what extent are you willing to accept both Construction Plan A and
##           Construction Plan B? ... 1 Absolutely not willing to accept it ... 7 Very strongly
##           willing to accept it", per plan; higher = more willing (raw).
##Attributes (codebook names; the codebook gives no attribute row labels beyond these): distance,
##political (stated purpose), social (local opinion split), administrative (benefit offered),
##population, average income. Population levels are stored as in the codebook ("19000"); the
##authors' plotting code writes "19,000"; the displayed Japanese text is not deposited.
##Attribute order: zoku_* give the display row (1-6) of each attribute; each row is a permutation of
##1-6 and constant within respondent -> attrpos_* and attr_order = respondent.
##Restrictions/weights: no source documents either; all level combinations occur; level shares are
##near-equal.
##Covariates: cov_gender (sex: 1 Male, 2 Female; codebook), cov_age (age, years, as recorded: 112
##rows (14 respondents) have ages 3-17 in a sample of adults; kept, flagged), cov_education (ac_ba,
##codebook text), cov_group (sampling group, codebook text verbatim incl. its typos "are"),
##cov_sc (codebook: "Thermal power station route (1), Nuclear power station (2), Self-Defence Force
##base (3)"; constant per respondent; its role is not documented, kept as codes); further covariates
##keep the source codes, labels in the codebook: mar, job, y_res, pre (prefecture), sup1-2, dev1-2,
##imp1-2, q3_1-16, q4_1_1, q4_2_1, em1-4, risk_g, risk_s1-6, psm01-16, tr1-4, inc (13 = "I do not
##want to answer"). Dropped: muni (municipality of residence; fine geography, many small towns).
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "HLWconjoint20210330.tab"), encoding = "UTF-8")
stopifnot(nrow(s) == 14400, uniqueN(s$no) == 1800, s[, .N, .(no, time)][, all(N == 2)],
          s[, uniqueN(rl), .(no, time)][, all(V1 == 2)], s[, uniqueN(hlw_fsu), .(no, time)][, all(V1 == 1)])
lab <- list(
  distance = c("less than 1 km", "1–5 km", "5–20 km", "20 km or more"),
  political = c("To create jobs in the town", "To improve the town’s administrative services",
                "To enhance the town’s economy", "Necessity for society"),
  social = c("70% agreed, 30% disagreed", "50% agreed, 50% disagreed", "30% agreed, 70% disagreed"),
  administrative = c("None", "Improvement of childbirth and childcare benefits",
                     "Improvement of medical and care services for the elderly",
                     "Reduction of public-school fees and expansion of school curriculum",
                     "Improvement of public facilities such as community centers and libraries",
                     "Reduction of water rates"),
  population = c("19000", "20000", "21000"),
  income = c("3.8 million yen", "4 million yen", "4.2 million yen"))
src <- c(distance = "dis", political = "pol", social = "so", administrative = "ad", population = "pop", income = "inc")
d <- s[, .(id = as.integer(no), task = as.integer(time), profile = as.integer(rl),
           choice = as.integer(hlw_fsu == rl), rating = as.integer(hlw_su))]
for (k in names(lab)) {
  v <- s[[paste0("hlw_", src[[k]])]]; stopifnot(all(v %in% seq_along(lab[[k]])))
  d[, paste0("attr_", k) := lab[[k]][v]]
}
for (k in names(lab)) d[, paste0("attrpos_", k) := as.integer(s[[paste0("zoku_", src[[k]])]])]
stopifnot(s[, uniqueN(paste(zoku_dis, zoku_pol, zoku_so, zoku_ad, zoku_pop, zoku_inc)), no][, all(V1 == 1)])
stopifnot(all(s$sex %in% 1:2), all(s$ac_ba %in% 1:7), all(s$group %in% 1:6))
d[, cov_gender := c("male", "female")[s$sex]]
d[, cov_age := as.integer(s$age)]
d[, cov_education := c("Elementary school", "Junior high school", "High school", "Junior college", "University",
                       "Graduate school", "None of the above")[s$ac_ba]]
d[, cov_group := c("Urban area (Group A)", "Urban area (Group B)", "Urban are (Group C)", "Rural are (Group A)",
                   "Rural are (Group B)", "Rural are (Group C)")[s$group]]
keep <- c("sc", "mar", "job", "y_res", "pre", "sup1", "sup2", "dev1", "imp1", "dev2", "imp2", paste0("q3_", 1:16),
          "q4_1_1", "q4_2_1", paste0("em", 1:4), "risk_g", paste0("risk_s", 1:6), sprintf("psm%02d", 1:16),
          paste0("tr", 1:4), "inc")
for (v in keep) d[, paste0("cov_", v) := s[[v]]]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d$rating), all(d$rating %in% 1:7))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hayashi_2024_nuclear_waste_site.csv"))
