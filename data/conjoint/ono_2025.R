##Japanese Diet candidate single-profile conjoint (House of Representatives vs House of Councillors) from
##Ono, Y., Kasuya, Y., & Miwa, H. (2025). Analyzing gender gaps in bicameral legislatures: How
##asymmetrical institutions affect the supply and demand for female candidates. Legislative
##Studies Quarterly, 50(3), e12493. https://doi.org/10.1111/lsq.12493
##Replication data: Harvard Dataverse doi:10.7910/DVN/8SX9CK, CC0 1.0, no restricted files.
##Files read: demand_side_data.tab (original-format download saved as demand_side_data.csv, UTF-8),
##codebook.pdf, readme.txt; demand_side_study.R read as text, not run. Design, wording and level
##probabilities: the working paper version, RIETI DP 22-E-094 ("Why are there more women in the
##Upper House?", https://www.rieti.go.jp/jp/publications/dp/22e094.pdf), section 3.1 and
##appendix A.1, Table A1. The supply-side study (vignette with one manipulated setting per
##respondent, supply_side_data) is not a conjoint and is not built.
##Usage: Rscript ono_2025.R <raw dir> <output dir>
##
##2,267 attentive Rakuten Insight panel respondents (Japan, July 27-31 2020; quotas on gender, age
##and prefecture; inattentive respondents already removed by the authors). Single-profile design:
##each respondent rated 10 candidates for the HoR election and 10 for the HoC election (one profile
##per task, 20 tasks); which chamber came first was randomized (source HOR_first). In the source,
##F-1..F-10 are always the HoR profiles (Q1_HOR..Q10_HOR) and F-11..F-20 the HoC profiles
##(Q1_HOC..Q10_HOC); task = the order shown, rebuilt as in the authors' code: HoR tasks are 1-10
##when HOR_first = 1, else 11-20 (and HoC the other block). trial_chamber = HoR / HoC.
##trial_priming = 1 if the respondent read the paragraph on the HoR's supremacy in electing the
##PM before the tasks (random half), else 0. Both chambers share one table (same attributes,
##same respondents, the authors analyse them together with a HoC dummy).
##Outcome: rating = "To what extent is this candidate favorable as a [HoR/HoC] member? Please
##evaluate this candidate using an eight-point scale from 'not favorable at all' to 'very
##favorable.'" (authors' translation; Japanese in WP p.19), 1 = not favorable at all ... 8 = very
##favorable (codebook), unnumbered bipolar scale. No missing ratings.
##Attributes (8): attr_gender, attr_age, attr_education, attr_occupation, attr_hometown,
##attr_experience, attr_dynasty, attr_party; stored as the Japanese text displayed (as in the
##source; English translations in WP Table A1). attr_hometown: the displayed text had the
##respondent's prefecture of residence inserted for X ("X出身" = hometown is X, "X外出身" = not X);
##the source stores the template with X and so does this table (the prefecture is cov_prefecture).
##Attribute order randomized once per respondent and kept for all 20 tasks (codebook F-x-y);
##attrpos_<attr> = its row position 1-8. Level probabilities were set to real-world
##distributions (WP Table A1, e.g. female 0.187), so level_weights are nonuniform; no
##restriction on combinations is documented.
##Covariates: cov_gender (R.gender 1 Man = male, 2 Woman = female, 3 Other = other; codebook),
##cov_age (R.age, years), cov_prefecture (prefecture, codebook English names), cov_education
##(R.education, codebook English text), cov_party_id (partisanship, codebook English text;
##code 11 "I don't know/Prefer not to say" mixes don't know and refusal and is kept as text),
##cov_importance_hor / _hoc / _local (pre-treatment importance of each election's results, 1-11,
##1 = not at all important; the source stores them by list position importance_1..3 with
##election_1..3 naming the election, re-sorted here by election).
##Dropped: HOR_first (implied by task), election_x / importance_x position columns.
##No survey weight in the deposit. N = 2,267 matches the paper (2,267 x 20 = 45,340 obs).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "demand_side_data.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 2267L)
s[, id := .I]
attrs <- c("gender", "party", "age", "education", "occupation", "hometown", "experience", "dynasty")
L <- vector("list", 20)
for (x in 1:20) {
  hor <- x <= 10
  q <- if (hor) paste0("Q", x, "_HOR") else paste0("Q", x - 10, "_HOC")
  d <- data.table(id = s$id,
                  task = ifelse(s$HOR_first == 1, ifelse(hor, x, x), ifelse(hor, x + 10L, x - 10L)),
                  profile = 1L, rating = as.integer(s[[q]]),
                  trial_chamber = if (hor) "HoR" else "HoC", trial_priming = as.integer(s$priming))
  for (y in 1:8) {
    nm <- s[[paste0("F-", x, "-", y)]]; lv <- s[[paste0("F-", x, "-1-", y)]]
    stopifnot(nm %in% attrs, !is.na(lv), lv != "")
    for (an in attrs) {
      w <- nm == an
      if (y == 1) { d[, paste0("attr_", an) := NA_character_]; d[, paste0("attrpos_", an) := NA_integer_] }
      d[w, paste0("attr_", an) := lv[w]]; d[w, paste0("attrpos_", an) := y]
    }
  }
  L[[x]] <- d
}
d <- rbindlist(L)
stopifnot(!anyNA(d), d[, all(rating %in% 1:8)], d[, .N, .(id, task)][, all(N == 1)], d[, uniqueN(task), id][, all(V1 == 20)])
# attribute order fixed within respondent
stopifnot(d[, uniqueN(paste(attrpos_gender, attrpos_party, attrpos_age, attrpos_education, attrpos_occupation,
                            attrpos_hometown, attrpos_experience, attrpos_dynasty)), id][, all(V1 == 1)])
pref <- c("Hokkaido","Aomori","Iwate","Miyagi","Akita","Yamagata","Fukushima","Ibaraki","Tochigi","Gumma","Saitama",
          "Chiba","Tokyo","Kanagawa","Niigata","Toyama","Ishikawa","Fukui","Yamanashi","Nagano","Gifu","Shizuoka","Aichi",
          "Mie","Shiga","Kyoto","Osaka","Hyogo","Nara","Wakayama","Tottori","Shimane","Okayama","Hiroshima","Yamaguchi",
          "Tokushima","Kagawa","Ehime","Kochi","Fukuoka","Saga","Nagasaki","Kumamoto","Oita","Miyazaki","Kagoshima","Okinawa")
edu <- c("Junior high school", "High school", "Vocational school", "Junior college", "Technical college", "University", "Graduate school")
pid <- c("Liberal Democratic Party", "Constitutional Democratic Party", "Democratic Party For the People", "Komeito",
         "Japanese Communist Party", "Japan Innovation Party", "Social Democratic Party", "Reiwa Shinsengumi",
         "Other political organization", "I don't support any party", "I don't know/Prefer not to say")
stopifnot(s$R.gender %in% 1:3, s$prefecture %in% 1:47, s$R.education %in% 1:7, s$partisanship %in% 1:11)
imp <- function(e) ifelse(s$election_1 == e, s$importance_1, ifelse(s$election_2 == e, s$importance_2,
                    ifelse(s$election_3 == e, s$importance_3, NA)))
cv <- data.table(id = s$id, cov_gender = c("male", "female", "other")[s$R.gender], cov_age = as.integer(s$R.age),
                 cov_prefecture = pref[s$prefecture], cov_education = edu[s$R.education], cov_party_id = pid[s$partisanship],
                 cov_importance_hor = as.integer(imp("HOR")), cov_importance_hoc = as.integer(imp("HOC")),
                 cov_importance_local = as.integer(imp("local")))
stopifnot(!anyNA(cv))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating", paste0("attr_", attrs), paste0("attrpos_", attrs), "trial_chamber", "trial_priming"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ono_2025_bicameral_gender.csv"))
