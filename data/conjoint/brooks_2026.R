##Critical-mineral mining project conjoint (Argentina) from
##Brooks, S. M., Lacroix Eussler, S., & Voeten, E. (2026). Environmental, economic, and
##geopolitical trade-offs in critical mineral mining projects: Evidence from a conjoint
##experiment in Argentina. The Extractive Industries and Society, 27, 101925.
##https://doi.org/10.1016/j.exis.2026.101925
##Replication data: Harvard Dataverse doi:10.7910/DVN/TSNBBM, CC0 1.0, no restricted files,
##no terms. File read: Datatxt.tab (Dataverse "original format" download: the Qualtrics
##export with answer TEXT, 3 header rows: names, question text, ImportIds). Read as text:
##AppendixFinalEXIS.Rmd (the authors' analysis and sample rules). Data.tab (numeric codes) not
##used. The article was not read.
##Usage: Rscript brooks_2026.R <raw dir> <output dir>
##
##Argentine online panel (IPSOS, per the consent text), survey in Spanish. Each respondent saw
##4 pairs of hypothetical mining projects ("Proyecto A" = profile 1, "Proyecto B" = profile 2)
##with 6 attributes; level text is the Spanish displayed text from the F-<task>-<profile>-<pos>
##fields, matched to attributes by the F-<task>-<pos> attribute-name fields:
##  attr_community   Comunidad local: Comunidad agrícola / Comunidad indígena
##  attr_owner       Propietario: "Propietario: YPF" / "Proprietario: Chino" / "Proprietario:
##                   Norteamericano" (spelling as displayed)
##  attr_jobs        Nuevos empleos: 250 / 1000 / 4000 nuevos empleos
##  attr_green       Crítico para la transición verde: Nada importante / Algo importante para las
##                   tecnologías verdes / Crítico para las tecnologías verdes
##  attr_damage      Daño al agua y al suelo: Ningún / Algún / Mucho daño al agua y al suelo
##  attr_tax         Incentivos fiscales del gobierno: Ningún incentivo del gobierno / Algún
##                   incentivo fiscal del gobierno / Gran incentivo fiscal del gobierno
##Attribute row order was randomized once per respondent (identical in all 4 tasks, checked):
##attrpos_<attr> = row position 1-6.
##Outcomes (question-text header row):
##  choice  "¿Qué proyecto es mejor?" (Which project is better?), Proyecto A / Proyecto B, no
##          opt-out (Q10, Q11, Q12, Q13 for tasks 1-4);
##  rating  "Califica cada proyecto de 1 estrella (malo) a 5 estrellas (bueno)" (Rate each
##          project from 1 star (bad) to 5 stars (good)), per profile (Q20, Q19, Q17, Q21 _1/_2 for
##          tasks 1-4, per the authors' Rmd). Stored raw: 77 ratings are 0, outside the stated
##          1-5 range (kept as recorded).
##Sample: rows with no conjoint answer (screen-outs, quota rejections, break-offs) dropped;
##tasks with neither a choice nor a rating dropped (break-offs); the panel ID `uid` is
##duplicated for some rows, and as in the authors' Rmd (distinct(uid, task, profile)) only the
##first record per uid is kept. The authors further drop respondents faster than 200 seconds
##(< 50% of the median duration); they are KEPT here with cov_duration_sec so the rule can be
##applied (cov_duration_sec <= 200: 157 respondents). Result: 2,424 respondents (2,473 records
##with conjoint answers, 45 uids repeated); 2,267 after the authors' duration rule; 2,367 have
##all 4 tasks. Ratings are missing on 1,604 profile rows (choice answered, stars skipped).
##Covariates (answer text as exported, Spanish): cov_gender (GENDER "Eres…": Mujer = female,
##Hombre = male, Otro género = other, Prefiero no responder = NA), cov_age_group (AGE),
##cov_province (Region), cov_education_household_head (Education: highest level of the person
##who contributes most to household expenses, NOT the respondent: so not cov_education),
##cov_vote_first_round (Pol1, first-round 2023 presidential vote), cov_attention_pass (Q18:
##asked to tick both "Nunca" and "Cada día": 1 = exactly those two, 0 = other answer, NA = not
##answered; the authors' Attention), cov_duration_sec (whole survey), trial_delegate (Delegate:
##the "who should regulate mining" question came Before or After the conjoint, a randomized
##survey arm).
##Dropped: post-conjoint experiment fields (comtype, ManipulatedText, env, EnText) and items,
##other attitude items, free-text Q8, CompleteUrl.
##PII: the deposited files (Data.tab, Datatxt.tab) contain IPAddress, LocationLatitude/
##LocationLongitude, ResponseId and the panel uid; all dropped. Respondents re-keyed to
##integers in file order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "Datatxt.csv"), colClasses = "character", encoding = "UTF-8", na.strings = NULL)
stopifnot(k$StartDate[1] == "Start Date", startsWith(k$StartDate[2], "{"))   # question-text and ImportId rows
k <- k[-(1:2)]
chq <- c("Q10", "Q11", "Q12", "Q13"); rq <- c("Q20", "Q19", "Q17", "Q21")
k <- k[k[, rowSums(.SD != "") > 0, .SDcols = c(chq, paste0(rep(rq, each = 2), c("_1", "_2")))]]
k <- k[!duplicated(uid)]
k[, id := .I]
anames <- c("Comunidad local" = "community", "Propietario" = "owner", "Nuevos empleos" = "jobs",
            "Crítico para la transición verde" = "green", "Daño al agua y al suelo" = "damage",
            "Incentivos fiscales del gobierno" = "tax")
for (t in 2:4) for (p in 1:6) stopifnot(identical(k[[sprintf("F-%d-%d", t, p)]], k[[sprintf("F-1-%d", p)]]))
stopifnot(k[, all(apply(.SD, 1, function(r) setequal(r, names(anames)))), .SDcols = sprintf("F-1-%d", 1:6)])
d <- rbindlist(lapply(1:4, function(t) rbindlist(lapply(1:2, function(p) {
  ch <- k[[chq[t]]]; stopifnot(all(ch %in% c("", "Proyecto A", "Proyecto B")))
  rt <- k[[paste0(rq[t], "_", p)]]; stopifnot(all(rt %in% c("", 0:5)))
  s <- data.table(id = k$id, task = t, profile = p,
                  choice = fifelse(ch == "", NA_integer_, as.integer(ch == c("Proyecto A", "Proyecto B")[p])),
                  rating = fifelse(rt == "", NA_integer_, as.integer(rt)))
  for (pos in 1:6) {
    an <- anames[k[[sprintf("F-1-%d", pos)]]]; lv <- k[[sprintf("F-%d-%d-%d", t, p, pos)]]
    for (x in anames) { s[an == x, paste0("attr_", x) := lv[an == x]]; s[an == x, paste0("attrpos_", x) := pos] }
  }
  s
}))))
d <- d[d[, .(keep = any(!is.na(choice) | !is.na(rating))), .(id, task)], on = .(id, task)][keep == TRUE][, keep := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", anames), paste0("attrpos_", anames)))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d[, .SD, .SDcols = patterns("^attr_")] != ""),
          d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
g <- c(Mujer = "female", Hombre = "male", "Otro género" = "other", "Prefiero no responder" = NA, " " = NA)
cv <- k[, .(id, cov_gender = unname(g[fifelse(GENDER == "", " ", GENDER)]), cov_age_group = fifelse(AGE == "", NA_character_, AGE),
            cov_province = fifelse(Region == "", NA_character_, Region),
            cov_education_household_head = fifelse(Education == "", NA_character_, Education),
            cov_vote_first_round = fifelse(Pol1 == "", NA_character_, Pol1),
            cov_attention_pass = fifelse(Q18 == "", NA_integer_, as.integer(Q18 == "Nunca,Cada día")),
            cov_duration_sec = as.integer(`Duration (in seconds)`),
            trial_delegate = fifelse(Delegate == "", NA_character_, Delegate))]
stopifnot(all(k$GENDER %in% c("", names(g))))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "brooks_2026_mining_argentina.csv"))
