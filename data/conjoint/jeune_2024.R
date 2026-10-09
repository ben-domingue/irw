##Factorial survey on teachers' use of research (France) from
##Jeune, N., Juhel, J., Dessus, P., & Atal, I. (2024). Six factors facilitating teachers' use of
##research: An experimental factorial survey of educational stakeholders' perspectives. Frontiers
##in Education, 9, 1368565. https://doi.org/10.3389/feduc.2024.1368565
##Data: OSF project https://osf.io/xc948/ (doi:10.17605/OSF.IO/XC948), CC BY 4.0 (node licence).
##Files read: Archive/results-survey118174_Feb9.csv (block 1, vignettes A-H) and
##Archive/results-survey775676_Feb9.csv (block 2, vignettes I-P), the LimeSurvey exports;
##Archive/vignette_structure.csv (level of each factor per vignette, 1 = negative, 2 = positive
##framing; README.txt); level wording from "Six Factors and two Levels.pdf" (French, as shown, with
##the authors' English); sample rules from Annotated code/CreationData_Public.R (read as text).
##Usage: Rscript jeune_2024.R <raw dir> <output dir>
##
##LimeSurvey, convenience/snowball sample of French education stakeholders (teachers, trainers,
##decision makers, researchers), launched 23 June 2022 for six months. Respondents were randomly
##assigned to one of two blocks of 8 text vignettes (a D-efficient fixed sample of 16 of the 64
##vignettes of a 2^6 design; each level appears in 8 of the 16) about a teacher "Mx. A." who
##accessed research; 6 binary factors, one sentence each, in fixed order within the vignette. One
##profile per task (profile = 1). attr_ = the French level text from the Six Factors pdf:
##  attr_target_audience (TchAudience), attr_teacher_involvement (TchInvolv), attr_conceptual_utility
##  (ConceptUtil), attr_instrumental_utility (InstrumUtil), attr_collaboration (CollabRes),
##  attr_institutional_support (SupportInst).
##  (The sentences inside a vignette adapt them grammatically, e.g. "Ces recherches ont été
##  produites avec une contribution significative d'enseignant·es".)
##Outcome: rating = "À quel point vous semble-t-il probable que Mx. A utilise la recherche qui
##  l'intéresse dans ces conditions ?" slider, -5 "Extrêmement improbable" .. 5 "Extrêmement
##  probable", stored as exported (higher = more likely).
##task: the order of the vignettes was randomized within the block but NOT recorded; task is the
##  vignette's position in the questionnaire (A-H / I-P -> 1-8), not the display order
##  (trial_vignette keeps the letter).
##Sample: rows with last page >= 3 and one of the four main roles (the authors' rules drop blank and
##  "Je n'ai occupé aucun de ces quatre rôles", 10 respondents); all have at least one rated vignette: 440 respondents = the paper's 100 pilot + 340 main-study participants. cov_pilot = 1
##  for the first 50 of each block (the authors' pilot, excluded from their main study).
##Covariates: cov_block (1/2), cov_role (main role in the last three years, French answer text),
##  cov_years_experience (years of experience in education, as typed; non-numbers -> NA).
##Dropped: response id, submission date (dates are masked as 1980-01-01 in the export), seed,
##  free-text answers (disciplines, "other" fields) and the multiple-choice background items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lev <- list(
  target_audience = c("communiquées de façon non adaptée à un public d'enseignant·es",
                      "communiquées de façon tout à fait adaptée à un public d'enseignant·es"),
  teacher_involvement = c("sans contribution d'enseignant·es", "avec une contribution significative d'enseignant·es"),
  conceptual_utility = c("n'apportent pas d'éléments facilitant la réflexion sur le sujet traité",
                         "apportent des éléments facilitant la réflexion sur le sujet traité"),
  instrumental_utility = c("n'apportent pas d'éléments facilitant un changement concret de pratiques éducatives en lien avec ce sujet",
                           "apportent des éléments facilitant un changement concret de pratiques éducatives en lien avec ce sujet"),
  collaboration = c("n'a pas la possibilité de collaborer avec ses pairs, avec des chercheur·euses ou d'autres professionnel·les de l'éducation pour l'utilisation de recherches",
                    "a la possibilité de collaborer avec ses pairs, des chercheur·euses ou d'autres professionnel·les de l'éducation pour l'utilisation de recherches"),
  institutional_support = c("La hiérarchie ou l'institution ne met rien en place pour faciliter l'utilisation des recherches par les enseignant·es.",
                            "La hiérarchie ou l'institution met à disposition des aménagements (ex: temps dédié, formations, budget, etc.) pour faciliter l'utilisation des recherches par les enseignant·es."))
vs <- fread(file.path(raw, "vignette_structure.csv"))
setnames(vs, c("Vign", "TchAudience", "TchInvolv", "ConceptUtil", "InstrumUtil", "CollabRes", "SupportInst"), c("vign", names(lev)))
for (k in names(lev)) { stopifnot(all(vs[[k]] %in% 1:2)); vs[, (k) := lev[[k]][get(k)]] }
vs[, letter := sub("vign_", "", vign)][, vign := NULL]
files <- c("results-survey118174_Feb9.csv", "results-survey775676_Feb9.csv")
parts <- list()
for (b in 1:2) {
  x <- read.csv(file.path(raw, files[b]), check.names = FALSE, colClasses = "character", encoding = "UTF-8")
  stopifnot(ncol(x) == 53, grepl("^ID de la r", names(x)[1]), grepl("^Derni", names(x)[3]), grepl("^Depuis trois ans, quel", names(x)[7]),
            all(grepl("probable que Mx", names(x)[46:53])))
  letters8 <- sub("^.*probable que Mx\\. ([A-P]) utilise.*$", "\\1", names(x)[46:53])
  stopifnot(identical(letters8, LETTERS[(b - 1) * 8 + 1:8]))
  x <- x[as.numeric(x[[3]]) >= 3 & x[[7]] != "" & x[[7]] != "Je n'ai occupé aucun de ces quatre rôles", ]
  x$pilot <- as.integer(seq_len(nrow(x)) <= 50)
  r <- as.matrix(x[, 46:53])
  for (j in 1:8) {
    parts[[length(parts) + 1]] <- data.table(src = paste(b, x[[1]]), task = j, profile = 1L, letter = letters8[j],
                                             rating = suppressWarnings(as.integer(r[, j])), raw = r[, j],
                                             cov_block = b, cov_pilot = x$pilot, cov_role = x[[7]],
                                             cov_years_experience = suppressWarnings(as.numeric(x[[6]])))
  }
}
d <- rbindlist(parts)
stopifnot(all(is.na(d$rating) == (d$raw == "")), all(d$rating %in% c(-5:5, NA)))
d <- d[!is.na(rating)][, raw := NULL]
d <- merge(d, vs, by = "letter")
d[, id := match(src, unique(src[order(cov_block, as.integer(sub("^[12] ", "", src)))]))]
setnames(d, "letter", "trial_vignette")
setnames(d, names(lev), paste0("attr_", names(lev)))
d[, src := NULL]
setcolorder(d, c("id", "task", "profile", "rating", paste0("attr_", names(lev)), "trial_vignette"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jeune_2024_research_use.csv"))
print(d[, .(resp = uniqueN(id), rows = .N), .(cov_block, cov_pilot)])
