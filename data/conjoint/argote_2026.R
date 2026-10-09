##Venezuelan-migrant vignette experiment (Colombia) from
##Argote, P., & Carreras, M. Informality and attitudes towards immigrants in Latin America
##(manuscript; no published version or article DOI found).
##Replication data: Carreras, M. (2026), Harvard Dataverse doi:10.7910/DVN/MRBYOX, CC0 1.0.
##Files read: informality_immigration_colombia_rawdata.xlsx, sheet "Labels" (answer text;
##same rows and keys as sheet "Datos", checked) and sheet "Datos" (numeric age, duration).
##Vignette and outcome wording from informality_immigration_colombia_questionnaire_ES.pdf
##(Section D; Spanish, the language of administration) and _EN.pdf; README.pdf;
##informality_immigration_colombia_replication.do read as text.
##Usage: Rscript argote_2026.R <dir holding the .xlsx> <output dir>
##
##1,203 economically active Colombian adults (Netquest online panel, 2025 per the timestamps;
##README says 2024; 50/50 quota of formal and informal workers, cov_sample), ONE text
##vignette each (task = profile = 1, inferred: one vignette per respondent). The vignette
##described a 35-year-old Venezuelan migrant, randomized in four dimensions:
##  attr_name: "Juan Pérez" / "María Pérez" (the questionnaire's "sex of the migrant").
##  attr_previous_job: previous occupation (4 levels).
##  attr_degree: degree recognition, shown ONLY for engineer/doctor (questionnaire
##    programming note); "(not shown)" for street vendor / delivery person.
##  attr_salary: salary expectation (2 levels).
##Attribute text is the level text of the Spanish questionnaire's dimension list, mapped
##from the short codes stored in the data (e.g. OCUPACION "Medico/a"); the gendered forms
##are written as in that list ("ingeniero/a", "Él/ella"), while the screen showed the form
##matching the name.
##Level weights: occupation is non-uniform in the data (engineer 401, doctor 398, street
##vendor 200, delivery 204: the formal/informal split was 50/50); the others are 50/50.
##Outcomes (5-point / 3-point answer codes stored raw; LOWER = more favourable on D1, D2;
##see design_outcomes):
##  rating (D1) presence of Venezuelan immigrants like [name] 1 Muy positiva .. 5 Muy negativa
##  rating_stay (D2) "[name] debería poder quedarse en Colombia" 1 Muy de acuerdo .. 5 Muy en desacuerdo
##  rating_job_chances (D3) 1 Disminuye .. 3 Mejora mis posibilidades de encontrar trabajo
##  rating_salary (D4) 1 Reduce .. 3 Aumenta mi salario
##  rating_compete (D5) likely to compete for a job 1 Muy probable .. 5 Muy improbable
##No outcome is missing. Covariates are the "Labels" answer text: cov_gender (A2: Masculino
##-> male, Femenino -> female, No Binario -> other, Prefiero no responder -> NA; Codigos
##sheet), cov_age (A1, years), cov_age_group (A1R band text), cov_education (A3 text),
##cov_party_id (C2B party text; asked only of those who identify with a party, C2 =
##cov_party_identifies; "No sabe / No responde" kept as text), cov_duration_sec (survey
##duration, seconds: equals endTime - startTime), and the remaining items under lowercase
##source names (cov_b1 ..., cov_e1 ..., cov_g1 ...; text as stored, so "No sabe / Prefiere
##no responder" categories stay as text, except cov_ideology (C1, 1 left .. 10 right) whose
##"No sabe / Prefiere no responder" is NA, as in the do-file).
##Dropped: key (UUID), numericalId, CodPanelista (Netquest panelist code), start/end
##timestamps, status/type/CONSENT (constant), municipality (A6), B3 (free-text first word
##about "venezolano"), VINETA (concatenation of the four factors).
##N: 1,203 respondents = README N; the paper was not available to compare further.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
p <- file.path(raw, "informality_immigration_colombia_rawdata.xlsx")
l <- as.data.table(read_excel(p, "Labels")); n <- as.data.table(read_excel(p, "Datos"))
stopifnot(nrow(l) == 1203, identical(l$key, n$key), all(l$status == "end"), all(l$type == "complete"))
job <- c("Ingeniero/a" = "Antes de migrar, trabajaba como ingeniero/a, con contrato formal.",
         "Medico/a" = "Antes de migrar, trabajaba como médico/a, con contrato formal.",
         "Vendedor/a Ambulante" = "Antes de migrar, trabajaba como vendedor/a ambulante, sin contrato formal",
         "Repartidor/a" = "Antes de migrar, trabajaba como repartidor/a, sin contrato formal.")
deg <- c("Titulo NO reconocido" = "Su título no fue reconocido en Colombia. Por eso, ahora trabaja sin un contrato formal como repartidor/repartidora",
         "Titulo reconocido" = "Su título fue reconocido en Colombia. Por eso, ahora trabaja con un contrato formal como ingeniero/a o médico/a")
sal <- c("Salario mas bajo" = "Él/ella aceptaría un salario más bajo que los colombianos.",
         "Salario igual" = "Él/ella busca un salario igual al de los colombianos.")
stopifnot(all(l$OCUPACION %in% names(job)), all(l$SALARIO %in% names(sal)), all(l$NOMBRE %in% c("Juan Pérez", "María Pérez")),
          l[OCUPACION %in% c("Ingeniero/a", "Medico/a"), all(RECONOCIMIENTO %in% names(deg))],
          l[!OCUPACION %in% c("Ingeniero/a", "Medico/a"), all(is.na(RECONOCIMIENTO))])
code <- function(v, lv) { x <- match(n[[v]], seq_along(lv)); stopifnot(!anyNA(x), identical(lv[x], l[[v]])); as.integer(n[[v]]) }
d <- data.table(id = seq_len(nrow(l)), task = 1L, profile = 1L,
  rating = code("D1", c("Muy positiva", "Positiva", "Neutral", "Negativa", "Muy negativa")),
  rating_stay = code("D2", c("Muy de acuerdo", "De acuerdo", "Neutral", "En desacuerdo", "Muy en desacuerdo")),
  rating_job_chances = code("D3", c("Disminuye mis posibilidades de encontrar trabajo", "No afecta mis posibilidades de encontrar trabajo", "Mejora mis posibilidades de encontrar trabajo")),
  rating_salary = code("D4", c("Reduce mi salario", "No afecta mi salario", "Aumenta mi salario")),
  rating_compete = code("D5", c("Muy probable", "Algo probable", "Ni probable ni improbable", "Algo improbable", "Muy improbable")),
  attr_name = l$NOMBRE, attr_previous_job = unname(job[l$OCUPACION]),
  attr_degree = fifelse(is.na(l$RECONOCIMIENTO), "(not shown)", unname(deg[l$RECONOCIMIENTO])),
  attr_salary = unname(sal[l$SALARIO]))
stopifnot(all(l$A2 %in% c("Masculino", "Femenino", "No Binario", "Prefiero no responder")))
d[, cov_gender := c(Masculino = "male", Femenino = "female", "No Binario" = "other")[l$A2]]
d[, cov_age := as.integer(n$A1)][, cov_age_group := as.character(l$A1R)][, cov_education := as.character(l$A3)]
d[, cov_party_identifies := as.character(l$C2)][, cov_party_id := as.character(l$C2B)]
d[, cov_duration_sec := as.integer(n$duration)][, cov_sample := as.character(l$MUESTRA)]
rest <- c("DEVICE", "A5", "REGION", "NSE", "OCCUP", "OCCUP_HORAS", "INF_SOCPROT_A", "INF_SOCPROT_B", "INF_SOCPROT_SPOUSE", "A4",
          "B1", "B2", "B4", "B5", "B6", "B7", "B8_1", "B8_2", "B8_3", "B8_4", "C1", "C3",
          "E1", "E2", "E3", "E4_1", "E4_2", "E4_3", "E5", "E6_1", "E6_2", "E6_3", "E6_4", "E7", "E8", "E9",
          "E10_1", "E10_2", "E10_3", "E11", "G1", "G2", "G3", "G4")
for (v in rest) d[, (paste0("cov_", tolower(v))) := as.character(l[[v]])]
stopifnot(all(is.na(d$cov_c1) | d$cov_c1 %in% c(1:10, "No sabe / Prefiere no responder")))
d[, cov_c1 := suppressWarnings(as.integer(cov_c1))]
setnames(d, c("cov_a5", "cov_a4", "cov_c1"), c("cov_department", "cov_income", "cov_ideology"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "argote_2026_informality_immigrants.csv"))
