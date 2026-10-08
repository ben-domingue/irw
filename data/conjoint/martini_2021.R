##"Good politician" candidate conjoint (Italy, 2019) from
##Martini, S., & Olmastroni, F. (2021). From the lab to the poll: The use of survey experiments in
##political research. Italian Political Science Review / Rivista Italiana di Scienza Politica, 51(2),
##231-249. https://doi.org/10.1017/ipo.2021.20
##Replication data: Harvard Dataverse doi:10.7910/DVN/AG0JK6, CC0 1.0. Files read (Dataverse "original
##format" .dta downloads): ConjointExp_goodpolitician_artisan.dta (file 4597987, the full sample),
##ConjointExp_goodpolitician.dta (4597986, for the populism items) and
##ConjointExp_goodpolitician_attention.dta (4597982, the attention-check subsample; used only for a flag).
##Value labels come from the .dta files; the authors' .do/.R files were read as text, not run.
##Usage: Rscript martini_2021.R <dir holding the three .dta files> <output dir>
##
##Wave 2 (28 May - 26 June 2019) of the University of Siena panel, a GfK Italy probability panel, adults
##only. Each respondent saw 2 pairs of candidates for the European Parliament; 8 attributes (gender, job
##position, communication style, social skills, integrity, competence, vision of role, leadership).
##The article: "all attributes were randomly assigned without restrictions on their possible
##combination"; the order of the attributes was randomized per respondent and fixed across the two
##pairs, but it is not in the deposit (no attrpos_).
##Sample: the article's analysed sample is n = 3,096, but its main models use 2,676 respondents (10,704
##profiles) from goodpolitician.dta. The deposit's "_artisan" file holds all 3,096: the 420 extra
##respondents each saw exactly one profile with job position "artisan", a level that the article's
##design count (1,536 combinations = 6 jobs) and main text leave out; the appendix model "full sample
##(artisan included)" uses all 3,096. This table keeps all 3,096 and the artisan level (420 of 12,384
##profiles, 3.4%, against about 16% for each other job): the artisan level was clearly not drawn
##uniformly, so restrictions = observed. Why artisan was dropped is not documented.
##task/profile: the source `profile` (Candidate 1-4) is mapped to task = 1 for candidates 1-2 and 2 for
##3-4, profile = position within the pair. This is inferred from row order and checked: exactly one
##candidate is chosen in each of the 6,192 pairs.
##Outcome: choice = CHO, "which of the two candidates would you personally have preferred to win a seat in
##the European Parliament" (article's English; forced choice, no opt-out). The article also reports a
##7-point favourability rating, but the deposit has only a 0/1 dichotomized version (RATE in
##goodpolitician_ratingd.dta, cut point undocumented), so no rating column is built.
##Attribute text: the English value labels of the .dta (the authors' translations; respondents saw
##Italian, the survey's own items in the .dta carry Italian labels). Kept exactly as labelled.
##Covariates: cov_survey_weight = weight1_istr_w2 (the authors' weight); cov_pop1_w1..cov_pop6_w1 and
##cov_pop1_w2..cov_pop6_w2 = the six populism items P10A-F in waves 1 and 2 (1 = Molto in disaccordo ..
##5 = Molto d'accordo; 97 = Non so / preferisco non rispondere, 98 = Ho un'opinione, ma preferisco non
##indicarla, 99 = Non ho un'opinione; codes kept); cov_attention_pass = 1 if the respondent is in the
##authors' attention-check subsample (2,428 respondents), 0 if not, blank for the 420 artisan respondents
##(the authors built that subsample from the 2,676 only, so their status is unknown). The populism items
##are joined from goodpolitician.dta by id (ids are shared across the deposit's files; checked) and are
##blank for the 420 artisan respondents, whose populism answers were not deposited.
##Dropped: the authors' populism indices and median splits (populism1/2, popmedian1/2).
##IDs are the authors' sequential integers 1-3,096.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "ConjointExp_goodpolitician_artisan.dta"))
lab <- function(x) { l <- attr(x, "labels"); y <- names(l)[match(as.numeric(x), l)]; stopifnot(!anyNA(y)); y }
d <- data.table(id = as.integer(s$id), task = as.integer((s$profile + 1) %/% 2), profile = as.integer(2 - s$profile %% 2),
                choice = as.integer(s$CHO))
map <- c(gender = "SESSO", job = "POS", communication = "STILE", social_skills = "CAPA", integrity = "INTE",
         competence = "COMPE", vision_of_role = "VISI", leadership = "LEAD")
for (v in names(map)) d[, paste0("attr_", v) := lab(s[[map[[v]]]])]
d[, cov_survey_weight := as.numeric(s$weight1_istr_w2)]
stopifnot(d[, .N, id][, all(N == 4)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
g <- as.data.table(zap_labels(read_dta(file.path(raw, "ConjointExp_goodpolitician.dta"))))
gp <- unique(g[, c("id", paste0("P10", LETTERS[1:6], "_W1"), paste0("P10", LETTERS[1:6], "_W2")), with = FALSE])
stopifnot(!anyDuplicated(gp$id))
setnames(gp, -1, c(paste0("cov_pop", 1:6, "_w1"), paste0("cov_pop", 1:6, "_w2")))
d <- merge(d, gp, by = "id", all.x = TRUE, sort = FALSE)
att <- unique(as.integer(read_dta(file.path(raw, "ConjointExp_goodpolitician_attention.dta"))$id))
d[, cov_attention_pass := fifelse(id %in% gp$id, as.integer(id %in% att), NA_integer_)]
stopifnot(uniqueN(d$id) == 3096L, sum(d$attr_job == "artisan") == 420L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "martini_2021_good_politician.csv"))
