##Party-platform conjoint (Norway) from
##Binningsbø, H. M., Dyrstad, K., & Finseraas, H. (2025). How does public opinion respond to
##government injustices against historically discriminated minorities? Evidence from Norway.
##British Journal of Political Science, 55, e91. https://doi.org/10.1017/S0007123425100537
##Replication data: Harvard Dataverse doi:10.7910/DVN/DDIVVK, CC0 1.0, no restricted files.
##File read: replicationdata_final.dta (Dataverse "original format" download; Norwegian Stata
##value labels). Also read as text: replication.do (authors' conjoint block, L536-590) and
##"supplementary materials.pdf" (appendix C sampling, D conjoint description, H pre-analysis plan).
##Usage: Rscript binningsbo_2025.R <raw dir> <output dir>
##
##3,317 respondents of Kantar Norway's online access panel (May-June 2023; oversample of 139
##municipalities with a high share of Sami/Kven/Forest Finn population), each choosing between
##Parti A (profile 1) and Parti B (profile 2) in 5 tasks. Six policy attributes, levels as the
##Norwegian value labels of dimSkatt/dimFlykt/dimMiljo/dimMino/dimUkra/dimDist (the text shown
##in the Dimensions grid; the conjointAB* variable label is the grid template "Parti A Parti B
##Partiets skattepolitikk {#dimSkattA1}{#dimSkattB1} Partiets flyktnin...", so rows were in a
##fixed order): tax, refugee, environmental, minority (indigenous rights; 5 levels, English in
##appendix D), Ukraine and district (municipality merger) policy.
##Outcome: choice = the conjointAB<k> answer (1 = Parti A, 2 = Parti B). The deposit does not
##hold the question wording; the article describes it as vote choice for a party (paraphrase in
##the design record). No opt-out was offered; 9996 (not answered) occurs in 106-137 tasks per
##round and those tasks are omitted (rows with no outcome), as the authors' code does.
##REPEATED TASK: task 5 shows task 1 again with the profiles swapped (dimKombPartA5 ==
##dimKombPartB1 and B5 == A1 for every respondent; checked below) -> trial_repeat_of = 1 on task 5.
##The authors pool all 5 rounds in their cregg-style `conjoint` models.
##No randomization restriction is documented; all 360 attribute combinations occur and level
##shares are near-equal. 17 tasks show two identical profiles (kept as fielded).
##Covariates: cov_age (years, "Hva er din alder?"); cov_age_group (stdalder value labels);
##cov_gender from the authors' `male` (RECODE of _v62 "Registrer kjønn"; 1 -> male, 0 -> female;
##the raw item is not deposited); cov_vote_2021 (_v74 "Stemte du ved sist Stortingsvalg..." value
##label text: a vote, not party identification; "Ubesvart/Vil ikke oppgi parti" -> NA);
##cov_attention_pass (testPASSED: Riktig = 1, Feil = 0; the PAP's "extremely + very interested"
##check); cov_survey_weight (Vekt, Kantar weight; the authors do not weight); cov_field_period
##(felt value label: "Til og med 1.juni" = before the TRC report, "Etter 1.juni" = after);
##cov_post_trc_demo (authors' 0 = before report, 1 = after report before demonstrations,
##2 = after demonstrations); cov_oversampled_munic (1 = oversampled high-share municipality
##stratum, Sample == 1); cov_minority_group (Gruppe_1/2/3: which minority the respondent was
##randomized to answer questions about: Samer/Kvener/norskfinner/Skogfinner).
##Dropped: the minority-attitude batteries and derived indices, the free-text ethnic background
##(_v1), interview timestamps, page timings, the authors' recodes and interactions.
##N: 3,317 respondents in the deposit (felt 1,743 / 1,574); the article reports 1,552 + 1,410 =
##2,962 "native Norwegian" respondents, with no native-born flag in the deposit. Not resolved.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "replicationdata_final.dta"))
stopifnot(all(s$dimKombPartA5 == s$dimKombPartB1), all(s$dimKombPartB5 == s$dimKombPartA1))
lab <- function(x) { l <- attr(x, "labels"); r <- names(l)[match(as.numeric(x), l)]; stopifnot(!anyNA(r)); trimws(r) }
dims <- c(tax = "dimSkatt", refugees = "dimFlykt", environment = "dimMiljo", minority_rights = "dimMino",
          ukraine = "dimUkra", municipalities = "dimDist")
nolab <- function(x, drop) { l <- attr(x, "labels"); r <- trimws(names(l)[match(as.numeric(x), l)]); r[r %in% drop] <- NA; r }
cov <- data.table(id = as.integer(s$Respondent_Serial), cov_age = as.integer(s$age), cov_age_group = lab(s$stdalder),
                  cov_gender = fifelse(s$male == 1, "male", "female"),
                  cov_vote_2021 = nolab(s$`_v74`, "Ubesvart/Vil ikke oppgi parti"),
                  cov_attention_pass = c(1L, 0L)[as.integer(s$testPASSED)],
                  cov_survey_weight = as.numeric(s$Vekt), cov_field_period = lab(s$felt),
                  cov_post_trc_demo = as.integer(s$post_trc_demo), cov_oversampled_munic = as.integer(s$Sample == 1),
                  cov_minority_group = c("Samer", "Kvener/norskfinner", "Skogfinner")[as.integer(s$Gruppe_2) + 2L * as.integer(s$Gruppe_3) + 1L])
stopifnot(all(s$Gruppe_1 + s$Gruppe_2 + s$Gruppe_3 == 1), all(s$testPASSED %in% 1:2), all(s$male %in% 0:1))
L <- list()
for (k in 1:5) {
  ch <- as.numeric(s[[paste0("conjointAB", k)]])
  for (p in 1:2) {
    side <- c("A", "B")[p]
    x <- data.table(id = as.integer(s$Respondent_Serial), task = k, profile = p, ans = ch)
    for (n in names(dims)) x[, paste0("attr_", n) := lab(s[[paste0(dims[[n]], side, k)]])]
    L[[length(L) + 1]] <- x
  }
}
d <- rbindlist(L)
stopifnot(all(d$ans %in% c(1, 2, 9996)))
d <- d[ans != 9996]
d[, choice := as.integer(ans == profile)][, ans := NULL]
d[, trial_repeat_of := fifelse(task == 5L, 1L, NA_integer_)]
d <- merge(d, cov, by = "id")
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "binningsbo_2025_party_platforms.csv"))
