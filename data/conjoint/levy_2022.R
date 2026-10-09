##Wartime-perpetrator candidate conjoint (Colombia, online, October 2019) from
##Levy, G. (2022). Evaluations of violence at the polls: Civilian victimization and support for
##perpetrators after war. The Journal of Politics, 84(2), 783-797.
##https://doi.org/10.1086/715248
##Replication data: Harvard Dataverse doi:10.7910/DVN/0Y1E2B, CC0 1.0, no restricted files.
##Files read: GLevy_JOP_Data.csv (Dataverse original format; one row per respondent x task x
##profile) and "GLevy _JOP_Codebook.docx" (questions and the Spanish attribute levels shown to
##respondents). Read as text only: GLevy_JOP_Replication.R.
##Usage: Rscript levy_2022.R <dir holding the csv> <output dir>
##
##1,589 Colombian citizens (soft-launch, non-consenting and non-citizen respondents already
##excluded by the author, codebook) x 4 tasks x 2 candidate profiles (task, profile recorded),
##10 attributes. The survey was in Spanish.
##Outcomes (codebook, Spanish as shown, English translation in the codebook):
##  choice = selected_FC: "¿Si tuviera que elegir, por cuál de los dos candidatos votaría?"
##           (If you had to choose between them, which of these two candidates would you vote
##           for?); forced, one per answered task. 744 tasks unanswered -> NA (the author drops
##           them, Replication.R line 68).
##  rating = selected_Rating: "¿En una escala del 1 a 5, donde 1 es "muy improbable" y 5 es
##           "muy probable," ¿qué tan probable es que usted vote por el/la candidato/a A [B]?"
##           1 very unlikely ... 5 very likely; 832 profile ratings NA. The author's 0-1
##           rescaling (selected_Rating_rescaled) is dropped.
##  Rows where both are missing (787) are omitted: 1,528 respondents remain (61 answered no
##  task) and 90 of them have fewer than 4 tasks. Choice rows: 11,224 (= the author's FC data).
##Attributes: the data file stores shortened English translations; this table stores the
##Spanish level text "presented to respondents" from the codebook (mapping English -> Spanish
##is the codebook's own table). Where the codebook writes a gendered form as "/a" (e.g.
##"obligado/a", "Ambicioso/a", "involucrado/a") the stored text keeps it: whether respondents
##saw the form matching the profile's gender is not documented.
##Attribute order fixed (codebook: "attribute order was held constant"; *.rowpos constant):
##no attrpos_. Levels randomized; no restrictions or probabilities documented (all 6
##crime x target combinations occur, level shares near equal).
##Covariates: cov_gender (ResGender: 1 Male -> male, 2 Female -> female, 3 Other gender ->
##other, 99 refused -> NA; codebook), cov_birth_year (ResAge, "In what year were you born?"),
##cov_education (Edu, codebook English answer text), cov_income (Income codes as stored,
##codebook bands, 99 = inapplicable), cov_urban (Urban codes 1 rural ... 5 national capital),
##cov_ideology (1 left - 10 right), cov_economic (-1 worse, 0 same, 1 better),
##cov_peace_vote_2016 (PeaceAgreementVote codes: 1 for, 0 against, 99 did not vote / refused,
##as stored; the codebook uses 99 for both).
##Dropped: Response.ID (Qualtrics ID; re-keyed), StartDate, Consent/Citizen (constant),
##BirthLoca/LiveLoca (free-typed municipalities), other attitude items, rescaled rating.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "GLevy_JOP_Data.csv"))
x[, id := match(Response.ID, unique(Response.ID))]
es <- list(
  `Age` = c("25" = "25", "47" = "47", "68" = "68"),
  `Gender` = c("Man" = "Hombre", "Woman" = "Mujer"),
  `Education Level` = c("Primary School" = "Primaria", "Secondary School" = "Bachillerato", "Associate Degree" = "Técnica",
                        "University" = "Universitaria"),
  `Recruitment` = c("Ideology" = "Se unió a un grupo armado o el ejército debido a su ideología",
                    "A Job" = "Se unió a un grupo armado o el ejército porque necesitaba un trabajo",
                    "Forced Recruitment" = "Se unió a un grupo armado o el ejército porque fue obligado/a a hacerlo"),
  `Reputation According to the Troops` = c("Good Example" = "Buen ejemplo", "Kind" = "Amable", "Power-hungry" = "Ambicioso/a",
                                           "Unjust" = "Injusto/a"),
  `Military Success` = c("Won almost all battles" = "Ganó casi todas las batallas",
                         "Won half of battles" = "Ganó aproximadamente la mitad de las batallas",
                         "Won few battles" = "Ganó pocas batallas"),
  `Crime` = c("Killing" = "Acusado de estar involucrado/a en la matanza de algunos civiles que no estaban luchando y que no eran miembros de un grupo armado ni del ejército",
              "Sexual Violence" = "Acusado de estar involucrado/a en la violencia sexual contra algunos civiles que no estaban luchando y que no eran miembros de un grupo armado ni del ejército"),
  `Target of the Crime` = c("Enemy Informants" = "Estas víctimas fueron informantes del enemigo",
                            "People living in an area that supported the enemy" = "Estas víctimas estaban viviendo en un área en que la población apoyaba principalmente al enemigo",
                            "People living in an area controlled by the enemy" = "Estas víctimas estaban viviendo en un área controlado del enemigo"),
  `Type of Involvement in the Crime` = c("Decided to commit on his/her own" = "Supuestamente decidió cometer el crimen por propia cuenta",
                                         "Did not prevent someone else from committing" = "Supuestamente no impidió que otra persona cometiera el crimen",
                                         "Followed an order to commit" = "Supuestamente siguió una orden para cometer el crimen",
                                         "Ordered someone else to commit" = "Supuestamente le ordenó a otra persona que cometiera el crimen"),
  `Attitude Toward the Crime` = c("Reluctant" = "Lo hizo con desgana", "Enthusiastic" = "Lo hizo con entusiasmo"))
nm <- c("age", "gender", "education", "recruitment", "reputation", "military_success", "crime", "crime_target",
        "involvement", "attitude")
d <- x[, .(id, task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected_FC),
           rating = as.integer(selected_Rating))]
for (k in seq_along(es)) {
  v <- trimws(as.character(x[[names(es)[k]]]))
  stopifnot(all(v %in% names(es[[k]])), uniqueN(x[[paste0(names(es)[k], ".rowpos")]]) == 1)
  d[, paste0("attr_", nm[k]) := unname(es[[k]][v])]
}
edu <- c("None", "Some Primary School", "Primary School", "Some Secondary School", "Secondary School", "Some Associate Degree",
         "Associate Degree", "Some University", "University")
stopifnot(all(x$ResGender %in% c(1, 2, 3, 99, NA)), all(x$Edu %in% c(0:8, NA)))
d[, `:=`(cov_gender = c("male", "female", "other")[match(x$ResGender, 1:3)], cov_birth_year = as.integer(x$ResAge),
         cov_education = edu[x$Edu + 1L], cov_income = as.integer(x$Income), cov_urban = as.integer(x$Urban),
         cov_ideology = as.integer(x$Ideology), cov_economic = as.integer(x$Economic),
         cov_peace_vote_2016 = as.integer(x$PeaceAgreementVote))]
stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)])
d <- d[!(is.na(choice) & is.na(rating))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "levy_2022_perpetrator_candidates.csv"))
