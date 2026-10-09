##Presidential-candidate conjoint with candidate emotions (Chile) from
##Segovia, C. (2020). Replication Data for: Hoping for a Better Future [Data set]. Harvard
##Dataverse. The same experiment ("Experimento 2") is reported in Segovia, C. (2021).
##Decidiendo por quién votar. Evidencia experimental del efecto de las emociones en el voto.
##Colombia Internacional, 107, 3-28. https://doi.org/10.7440/colombiaint107.2021.01 (open
##access; design facts below are from its section 4a and Tabla 2). The deposit's own paper
##("Hoping for a better future. A conjoint experiment on the effects of emotions on the vote")
##is not identified by a DOI in the deposit.
##Replication data: Harvard Dataverse doi:10.7910/DVN/RW6OLZ, CC0 1.0, no restricted files.
##Files read: "Hoping for a better future.tab" as Stata original (saved as data.dta, read with
##latin1 label encoding); "Online Appendix_Hoping for a better future.docx" (Figure A1, an
##English example of the question; Table A1) and the authors' do-file, read as text.
##Usage: Rscript segovia_2020.R <raw dir> <output dir>
##
##Probability sample of 1,800 adults resident in Chile, interviewed face to face at home with
##tablets, May-June 2019 (Segovia 2021, section 2). Each answered 5 forced choices (par =
##task) between two hypothetical presidential candidates (eleccion = profile, 1 = Candidato
##A); levels randomized when each question was asked, attribute order fixed (section 4a).
##  choice = Candidato (voto: "Candidato 1"/"Candidato 2"). Question (Segovia 2021): "Suponga
##    ahora que los siguientes candidatos han pasado a la segunda vuelta de la elección
##    presidencial. Por favor, revise la información y dígame, ¿a cuál de estos dos candidatos
##    preferiría Ud. como presidente de Chile?" Forced choice. 2,245 of 9,000 tasks have no
##    recorded choice (voto missing; the code "Seleccionar" never occurs) and are omitted.
##Attributes: level text = the deposit's Spanish value labels. Stata cut four labels at 60
##characters; they are completed here from the same phrases elsewhere in the labels and in
##the article: "... todos los es" -> "todos los estudiantes", "... todos los" -> "todos los
##estudiantes", "... en Chile des" -> "en Chile desde 1990", "... en los próximos" / "en los
##próxi" -> "en los próximos años". NOTE: the article's Tabla 2 words several levels
##differently ("matrimonio entre personas del mismo sexo", "educación universitaria
##gratuita", "Está orgulloso de lo que ha pasado en el país desde 1990", "Está enojado por
##..."); the deposit labels are kept, and which wording respondents saw is not certain.
##The English example (Figure A1) shows gendered text ("He is"/"She is"); whether the Spanish
##"orgulloso" agreed with a female candidate is not recorded.
##Covariates: cov_gender (d01 "Registre sexo del entrevistado": 1. Hombre -> male, 2. Mujer
##-> female), cov_survey_weight (pond, "Ponderador"; the authors weight every model with it).
##Dropped: SbjNum (interview id, re-keyed to integers), id (row id), Candidato2 (the authors'
##recode of missing choices to 0), new_d01 / new2_d01 (recodes of d01).
##N: 1,800 respondents in the deposit, matching the article; 1,542 have at least one answered
##task and are in the table (258 answered none). Spot check: weighted LPM of choice on the attributes
##reproduces appendix Table A1 (free university in favour 0.174, optimism 0.049, Frente Amplio
##-0.067, constant 0.362) exactly.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "data.dta"), encoding = "latin1")
lab <- function(v) as.character(as_factor(s[[v]], levels = "labels"))
fix <- c("Está a favor de la gratuidad universitaria para todos los es" = "Está a favor de la gratuidad universitaria para todos los estudiantes",
         "Está en contra de la gratuidad universitaria para todos los" = "Está en contra de la gratuidad universitaria para todos los estudiantes",
         "Se siente orgulloso de las cosas que han pasado en Chile des" = "Se siente orgulloso de las cosas que han pasado en Chile desde 1990",
         "Tiene miedo de lo que pueda ocurrir en Chile en los próximos" = "Tiene miedo de lo que pueda ocurrir en Chile en los próximos años",
         "Está optimista de lo que pueda ocurrir en Chile en los próxi" = "Está optimista de lo que pueda ocurrir en Chile en los próximos años")
fx <- function(x) { x <- trimws(x); i <- x %in% names(fix); x[i] <- fix[x[i]]; x }
d <- data.table(sbj = as.numeric(s$SbjNum), task = as.integer(s$par), profile = as.integer(s$eleccion),
                choice = as.integer(s$Candidato),
                attr_coalition = lab("pacto"), attr_gender = lab("sexo"), attr_age = lab("edad"),
                attr_same_sex_marriage = fx(lab("matrimonio")), attr_free_university = fx(lab("educacion")),
                attr_past = fx(lab("pasado")), attr_future = fx(lab("futuro")),
                cov_gender = c("male", "female")[as.integer(s$d01)], cov_survey_weight = as.numeric(s$pond))
stopifnot(uniqueN(d$sbj) == 1800, d[, .N, .(sbj, task)][, all(N == 2)], all(d$profile %in% 1:2),
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d$cov_gender %in% c("male", "female")),
          d[, uniqueN(attr_free_university)] == 2, d[, uniqueN(attr_future)] == 2, d[, uniqueN(attr_past)] == 2)
d <- d[!is.na(choice)]
stopifnot(d[, .(.N, sum(choice)), .(sbj, task)][, all(N == 2 & V2 == 1)])
d[, id := match(sbj, sort(unique(sbj)))][, sbj := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "segovia_2020_candidate_emotions.csv"))
