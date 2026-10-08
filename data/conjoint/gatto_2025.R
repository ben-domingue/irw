##Candidate-selection conjoint among party elites in Austria, Germany and Switzerland from
##Gatto, M. A. C., & Radojevic, M. (2025). Choosing women: Party elites' preferences in the
##candidate selection process. British Journal of Political Science, 55, e36.
##https://doi.org/10.1017/S0007123424000723
##Replication data: Harvard Dataverse doi:10.7910/DVN/XRNZC7, CC0 1.0. File read:
##CandidateFinal.tab (the raw survey export, read as UTF-8). The authors' DataPrep.R (read as
##text) documents the columns; their data4.RData was used only to check counts.
##Usage: Rscript gatto_2025.R <dir holding CandidateFinal.tab> <output dir>
##
##Members of state/federal party executive boards of 19 parties, Nov-Dec 2019, online survey in
##German and French. 8 paired forced choices between two fictitious aspirants for a prominent
##place on the party's list for the next national election. Each profile is one string
##traits<t><a|b> (centre respondents), traitsR<t><a|b> (right-wing) or traitsL<t><a|b> (left-wing)
##"age_gender_education_experience_issue_ideology"; the three blocks differ only in the ideology
##wording, which was relative to the respondent's own self-placement (Rough_Ideology): centre
##saw "Etwas linker/rechter als Sie", left-wing respondents "Etwas linker als Sie" / "Etwas
##moderater als Sie", right-wing "Etwas rechter als Sie" / "Etwas moderater als Sie", all also
##"Etwa die gleiche Position wie Sie". The authors recode "moderater" to linker/rechter; this
##table keeps the displayed text (whitespace squished), so read attr_ideology with
##cov_ideology_group. Attributes: age (25-65, a number), gender (Frau/Mann), education
##(Abitur / Matura, Hochschulabschluss, Promotion / Doktorat; 6 profiles carry the French
##"Diplome universitaire"), parliamentary experience (Kommunales / Landes- bzw. Kantons- /
##Nationales Parlament), most important issue (6), ideology. The French-language responses are
##stored with German level text: display_language de;fr, label_language de.
##trial_list_share: the share of women among candidates already on the list ("10 Prozent Frauen,
##  90 Prozent Maenner" .. "50 Prozent Frauen, 50 Prozent Maenner"), shown once per task
##  (traits<t>c), randomized per task; stored on both profiles.
##Outcome: choice = "Based on the information provided, please select the aspirant that you would
##  prefer to place on a prominent placement in your party's candidate list" (article's English
##  rendering of the instructions; the German item text is not deposited). Kandidat A / B only.
##Randomization: article Table 1 note: all attributes completely randomized per profile; gender
##  pairs man-man 25%, woman-woman 25%, mixed 50% (i.e. independent 50/50): restrictions none.
##Sample: 1,945 records; 89 made no choice and are dropped (1,856 respondents). The authors keep
##  board members who select lists (drop "Nein", "Kein Vorstandsmitglied", "Bezirksvorstand") and
##  respondents who gave an ideology: cov_in_authors_sample = 1 for those 1,389 (AT 219, DE 385,
##  CH 785, exactly the article's counts), of whom 1,343 made at least one choice. Respondents
##  who answered only some tasks keep the tasks they answered.
##Covariates (stored text): cov_country, cov_party_family, cov_party_quota, cov_ideology_group
##  (Left Wing / Center / Right Wing; decides the ideology wording), cov_left_right (0-10),
##  cov_economic_position (0-10), cov_gender, cov_age_group, cov_education, cov_migration.
##Dropped: raw ID (re-keyed), party name, state, board level, salutation and academic title
##  (Anrede2, Titel2, from the sampling list), Party2/State2/Country2, policy and representation
##  items, the authors' derived columns.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "CandidateFinal.tab"), encoding = "UTF-8", colClasses = "character")
sq <- function(x) trimws(gsub("\\s+", " ", x))
pick <- function(v) { x <- s[[paste0("traits", v)]]; r <- s[[paste0("traitsR", v)]]; l <- s[[paste0("traitsL", v)]]
  stopifnot(((x != "") + (r != "") + (l != ""))[x != "" | r != "" | l != ""] == 1); fifelse(x != "", x, fifelse(r != "", r, l)) }
ex <- paste(s$Ger_Executive, s$AT_Executive, s$CH_Executive)
s[, insample := as.integer(!(ex %in% c("  Nein", "Nein  ", " Kein Vorstandsmitglied ", " Bezirksvorstand ")) & Rough_Ideology != "")]
s[, nid := .I]
rows <- list()
for (t in 1:8) {
  ch <- paste0(s[[paste0("Left_Choice_", t)]], s[[paste0("Center_Choice_", t)]], s[[paste0("Right_Choice_", t)]])
  stopifnot(ch %in% c("", "Kandidat A", "Kandidat B"))
  sh <- pick(paste0(t, "c"))
  for (p in 1:2) {
    pr <- pick(paste0(t, c("a", "b")[p]))
    z <- tstrsplit(pr, "_", fill = NA)
    rows[[length(rows) + 1]] <- data.table(nid = s$nid, task = t, profile = p,
      choice = fifelse(ch == "", NA_integer_, as.integer(ch == c("Kandidat A", "Kandidat B")[p])),
      attr_age = sq(z[[1]]), attr_gender = sq(z[[2]]), attr_education = sq(z[[3]]), attr_experience = sq(z[[4]]),
      attr_issue = sq(z[[5]]), attr_ideology = sq(z[[6]]), trial_list_share = sq(sh))
  }
}
d <- rbindlist(rows)[!is.na(choice)]
stopifnot(!anyNA(d), d[, all(attr_age != "" & trial_list_share != "")], d[, uniqueN(trial_list_share)] == 5,
          d[, uniqueN(attr_gender)] == 2, d[, uniqueN(attr_ideology)] == 4)
stopifnot(d[, .(s = sum(choice), n = .N), .(nid, task)][, all(s == 1 & n == 2)])
cv <- s[, .(nid, cov_country = Country, cov_party_family = PartyFam, cov_party_quota = Quota,
            cov_ideology_group = Rough_Ideology, cov_left_right = as.integer(Ideology),
            cov_economic_position = as.integer(Economic_Pos), cov_gender = Gender, cov_age_group = Age,
            cov_education = Education, cov_migration = Migration, cov_in_authors_sample = insample)]
for (v in names(cv)) if (is.character(cv[[v]])) cv[get(v) == "", (v) := NA]
d <- merge(d, cv, by = "nid")
used <- sort(unique(d$nid)); d[, id := match(nid, used)][, nid := NULL]
stopifnot(uniqueN(d$id) == 1856, s[insample == 1, .N] == 1389, d[cov_in_authors_sample == 1, uniqueN(id)] == 1343)
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gatto_2025_candidate_selection.csv"))
