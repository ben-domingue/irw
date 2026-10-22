##Brazilian candidate conjoint on clientelism and programmatic redistribution from
##Justesen, M. K., Koob, S., & Smid, S. (2025). Clientelism and programmatic redistribution:
##Evidence from a conjoint survey experiment in Brazil. World Development, 195, 107124.
##https://doi.org/10.1016/j.worlddev.2025.107124
##Replication data: Harvard Dataverse doi:10.7910/DVN/S1R72I, CC0 1.0, no restricted files.
##File read: "R Data - Voter Support_1" (an .RData, no file extension in the deposit, holding
##one data frame `conjoint_redistribution_voting_na`, 8,520 rows of respondent x task x profile;
##loaded into its own environment). Read as text: the authors' replication script
##"Script1_Replicationfiles_..._Main.R", which loads this file as
##conjoint_redistribution_voting_na.Rdata.
##Usage: Rscript justesen_2025.R <dir holding the two "R Data - Voter Support" files> <output dir>
##
##1,420 Brazilian respondents, 3 tasks of two candidates each, 8,520 rows, exactly one chosen
##profile in every one of the 4,260 tasks. task, profile and the chosen profile (`selected`) are
##all recorded, as are the attribute row positions.
##The deposit's second file, "R Data - Voter Support_2", is the same 8,520 rows with
##education_st recoded (High / Med / Low instead of three named levels); it is not read, and the
##table carries the first file's education wording.
##
##Design. Six attributes, stored as the authors' English level text while the survey ran in
##Portuguese (the attribute columns carry Portuguese names, e.g.
##"Implementação.de.políticas.locais.rowpos"): political behaviour (attr_clientelism:
##No clientelism / Patronage / Vote buying), attr_gender, attr_age (35 / 45 / 55 years),
##local policy implementation (attr_local_politics: No change / Health clinics / Local CCT, a
##conditional cash transfer), attr_occupation (Lawyer / Manager / Factory Worker) and income-tax
##preferences (attr_tax_preferences: Same tax / Taxing the rich / 1% tax increase for all).
##All six are near-uniform and no combination is missing. The attribute order was randomized
##once per respondent (the six `.rowpos` columns are a permutation of 1-6, identical across that
##respondent's tasks and across the two profiles of a task) and is kept in the attrpos_ columns.
##
##Outcome. choice: which of the two candidates the respondent would vote for (`selected`;
##forced, exactly one per task). The deposit ships no instrument, so the wording is a paraphrase.
##
##Covariates, all as the deposit's own text: cov_gender, cov_income_group, cov_education,
##cov_region, cov_ethnicity ("Branco" or "Other", the deposit's own Portuguese level for White),
##cov_employment, cov_party_id (PT / other party / no party affiliation), cov_bolsa_familia,
##cov_attention_pass (1 = "Attentive", 0 = "Not attentive"), cov_lowest_income,
##cov_poverty, cov_received_transfer, cov_received_meal, cov_received_medicine (the last three
##record clientelist offers the respondent reported receiving) and cov_duration_sec (the whole
##survey). Dropped: the authors' derived `diff_age` / `diff_age_dum` contrasts, the grouping
##columns `respondent` and `respondentIndex`, and the unlabelled Qualtrics item columns
##(Q3_*, Q11_*, Q12_*, Q14_*), which no codebook in the deposit explains.
##Response.ID is an integer with no platform identifier; it is re-keyed 1..n in file order.
##No survey weight ships with the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "R Data - Voter Support_1"), envir = e)
s <- as.data.table(as.data.frame(e$conjoint_redistribution_voting_na, check.names = FALSE))
stopifnot(nrow(s) == 8520L, uniqueN(s$Response.ID) == 1420L)

ROWPOS <- c(clientelism = "Comportamento.politico:.o.candidato(a)....rowpos",
            gender = "Gênero.rowpos", age = "Idade.rowpos",
            local_politics = "Implementação.de.políticas.locais.rowpos",
            occupation = "Ocupação.rowpos",
            tax_preferences = paste0("Preferências.quanto.a.à.tributação.da.renda:",
                                     ".o.candidato(a).defende.com.muita.ênfase....rowpos"))
ROWPOS <- vapply(ROWPOS, function(p) {        # the Portuguese names differ by a dot or two
  hit <- grep(substr(gsub("[^A-Za-zÀ-ÿ]", "", p), 1, 12), gsub("[^A-Za-zÀ-ÿ]", "", names(s)), fixed = TRUE)
  stopifnot(length(hit) == 1L); names(s)[hit]
}, character(1))

d <- data.table(
  id = as.integer(frank(s$Response.ID, ties.method = "dense")),
  task = as.integer(s$task), profile = as.integer(s$profile),
  choice = as.integer(s$selected),
  attr_clientelism = as.character(s$Clientelism),
  attr_gender = as.character(s$Gender),
  attr_age = as.character(s$Age),
  attr_local_politics = as.character(s$Local.politics),
  attr_occupation = as.character(s$Occupation),
  attr_tax_preferences = as.character(s$Tax.preferences))
for (nm in names(ROWPOS))
  set(d, j = paste0("attrpos_", nm), value = as.integer(s[[ROWPOS[[nm]]]]))
d[, `:=`(cov_gender = c(Female = "female", Male = "male")[as.character(s$gender_st)],
         cov_income_group = as.character(s$income_st),
         cov_education = as.character(s$education_st),
         cov_region = as.character(s$region_st),
         cov_ethnicity = as.character(s$ethnic_st),
         cov_employment = as.character(s$employed_st),
         cov_party_id = as.character(s$PT_support_st),
         cov_bolsa_familia = as.character(s$bolsa_st),
         cov_attention_pass = as.integer(s$attention_check_1 == "Attentive"),
         cov_lowest_income = as.character(s$low_income_st),
         cov_poverty = as.character(s$ind_poverty),
         cov_received_transfer = as.character(s$transfer_st),
         cov_received_meal = as.character(s$meal_st),
         cov_received_medicine = as.character(s$med_st),
         cov_duration_sec = suppressWarnings(as.numeric(s$Duration__in_seconds_)))]

stopifnot(d[, .N, .(id, task)][, all(N == 2L)],
          d[, sum(choice), .(id, task)][, all(V1 == 1L)],
          d[, uniqueN(profile), .(id, task)][, all(V1 == 2L)],
          !anyNA(d[, grep("^attr_", names(d)), with = FALSE]),
          d[, all(attr_gender %in% c("Female", "Male"))],
          d[, all(sort(unlist(.SD)) == 1:6), by = .(id, task, profile),
            .SDcols = patterns("^attrpos_")][, all(V1)],
          d[, uniqueN(do.call(paste, .SD)), id, .SDcols = patterns("^attrpos_")][, all(V1 == 1L)],
          d[, uniqueN(id)] == 1420L, nrow(d) == 8520L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "justesen_2025_brazil_clientelism.csv"))
