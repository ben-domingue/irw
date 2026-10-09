##Image-based factorial survey of mayoral candidate leaflets (santinhos), Brazil, from
##Vilaça, L., & Turner, J. R. (2024). The new corruption crusaders: Security sector ties as an
##anti-corruption voting heuristic. Latin American Politics and Society.
##https://doi.org/10.1017/lap.2023.39
##Replication data: Harvard Dataverse doi:10.7910/DVN/BK7S1G, CC0 1.0. Files read:
##survey_data_raw_final.tab (original .csv), cleaned_factorial_frame.tab (only for the authors'
##analysis sample), key.tab (question text and answer codes), appendix.docx (questionnaire in
##English and Portuguese, Appendix C "Realization of Candidate Features"), analysis.R (as text).
##Usage: Rscript vilaca_2024.R <dir holding survey_data_raw_final.csv, cleaned_factorial_frame.csv> <output dir>
##
##Online Qualtrics survey, Brazil, November 2021, Portuguese. Each respondent rated 3 hypothetical
##mayoral candidates shown ONE AT A TIME as campaign leaflets (images; Candidate 1-3 blocks), so
##task = candidate block (1-3) and profile = 1 (single-profile tasks; recorded by the _1/_2/_3
##column suffixes). Attributes (independently randomized per candidate; restrictions not
##documented):
##  attr_gender, attr_race: shown by the actor in the photo (authors' coding: male/female;
##    black/pardo/white; Appendix D base models). Stored as the authors' English labels.
##  attr_occupation: shown by costume and title (Appendix C): police -> "Delegado (sheriff)",
##    captain -> "Coronel (soldier)" (analysis.R labels captain "Coronel"), pastor -> "Pastor",
##    doctor -> "Doutor (doctor)", professor -> "Professor (teacher)", office -> "Not stated"
##    (baseline: no occupational title or costume; analysis.R "Neutral"). The title form shown
##    on female leaflets (e.g. Delegada) is not documented; the appendix's masculine form is used.
##  attr_slogan: the authors' slogan CATEGORY ("Anti-corruption", "Unemployment", "Generic").
##    The deposit records which of three slogans per category was shown (corruption1-3, jobs1-3,
##    generic1-3, kept as attr_slogan_variant 1-3), but no source maps the numbers to the three
##    texts Appendix C lists per category ("Vamos Acabar com a Corrupção!", "Chega de Corrupção!",
##    "Não aceito corrupção!"; "Trabalho para Todos!", "Vamos Combater o Desemprego!", "Pela Criação
##    de Mais Empregos!"; "Por um Brasil melhor!", "Por um Novo Brasil!", "Vamos Mudar o Brasil!"),
##    so the displayed slogan text is NOT stored (category label = authors' grouping).
##  attr_experience: politician -> "6 anos de experiência na Assembleia Legislativa", novice ->
##    "Novas ideias na prefeitura" (Appendix C seal text).
##  attr_economic_policy: left -> "Vamos investir em programas de assistência social para acabar
##    com a pobreza", right -> "Menos imposto e mais eficiência é o nosso lema" (Appendix C).
##  attr_name: the name printed on the leaflet (6 names; names follow the actor's gender).
##Outcomes (raw Qualtrics codes; the cleaned frame's `choice` is 6 - Q11, not used):
##  rating: "Qual a chance de você apoiar esse(a) candidato(a)?" 1 = Extremamente provável ...
##    5 = Extremamente improvável (LOWER = more support; stored raw, not reversed).
##  rating_security / rating_corruption / rating_unemployment: "Quão efetivo você acha que o(a)
##    candidato(a) seria nos seguintes temas: Segurança Pública / Corrupção / Desemprego",
##    1 = Nada efetivo ... 5 = Extremamente efetivo.
##Sample: consenting, non-preview respondents with at least one rating: 1,116 respondents
##(1,093 rated all three candidates). cov_analysis_sample = 1 for the 1,010 respondents in the
##authors' cleaned_factorial_frame (their analysis sample; the filter is not documented).
##Tasks with no rating at all are omitted (15+ respondents broke off).
##Covariates (Portuguese answer text from the appendix B questionnaire / key.tab; codes as in
##the export): cov_gender (Q5: Masculino male, Feminino female, Não-binário other, Prefiro não
##responder NA), cov_state (Q6), cov_income (Q7; "Prefiro não responder" NA), cov_trust_* (Q8_1-7,
##1 = Desconfio totalmente ... 5 = Confio totalmente), cov_ideology_self (Q30_1, 1 = esquerda ...
##7 = direita), cov_religion (Q36), cov_race (Q37, multi-select, labels joined by ";"),
##cov_urban (Q40), cov_education (Q41), cov_mobile, cov_duration_sec (whole survey).
##Dropped: PII FOUND in survey_data_raw_final: IPAddress, LocationLatitude/Longitude, ResponseId,
##city (Q38), CEP postal code (Q39), free-text answers (Q27, Q46-Q48). Also dropped: age (Q4 and
##age_bracket hold dropdown codes with no mapping), party (Q34 codes do not match the key's
##order: code 12 = "PDT" for 610 of 1,116), the second (post-conjoint) municipal-finance
##experiment (vignette, Q24, Q25), metadata. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "survey_data_raw_final.csv"), encoding = "UTF-8")
f <- fread(file.path(raw, "cleaned_factorial_frame.csv"), encoding = "UTF-8")
s <- s[Q2 == 1 & Status == 0 & (!is.na(Q11) | !is.na(Q14) | !is.na(Q17))]
stopifnot(nrow(s) == 1116L, all(unique(f$id) %in% s$ResponseId))
s[, rid := .I]
q <- list(c("Q11", "Q12_1", "Q12_2", "Q12_3"), c("Q14", "Q15_1", "Q15_2", "Q15_3"), c("Q17", "Q18_1", "Q18_2", "Q18_3"))
occ <- c(police = "Delegado (sheriff)", captain = "Coronel (soldier)", pastor = "Pastor", doctor = "Doutor (doctor)",
         professor = "Professor (teacher)", office = "Not stated")
slog <- c(corruption = "Anti-corruption", jobs = "Unemployment", generic = "Generic")
expe <- c(politician = "6 anos de experiência na Assembleia Legislativa", novice = "Novas ideias na prefeitura")
econ <- c(left = "Vamos investir em programas de assistência social para acabar com a pobreza",
          right = "Menos imposto e mais eficiência é o nosso lema")
d <- rbindlist(lapply(1:3, function(k) {
  g <- function(v) s[[paste0(v, "_", k)]]
  data.table(id = s$rid, task = k, profile = 1L,
             rating = as.integer(s[[q[[k]][1]]]), rating_security = as.integer(s[[q[[k]][2]]]),
             rating_corruption = as.integer(s[[q[[k]][3]]]), rating_unemployment = as.integer(s[[q[[k]][4]]]),
             attr_gender = g("sex"), attr_race = g("race"), attr_occupation = unname(occ[g("prof")]),
             attr_slogan = unname(slog[sub("[123]$", "", g("slogan"))]), attr_slogan_variant = sub("^[a-z]+", "", g("slogan")),
             attr_experience = unname(expe[g("politician")]), attr_economic_policy = unname(econ[g("econ")]),
             attr_name = g("name"))
}))
d <- d[!(is.na(rating) & is.na(rating_security) & is.na(rating_corruption) & is.na(rating_unemployment))]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
stopifnot(d[, all(attr_gender %in% c("female", "male") & attr_race %in% c("black", "pardo", "white"))],
          d[, all(attr_slogan_variant %in% c("1", "2", "3"))], all(d$rating %in% c(1:5, NA)))
# respondent covariates
lab <- function(x, l) unname(l[as.character(x)])
states <- c("Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal", "Espírito Santo", "Goiás",
            "Maranhão", "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará", "Paraíba", "Paraná", "Pernambuco",
            "Piauí", "Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima",
            "Santa Catarina", "São Paulo", "Sergipe", "Tocantins")
inc <- c("1" = "Até 2 salários mínimos (até R$ 2.200)", "2" = "De 2 a 4 salários mínimos (de R$ 2.200 a R$ 4.400)",
         "3" = "De 4 a 10 salários mínimos (de R$ 4.400 a R$ 11.000)", "5" = "De 10 a 20 salários mínimos (de R$ 11.000 a R$ 22.000)",
         "6" = "Acima de 20 salários mínimos (mais de R$ 22.000)")
rel <- c("1" = "Não pertenço a nenhuma religião", "2" = "Católico", "4" = "Evangélico", "5" = "Judeu", "6" = "Espírita",
         "7" = "Umbanda, candomblé ou outras religiões afro-brasileiras", "8" = "Ateu", "11" = "Outra religião")
race <- c("1" = "Branco", "2" = "Indígena", "3" = "Negro", "4" = "Pardo", "5" = "Asiático", "6" = "Outro")
edu <- c("1" = "Nunca frequentou escola", "2" = "Ensino fundamental completo", "3" = "Ensino médio completo",
         "4" = "Curso técnico", "5" = "Ensino superior completo", "6" = "Mestrado ou doutorado")
stopifnot(all(s$Q7 %in% c(1, 2, 3, 5, 6, 7, NA)), all(s$Q36 %in% c(names(rel), NA)), all(s$Q6 %in% c(1:27, NA)))
rc <- sapply(strsplit(as.character(s$Q37), ","), function(z) if (length(z) == 0 || all(is.na(z))) NA_character_ else paste(race[z], collapse = ";"))
cv <- data.table(id = s$rid, cov_gender = lab(s$Q5, c("1" = "male", "2" = "female", "3" = "other")),
                 cov_state = states[s$Q6], cov_income = lab(s$Q7, inc),
                 cov_trust_civpol = s$Q8_1, cov_trust_milpol = s$Q8_2, cov_trust_congress = s$Q8_3, cov_trust_minpub = s$Q8_4,
                 cov_trust_mayor = s$Q8_5, cov_trust_vereadores = s$Q8_6, cov_trust_army = s$Q8_7,
                 cov_ideology_self = s$Q30_1, cov_religion = lab(s$Q36, rel), cov_race = rc,
                 cov_urban = lab(s$Q40, c("1" = "Rural", "2" = "Urbana")), cov_education = lab(s$Q41, edu),
                 cov_mobile = s$mobile, cov_duration_sec = as.integer(s[["Duration (in seconds)"]]),
                 cov_analysis_sample = as.integer(s$ResponseId %in% f$id))
d <- merge(d, cv, by = "id")
stopifnot(uniqueN(d$id) == 1116L, d[cov_analysis_sample == 1, uniqueN(id)] == 1010L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vilaca_2024_corruption_crusaders.csv"))
