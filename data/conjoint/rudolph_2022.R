##Swiss corporate-responsibility law: conjoint and factorial vignette (Switzerland) from
##Rudolph, L., Kolcava, D., & Bernauer, T. (2023). Public demand for extraterritorial
##environmental and social public goods provision. British Journal of Political Science, 53(2),
##516-535. https://doi.org/10.1017/S0007123422000175 (online 2022)
##Replication data: Harvard Dataverse doi:10.7910/DVN/LQ5LYL, CC0 1.0, no restricted files, no
##terms. Files read: master.dta (Dataverse original format, Stata labels), survey_instrument.pdf
##("KVI Surveyv6", German Qualtrics printout), readme.txt; replication.do read as text.
##Usage: Rscript rudolph_2022.R <dir holding master.dta> <output dir>
##
##3,010 Swiss voters (article abstract N = 3,010; master.dta has 3,010 ids x 6 rows), surveyed in
##German, French or Italian (cov_language). Before both experiments a random half read a "norms"
##text on the UN norm that states must make their firms act responsibly abroad (Q9; trial_norms =
##normstreatment, 1 = shown). Two experiments on the same two policy dimensions, built as two
##tables (different designs):
##
##rudolph_2022_supply_law_conjoint: 3 paired tasks ("Vorschlag A/B" for a new law regulating
##Swiss firms abroad), 2 attributes x 3 levels: reciprocity (row "Die Schweiz verpflichtet ihre
##Firmen:") and stringency (row "Inhalt des Gesetzes:"). The conjoint cells were filled by script
##and their text is not in the instrument, so the levels are the .dta value labels (English):
##reciprocity "in any case" / "only w/ west" / "only w/ world"; stringency "round-tables" /
##"public report" / "liability" (the vignette below shows the full German wording of the same
##levels). Outcomes: rating = Q11/Q13/Q15 "Auf einer Skala von 1 (total dagegen) bis 7 (total
##dafür), wie stark sind Sie für oder gegen: Vorschlag A / Vorschlag B", 1-7 raw; choice =
##Q12/Q14/Q16 "Wenn Sie heute in einer Volksabstimmung zwischen beiden Vorschlägen entscheiden
##müssten, welchen Vorschlag würden Sie eher annehmen?" (A/B, no opt-out). In 70 tasks neither
##profile has policychosen = 1 (the source codes the unanswered choice 0): choice is set NA on
##both rows of those tasks (46 after the drop below); their ratings are kept. The 47 profile rows
##with neither a choice nor a rating are dropped (rows with no outcome are omitted), so 47 tasks
##keep only one profile row (choice NA there). Result: 17,937 rows, 3,006 respondents. task = `task`; profile = `conjoint` element order within the task (odd = 1, even =
##2), taken to be Vorschlag A / B: the codebook only says "Conjoint element 1 to 6" (inferred).
##Dropped: 38 tasks (38 respondents, 76 rows) whose two profiles have no reciprocity/stringency
##level in the source although choices and ratings exist (levels not saved).
##Levels drawn independently? Not documented (restrictions unknown); all 9 combinations occur.
##
##rudolph_2022_supply_law_vignette: one text vignette per respondent (Q17-Q25 = `lawtreat`, a
##full 3 x 3 of the same two dimensions; mapping as in replication.do L85-90): "Nehmen Sie nun
##einmal an, es hätte eine eidgenössische Volksabstimmung stattgefunden und ein neues Gesetz mit
##folgendem Inhalt sei angenommen worden und würde nun umgesetzt:" + a reciprocity sentence + a
##stringency sentence. Level text = those German sentences, verbatim from the instrument.
##Outcomes Q26 "Wenn ein neues Gesetz in dieser konkreten Form zustande gekommen und umgesetzt
##wäre, stimmen Sie persönlich den folgenden Aussagen zu oder nicht zu? Dieses Gesetz..." 7
##statements (q26_1..7: strengthens Swiss reputation, is good behaviour, is an expert solution, is
##costly, disadvantages Switzerland, reduces damage, is window-dressing; English from the .dta
##variable labels), 1 "stimme überhaupt nicht zu" .. 5 "stimme voll und ganz zu"; the
##instrument's 6 "Weiss nicht" is absent from the data (NA), as stored. Respondents with no
##answer to any statement are dropped.
##
##Covariates: cov_gender (wdummy, variable label "1=female, 0=male"), cov_age_group (agegroup
##value label text), cov_language (DE/FR/IT), cov_region (value label text), cov_env_concern_1..10
##(q60_*) and cov_social_concern_1..5 (q59_11..15), 1-5 as stored (item wording in the
##instrument, not mapped here). ids (8-9 digit panel numbers) re-keyed to integers.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
h <- read_dta(file.path(raw, "master.dta"))
lab <- function(x) { l <- attr(x, "labels"); names(l)[match(as.numeric(x), l)] }
x <- as.data.table(zap_labels(h))
x[, attr_reciprocity := lab(h$reciprocity)][, attr_stringency := lab(h$stringency)]
x[, agegroup_t := lab(h$agegroup)][, language_t := lab(h$language)][, region_t := lab(h$region)]
stopifnot(x[, .N, id][, all(N == 6)], uniqueN(x$id) == 3010, x[, uniqueN(lawtreat), id][, all(V1 == 1)])
ids <- data.table(id0 = sort(unique(x$id)))[, nid := .I]
x <- merge(x, ids, by.x = "id", by.y = "id0")
cov <- function(z) z[, .(cov_gender = fifelse(wdummy == 1, "female", fifelse(wdummy == 0, "male", NA_character_)),
                        cov_age_group = agegroup_t, cov_language = language_t, cov_region = region_t,
                        cov_env_concern_1 = q60_1, cov_env_concern_2 = q60_2, cov_env_concern_3 = q60_3,
                        cov_env_concern_4 = q60_4, cov_env_concern_5 = q60_5, cov_env_concern_6 = q60_6,
                        cov_env_concern_7 = q60_7, cov_env_concern_8 = q60_8, cov_env_concern_9 = q60_9,
                        cov_env_concern_10 = q60_10, cov_social_concern_1 = q59_11, cov_social_concern_2 = q59_12,
                        cov_social_concern_3 = q59_13, cov_social_concern_4 = q59_14, cov_social_concern_5 = q59_15)]
## conjoint
setorder(x, nid, conjoint)
stopifnot(x[, all(task == (conjoint + 1) %/% 2)], x[, sum(policychosen), .(nid, task)][, all(V1 <= 1)])
x[, profile := 2L - conjoint %% 2L]
x[, nch := sum(policychosen), .(nid, task)]
d <- x[, .(id = nid, task = as.integer(task), profile = as.integer(profile),
           choice = fifelse(nch == 1, as.integer(policychosen), NA_integer_), rating = as.integer(ratingConjoint),
           attr_reciprocity, attr_stringency, trial_norms = as.integer(normstreatment))]
d <- cbind(d, cov(x))
d <- d[!is.na(attr_reciprocity) & !is.na(attr_stringency)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], !anyNA(d$attr_reciprocity), !anyNA(d$attr_stringency))
cat("rows with no outcome dropped:", d[is.na(choice) & is.na(rating), .N], "\n")
d <- d[!(is.na(choice) & is.na(rating))]
cat("conjoint", nrow(d), uniqueN(d$id), d[, sum(is.na(choice)) / 2], "\n")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rudolph_2022_supply_law_conjoint.csv"))
## vignette
rec <- c("Die Schweiz verpflichtet ihre Firmen in jedem Fall zu einem stärkeren Schutz von Mensch und Umwelt im Ausland.",
         "Die Schweiz verpflichtet ihre Firmen nur dann zu einem stärkeren Schutz von Mensch und Umwelt im Ausland, wenn andere westliche Wirtschaftsnationen in Europa und Nordamerika (z.B. Deutschland und die USA) ihre Firmen auch dazu verpflichten.",
         "Die Schweiz verpflichtet ihre Firmen nur dann zu einem stärkeren Schutz von Mensch und Umwelt im Ausland, wenn andere Wirtschaftsnationen in Asien, Amerika und Europa (z.B. China, Brasilien, die USA oder Deutschland) ihre Firmen auch dazu verpflichten.")
str <- c("Firmen müssen sich an regelmässig stattfindenden Gesprächen dazu beteiligen, wie Mensch und Umwelt im Ausland besser geschützt werden können. Diese Gespräche werden von Wirtschaftsverbänden und dem Staatssekretariat für Wirtschaft organisiert.",
         "Firmen müssen jedes Jahr einen öffentlich zugänglichen, detaillierten Bericht über ihre Standorte im Ausland erstellen.",
         "Firmen müssen einen öffentlich zugänglichen, detaillierten Bericht über ihre Standorte im Ausland erstellen. Zudem können Schweizer Firmen für Schäden an Mensch und Umwelt, die sie im Ausland verursachen, nicht nur vor Ort im Ausland, sondern auch in der Schweiz vor Gericht gebracht werden.")
v <- x[conjoint == 1]
k <- as.integer(sub("Q", "", v$lawtreat)) - 16L
stopifnot(all(k %in% 1:9))
items <- c("reputation", "good_behaviour", "expert_solution", "costly", "disadvantages_ch", "reduces_damage", "window_dressing")
w <- data.table(id = v$nid, task = 1L, profile = 1L)
for (i in 1:7) w[, paste0("rating_", items[i]) := as.integer(v[[paste0("q26_", i)]])]
w[, attr_reciprocity := rec[(k - 1L) %/% 3L + 1L]][, attr_stringency := str[(k - 1L) %% 3L + 1L]]
w[, trial_norms := as.integer(v$normstreatment)]
w <- cbind(w, cov(v))
w <- w[rowSums(!is.na(w[, paste0("rating_", items), with = FALSE])) > 0]
stopifnot(w[, all(unlist(.SD) %in% c(1:5, NA)), .SDcols = patterns("^rating_")])
cat("vignette", nrow(w), "\n")
setorder(w, id, task, profile)
fwrite(w, file.path(out, "rudolph_2022_supply_law_vignette.csv"))
