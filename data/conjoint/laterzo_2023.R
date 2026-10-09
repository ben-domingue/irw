##Candidate conjoint on crime policy from
##Laterzo, I. G. (2023). Progressive ideology and support for punitive crime policy: Evidence
##from Argentina and Brazil. Comparative Political Studies. https://doi.org/10.1177/00104140231193011
##Replication data: Harvard Dataverse doi:10.7910/DVN/18FDDI, CC0 1.0. Files read: arg_clean.rds,
##brazil_clean.rds (one per country), codebook.pdf (Laterzo_ProgressivePunitive_Codebook.pdf, level
##text and covariate codes), READ ME.txt; the authors' R scripts were read as text only.
##Usage: Rscript laterzo_2023.R <dir holding arg_clean.rds and brazil_clean.rds> <output dir>
##
##Online samples in Argentina (1,336 respondents) and Brazil (1,356); each saw 5 pairs of
##candidate profiles with 6 binary attributes (sex; positions on abortion, taxes, same-sex
##marriage, environment, crime/public security) and chose one. The paper pools the two countries
##(laterzo_cps_2023c.RDS, country column; 2,301 respondents after its ideology filter), so one
##table with cov_country. Attribute text: the codebook's English wording of each level (the
##deposit stores short labels, mapped here one-to-one from the codebook rows); the environment
##level names Patagonia in Argentina and the Amazon in Brazil (codebook note). Respondents saw
##Spanish (Argentina) or Portuguese (Brazil); that text is not deposited.
##STRUCTURE IS INFERRED. The files have no task or profile column: README says each respondent has
##10 rows, 5 chosen and 5 not chosen. The rows form 10 blocks of N respondents in identical id
##order: blocks 1-5 are the chosen profiles (chosen = 1) and blocks 6-10 the rejected ones. Task k
##= block k paired with block k+5 (verified: in Argentina the 100 task-pairs with missing levels
##are missing in both blocks of the same pair and nowhere else). Display order of tasks and the
##left/right position of the profiles are NOT recorded: task numbers follow the block order, and
##profile numbering is ARBITRARY and outcome-independent: within each task the two profiles are
##sorted by their concatenated attr_ level text. In the 193 tasks whose two profiles are identical,
##the source-block order would put the chosen one first, so there the order alternates with the
##parity of id + task instead. Do not use profile for position analyses.
##Choice wording not deposited (codebook: "Whether or not a conjoint profile was chosen by the
##respondent"); forced choice (exactly one chosen per task by construction).
##Dropped: 100 Argentine tasks whose levels are missing in the source (both profiles NA).
##Covariates (codes per codebook unless noted): cov_age (years); cov_gender_code (female: 1 = female, 0 = other,
##codebook; not mapped to cov_gender because 0 is "other"); cov_education (edu, country-specific
##codebook answer text); cov_state_code; ideo_* items, vic, vic_fam, crime_gang, safety_neighb,
##assist_effect, pol_04, pol_05, demo_14 (race), demo_06, demo_07, social_pol, toilet keep codes
##(codebook gives the wording). NSE_Score (survey-firm quota score) dropped. Qualtrics ResponseIds
##re-keyed to integers. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv <- list(
  attr_sex = c(Female = "Female", Male = "Male"),
  attr_abortion = c("Oppose Abort" = "In the majority of cases, abortion should be illegal", "Support Abort." = "Abortion should be legal"),
  attr_taxes = c("Reduce Taxes" = "Taxes should be reduced in general", "Increase Taxes on Rich" = "Taxes should be increased on the rich"),
  attr_same_sex_marriage = c("Oppose Same Sex Marriage" = "Same sex marriage should not be permitted",
                             "Support Same Sex Marriage" = "Marriage should be permitted, irrespective of the individuals' gender identities"),
  attr_environment = c("Low Concern for Environ" = "Believes in investment in business and the economy, regardless of its impact on the environment",
                       "High Concern for Environ" = "Believes in investment in \"green\" practices and in the protection of natural resources (for example %s)"),
  attr_crime = c("Social Assistance" = "Investment in community-based social programs, such as prisoner reinsertion and jobs training programs, will reduce crime",
                 "Tough on Crime" = "Harsher sentencing, increased presence of police in high violence areas, and increased use of force by the police will reduce crime"))
src <- c(attr_sex = "sex", attr_abortion = "abort", attr_taxes = "tax", attr_same_sex_marriage = "lgbtq", attr_environment = "environ", attr_crime = "crime")
edut <- list(argentina = c("Sin instrucción", "Primario incompleto", "Primario completo", "Secundario incompleto", "Secundario completo",
                          "Terciario incompleto", "Universitario incompleto", "Terciario completo", "Universitario completo", "Posgrado completo o incompleto"),
            brazil = c("Sem instrução", "Primeiro grau/Ensino fundamental anos inicias: incompleto", "Primeiro grau/Ensino fundamental anos inicias: completo",
                       "Ginásio/Ensino fundamental anos finais: incompleto", "Ginásio/Ensino fundamental anos finais: complete",
                       "Segundo grau/Ensino médio: incompleto", "Segundo grau/Ensino médio: completo", "Superior/universidade: incompleto",
                       "Superior não-universitário: completo", "Superior/universidade: completo", "Pós-graduação completo ou incompleto"))
one <- function(f, ctry, place, idoff) {
  x <- as.data.table(readRDS(file.path(raw, f)))
  n <- uniqueN(x$id); stopifnot(nrow(x) == 10 * n)
  x[, blk := (seq_len(.N) - 1L) %/% n + 1L]
  stopifnot(x[, identical(id, x[blk == 1]$id), blk]$V1, all(x[blk <= 5]$chosen == 1), all(x[blk > 5]$chosen == 0))
  x[, `:=`(task = ifelse(blk <= 5, blk, blk - 5L), profile = blk)]   # profile reset below (outcome-independent)
  for (nm in names(src)) {
    v <- as.character(x[[src[[nm]]]]); stopifnot(all(is.na(v) | v %in% names(lv[[nm]])))
    x[, (nm) := unname(lv[[nm]][v])]
  }
  x[!is.na(attr_environment), attr_environment := sprintf(attr_environment, place)]
  ac <- names(src)
  x[, miss := Reduce(`|`, lapply(.SD, is.na)), .SDcols = ac]
  stopifnot(x[, uniqueN(miss), .(id, task)][, all(V1 == 1)])
  cat(f, "tasks dropped for missing levels:", x[miss == TRUE, uniqueN(paste(id, task))], "\n")
  x <- x[miss == FALSE]
  ids <- unique(x$id)
  e <- as.integer(as.character(x$edu))
  d <- x[, c(list(id = match(id, ids) + idoff, task = task, profile = profile, choice = as.integer(chosen)), .SD,
             list(cov_country = ctry, cov_age = as.integer(age), cov_gender_code = as.integer(as.character(female)),
                  cov_education = edut[[ctry]][e], cov_state_code = as.integer(as.character(state)),
                  cov_ideo_01b = ideo_01b, cov_ideo_01c = ideo_01c, cov_ideo_01d = ideo_01d, cov_ideo_05b = ideo_05b,
                  cov_ideo_05c = ideo_05c, cov_ideo_05d = ideo_05d, cov_ideo_05e = ideo_05e,
                  cov_vic = as.integer(as.character(vic)), cov_vic_fam = as.integer(as.character(vic_fam)),
                  cov_crime_gang = as.integer(as.character(crime_gang)), cov_safety_neighb = as.integer(as.character(safety_neighb)),
                  cov_assist_effect = as.integer(as.character(assist_effect)), cov_pol_04 = as.integer(pol_04), cov_pol_05 = as.integer(pol_05),
                  cov_demo_14 = as.integer(demo_14), cov_demo_06 = as.integer(demo_06), cov_demo_07 = as.integer(demo_07),
                  cov_social_pol = social_pol, cov_toilet = toilet)), .SDcols = ac]
  stopifnot(all(is.na(e) | e %in% seq_along(edut[[ctry]])))
  d
}
d <- one("arg_clean.rds", "argentina", "Patagonia", 0L)
d <- rbind(d, one("brazil_clean.rds", "brazil", "the Amazon", max(d$id)))
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
## profile = rank of the concatenated attribute text within the task, ties by source block (no outcome used)
ac <- grep("^attr_", names(d), value = TRUE)
d[, key := do.call(paste, c(.SD, sep = "|")), .SDcols = ac]
d[, tie := uniqueN(key) == 1L, by = .(id, task)]
d[, tb := ifelse(tie & (id + task) %% 2L == 1L, -profile, profile)]   # alternate identical pairs
setorder(d, id, task, key, tb)
d[, profile := seq_len(.N), by = .(id, task)][, c("key", "tie", "tb") := NULL]
cat("share chosen at profile 1:", d[profile == 1, mean(choice)], "\n")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "laterzo_2023_crime_candidates.csv"))
cat(nrow(d), uniqueN(d$id), "\n"); print(d[, .N, .(cov_country, attr_environment)])
