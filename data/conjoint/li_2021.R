##Chinese public opinion on government intervention / peacekeeping, two factorial vignette experiments, from
##Li, X., & Chen, D. (2021). Public opinion, international reputation, and audience costs in an authoritarian
##regime. Conflict Management and Peace Science (published online 2020, doi 10.1177/0738894220906374).
##Replication data: Harvard Dataverse doi:10.7910/DVN/QVTAKG, CC0 1.0. Files read: "wave 1+2.tab" and "wave 3.tab"
##(Dataverse original-format Stata downloads, saved here as w12.dta and w3.dta), the authors' "wave 1+2.do" and
##"wave 3.do" (read as text, not run) and "Online Appendix.pdf" (vignette wording and questionnaire).
##Usage: Rscript li_2021.R <dir holding w12.dta and w3.dta> <output dir>
##
##Two tables, because the attribute sets differ (an invasion-and-intervention scenario vs a UN-peacekeeping
##scenario, each fielded to its own sample):
##li_2021_china_intervention: waves 1 and 2 (Chinese adults, online; 1,037 + 2,224 = 3,261), pooled with
##  trial_wave because the authors pool them (one "wave 1+2" file and pooled figures) and the design is identical.
##  One vignette per respondent, 2^4 factorial of context facts x one of five randomized government-behaviour
##  scenarios. Attributes (appendix English text; labels in the dta: regime 0 dictatorship / 1 democracy, goal 0 historical
##  feud / 1 more resource, cost 0 low / 1 high, interest 0 no impact / 1 high impact):
##  attr_regime ("led by a dictator, who invaded" / "democratically elected government, which invaded"),
##  attr_goal, attr_military (strong military: major effort for China to push them out / weak military: no major
##  effort; the authors' variable `cost`), attr_interests (a victory would hurt / not affect China's economic and
##  security interests), attr_government_behavior (q1random 1-5: 1 not intervene, 2 threat then no troops, 3 troops
##  to the border but no fighting, 4 fought, no casualties, then pulled back, 5 fought, 200 casualties, then pulled back;
##  the order matches the do-file coefficient labels). Presentation text, profile = 1, task = 1, id = row number.
##  Outcome rating = approval of how the Chinese government handled the situation on a 5-point scale,
##  1 strongly disapprove ... 5 strongly approve, the authors' q1rating2 (for wave 1 their collapse of the 7-point
##  branching answer: 1-2 disapprove strongly/somewhat, 3-5 neutral incl. leaners, 6-7 approve somewhat/strongly;
##  rebuilt from q1response and checked equal). rating_7pt = wave 1 only q1response 1 strongly disapprove ... 7 strongly
##  approve (wave 2 NA). DIRECTION CAVEAT: for wave 2 the authors' flags (dis, app, strongdis, strongapp) treat q1rating 1-2 as
##  disapprove and 5 as strongly approve, although the questionnaire lists "Strongly approve" first; the authors' coding is kept
##  (wave 2 approval is much lower than wave 1, which hints that the stored coding might be reversed; unresolved).
##  Rows with no outcome (3 in wave 1) omitted.
##li_2021_china_peacekeeping: wave 3 (2,114 adults), same four context facts (the military-strength fact is replaced by
##  the size of the conflict zone: large, requiring significant contributions of material and human resources / small,
##  small contributions) and four behaviour scenarios (q2: 1 neutral, did not participate; 2 promised, sent no
##  peacekeepers; 3 sent peacekeepers; 4 sent then withdrew; all with the operation failing). The wave-3 export has
##  unlabelled q1-q31; levels follow the do-file recodes (regime=1 if q1>=9; goal, cost, interest listed there by q1 code)
##  and the appendix bracket order, which agrees with the wave-1/2 labels. Outcome rating = q3 evaluation: stored
##  1 approve, 2 disapprove, 3 neutral (do-file); RECODED here to an ordered 1 disapprove, 2 neutral, 3 approve. The follow-up strength
##  questions (q4-q6) are not used (option order not labelled).
##Covariates: cov_gender (waves 1-2 `male`, equal to the text `gender` where that is filled (wave 1; 14 wave-1 rows with blank gender and age are NA although the authors' male = 1); wave 3 q22 1 male 2 female per appendix), cov_age (years; wave 1 age and wave 3
##  q23, kept only if 16-100), cov_age_group (wave 2 six bands from the appendix), cov_education (wave 3 q25, the appendix
##  nine-category list), cov_political_affiliation (wave 1 `political` mapped ccp/cyp/dem/none; wave 2 only has a CCP-member dummy, so NA; wave 3 q28 1-4).
##Dropped: free text (q7, q15, q16), job, province and region (location), income, social status, news interest, the
##  authors' dummies and derived variables.
##Count check: 1,037 + 2,224 + 2,114 = 5,375 respondents = the paper's 5,375 Chinese adults.
##Restrictions: none stated; the 16 context cells are balanced (130-137 per cell in wave 3).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
w <- as.data.table(read_dta(file.path(raw, "w12.dta")))
stopifnot(all(w$male %in% 0:1), all(w$gender[w$wave == 1 & w$gender != ""] == c("Female", "Male")[w$male[w$wave == 1 & w$gender != ""] + 1L]), nrow(w) == 3261, all(w$q1random %in% 1:5), all(w$regime %in% 0:1))
w[, id := .I]
sc1 <- c("The Chinese government said it will not intervene in the conflict. Country A continued to attack; in the end, the Chinese government did not send troops, and the invading country prevailed.",
 "The Chinese government said if the invading country did not stop attacking, China would send troops to intervene. Country A continued to attack; in the end, the Chinese government did not send troops, and the invading country prevailed.",
 "The Chinese government said if the invading country did not stop attacking, China would send troops to intervene. Country A continued to attack; The Chinese government sent troops to the border but did not intervene in the conflict. In the end, the invading country prevailed.",
 "The Chinese government said if the invading country did not stop attacking, China would send troops to intervene. Country A continued to attack; The Chinese government sent in the troops, which destroyed a part of the military power of the invading countries and incurred no casualties; Country A continued its invasion, while Chinese troops pulled back. In the end, the invading country prevailed.",
 "The Chinese government said if the invading country did not stop attacking, China would send troops to intervene. Country A continued to attack; The Chinese government sent in the troops, which destroyed a part of the military power of the invading countries and incurred 200 casualties; Country A continued its invasion, while Chinese troops pulled back. In the end, the invading country prevailed.")
# check the authors' 5-point rating against a rebuild from raw answers
w[wave == 1, r5 := fcase(q1response %in% 1:2, as.numeric(q1response), q1response %in% 3:5, 3, q1response == 6, 4, q1response == 7, 5)]
w[wave == 2, r5 := as.numeric(q1rating)]
stopifnot(all(w$r5 == w$q1rating2, na.rm = TRUE), sum(is.na(w$r5)) == 3)
pol <- c(none = "No affiliation", ccp = "Chinese Communist Party member", cyp = "Chinese Youth League member", dem = "Member of other democratic parties")
agb <- c("Less than 20", "20-29", "30-39", "40-49", "50-59", "60 and above")
d1 <- data.table(id = w$id, task = 1L, profile = 1L, rating = as.integer(w$r5),
  rating_7pt = ifelse(w$wave == 1, as.integer(w$q1response), NA_integer_),
  attr_regime = c("a dictator, who invaded", "a democratically elected government, which invaded")[w$regime + 1],
  attr_goal = c("because of a longstanding historical feud", "to get more power and resources")[w$goal + 1],
  attr_military = c("a weak military, so it would not have taken a major effort for China to help push them out",
                    "a strong military, so it would have taken a major effort for China to help push them out")[w$cost + 1],
  attr_interests = c("A victory by the attacking country would not affect China's economic and security interests",
                     "A victory by the attacking country would hurt China's economic and security interests")[w$interest + 1],
  attr_government_behavior = sc1[w$q1random],
  cov_gender = ifelse(w$wave == 1 & w$gender == "", NA, c("female", "male")[w$male + 1L]),
  cov_age = ifelse(w$wave == 1 & w$age >= 16 & w$age <= 100, as.integer(w$age), NA_integer_),
  cov_age_group = ifelse(w$wave == 2, agb[as.integer(w$age_group)], NA_character_),
  cov_political_affiliation = ifelse(w$wave == 1 & w$political != "", unname(pol[w$political]), NA_character_),
  trial_wave = as.integer(w$wave))
d1 <- d1[!is.na(rating)]
stopifnot(nrow(d1) == 3258, !anyNA(d1$attr_goal), !anyNA(d1$attr_government_behavior), !anyNA(d1$attr_military))
setorder(d1, id, task, profile); fwrite(d1, file.path(out, "li_2021_china_intervention.csv"))
# wave 3
v <- as.data.table(read_dta(file.path(raw, "w3.dta")))
stopifnot(nrow(v) == 2114, all(v$q1 %in% 1:16), all(v$q2 %in% 1:4), all(v$q3 %in% 1:3))
v[, id := .I]
chk <- function(x) as.integer(x)
reg <- as.integer(v$q1 >= 9)
goal <- as.integer(v$q1 %in% c(1:4, 9:12)); cost <- as.integer(v$q1 %in% c(1, 2, 5, 6, 9, 10, 13, 14)); int <- as.integer(v$q1 %% 2 == 1)
sc3 <- c("The Chinese government said it would remain neutral about the conflict and did not participate in UN peacekeeping operations. The peacekeeping operations eventually failed, and the humanitarian crisis in the conflict zone continued to worsen.",
 "The Chinese government committed to participating in United Nations peacekeeping operations, but did not actually send peacekeepers. The peacekeeping operations eventually failed, and the humanitarian crisis in the conflict zone continued to worsen.",
 "The Chinese government committed to participating in United Nations peacekeeping operations, and sent peacekeepers to the conflict zone. The peacekeeping operations eventually failed, and the humanitarian crisis in the conflict zone continued to worsen.",
 "The Chinese government committed to participating in United Nations peacekeeping operations. It initially sent peacekeepers to the conflict zone but withdrew during the middle of the operation. The peacekeeping operations eventually failed, and the humanitarian crisis in the conflict zone continued to worsen.")
edu <- c("No formal education", "Primary school", "Junior high school", "Senior high school", "Technical or Vocational school",
         "Associate degree", "Bachelor's degree", "Master's degree", "PhD")
pol3 <- c("No affiliation", "Chinese Communist Party member", "Chinese Youth League member", "Member of other democratic parties")
stopifnot(all(v$q22 %in% 1:2), all(v$q25 %in% 1:9), all(v$q28 %in% 1:4))
d3 <- data.table(id = v$id, task = 1L, profile = 1L, rating = c(3L, 1L, 2L)[v$q3],
  attr_regime = c("a dictator, who invaded", "a democratically elected government, which invaded")[reg + 1],
  attr_goal = c("because of a longstanding historical feud", "to get more power and resources")[goal + 1],
  attr_conflict_zone = c("small, and thus requires small contributions of material and human resources from China",
                         "large, and thus requires significant contributions of material and human resources from China")[cost + 1],
  attr_interests = c("failure of the peacekeeping operation would not affect China's economic and security interests",
                     "failure of the peacekeeping operation would hurt China's economic and security interests")[int + 1],
  attr_government_behavior = sc3[v$q2],
  cov_gender = c("male", "female")[v$q22], cov_age = ifelse(v$q23 >= 16 & v$q23 <= 100, as.integer(v$q23), NA_integer_),
  cov_education = edu[v$q25], cov_political_affiliation = pol3[v$q28])
stopifnot(!anyNA(d3$attr_goal), d3[, uniqueN(.SD), .SDcols = patterns("^attr_")] == 16 * 4)
setorder(d3, id, task, profile); fwrite(d3, file.path(out, "li_2021_china_peacekeeping.csv"))
