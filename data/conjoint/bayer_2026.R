##Migration-destination conjoint (Nigeria) from
##Bayer, P., Ozturk, A., & Pardos-Prado, S. (2026). Climate migration or climate immobility?
##Evidence from micro-level causal analysis of migration intentions in Nigeria. Journal of Ethnic
##and Migration Studies. https://doi.org/10.1080/1369183X.2026.2707755
##Replication data: Harvard Dataverse doi:10.7910/DVN/47IM5S, CC0 1.0, no restricted files.
##File read: "raw data.dta" (Dataverse "original format" download of "raw data.tab"; the
##Qualtrics export with value labels). 0_data_setup.R and 3_conjoint.R read as text; design facts
##and wording from the deposited article (Bayeretal_JEMS2026.pdf, "Pull factors").
##"reshaped data.dta" (400 MB) not used.
##Usage: Rscript bayer_2026.R <raw dir> <output dir>
##
##Respondents recruited through Facebook/Instagram ads, Qualtrics, in English. The authors' sample
##(0_data_setup.R) is Status == 0 & Progress == 100: 3,450 respondents (= the article's N); 124
##of them have no conjoint answers (all six choices missing) and are omitted, leaving 3,326.
##Each saw 6 tasks of 2 hypothetical destination countries (Qualtrics conjoint block
##CBCONJOINT: feature<k>.<task>.<profile>_CBCONJOINT = level text, feature<k>.DISPLAY_NAME =
##attribute shown in row k), 6 attributes, all shown. Intro (article): "... we would like to know
##which of this pair of countries you would consider as better to travel to and start a new life."
##  choice = C<task> (values 1/2 = option 1/2): "Generally speaking, if you had to choose, which one
##           of these two options w..." (Stata variable label, truncated at 80 characters in the
##           source). Forced, no opt-out; one choice per task (checked).
##Attribute text = the exported level text (as displayed). Attribute names follow the displayed
##names: Jobs, Climate, Access to healthcare, Family reunification, Permanent settlement,
##Government (the 2 respondents under the earlier revision, below, saw the row name "Settlement"
##instead of "Permanent settlement", same levels; both stored as attr_settlement).
##Row order randomized per respondent and fixed across that respondent's tasks
##(DISPLAY_NAME fields; checked) -> attrpos_<attr> = row 1-6. Levels are drawn by the Qualtrics
##conjoint tool from pre-generated design versions (vers_CBCONJOINT, 260 versions; kept as
##trial_design_version); probabilities and restrictions not documented. 2 respondents ran under
##an earlier revision of the block (revision_CBCONJOINT), same levels (checked).
##trial_priming = the respondent's arm in the separate priming experiment (control: migration
##questions before climate questions; treated: reversed), asked before the conjoint.
##Covariates: cov_gender ("Which of the following best describes how you think of yourself?" 0
##Male -> male, 1 Female -> female; -1 "Other / Do not want to answer" (17) -> NA, since the
##option mixes other and refusal); cov_age (years as entered; 15 respondents report < 18);
##cov_education (value-label text; "Don't know/prefer not to answer" -> NA); cov_state, cov_area,
##cov_language, cov_religion, cov_occupation (value-label text; "Don't know" answers kept as text,
##prefer-not-to-say -> NA); cov_migrate_like (Q43), cov_migrate_likely (Q47), cov_region_like (Q48),
##cov_region_likely (Q49) as value-label text (-1 "Don't know/prefer not to answer" -> NA);
##cov_duration_sec (Qualtrics duration, whole survey). No survey weight.
##Dropped: IPAddress, LocationLatitude/Longitude (real values present in the deposit),
##ResponseId, ad-campaign utm_* fields, dates, the other attitude items, and the authors' derived
##variables.
##Spot check: the marginal mean of "There are no climate change risks." is 0.586, the article's
##"58.6% of respondents would prefer to go to a country with no climate risks".
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "raw data.dta"))
k <- k[k$Status == 0 & k$Progress == 100, ]
stopifnot(nrow(k) == 3450)
ch <- as.data.frame(lapply(k[paste0("C", 1:6)], function(v) as.integer(zap_labels(v))))
none <- rowSums(is.na(ch)) == 6
stopifnot(all(rowSums(is.na(ch)) %in% c(0, 6)), sum(none) == 124)
k <- k[!none, ]; ch <- ch[!none, ]
vl <- sapply(k, function(v) { l <- attr(v, "label"); if (is.null(l)) "" else l })
nm <- c(Jobs = "jobs", Climate = "climate", "Access to healthcare" = "healthcare", "Family reunification" = "family_reunification",
        "Permanent settlement" = "settlement", Settlement = "settlement", Government = "government")
dn <- sapply(0:5, function(f) k[[names(vl)[vl == sprintf("feature%d.DISPLAY_NAME", f)]]])
stopifnot(all(dn %in% names(nm)), all(apply(dn, 1, function(r) setequal(nm[r], unique(nm)))))
stopifnot(sum(apply(dn, 1, function(r) "Settlement" %in% r)) == 2)
id <- seq_len(nrow(k))
L <- list()
for (t in 1:6) for (p in 1:2) {
  stopifnot(all(ch[[t]] %in% 1:2))
  x <- data.table(id = id, task = t, profile = p, choice = as.integer(ch[[t]] == p))
  for (f in 0:5) {
    lev <- as.character(k[[names(vl)[vl == sprintf("feature%d.%d.%d_CBCONJOINT", f, t, p)]]])
    stopifnot(all(lev != ""))
    for (an in unique(nm)) {
      w <- nm[dn[, f + 1]] == an
      if (any(w)) { col <- paste0("attr_", an); if (!col %in% names(x)) x[, (col) := NA_character_]; x[w, (col) := lev[w]]
                    pc <- paste0("attrpos_", an); if (!pc %in% names(x)) x[, (pc) := NA_integer_]; x[w, (pc) := f + 1L] }
    }
  }
  L[[length(L) + 1]] <- x
}
d <- rbindlist(L, use.names = TRUE)
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", unique(nm)), paste0("attrpos_", unique(nm))))
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)])
levs <- list(jobs = c("No job opportunities", "Few job opportunities", "Many job opportunities"),
             climate = c("There are no climate change risks.", "Floodings have recently become more serious", "Droughts have recently become more serious"),
             healthcare = c("You always need to pay for medical care", "Access to healthcare only if you have a job", "Free access to health care for everyone"),
             family_reunification = c("You cannot bring family members", "You can bring family members after 5 years", "You can bring family members from the first day"),
             settlement = c("After 5 years of working, you need to leave the country", "After 5 years of working, you can stay freely as long as you want",
                            "From the first day, you can stay freely as long as you want"),
             government = c("No free and fair elections", "Elections that are only partially free and fair to choose the government",
                            "Free and fair elections to choose the government"))
for (v in names(levs)) stopifnot(setequal(unique(d[[paste0("attr_", v)]]), levs[[v]]))  # = the levels in 3_conjoint.R
lab <- function(v, na = character(0)) { x <- as.character(as_factor(k[[v]], levels = "labels")); x[x %in% na] <- NA; x }
dk <- c("Don’t know/prefer not to answer", "Don’t know / prefer not to say")
g <- as.integer(zap_labels(k$female)); stopifnot(all(g %in% c(-1, 0, 1, NA)))
cv <- data.table(id = id, trial_priming = k$priming, trial_design_version = as.integer(k$vers_CBCONJOINT),
                 cov_gender = c("male", "female")[match(g, 0:1)], cov_age = as.integer(lab("age")),
                 cov_education = lab("education", dk), cov_state = lab("state"), cov_area = lab("area", dk),
                 cov_language = lab("language"), cov_religion = lab("Q42", dk), cov_occupation = lab("occupation"),
                 cov_migrate_like = lab("Q43", dk), cov_migrate_likely = lab("Q47", dk), cov_region_like = lab("Q48", dk),
                 cov_region_likely = lab("Q49", dk), cov_duration_sec = as.integer(k$Duration__in_seconds_))
stopifnot(all(cv$trial_priming %in% c("control", "treated")))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bayer_2026_migration_destinations.csv"))
