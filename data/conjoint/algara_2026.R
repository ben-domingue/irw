##Ideological extremity conjoints (U.S. Congress candidates) from
##Algara, C., Bae, B., & Hale, I. (2026). Taking the median voter seriously: Experimental and observational
##evaluation of the extremity penalty in U.S. congressional elections. Political Science Research and Methods.
##(Article DOI not in the deposit.) Replication data: Harvard Dataverse doi:10.7910/DVN/ABTI18, CC0 1.0.
##File read: PSRM_Replication_Package.zip, extracted: Posted_PSRM_Replication/Conjoint Analysis/ (README.txt and
##"Replication Code.R" read as text). Only the conjoint survey files are used, not the observational election data.
##Usage: Rscript algara_2026.R <dir holding Posted_PSRM_Replication> <output dir>
##
##TABLE algara_2026_median_ces_general: general-election conjoint in a 2022 Cooperative Election Study (YouGov) team
##module (file CCES22_CGU_OUTPUT.dta, value labels give the displayed text). 1,000 respondents, 5 pairs of
##candidates (task 1-5; profile 1 = candidate "a" = Candidate 1, profile 2 = "b" = Candidate 2, as the authors'
##reshaping code), 7 attributes: gender, race, age, party, ideology, issue, experience. Every pair is a general
##election pair (the authors' label "Major-Party Competition"). choice = CGU_cand_comp1-5 (1 = Candidate 1 chosen,
##2 = Candidate 2; forced, no opt-out; question wording not in the deposit, the code names it a "Candidate Comparison").
##Attribute text is the value-label text of the .dta (e.g. "30 years old", "Democratic Party", "Middle of the Road",
##"No experience"/"4 years"/..., "Asian American" as stored; the authors recode it to "Asian" for analysis).
##Attribute order is not documented (att1..att7 are in a fixed attribute order in the file, display order unknown).
##Covariates: cov_gender (gender4: Man -> male, Woman -> female, Non-binary/Other -> other), cov_birth_year,
##cov_education (educ answer text), cov_race (race answer text, "Middle Eastern" etc.), cov_hispanic (Yes/No),
##cov_party_id7 (pid7 answer text, "Not sure" and skipped codes are not answers: "Not sure" stays text, skipped NA),
##cov_ideology (CC22_340a self-placement text), cov_survey_weight (teamweight, used by the authors in the AMCEs).
##Dropped: all other CES items, the zip fields, the CGU_att*_cand<k> columns without a/b suffix (not used by the
##authors), derived dummies. caseid (a CES id) is re-keyed to an integer id.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- file.path(a[1], "Posted_PSRM_Replication", "Conjoint Analysis"); out <- a[2]
lab <- function(x) { l <- attr(x, "labels"); v <- as.integer(x); r <- names(l)[match(v, l)]; r[v >= 8 & v != 0 & !is.na(v) & r %in% c("skipped", "not asked")] <- NA; r }
## ---- CES general ----
y <- read_dta(file.path(raw, "CCES22_CGU_OUTPUT.dta"))
stopifnot(nrow(y) == 1000, uniqueN(y$caseid) == 1000)
an <- c("gender", "race", "age", "party", "ideology", "issue", "experience")
L <- list()
for (t in 1:5) for (p in 1:2) {
  s <- c("a", "b")[p]
  r <- data.table(id = seq_len(nrow(y)), task = t, profile = p,
                  choice = as.integer(as.integer(y[[paste0("CGU_cand_comp", t)]]) == p))
  for (k in 1:7) r[[paste0("attr_", an[k])]] <- as.character(as_factor(y[[sprintf("CGU_att%d_cand%d%s", k, t, s)]]))
  L[[length(L) + 1]] <- r
}
d <- rbindlist(L)
stopifnot(all(as.integer(y$CGU_cand_comp1) %in% 1:2), !anyNA(d))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
cv <- data.table(id = seq_len(nrow(y)),
  cov_gender = c("1" = "male", "2" = "female", "3" = "other", "4" = "other")[as.character(as.integer(y$gender4))],
  cov_birth_year = as.integer(y$birthyr), cov_education = lab(y$educ), cov_race = lab(y$race),
  cov_hispanic = lab(y$hispanic), cov_party_id7 = lab(y$pid7), cov_ideology = lab(y$CC22_340a),
  cov_survey_weight = as.numeric(y$teamweight))
d <- merge(d, cv, by = "id"); setcolorder(d, c("id", "task", "profile", "choice")); setorder(d, id, task, profile)
fwrite(d, file.path(out, "algara_2026_median_ces_general.csv"))
## ---- Lucid primary ----
##TABLE algara_2026_median_lucid_primary: same-party (primary-election) conjoint in a Lucid online sample (Lucid.csv, a
##Qualtrics export). Wide layout: F-<task>-<k> holds the attribute name shown in row k, F-<task>-1-<k> and
##F-<task>-2-<k> the displayed level of profile 1 and 2 (text as displayed). 10 pairs (task 1-10), 7 attributes:
##political experience, position on the Senate party leader (approves/disapproves of Mitch McConnell for
##Republican-primary respondents, Chuck Schumer for Democratic-primary respondents: the level text carries the
##leader's name), ideology, gender, occupation, race, age. The ORDER of the attributes is randomized per respondent
##and task and is recorded (attrpos_ = row position k). choice = the answer in cjoint<t> (block 1), cjoint<t+10>
##(block 2) or cjoint<t+20> (block 3), exactly one of the three is filled per respondent and task: three versions of
##the same screen: block 1 = Democratic-primary version (ideology levels Very Liberal ... Middle of the Road, Schumer
##text; shown to pid3 2 and to some independents), block 2 = Republican-primary version (Middle of the Road ... Very
##Conservative, McConnell text; pid3 1 and some independents), block 3 = Republican-primary version shown only to
##independents/others (pid3 3/4). The restriction is observed, not documented. 1 = profile 1 chosen, 2 =
##profile 2 (the authors recode 1 -> profile 1 chosen, 2 -> profile 2 chosen); forced, no opt-out; wording not in
##the deposit. trial_block = 1/2/3 (the version shown).
##Respondents kept: every respondent with a conjoint answer (Ben's ruling 11-10: the authors' sample exclusions are NOT
##applied). The authors' rules, not applied: consent_q == 1, passing the 5-item attention check (att _1 = att _2 = 1, others
##0; kept as cov_attention_pass), Finished == 1, then dropping independents and partisans whose ideology contradicts their
##party (pid3_new, flag): cov_party_id7_code and cov_ideology let a user apply it.
##Covariates: cov_age (age), cov_gender (gender: 1 male, 2 female, per the authors' recode `female`), cov_party_id7_code
##(the authors' pid7_r recode: 1 strong Democrat ... 7 strong Republican; pid3 1 = Republican, 2 = Democrat in this file;
##independents split by pidlean), cov_ideology (ideo 1-7 text as the authors' map: 1 Very Liberal ... 4 Middle of the
##Road ... 7 Very Conservative), cov_education_code and cov_income_code (Lucid answer codes, no labels in the deposit),
##cov_duration_sec, cov_attention_pass (authors' 5-item check, NA treated as not ticked). Dropped: ZIP/region and other items, ResponseId (re-keyed), derived dummies. No survey weight.
##The CloudResearch Connect general- and primary-election conjoints in Cloud.csv are NOT built (see return: 110
##conditional blocks cjoint1-41 / F-1..F-110 with no documented mapping).
df <- fread(file.path(raw, "Lucid.csv"), na.strings = c("NA", ""))
for (n in paste0("att _", 1:5)) df[is.na(get(n)), (n) := 0L]
df[, att_pass := as.integer(`att _1` == 1 & `att _2` == 1 & `att _3` == 0 & `att _4` == 0 & `att _5` == 0)]
nmap <- c("Political Experience" = "experience", "Position on Senate Leader" = "senate_leader", "Ideology" = "ideology",
          "Gender" = "gender", "Occupation" = "occupation", "Race" = "race", "Age" = "age")
df[, rid := .I]
L <- list()
for (t in 1:10) {
  ch <- df[[paste0("cjoint", t)]]; c2 <- df[[paste0("cjoint", t + 10)]]; c3 <- df[[paste0("cjoint", t + 20)]]
  stopifnot(all(rowSums(cbind(!is.na(ch), !is.na(c2), !is.na(c3))) <= 1))
  resp <- fifelse(!is.na(ch), ch, fifelse(!is.na(c2), c2, c3)); blk <- fifelse(!is.na(ch), 1L, fifelse(!is.na(c2), 2L, 3L))
  for (p in 1:2) {
    r <- data.table(id = df$rid, task = t, profile = p, choice = as.integer(resp == p), blk = blk, ok = !is.na(resp))
    for (a2 in nmap) { r[[paste0("attr_", a2)]] <- NA_character_; r[[paste0("attrpos_", a2)]] <- NA_integer_ }
    for (k in 1:7) {
      nm <- nmap[as.character(df[[sprintf("F-%d-%d", t, k)]])]; lv <- as.character(df[[sprintf("F-%d-%d-%d", t, p, k)]])
      for (a2 in unique(na.omit(nm))) { w <- which(nm == a2); set(r, w, paste0("attr_", a2), lv[w]); set(r, w, paste0("attrpos_", a2), k) }
    }
    L[[length(L) + 1]] <- r
  }
}
d <- rbindlist(L)[ok == TRUE]
d[, trial_block := blk]; d[, c("blk", "ok") := NULL]
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
pid <- df[, .(id = rid, p7 = fcase(pid3 == 1 & pidstrength == 1, 7L, pid3 == 1 & pidstrength == 2, 6L, pidlean == 2, 5L, pidlean == 3, 4L,
                                    pidlean == 1, 3L, pid3 == 2 & pidstrength == 2, 2L, pid3 == 2 & pidstrength == 1, 1L))]
ideo_t <- c("Very Liberal", "Liberal", "Somewhat Liberal", "Middle of the Road", "Somewhat Conservative", "Conservative", "Very Conservative")
cv <- df[, .(id = rid, cov_age = fifelse(age >= 18 & age <= 100, as.integer(age), NA_integer_),
             cov_gender = c("1" = "male", "2" = "female")[as.character(gender)],
             cov_ideology = ideo_t[as.integer(ideo)],
             cov_education_code = fifelse(education < 0, NA_integer_, as.integer(education)),
             cov_income_code = fifelse(hhi < 0, NA_integer_, as.integer(hhi)),
             cov_duration_sec = as.integer(`Duration (in seconds)`), cov_attention_pass = att_pass)]
cv <- merge(cv, pid, by = "id"); setnames(cv, "p7", "cov_party_id7_code")
d <- merge(d, cv, by = "id"); d[, id := as.integer(factor(id))]
ac <- sort(grep("^attr_", names(d), value = TRUE)); pc <- sort(grep("^attrpos_", names(d), value = TRUE))
setcolorder(d, c("id", "task", "profile", "choice", ac, pc)); setorder(d, id, task, profile)
fwrite(d, file.path(out, "algara_2026_median_lucid_primary.csv"))
