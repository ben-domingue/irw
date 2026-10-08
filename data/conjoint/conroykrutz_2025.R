##Media-restriction factorial (conjoint) experiment in four African countries from
##Conroy-Krutz, J. (2025). Muzzling the media? Explaining popular support for media
##restrictions in Africa. The Journal of Politics, 87(3), 1169-1181.
##https://doi.org/10.1086/732998
##Replication data: Harvard Dataverse doi:10.7910/DVN/GO75QE, CC0 1.0, no restricted files.
##Files read: Muzzling_Long_JOP_23.dta (Dataverse "original format" download; value labels
##used) and, for the task-order check only, Muzzling_Wide_JOP_23.dta. Labels and question
##wording were checked against Muzzling_Codebook_JOP_23.xlsx and Muzzling_Long_JOP_23.do
##(read as text, not run).
##Usage: Rscript conroykrutz_2025.R <dir holding the two .dta files> <output dir>
##
##4,975 respondents (Cote d'Ivoire 1,200, Kenya 1,222, Nigeria 1,353, Uganda 1,200), each
##rating 4 single hypothetical scenarios about a media outlet (one profile per task, so
##profile = 1 throughout). 3 randomized attributes; the level text is the codebook's / Stata
##value labels (English): funding source (Domestic / Foreign), accuser (Independent Agency /
##The Opposition / The President), infraction (6 levels, e.g. "Using hate speech against
##members of certain ethnic groups"). The full vignette text and the language(s) of
##administration are not in the deposit. The authors pool the four countries (country fixed
##effects, Figure 1), and the attribute text is common, so this is ONE table with cov_country.
##Outcome: rating = Pref, codebook "Task k Preference", what should be done to the station:
##1 Nothing, 2 Issue a written warning to the station, 3 Fine the station, 4 Shut down the
##station for a temporary period, 5 Shut down the station permanently. Stored 1-5 as in the
##source; higher = HARSHER restriction (the authors analyse it as 0-4 "punish"). Refused (98)
##and Don't know (99) are outcome-less and dropped: 504 of 19,900 rows, leaving 19,396, the
##N of the authors' conjoint marginal-means runs in the log (Long_JOP_23.pdf); 55
##respondents answered no task, so the table has 4,920 respondents.
##Task: the long file has no task column. Within respondent, the row order matches the
##task-numbered AttC1-4 and Pref1-4 of the wide file for all 4,975 respondents (matched on
##covariates), so task = row order (INFERRED, verified). Randomization restrictions are not
##documented; level shares are roughly but not exactly equal.
##Covariates keep the source's numeric codes (labels in the .dta / codebook): cov_age (years),
##cov_female (V7), cov_lived_poverty (V8), cov_trust_president (V23), cov_trust_opposition
##(V24), cov_education (V25), cov_ethnicity (V26); 8/9 and 98/99 are refused/don't know.
##The interview date (V2) and the subject ID's source are not needed; subj is already 1..4975.
##Spot check: MASS::polr of 0-4 punish on the same terms as the authors' pooled ologit
##(Figure 1, N 17,781) reproduces all 8 attribute coefficients in the log to 4 decimals
##(e.g. armed groups .8660, partisan bias -.6370).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Muzzling_Long_JOP_23.dta"))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
s <- data.table(subj = as.integer(k$subj), cou = lab(k$COU), A = lab(k$AttA), B = lab(k$AttB), C = lab(k$AttC),
                pref = as.integer(zap_labels(k$Pref)), cAttC = as.integer(zap_labels(k$AttC)),
                age = as.integer(k$V6), fem = as.integer(zap_labels(k$V7)), pov = as.integer(zap_labels(k$V8)),
                tp = as.integer(zap_labels(k$V23)), to = as.integer(zap_labels(k$V24)),
                ed = as.integer(zap_labels(k$V25)), eth = as.integer(zap_labels(k$V26)))
stopifnot(s[, .N, subj][, all(N == 4)], !is.unsorted(s$subj))
s[, task := seq_len(.N), subj]
##task-order check against the wide file (task-numbered AttC1-4 / Pref1-4)
w <- as.data.table(zap_labels(read_dta(file.path(raw, "Muzzling_Wide_JOP_23.dta"))))
cv <- c("COU", "V6", "V7", "V8", "V23", "V24", "V25", "V26")
w[, key := do.call(paste, c(.SD[, cv, with = FALSE], sep = "_"))]
w[, seq := paste(AttC1, AttC2, AttC3, AttC4, Pref1, Pref2, Pref3, Pref4)]
k2 <- as.data.table(zap_labels(k))[, .(key = do.call(paste, c(.SD[1, cv, with = FALSE], sep = "_")),
                                       seq = paste(c(AttC, Pref), collapse = " ")), subj]
m <- merge(k2, w[, .(key, wseq = seq)], by = "key", allow.cartesian = TRUE)
stopifnot(m[, any(seq == wseq), subj][, all(V1)], uniqueN(m$subj) == 4975)
s <- s[pref %in% 1:5]
iso <- c("Cote d'Ivoire" = "CI", Kenya = "KE", Nigeria = "NG", Uganda = "UG")
d <- s[, .(id = subj, task, profile = 1L, rating = pref,
           attr_funding = A, attr_accuser = B, attr_infraction = C,
           cov_country = unname(iso[cou]), cov_age = age, cov_female = fem, cov_lived_poverty = pov,
           cov_trust_president = tp, cov_trust_opposition = to, cov_education = ed, cov_ethnicity = eth)]
stopifnot(nrow(d) == 19396, !anyNA(d$cov_country), d[, uniqueN(attr_infraction)] == 6)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "conroykrutz_2025_media_restrictions.csv"))
