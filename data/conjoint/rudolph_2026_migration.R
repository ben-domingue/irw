##Environmental-migration vignette experiment (rural Bangladesh, 2021) from
##Rudolph, L. (2026). Vignette experiments can replicate actual behavioral intent and partly actual
##behavior: Panel evidence on environmental migration from Bangladesh. Journal of Experimental
##Political Science, 1-22 (First View). https://doi.org/10.1017/XPS.2026.10035
##Replication data: Harvard Dataverse doi:10.7910/DVN/CON75O, CC0 1.0, no restricted files.
##File read: replication_rec.dta (Dataverse "original format"; the author's recoded panel file,
##household heads, waves 1-4; only wave 1, when the vignette was asked, is used). helpfile.txt,
##data_preparation.do and data_analysis.do read as text (not run). Vignette and question text:
##the wave-1 English questionnaire bemp_w1_questionnaire.pdf (Q246-Q248, pp. 61-64) from the
##project's full data release, Zenodo doi:10.5281/zenodo.18229498 (CC BY 4.0), file
##bemp_questionnaires.zip.
##Usage: Rscript rudolph_2026_migration.R <raw dir> <output dir>
##
##Bangladesh Environmental Mobility Panel, wave 1 (pre-monsoon, May-June 2021): face-to-face
##interviews of household heads along the Jamuna river (interviews in Bengali; only the English
##master questionnaire survives, so the stored text is English). Each respondent heard ONE vignette
##(task = 1, profile = 1), drawn uniformly from six (questionnaire: "16.6% of Sample" each), a 3 x 2
##design of hypothetical damage (none / medium / high) x future risk (low / high): hyp_group 1-6 =
##questionnaire treatment groups 0-5 (data_preparation.do L43 labels: 1 no damage/risk, 2 medium
##damage high risk, 3 high damage high risk, 4 medium damage low risk, 5 high damage low risk, 6 no
##damage high risk).
##Attributes = the two parts of the vignette as read out (after "Now I would like you to imagine
##the following situation for your household:"):
##  attr_situation: what happens to the village, the household and the neighbours. Four texts:
##     normal year (group 0), flood destroys half (groups 1, 3), erosion destroys all (groups 2, 4),
##     village hit but own household spared (group 5).
##  attr_outlook: what the village elders expect, the villagers' mood and the government's
##     protection. Four texts: stays like this / good hope (group 0), likely again / dire spirits /
##     government "cannot install any" protection (groups 1, 2), the same with "cannot install flood
##     and erosion protection" (group 5), bad luck / hold up spirits / government installs (3, 4).
##  The parts are not separately randomized: the six vignettes are fixed combinations, so the
##  no-damage situation text differs by risk (restriction). trial_design_cell = the author's label
##  of the cell (hyp_group value label), so the damage x risk factors can be used directly.
##Outcome: "If you were in this situation, would you stay here in your present village or would you
##prefer to move to another place?" (Stay in present village / Move somewhere else / Depends,
##recorded only if unprompted / RA). If "depends": "Now, if you really had to choose, would you stay
##in your present home or move somewhere else?" choice = the author's narrow migration intent
##(hyp_choice_forced): 1 = move (first or forced follow-up answer), 0 = stay. Single-profile
##stay/move question, so staying is the outside option (opt_out = yes). trial_depends = 1 if the
##first answer was "depends" (the choice then comes from the follow-up), else 0.
##Sample: 1,684 wave-1 household heads; 1,561 heard a vignette (hyp_group non-missing; the
##article's 1,561); 27 more refused/no answer (first answer RA or follow-up RA) and are omitted,
##leaving 1,534 respondents (= the author's narrow-intent N).
##Dropped: waves 2-4 (real-world outcomes), pid / hh_id / id (project household codes with
##location and zone, re-keyed to integers in file order), location and village codes, the author's
##derived dummies, indices and other hypothetical items. No survey weight.
##Covariates (wave 1): cov_age (years), cov_gender (sex: 0 = female, 1 = male; .dta label
##"gender=male"), cov_education (the author's recode labels, e.g. "edu: illiterate" ... "edu:
##higher"), cov_district (district name), cov_zone (distance band to the river at sampling, label
##text), cov_attachment (place attachment 1-5), cov_risk_pref (risk preference 1-5), cov_land_size.
##Check: lm(choice ~ damage + risk) on this table reproduces the author's data_analysis.smcl log
##(reg hyp_choice_forced i.damage i.risk2): N = 1,534; medium .0605, high .1357, high risk .0783,
##constant .1099.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- read_dta(file.path(raw, "replication_rec.dta"))
r <- r[r$wave_id == 1, ]
stopifnot(nrow(r) == 1684, !anyDuplicated(r$pid))
sit <- c(
  normal = "Assume that the next monsoon season the river is normal. There is flooding as you see it in a normal year in your village. Also, riverbank erosion is low. The flooding and erosion does not affect your household in an adverse way. Your neighbors are not particularly affected from floods or erosion either.",
  half = "Assume that the next monsoon season the river is bad. There is severe flooding in your village. At least, there is no riverbank erosion. But the flooding does affect your household very adversely. The floods damage and destroy half of your house, half of your belongings, and half of the things your life depends on (for example crop, livestock, assets). The neighbors in your village have also lost a lot.",
  all = "Assume that the next monsoon season the river is bad. There is severe flooding and riverbank erosion. The erosion destroys your house, your belongings, and most of the things your life depends on (for example crop, livestock, assets). The neighbors in your village have also lost a lot.",
  spared = "Assume that the next monsoon season the river is bad. There is severe flooding and riverbank erosion in the village. However, your family has been in good luck. Your house is not damaged and most of your belongings and most of the things your life depends on (for example crop, livestock, assets) are not permanently damaged. But many of your neighbors see that erosion and floods destroy their houses, belongings, and most of the things their life depends on (for example crop, livestock, assets).")
outl <- c(
  stay = "The elderly of the village analyze the situation and believe that it is going to stay like this in the subsequent year. The people of the village are in good hope. To make sure it stays like this, the government begins to install flood and erosion protection.",
  high = "The elderly of the village analyze the situation and believe that such a situation will likely happen again in the subsequent year. The people of the village agree and are in dire spirits. Unfortunately, the government cannot install any flood and erosion protection.",
  high5 = "The elderly of the village analyze the situation and believe that such a situation will likely happen again in the subsequent year. The people of the village agree and are in dire spirits. Unfortunately, the government cannot install flood and erosion protection.",
  low = "The elderly of the village analyze the situation and believe that such a situation was really bad luck. This is not likely to happen again in the subsequent year. The people of the village agree and, despite the losses, hold up their spirits. To make sure it stays like this, the government begins to install flood and erosion protection.")
# hyp_group 1..6 = questionnaire treatment groups 0..5
g_sit <- c("normal", "half", "all", "half", "all", "spared")
g_out <- c("stay", "high", "high", "low", "low", "high5")
lv <- attr(r$hyp_group, "labels")
stopifnot(identical(names(lv)[match(1:6, lv)], c("no damage/risk", "medium damage, high risk", "high damage, high risk",
                                                 "medium damage, low risk", "high damage, low risk", "no damage, high risk")))
hg <- as.integer(zap_labels(r$hyp_group)); h1 <- as.integer(zap_labels(r$hyp_choice)); h2 <- as.integer(zap_labels(r$hyp_choice_q2))
stopifnot(all(h1 %in% c(0:2, NA)), all(h2 %in% c(0, 1, 99, NA)), all(is.na(h2) | h1 %in% 2))
narrow <- as.integer(ifelse(h1 %in% 0:1, h1, ifelse(h1 %in% 2 & h2 %in% 0:1, h2, NA)))
stopifnot(identical(narrow, as.integer(zap_labels(r$hyp_choice_forced))))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
d <- data.table(id = seq_len(nrow(r)), task = 1L, profile = 1L, choice = narrow, hg = hg,
                attr_situation = unname(sit[g_sit[hg]]), attr_outlook = unname(outl[g_out[hg]]),
                trial_design_cell = names(lv)[match(hg, lv)], trial_depends = as.integer(h1 %in% 2),
                cov_age = as.integer(zap_labels(r$age)), cov_gender = c("female", "male")[as.integer(zap_labels(r$sex)) + 1L],
                cov_education = lab(r$education), cov_district = as.character(r$district), cov_zone = lab(r$zone),
                cov_attachment = as.integer(zap_labels(r$attachment)), cov_risk_pref = as.integer(zap_labels(r$risk_pref)),
                cov_land_size = as.numeric(r$land_size_total))
stopifnot(sum(!is.na(d$hg)) == 1561)
d <- d[!is.na(hg) & !is.na(choice)][, hg := NULL]
stopifnot(nrow(d) == 1534, !anyNA(d$attr_situation), !anyNA(d$attr_outlook))
d[, id := match(id, sort(unique(id)))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rudolph_2026_migration_vignette.csv"))
