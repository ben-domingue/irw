##Partisan-label conjoint (US) from
##Ogura, I., Miwa, H., & Iida, T. (2022). What do you mean by "Democrat" and "Republican"?
##Evidence from a conjoint experiment. International Journal of Public Opinion Research,
##34(1), edab025. https://doi.org/10.1093/ijpor/edab025
##Replication data: Harvard Dataverse doi:10.7910/DVN/3NZZXU, CC0 1.0, no restricted files.
##File read: raw_data.csv ("original format" of raw_data.tab; the Qualtrics export with the
##Conjoint Survey Design Tool F.* text columns). Read as text, not run: readme.txt,
##codebook.pdf, 0_data_preparation.R, 1_main_analyses.R. The question wording is in the
##article's Online Appendix A, which is not in the deposit and was not accessible (paywall):
##outcome wording below is a PARAPHRASE from the abstract and the authors' code.
##Usage: Rscript ogura_2022.R <dir holding raw_data.csv> <output dir>
##
##1,051 US online respondents (platform not stated in the deposit; no platform IDs in the
##file). Each saw 4 tasks of 2 hypothetical persons described by 6 attributes and judged
##their partisanship. Two arms (trial_condition): "Democrat" (profiles described relative to
##the Democratic Party, 551 respondents) and "Republican" (500). Self-identified Democrats
##(Q4 = 1) always got the Democrat arm, Republicans (Q4 = 2) the Republican arm, everyone else
##the randomized `condition` column (0 = Democrat, 1 = Republican); this is the authors' rule
##(0_data_preparation.R) and the F.* text agrees with it for every respondent. The attribute
##texts are mirror images across arms ("Participation in Democratic party activities" vs
##"... Republican party activities"; "the Democratic Party" listed first vs the Republican);
##the authors pool both arms in their main AMCEs (1_main_analyses.R), so ONE table.
##Attribute columns (names generic; text as displayed, from the F.t.p.k columns):
##  attr_parents_party ("Political party their parents supported" / "... his/her parents ..."),
##  attr_party_activities ("Participation in <party> party activities"),
##  attr_criticism ("When someone criticizes the <party> party ..."),
##  attr_policy_opinions ("Opinions on recent political issues"),
##  attr_voting_habits ("Voting habits in previous federal elections"),
##  attr_vote_intention ("Vote intention for next presidential election").
##Attribute row order was randomized per respondent and fixed across that respondent's 4
##tasks (checked): attrpos_* = row position 1-6. Profiles also carried fixed first names by
##position (task 1 James/Richard, 2 Mary/Jennifer, 3 Robert/Michael, 4 Patricia/Elizabeth,
##per the authors' code); names were not randomized and are not stored.
##Outcomes (Q14-Q17 .D / .R by arm):
##  choice: which of the two persons is more of a Democrat (Democrat arm) / Republican
##    (Republican arm) (paraphrase). Forced choice between the two, no opt-out.
##  rating: 7-point rating of each person's partisanship (paraphrase), stored RAW 1-7. The
##    anchors are not in the deposit. The authors compute 8 - raw in the Democrat arm and keep
##    raw in the Republican arm so that larger = "more Democrat" / "more Republican"; the raw
##    distributions (Democrat arm piled at 1-4, Republican arm at 4-7) fit one scale running
##    from Democrat (1) to Republican (7) in both arms, but that is INFERRED. Note for users:
##    the authors' code reads the task-2 profile-2 rating from Q14.2.*_2 (task 1) instead of
##    Q15.2.*_2; this table uses Q15.2.*_2.
##trial_page_seconds = time on the conjoint page (T9-T12 .D/.R _3, "page submit" seconds);
##the authors drop tasks of <= 5 seconds and respondents failing the directed questions; this
##table keeps everyone.
##Restrictions: none documented; level weights not documented (see design record).
##Covariates (mappings from the codebook and the authors' recode code):
##  cov_gender: Q1, 1 = male, 2 = female (0_data_preparation.R gender = Q1 - 1 and the raking
##    block's gender.f 0 = "Male").
##  cov_age_group: Q2 codes 2-7 -> "18-29", "30-39", "40-49", "50-59", "60-69", "70+" (authors'
##    age = Q2 - 1 -> a20..a70, and the CPS targets AGE <= 29, 30-39, ..., >= 70).
##  cov_education_code: Q19 codes 1-7 (authors: 1 less than high school, 2 high school,
##    3 some college, 4-5 college, 6-7 set missing; answer text not in the deposit).
##  cov_party_id_code: Q4 codes (1 Democrat, 2 Republican per the authors' code; 3/4 are
##    "Independent" and "Other party" per the codebook, which does not say which is which).
##  cov_party_strength_dem (Q4.D: 1 strong, 2 not very strong Democrat), cov_party_strength_rep
##    (Q4.R, same for Republican), cov_party_lean (Q4.I: 1 closer to Republican, 2 closer to
##    Democratic, 3 neither): codes, labels from the codebook.
##  cov_state_code (Q3, 1-51, state order not documented), cov_race_code (Q21: 1 white,
##    2 black, 8 missing per the authors' code; other codes undocumented).
##  cov_vote_intent_2016 (Q6), cov_occupation (Q20), cov_religion (Q22), cov_religious_attendance
##    (Q22.2), cov_income (Q23): answer text from the codebook.
##  cov_attention_pass_directed: 1 if both directed questions in the issue battery were
##    answered as instructed (Q5_4 == 1 and Q5_8 == 4, the authors' rule); cov_attention_pass_imc:
##    1 if the instructional manipulation check Q18 was passed (exactly options 3 and 8 ticked,
##    the authors' rule; the authors did not use it).
##Dropped: issue attitudes Q5 and political-knowledge items Q7-Q13 (answer options not in the
##deposit), other page timers, display placeholders (E*, Q0, Q*.0.*), the authors' derived
##variables (IRT scores, region, dummies) and their raking weights (computed by the authors
##from ACS/CPS for attentive respondents only; not a survey weight of the deposit).
##N: 1,051 respondents in the deposit; the authors' analyses use 864 attentive respondents
##(clean_data.Rdata); the article text was not accessible to check its reported N.
##Spot check (against the authors' clean_data.Rdata, 864 attentive respondents, 6,824 profile
##rows): choice agrees 100%; rating (after the authors' 8 - raw flip in the Democrat arm)
##agrees on every row except task 2 profile 2, the authors' Q14/Q15 slip noted above.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "raw_data.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 1051)
s[, id := seq_len(.N)]
s[, arm := fifelse(Q4 == 1 | (Q4 > 2 & condition == 0), "Democrat", "Republican")]
# attribute names of task 1 define the row order; identical in tasks 2-4
for (t in 2:4) for (k in 1:6) stopifnot(all(s[[sprintf("F.%d.%d", t, k)]] == s[[sprintf("F.1.%d", k)]]))
key <- function(x) {
  x <- sub("his/her parents", "their parents", x)
  r <- character(length(x))
  r[x == "Political party their parents supported"] <- "parents_party"
  r[grepl("^Participation in (Democratic|Republican) party activities$", x)] <- "party_activities"
  r[grepl("^When someone criticizes the (Democratic|Republican) party \\.\\.\\.$", x)] <- "criticism"
  r[x == "Opinions on recent political issues"] <- "policy_opinions"
  r[x == "Voting habits in previous federal elections"] <- "voting_habits"
  r[x == "Vote intention for next presidential election"] <- "vote_intention"
  stopifnot(all(nzchar(r))); r
}
pos <- sapply(1:6, function(k) key(s[[sprintf("F.1.%d", k)]]))   # N x 6 attribute key at row k
stopifnot(all(apply(pos, 1, function(r) length(unique(r)) == 6)))
attrs <- c("parents_party", "party_activities", "criticism", "policy_opinions", "voting_habits", "vote_intention")
# party words in attribute names agree with the arm
fn <- do.call(paste, s[, paste0("F.1.", 1:6), with = FALSE])
stopifnot(all(mapply(grepl, paste0("Participation in ", c(Democrat = "Democratic", Republican = "Republican")[s$arm], " party activities"), fn)))
rows <- list()
for (t in 1:4) for (p in 1:2) {
  d <- data.table(id = s$id, task = t, profile = p)
  qn <- c("Q14", "Q15", "Q16", "Q17")[t]
  ch <- fifelse(s$arm == "Democrat", s[[paste0(qn, ".1.D")]], s[[paste0(qn, ".1.R")]])
  rt <- fifelse(s$arm == "Democrat", s[[sprintf("%s.2.D_%d", qn, p)]], s[[sprintf("%s.2.R_%d", qn, p)]])
  tm <- fifelse(s$arm == "Democrat", s[[sprintf("T%d.D_3", t + 8)]], s[[sprintf("T%d.R_3", t + 8)]])
  d[, choice := as.integer(ch == p)][, rating := as.integer(rt)]
  for (v in attrs) {
    k <- apply(pos, 1, function(r) which(r == v))
    lev <- vapply(seq_len(nrow(s)), function(i) s[[sprintf("F.%d.%d.%d", t, p, k[i])]][i], "")
    d[, paste0("attr_", v) := lev][, paste0("attrpos_", v) := as.integer(k)]
  }
  d[, trial_condition := s$arm][, trial_page_seconds := tm]
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
stopifnot(!anyNA(d$choice), all(d$rating %in% 1:7), d[, sum(choice), .(id, task)][, all(V1 == 1)])
for (v in attrs) stopifnot(all(nzchar(d[[paste0("attr_", v)]])))
lab <- function(x, l) { x <- as.integer(x); stopifnot(all(is.na(x) | x %in% seq_along(l))); l[x] }
cv <- s[, .(id,
  cov_gender = lab(Q1, c("male", "female")),
  cov_age_group = c(NA, "18-29", "30-39", "40-49", "50-59", "60-69", "70+")[as.integer(Q2)],
  cov_education_code = as.integer(Q19), cov_party_id_code = as.integer(Q4),
  cov_party_strength_dem = as.integer(Q4.D), cov_party_strength_rep = as.integer(Q4.R), cov_party_lean = as.integer(Q4.I),
  cov_state_code = as.integer(Q3), cov_race_code = as.integer(Q21),
  cov_vote_intent_2016 = lab(Q6, c("Hillary Clinton", "Donald Trump", "Other candidate", "Would not vote")),
  cov_occupation = lab(Q20, c("Management, professional, and related", "Service", "Sales and office", "Farming, fishing, and forestry",
                              "Construction, extraction, and maintenance", "Production, transportation, and material moving",
                              "Government", "Retired", "Unemployed", "Other", "Don't know")),
  cov_religion = lab(Q22, c("Protestant Christian", "Catholic", "Jewish", "Islam", "Buddhist", "Other", "Atheist", "Don't know")),
  cov_religious_attendance = lab(Q22.2, c("Every week", "Almost every week", "Once or twice a month", "A few times a year", "Never", "Don't know")),
  cov_income = lab(Q23, c("Less than $30,000", "$30,000-$39,999", "$40,000-$49,999", "$50,000-$59,999", "$60,000-$69,999",
                          "$70,000-$79,999", "$80,000-$89,999", "$90,000-$99,999", "$100,000 or more", "Don't know")),
  cov_attention_pass_directed = as.integer(Q5_4 %in% 1 & Q5_8 %in% 4))]
stopifnot(all(s$Q2 %in% 2:7))
imc <- as.matrix(s[, paste0("Q18_", 1:8), with = FALSE]); imc[is.na(imc)] <- 0
cv[, cov_attention_pass_imc := as.integer(apply(imc, 1, function(r) all(r == c(0, 0, 1, 0, 0, 0, 0, 1))))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ogura_2022_partisan_labels.csv"))
