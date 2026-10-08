##Democracy-promotion target conjoint (US, Prolific) from
##Escribà-Folch, A., Muradova, L. H., & Rodon, T. (2021). The effects of autocratic characteristics on
##public opinion toward democracy promotion policies: A conjoint analysis. Foreign Policy Analysis,
##17(1), 140-161. https://doi.org/10.1093/fpa/oraa016
##Replication data: Harvard Dataverse doi:10.7910/DVN/KGSGPW, CC0 1.0. Files read (Dataverse "original
##format"): data_analysis.xlsx (sheet data_final, the raw Qualtrics export) and socio_demo.xlsx
##(Prolific demographics). replication_readme.pdf, 01_clean&stack.R and replication_FPA.html read as
##text, not run. Wording from the article (author version, UPF repository).
##Usage: Rscript escribafolch_2021.R <dir holding the two .xlsx files> <output dir>
##
##US adults recruited on Prolific. 6 tasks, each a side-by-side pair of autocratic countries
##("Country A"/"Country B"), 9 attributes; the order of the attribute rows was randomized (per task in
##the data). Vignette: "The countries below are governed by an authoritarian regime ... Please read
##carefully the descriptions of the potential target countries and respond to the question below."
##Respondents then said, for each of the two countries separately, whether the US should use each of
##three tools (yes/no; any number of tools or none could be picked; not a choice between profiles):
##  rating_military_intervention, rating_economic_sanctions, rating_democracy_aid: 1 = yes, 0 = no.
##  Source codes 1/2 with 2 = yes (01_clean&stack.R recodes ==2 to 1; the yes shares, 13% military,
##  47% sanctions, 55% aid, match the article's Figure 2 ordering).
##There is no choice column. Columns follow the authors' mapping in 01_clean&stack.R: in task t the
##outcome block Q62/Q64/Q66/Q68/Q70/Q450 #1_1..3 (country A: military, sanctions, aid) and #2_1..3
##(country B), and the level block Q109/Q122/Q116/Q44/Q115/Q47 _1.._9 (A) and _10.._18 (B) in the
##fixed attribute order oil, ally, trade, years, power, leader, elections, religion, military (each
##column holds only that attribute's levels; checked). The _19 field lists the attribute row labels in
##the order shown; attrpos_<attr> is the position of that attribute's label (1-9).
##Attribute text as displayed (level strings in the export). No restrictions are stated; the article
##says each profile randomizes the nine attributes and their order.
##Sample: the deposit has 1,591 survey records fielded 25 May - 27 June 2017 (wave 1 = 1,487, wave 2 = 99,
##5 blank; kept as trial_wave). The article reports 1,464 respondents surveyed "between May and June
##2016"; the authors' code analyses all 1,591 records. Not reconciled here. One Prolific ID occurs
##twice, 4 records carry a Prolific completion URL instead of an ID and 104 have none; every record is
##kept as its own respondent, as the authors do. Tasks with no outcome are dropped; profiles keep a
##blank for an unanswered tool. Wave 2 used a different survey version: its records hold only 5 answered tasks,
##and for task 5 the levels were not saved (Q115 block empty) although the tools were answered, so
##wave-2 task 5 is dropped (101 respondents: 99 wave 2 and 2 with wave blank; the authors'
##complete-case models drop it too). In task 1 of those records three attribute row labels are
##spelled differently ("Natural Resources:", "The regime´s leader is...", "Years the regime has been
##in power..."), so the wave-2 screen text varied slightly.
##Covariates: cov_ideology = left_right_8 (1-7; the authors' code treats 1-3 as conservative, 4 moderate,
##5-7 liberal; wording not deposited). From socio_demo.xlsx, joined by Prolific ID where the ID occurs once
##in each file: cov_age, cov_sex, cov_education (Highest education level), cov_party (Political
##Affiliation (US)); Prolific's own profile fields, "N/A" stored as blank. Other survey items (control_1,
##war, leadersorexperts_*, promoting*, ps_*, pol_interest) are not documented and are dropped.
##PII in the deposit, not kept: ResponseId (V1), IP address (V6), Prolific IDs (prol_id; session_id and
##Participant id in socio_demo.xlsx), latitude/longitude, free-text feedback, randomization seeds.
##IDs are re-keyed to integers in file order (the authors' ID).
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_excel(file.path(raw, "data_analysis.xlsx"), sheet = "data_final"))
stopifnot(nrow(d) == 1591L)
oblock <- c(31, 58, 86, 114, 142, 171); ablock <- c(37, 64, 92, 120, 150, 179)
an <- c("oil", "ally", "trade", "years", "power", "leader", "elections", "religion", "military")
rowlab <- c("Natural resources:" = "oil", "International military alliance:" = "ally", "Trade relationships:" = "trade",
            "Years the regime has been in power:" = "years", "Political power and policy are controlled by..." = "power",
            "The regime's leader is..." = "leader", "Does the regime hold elections?" = "elections",
            "The country is predominantly..." = "religion", "The regime is militarily..." = "military",
            "Natural Resources:" = "oil", "The regime\u00b4s leader is..." = "leader", "Years the regime has been in power..." = "years")
yn <- function(x) { x <- as.integer(x); stopifnot(all(x %in% c(1L, 2L, NA))); as.integer(x == 2L) }
rows <- list()
for (t in 1:6) {
  ord <- strsplit(d[[ablock[t] + 18]], ",", fixed = TRUE)
  for (p in 1:2) {
    x <- data.table(id = seq_len(nrow(d)), task = t, profile = p,
                    rating_military_intervention = yn(d[[oblock[t] + 3 * (p - 1)]]),
                    rating_economic_sanctions = yn(d[[oblock[t] + 3 * (p - 1) + 1]]),
                    rating_democracy_aid = yn(d[[oblock[t] + 3 * (p - 1) + 2]]))
    for (j in 1:9) x[, paste0("attr_", an[j]) := d[[ablock[t] + 9 * (p - 1) + j - 1]]]
    for (j in 1:9) x[, paste0("attrpos_", an[j]) := vapply(ord, function(o) if (length(o) == 9) match(an[j], rowlab[o]) else NA_integer_, 1L)]
    x[, trial_wave := as.integer(d$wave)]
    rows[[length(rows) + 1]] <- x
  }
}
x <- rbindlist(rows)
x <- x[!(is.na(rating_military_intervention) & is.na(rating_economic_sanctions) & is.na(rating_democracy_aid))]
stopifnot(x[is.na(attr_oil), all(task == 5L & !trial_wave %in% 1L)], x[is.na(attr_oil), uniqueN(id)] == 101L)
x <- x[!is.na(attr_oil)]  # wave-2 task 5: answered, but its levels were not saved
stopifnot(!anyNA(x[, .SD, .SDcols = patterns("^attr")]))
lv <- list(oil = c("Oil-exporting country", "Non-oil-exporting country"), leader = c("A civilian who heads the regime's official party", "A member of the military", "A monarch"),
           years = c("4 years", "10 years", "25 years"), religion = c("Christian", "Muslim", "Buddhist"), military = c("Weak", "Strong"))
for (v in names(lv)) stopifnot(all(x[[paste0("attr_", v)]] %in% lv[[v]]))
s <- as.data.table(read_excel(file.path(raw, "socio_demo.xlsx")))
pid <- d$prol_id; ok <- !is.na(pid) & !pid %in% pid[duplicated(pid)] & !s$`Participant id`[match(pid, s$`Participant id`)] %in% s$`Participant id`[duplicated(s$`Participant id`)]
m <- match(ifelse(ok, pid, NA), s$`Participant id`)
na <- function(y) { y <- as.character(y); y[y %in% c("N/A", "")] <- NA; y }
cv <- data.table(id = seq_len(nrow(d)), cov_ideology = as.integer(d$left_right_8), cov_age = as.integer(na(s$Age[m])),
                 cov_sex = na(s$sex[m]), cov_education = na(s$`Highest education level`[m]), cov_party = na(s$`Political Affiliation (US)`[m]))
x <- merge(x, cv, by = "id")
setorder(x, id, task, profile)
fwrite(x, file.path(out, "escribafolch_2021_democracy_promotion.csv"))
