##Resolve-assessment paired conjoint (US public) from
##Kertzer, J. D., Renshon, J., & Yarhi-Milo, K. (2021). How do observers assess resolve? British
##Journal of Political Science, 51(1), 308-330. https://doi.org/10.1017/S0007123418000595
##Replication data: Harvard Dataverse doi:10.7910/DVN/VSVMY7, CC0 1.0. Files read:
##"Resolve Conjoint Raw 070718.RData" (object `data`; one row per respondent, the full displayed
##attribute text in F.<round>.<A|B>.<row> and the row's attribute name in F.<A|B>.<row>) and
##"Resolve Demographics 070718.RData" (object `dat_id`: survey weight); "BJPS Codebook 070818.pdf" and
##"BJPS Replication 1.R" (read as text, not run) for variable meanings.
##Usage: Rscript kertzer_2021.R <dir holding the two .RData files> <output dir>
##
##2,003 US respondents (online, fielded 28 January 2015 per the start/end timestamps), 8 rounds of two
##countries ("Country A" / "Country B") in an international dispute, 7 displayed attribute rows.
##task = round k (columns c<k>c, c<k>ra_1, c<k>rb_1), profile 1 = Country A, 2 = Country B.
##Attributes are stored as the full displayed sentence of each row:
##  attr_government_type, attr_military_capabilities, attr_interests (stakes), attr_foreign_relations
##  ("The country is an ally of / an adversary of / the United States."), attr_previous_behavior
##  (16 sentences crossing initiator/target, ally/adversary opponent, stood firm/backed down, and
##  same/different leader), attr_current_behavior, attr_leader_background (12 sentences crossing
##  tenure "recently took office"/"in power for many years", military service none/some/long career,
##  and the pronoun he/she, which is the leader's gender; one level reads "recently took office, she"
##  with a comma, as displayed). The authors' short labels (RegimeType, maleLeader, prevActLdr, ...) are
##  regex recodes of these sentences in BJPS Replication 1.R.
##Attribute row order was randomized once per respondent and kept for both countries and all rounds
##(Replication 1.R: "this will be constant across all rounds a subject plays"; checked here):
##attrpos_* = row number 1-7.
##Outcomes (codebook):
##  choice = c<k>c (1 = Country A, 2 = Country B): which country the respondent sees as more likely to
##           stand firm. Forced choice, no opt-out (exactly one per task, checked).
##  rating = c<k>ra_1 / c<k>rb_1: the respondent's estimated likelihood that the country will stand
##           firm, 0-100 as stored (100 = certain to stand firm). Wording paraphrased from the codebook.
##           5 ratings stored as "NaN" are NA (the choice is kept).
##trial_response_sec = t<k>_3 (page-submit timer of the round, seconds; the authors' responseTime).
##The paper's main analyses (Resolve Conjoint Cleaned No US) drop every task in which one country was
##"the United States"; those tasks are KEPT here (filter attr_foreign_relations to reproduce).
##Covariates: cov_survey_weight (eWeight: entropy-balancing weight on gender, age and education,
##trimmed at 5; Replication 1.R), cov_gender (Q58: the authors code male = (Q58 == 1), so 1 -> male,
##2 -> female; one blank -> NA), cov_birth_year (Q60), cov_age (2015 - Q60, the authors' computation),
##cov_education_code (Q62, codes 1-8; the codebook gives only the authors' grouping 1-2 high school or
##less, 3 some college, 4-5 college/university, 6-8 postgraduate), cov_party_id7 (Q64 as answer text:
##codebook order Strong Republican ... Strong Democrat, with Replication 1.R reversing Q64 "towards
##Republican", so 1 = Strong Republican, 7 = Strong Democrat), cov_duration_sec (V9 - V8, survey end
##minus start). V1 is a Qualtrics ResponseId: dropped, respondents re-keyed 1..2003 in file order.
##The authors' scales (mi1, ci1, iso1, ideology, interest*) and dummies are dropped; DispFirst and
##the other Q* items are not documented in the codebook and are dropped.
##Count check: 2,003 x 8 x 2 = 32,048 rows = the authors' "Resolve Conjoint Cleaned 070718.RData".; choice, rating,
##government type and leader gender match it row for row (checked when built).
##Restrictions (observed, not documented): a profile that "is the United States" is always a democracy
##with a very powerful military, and never both profiles of a task; level shares are unequal as a result.
##Spot check: weighted LPM of choice on five attributes in the paper's no-US sample (1,995 respondents,
##16,180 rows) gives powerful military +0.16, low stakes -0.14, dictatorship vs democracy +0.03 (the
##paper: democracies seen as less resolved), ally vs adversary +0.06; article figures not compared.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "Resolve Conjoint Raw 070718.RData"), envir = e)
r <- as.data.table(e$data)
g <- new.env(); load(file.path(raw, "Resolve Demographics 070718.RData"), envir = g)
w <- as.data.table(g$dat_id)[, .(V1 = as.character(ID), cov_survey_weight = eWeight)]
stopifnot(nrow(r) == 2003, uniqueN(r$V1) == 2003, nrow(w) == 2003, all(r$V1 %in% w$V1))
r[, rid := .I]
nm <- c("Government type" = "government_type", "Military capabilities" = "military_capabilities",
        "Interests in the dispute" = "interests", "Leader background" = "leader_background",
        "Foreign relations" = "foreign_relations", "Previous behavior in international disputes" = "previous_behavior",
        "Current behavior" = "current_behavior")
ordA <- as.matrix(r[, paste0("F.A.", 1:7), with = FALSE]); ordB <- as.matrix(r[, paste0("F.B.", 1:7), with = FALSE])
stopifnot(all(ordA == ordB), all(ordA %in% names(nm)), all(apply(ordA, 1, uniqueN) == 7))
d <- rbindlist(lapply(1:8, function(k) rbindlist(lapply(1:2, function(p) {
  cc <- c("A", "B")[p]
  x <- data.table(rid = r$rid, task = k, profile = p,
                  choice = as.integer(as.integer(r[[paste0("c", k, "c")]]) == p),
                  rating = suppressWarnings(as.integer(r[[paste0("c", k, "r", tolower(cc), "_1")]])),
                  trial_response_sec = as.numeric(r[[paste0("t", k, "_3")]]))
  txt <- as.matrix(r[, paste0("F.", k, ".", cc, ".", 1:7), with = FALSE])
  for (lv in names(nm)) {
    pos <- apply(ordA == lv, 1, which)
    x[, paste0("attr_", nm[[lv]]) := trimws(txt[cbind(seq_len(nrow(r)), pos)])]
    x[, paste0("attrpos_", nm[[lv]]) := as.integer(pos)]
  }
  x
}))))
stopifnot(all(as.character(r$c1c) %in% c("1", "2")), d[, sum(choice), .(rid, task)][, all(V1 == 1)],
          sum(is.na(d$rating)) == 5, all(d$rating >= 0 & d$rating <= 100, na.rm = TRUE))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(nzchar(d[[v]])))
stopifnot(uniqueN(d$attr_leader_background) == 12, uniqueN(d$attr_previous_behavior) == 16, uniqueN(d$attr_foreign_relations) == 3)
p7 <- c("Strong Republican", "Republican", "Independent, but lean Republican", "Independent",
        "Independent, but lean Democrat", "Democrat", "Strong Democrat")
q64 <- suppressWarnings(as.integer(as.character(r$Q64))); q58 <- as.character(r$Q58); q60 <- suppressWarnings(as.integer(as.character(r$Q60)))
stopifnot(all(q64 %in% c(1:7, NA)), all(q58 %in% c("1", "2", "")))
cv <- data.table(rid = r$rid, V1 = r$V1, cov_gender = c("1" = "male", "2" = "female")[q58], cov_birth_year = q60,
                 cov_age = 2015L - q60, cov_education_code = suppressWarnings(as.integer(as.character(r$Q62))),
                 cov_party_id7 = p7[q64],
                 cov_duration_sec = as.integer(difftime(as.POSIXct(r$V9, tz = "UTC"), as.POSIXct(r$V8, tz = "UTC"), units = "secs")))
cv <- merge(cv, w, by = "V1")[, V1 := NULL]
d <- merge(d, cv, by = "rid")
setnames(d, "rid", "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
stopifnot(nrow(d) == 32048)
fwrite(d, file.path(out, "kertzer_2021_resolve.csv"))
