##Factorial vignette experiments (Kosovo) from
##Krakowski, K., & Kursani, S. (2023). Why do people use informal justice? Experimental
##evidence from Kosovo. Journal of Experimental Political Science.
##https://doi.org/10.1017/XPS.2023.18
##Replication data: Harvard Dataverse doi:10.7910/DVN/KD3ZUN, CC0 1.0, no restricted files,
##no terms. File read: kosovo_survey.dta (Dataverse "original format" download of
##kosovo_survey.tab). Read as text: README.txt, 1_main_survey.do (the authors' keyword coding
##of the vignettes), kosovo_questionnaire.doc (English instrument, converted to text), and
##the article's online supplement (sampling, Table A1).
##Usage: Rscript krakowski_2023.R <raw dir> <output dir>
##
##2,405 Albanian-speaking adults in Kosovo, face-to-face at home in Albanian by co-ethnic
##enumerators (multi-stage stratified random sample, 1,000 in Prishtina; supplement A.2).
##The deposit stores the full Albanian text each respondent heard for every vignette
##(kept as trial_vignette_text). Factor levels were read from that text with the authors'
##keywords (1_main_survey.do) and are stored as the ENGLISH wording of the questionnaire
##(label_language en; respondents heard Albanian). Every vignette parses to exactly one level
##of each factor (checked). First names of the characters were filled from a list of Albanian
##names (not a design factor in the article; visible only in trial_vignette_text). The
##sentence order of the three manipulated clauses varies across vignettes; attrpos_* give
##each clause's position (1-3), found from its place in the stored text.
##
##TWO TABLES (separate experiments, different factors and outcomes):
##
##1. krakowski_2023_informal_justice (the article's experiment). Each respondent heard 2 of
##   4 dispute vignettes (task 1 = VINJETA1RANDOM, task 2 = VINJETA2RANDOM; profile = 1):
##   attr_dispute (questionnaire heading: Property [inheritance of land], Domestic violence,
##   Debt, Murder) and three binary clauses about the person seeking resolution:
##     attr_resources: "wealthy" / "poor" (Debt: "financially doing well" / "financially doing
##       poorly"), questionnaire H1;
##     attr_court_speed: "very quickly" / "very slowly" (thought the state courts would solve
##       the problem ...), H2;
##     attr_community: "everybody around him|her|them" / "nobody around him|her|them" (believed
##       that ... resolved such problems through the state), H3; pronoun as in the
##       questionnaire for that dispute.
##   The resources and community wording depends on the dispute (restrictions = yes), and in
##   the data every respondent heard one civil (Property or Debt) and one criminal (Domestic
##   violence or Murder) dispute, the four pairings about equally often (593-608 each).
##   Outcomes (each 3 options: state authority / religious cleric [the .dta label says "a
##   local imam"] / mediation according to tradition and Kanun), split into 0/1 indicators,
##   as in other nominal-outcome tables:
##     rating_tried_state, rating_tried_cleric, rating_tried_kanun: "Now, knowing this about
##       <name>, how do you think he/she/they tried to resolve this problem?" (PERGJIGJJETAI1/2)
##     rating_should_state, rating_should_cleric, rating_should_kanun: "Now I want to ask you,
##       in your opinion, how do you think people should resolve this issue?" (PERGJIJETAI1,
##       PERGJIJETAI21)
##   The article's outcome is informal = cleric or Kanun on the "tried" question. Per-dispute
##   counts 1,201 / 1,204 / 1,215 / 1,190 vignettes reproduce supplement Table A1's Ns, and
##   its standardized coefficients reproduce (Debt and Inheritance exactly; Domestic violence
##   and Murder within 0.003).
##
##2. krakowski_2023_violence: each respondent heard all 3 violence vignettes in random order
##   (task 1-3 = VINJETAEDHUNES1/2/3RANDOM): attr_event (foreign militancy: went to Syria in
##   2015 to take part in the armed conflict / nationalist riot against Serbs on the Mitrovica
##   bridge in 2014 / violent protest in Prishtina [questionnaire: "against corruption"; the
##   stored Albanian text says 2014, the questionnaire 2016]) and three clauses:
##     attr_job (event-specific: Syria "but couldn't find a job for many years" / "and had a
##       job with a good salary"; riot "but couldn't find a suitable job for years" / "and was
##       working in a law office"; protest "working in a parking lot" / "working in a bank"),
##     attr_community_tie "very detached from the community" / "very attached to the community",
##     attr_encourager "his brother" / "a person he had recently met online" (questionnaire:
##       "<name>'s brother" / "a person that <name> recently had met online").
##   rating = "...what do you think of his decision to ...? His decision was:" 1 Completely
##   expected, 2 Expected to some extent, 3 Neutral to his decision, 4 Unexpected to some
##   extent, 5 Completely unexpected (.dta value labels; stored raw, so HIGHER = MORE
##   UNEXPECTED). This experiment is not analysed in the article.
##
##Covariates (.dta value labels as text): cov_gender (Q2, recorded by the enumerator: Male =
##male, Female = female), cov_age (Q3, years), cov_education (Q4 label text), cov_marital
##(Q5), cov_years_in_neighborhood (Q6), cov_household_size (Q7), cov_trust_justice (Q8 "How
##much do you trust the current Kosovo justice system?" label text), cov_municipality
##(KOMUNA), cov_settlement (VENDBANIMI, Urban/Rural), cov_survey_weight (Weights, "Weights by
##municipality", used in supplement Table A3).
##PII: the .dta holds LATITUDE/LONGITUDE of the interview and free text (Q26TJETER); dropped
##along with all other questions. Respondent ID re-keyed to integers in file order.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "kosovo_survey.dta"))
stopifnot(nrow(k) == 2405L, !anyDuplicated(k$ID))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
cov <- data.table(id = seq_len(nrow(k)),
  cov_gender = c(Male = "male", Female = "female")[lab(k$Q2)], cov_age = as.integer(zap_labels(k$Q3)),
  cov_education = lab(k$Q4), cov_marital = lab(k$Q5), cov_years_in_neighborhood = as.integer(zap_labels(k$Q6)),
  cov_household_size = as.integer(zap_labels(k$Q7)), cov_trust_justice = lab(k$Q8),
  cov_municipality = trimws(lab(k$KOMUNA)), cov_settlement = lab(k$VENDBANIMI),
  cov_survey_weight = as.numeric(k$Weights))
stopifnot(!anyNA(cov$cov_gender))
hit <- function(txt, pat) grepl(pat, tolower(txt), fixed = TRUE)
pos <- function(txt, pats) { p <- sapply(pats, function(z) regexpr(z, tolower(txt), fixed = TRUE)); max(p) }

## ---- 1. informal justice ----
j <- rbind(data.table(id = cov$id, task = 1L, txt = k$VINJETA1RANDOM, tr = as.integer(k$PERGJIGJJETAI1), sh = as.integer(k$PERGJIJETAI1)),
           data.table(id = cov$id, task = 2L, txt = k$VINJETA2RANDOM, tr = as.integer(k$PERGJIGJJETAI2), sh = as.integer(k$PERGJIJETAI21)))
j[, profile := 1L]
j[, `:=`(debt = hit(txt, "borg"), inh = hit(txt, "toke"), dom = hit(txt, "rrahur"), mur = hit(txt, "rinj"))]
stopifnot(j[, all(debt + inh + dom + mur == 1)])
j[, attr_dispute := fifelse(inh, "Property", fifelse(dom, "Domestic violence", fifelse(debt, "Debt", "Murder")))]
j[, poor := hit(txt, "varf") | hit(txt, "dobët")][, rich := hit(txt, "pasur") | hit(txt, "mirë financiare")]
j[, slow := hit(txt, "ngadal")][, fast := hit(txt, "shpejt")]
j[, nobody := hit(txt, "askush në rrethin")][, everybody := hit(txt, "të gjithë në rrethin")]
stopifnot(j[, all(poor + rich == 1 & slow + fast == 1 & nobody + everybody == 1)],
          j[, all(hit(txt, "nuk p") == nobody)])   # authors' conventions keyword agrees
j[, attr_resources := fifelse(debt, fifelse(poor, "financially doing poorly", "financially doing well"), fifelse(poor, "poor", "wealthy"))]
j[, attr_court_speed := fifelse(slow, "very slowly", "very quickly")]
pr <- c(Property = "him", `Domestic violence` = "her", Debt = "him", Murder = "them")
pron <- c(him = "rrethin e tij", her = "rrethin e saj", them = "rrethin e tyre")
j[, pn := pr[attr_dispute]]
stopifnot(j[, all(mapply(hit, txt, pron[pn]))])
j[, attr_community := paste(fifelse(nobody, "nobody", "everybody"), "around", pn)]
## clause positions: resources / court speed / community, by first keyword position in the text
j[, p_res := mapply(function(t) pos(t, c("varf", "dobët", "pasur", "mirë financiare")), txt)]
j[, p_spd := mapply(function(t) pos(t, c("ngadal", "shpejt")), txt)]
j[, p_com := mapply(function(t) pos(t, c("askush në rrethin", "të gjithë në rrethin")), txt)]
j[, c("attrpos_resources", "attrpos_court_speed", "attrpos_community") :=
      as.data.table(t(apply(cbind(p_res, p_spd, p_com), 1, function(r) as.integer(rank(r)))))]
stopifnot(j[, all(p_res > 0 & p_spd > 0 & p_com > 0)], j[, all(tr %in% 1:3 & sh %in% 1:3)])
for (o in c("tried", "should")) { v <- j[[c(tried = "tr", should = "sh")[o]]]
  for (i in 1:3) j[, paste0("rating_", o, "_", c("state", "cleric", "kanun")[i]) := as.integer(v == i)] }
j[, trial_vignette_text := txt]
stopifnot(identical(j[, .N, attr_dispute][order(attr_dispute), N], c(1201L, 1215L, 1190L, 1204L)))  # Debt, Domestic, Murder, Property = Table A1
ji <- merge(j[, c("id", "task", "profile", grep("^(rating|attr|attrpos|trial)_", names(j), value = TRUE)), with = FALSE], cov, by = "id")
setcolorder(ji, c("id", "task", "profile", grep("^rating_", names(ji), value = TRUE), grep("^attr_", names(ji), value = TRUE)))
setorder(ji, id, task, profile)
fwrite(ji, file.path(out, "krakowski_2023_informal_justice.csv"))

## ---- 2. violence ----
v <- rbindlist(lapply(1:3, function(t) data.table(id = cov$id, task = t, txt = k[[paste0("VINJETAEDHUNES", t, "RANDOM")]],
                                                  rating = as.integer(k[[paste0("PERGJIGJETRD5", t)]]))))
v[, profile := 1L]
v[, `:=`(syria = hit(v$txt, "siri"), riot = hit(v$txt, "mitrovic"), prot = hit(v$txt, "protest"))]
stopifnot(v[, all(syria + riot + prot == 1)], v[, all(rating %in% 1:5)], v[, uniqueN(paste(syria, riot)), id][, all(V1 == 3)])
v[, attr_event := fifelse(syria, "went to Syria to participate in the armed conflict",
                   fifelse(riot, "participated in a violent riot against the Serbs on the Mitrovica bridge",
                           "participated in a violent protest in Prishtina"))]
v[, nojob := hit(txt, "nuk mund të gjente punë")][, parking := hit(txt, "vend parkimi")]
v[, job := hit(txt, "pagë të mirë") | hit(txt, "zyre ligjore") | hit(txt, "bankë")]
stopifnot(v[, all(nojob + parking + job == 1)], v[prot == TRUE, all(!nojob)], v[prot == FALSE, all(!parking)])
v[, attr_job := fifelse(syria, fifelse(nojob, "but couldn't find a job for many years", "and had a job with a good salary"),
                fifelse(riot, fifelse(nojob, "but couldn't find a suitable job for years", "and was working in a law office"),
                        fifelse(parking, "working in a parking lot", "working in a bank")))]
v[, det := hit(txt, "shkëput")][, att := hit(txt, "i lidhur me shoqërinë")]
v[, bro := hit(txt, "vëllau i")][, onl := hit(txt, "takuar së fundmi online")]
stopifnot(v[, all(det + att == 1 & bro + onl == 1)])
v[, attr_community_tie := fifelse(det, "very detached from the community", "very attached to the community")]
v[, attr_encourager := fifelse(bro, "his brother", "a person he had recently met online")]
v[, p_job := mapply(function(t) pos(t, c("nuk mund të gjente punë", "pagë të mirë", "zyre ligjore", "vend parkimi", "punësuar në një bankë")), txt)]
v[, p_tie := mapply(function(t) pos(t, c("shkëput", "i lidhur me shoqërinë")), txt)]
v[, p_enc := mapply(function(t) pos(t, c("vëllau i", "takuar së fundmi online")), txt)]
stopifnot(v[, all(p_job > 0 & p_tie > 0 & p_enc > 0)])
v[, c("attrpos_job", "attrpos_community_tie", "attrpos_encourager") :=
      as.data.table(t(apply(cbind(p_job, p_tie, p_enc), 1, function(r) as.integer(rank(r)))))]
v[, trial_vignette_text := txt]
vi <- merge(v[, c("id", "task", "profile", "rating", grep("^(attr|attrpos|trial)_", names(v), value = TRUE)), with = FALSE], cov, by = "id")
setorder(vi, id, task, profile)
fwrite(vi, file.path(out, "krakowski_2023_violence.csv"))
