##Image-based security-personnel conjoint (Mexico) from
##Flores-Macías, G., & Zarkin, J. (2022). Militarization and perceptions of law enforcement
##in the developing world: Evidence from a conjoint experiment in Mexico. British Journal of
##Political Science, 52(3), 1377-1397. https://doi.org/10.1017/S0007123421000259
##Replication data: Harvard Dataverse doi:10.7910/DVN/UMUEOK, CC0 1.0. File read:
##MilitConjoint.dta (Dataverse "original format"; the deposit lists it three times, same
##file). Subgroup_Results.R, Figure5_Figure.R, Figure6.R, RobustnessCheck_Effectiveness.R,
##TableA.2.do read as text. The article itself (paywalled) was not read.
##Usage: Rscript floresmacias_2022.R <dir holding MilitConjoint.dta> <output dir>
##
##1,205 respondents in Mexico (the abstract: "nationally representative"; skin tone is
##"surveyor perception", so interviews were probably in person; mode, firm and date not in
##the deposit), each shown ONE pair of photographs of security personnel (task = 1,
##profile = source `photo`). Four binary attributes, shown in the photo, not as text; the
##level text is the authors' factor labels from Subgroup_Results.R: uniform (Police /
##Military), weapon (None / Assault Rifle), gender (Female / Male), skin colour (Dark /
##Light; the .dta labels are Non-white / White). The 16 combinations are the 16 photos
##(`imageperson`, e.g. "Armed brown female police"), so the photo itself is not stored.
##The two photos in a pair always differ (checked); restrictions and weights are not
##documented. trial_prompt: the security prompt each respondent saw before the photos
##(.dta value labels "Fighting Crime" / "Public Security").
##Outcomes (wording NOT in the deposit; .dta variable labels):
##  choice = whicheffective, "Forced choice, who is more effective"; one per pair, no opt-out.
##  rating_effective ("Rating effectivenes"), rating_civil_liberties ("Rating civil
##  liberties"), rating_corrupt ("Rating corrupt"), rating_neighborhood ("Rating
##  neighborhood", acceptance of such personnel in one's own neighbourhood per the
##  abstract): each stored on the source's 0-1 scale, which takes 10 equally spaced values
##  (k/9), i.e. a 10-point item rescaled by the authors; the original endpoints and anchors
##  are not documented. Direction of rating_corrupt is NOT documented: it correlates weakly
##  positively with the other ratings (0.08), which suggests higher = less corrupt, but
##  this is not confirmed. No `rating` column: all four are named.
##Check: OLS of the standardized civil-liberties rating on the four attributes reproduces
##the deposit's All_CivLib.txt (gender -0.088, skin 0.038, uniform 0.078, weapon 0.133).
##Covariates (labels from the .dta): cov_female (sexo 2 = Female), cov_age (years),
##cov_education (ed_level text), cov_victim (crime victim in past 12 months, 1 = yes),
##cov_ideology (1 = Left to 10 = Right), cov_trust_army (1 = Not at all to 7 = Absolutely),
##cov_party (mixedPartyId text), cov_skin_tone (surveyor-perceived, 1 lightest to 11
##darkest), cov_state (state abbreviation).
##DROPPED: municipality code and name and the municipal homicide/confrontation measures
##(they locate the respondent to a municipality), household income code, the authors'
##dummies (trustarmy, upclass, old, mored, party and ideology dummies, light/dark, ...) and
##the standardized z* ratings.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "MilitConjoint.dta"))
s <- as.data.table(zap_labels(k))
stopifnot(nrow(s) == 2410, s[, .N, idresp][, all(N == 2)], s[, sort(unique(photo))] == 1:2,
          s[, sum(whicheffective), idresp][, all(V1 == 1)],
          s[, uniqueN(paste(uniform, weapon, gender, race)), idresp][, all(V1 == 2)], s[, uniqueN(mediation), idresp][, all(V1 == 1)])
lab <- function(v) { l <- attr(k[[v]], "labels"); names(l)[match(s[[v]], l)] }
d <- s[, .(id = as.integer(idresp), task = 1L, profile = as.integer(photo), choice = as.integer(whicheffective),
           rating_effective = effective, rating_civil_liberties = lib, rating_corrupt = corrupt, rating_neighborhood = neighb,
           attr_uniform = c("Police", "Military")[uniform + 1], attr_weapon = c("None", "Assault Rifle")[weapon + 1],
           attr_gender = c("Female", "Male")[gender + 1], attr_skin_color = c("Dark", "Light")[race + 1],
           cov_female = as.integer(sexo == 2), cov_age = as.integer(age), cov_victim = as.integer(vict),
           cov_ideology = as.integer(polspectrum), cov_trust_army = as.integer(army), cov_skin_tone = as.integer(skintone),
           cov_state = edo_name)]
d[, trial_prompt := lab("mediation")][, cov_education := lab("ed_level")][, cov_party := lab("mixedPartyId")]
stopifnot(!anyNA(d$trial_prompt), all(round(unlist(d[, .(rating_effective, rating_corrupt)]) * 9, 4) %% 1 == 0))
setcolorder(d, c("id", "task", "profile", "choice", grep("^rating_", names(d), value = TRUE), grep("^attr_", names(d), value = TRUE), "trial_prompt"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "floresmacias_2022_militarization.csv"))
