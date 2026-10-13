##Japanese candidate paired conjoints, preference vs expectation (two experiments, 2022) from
##Kato, G., Lu, F., & Endo, M. (2025). The preference-expectation gap in support for female
##candidates: Evidence from Japan. Public Opinion Quarterly, 89(1), 217-228.
##https://doi.org/10.1093/poq/nfaf002
##Replication data: Harvard Dataverse doi:10.7910/DVN/GJWDVM, CC0 1.0. Files read:
##elecvspref_jan22_conjoint_v4.1.rds (Experiment 1), elecvspref_mar16_conjoint_v4.1.rds
##(Experiment 2); analysis scripts read as text only (never run).
##Usage: Rscript kato_2025.R <dir holding the two .rds> <output dir>
##
##Two tables, one per experiment (different attribute sets and fieldings; the authors analyse
##them separately): kato_2025_candidates_jan22 (Rakuten Insight, Jan 21-25 2022, N = 1,803,
##6 tasks) and kato_2025_candidates_mar22 (Mar 16-24 2022, N = 2,406, 8 tasks). Paired forced
##choice between two hypothetical candidates. Each respondent did one block of preference tasks
##(3 in Exp 1, 4 in Exp 2) and one block of expectation tasks; each task asks ONE question, so the
##two outcomes sit in separate columns, NA on the other block's tasks:
##  choice        = selected on preference tasks (electability == 0): "Which of the following two
##                  persons do you think is more desirable as a Single Member District member of the
##                  House of Representatives? Even if you are not entirely sure, please indicate
##                  which of the two you would think is more desirable." (article fn. 3, translated)
##  choice_expect = selected on expectation tasks (electability == 1): "... more likely to win in a
##                  Single Member District election ..." (Exp 2: "more likely to be elected").
##  In Exp 2 "House of Representatives" is replaced by "Municipal Council" for a random half:
##  trial_election_level = conjoint_eleclevel (house / municipal), fixed per respondent.
##Task order: the deposit numbers preference tasks 1-3 (1-4) and expectation tasks 4-6 (5-8) for
##everyone, but the article says the two blocks were shown in reversed order for a random half;
##conjoint_order (prefelec / elecpref) records which. task here is the DISPLAY order rebuilt from
##conjoint_order (elecpref: expectation block first), kept in that order within a block;
##trial_block_order keeps conjoint_order. profile = source profile (1/2).
##Levels: the source factors carry an English label with a bracketed attribute prefix,
##"(Gender) Female"; the prefix is stripped, as in the authors' own recode (gsub("^\\(.*\\) ", "")).
##Respondents saw Japanese; only the English labels survive. Exp 1 includes attr_party_type
##(Ruling / Oppostion [sic], as stored), which has its own row position (row 9) and is fully
##determined by attr_party (LDP, Komeito = Ruling). Exp 1 attribute rows are fixed (rowpos constant);
##Exp 2 attribute order was randomized once per respondent: attrpos_* = source *.rowpos.
##Exp 2 never shows a 35-year-old with "Incumbent (5 terms)" (observed; no source states the rule).
##Dropped: Qualtrics Response.ID; tasks whose attributes were not assigned ("experimental
##assignment mechanically missing", 1 respondent in Exp 1, 2 in Exp 2, as in the article); tasks
##with no answer (203 / 121 tasks; the authors drop them too). respondent is an integer index and
##is kept as id. Covariates: cov_gender from face_gender ("Please answer your gender", value labels
##男性 = male, 女性 = female, その他 = other; blank = NA), cov_genderval_1..9 keep the codes of nine
##gender-role attitude items (value labels: 1 反対 disagree, 2 どちらかといえば反対, 3 どちらかと言えば賛成,
##4 賛成 agree). No survey weight ("All analyses are unweighted").
##Counts vs article (its "analytic cases" are profile rows): Exp 1 10,606 preference / 10,612
##expectation rows, reproduced exactly (checked below); 1,784 respondents answer at least one task.
##Exp 2 total 38,222 rows matches the authors' script, but the article's per-arm counts (House
##9,558 / 9,492, municipal 9,420 / 9,358; sum 37,828) do not: this table has House 9,774 / 9,694 and
##municipal 9,418 / 9,336 (printed below). Not resolved; 2,404 respondents.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
strip <- function(x) sub("^\\(.*\\) ", "", as.character(x))
build <- function(f, attrs, ntask, pos) {
  x <- as.data.table(readRDS(file.path(raw, f)))
  x <- x[!is.na(candgender)]
  stopifnot(!anyNA(x[, ..attrs]))
  x <- x[!is.na(selected)]
  half <- ntask / 2L
  stopifnot(x[, all((task > half) == (electability == 1))])
  d <- x[, .(id = as.integer(respondent),
             task = as.integer(fifelse(conjoint_order == "elecpref", (task - 1L + half) %% ntask + 1L, task)),
             profile = as.integer(profile),
             choice = fifelse(electability == 0, as.integer(selected), NA_integer_),
             choice_expect = fifelse(electability == 1, as.integer(selected), NA_integer_))]
  for (v in names(attrs)) d[, paste0("attr_", v) := strip(x[[attrs[[v]]]])]
  if (pos) for (v in names(attrs)) d[, paste0("attrpos_", v) := as.integer(x[[paste0(attrs[[v]], ".rowpos")]])]
  if ("conjoint_eleclevel" %in% names(x)) d[, trial_election_level := x$conjoint_eleclevel]
  d[, trial_block_order := x$conjoint_order]
  g <- if (is.character(x$face_gender)) x$face_gender else
    as.character(factor(as.integer(x$face_gender), 1:3, c("男性", "女性", "その他")))
  d[, cov_gender := c("男性" = "male", "女性" = "female", "その他" = "other")[g]]
  for (i in 1:9) d[, paste0("cov_genderval_", i) := as.integer(x[[paste0("genderval_", i)]])]
  stopifnot(d[, .N, .(id, task)][, all(N == 2L)],
            d[, .(s = sum(choice, choice_expect, na.rm = TRUE)), .(id, task)][, all(s == 1L)],
            d[, uniqueN(cov_gender), id][, all(V1 == 1L)])
  setorder(d, id, task, profile); d
}
a1 <- c(gender = "candgender", party = "candparty", age = "candage", experience = "candexperience",
        education = "candedu", marriage = "candmarriage", youngest_child = "candkidage",
        residence = "candlivetype", party_type = "candpartytype")
d1 <- build("elecvspref_jan22_conjoint_v4.1.rds", a1, 6L, FALSE)
x1 <- as.data.table(readRDS(file.path(raw, "elecvspref_jan22_conjoint_v4.1.rds")))
stopifnot(x1[!is.na(candgender), all(sapply(.SD, uniqueN) == 1L), .SDcols = patterns("rowpos$")], d1[!is.na(choice), .N] == 10606L,
          d1[!is.na(choice_expect), .N] == 10612L)
fwrite(d1, file.path(out, "kato_2025_candidates_jan22.csv"))
a2 <- c(gender = "candgender", party = "candparty", age = "candage", experience = "candexperience",
        education = "candedu", family = "candfam", origin = "candorigin", residence = "candlivetype",
        policy_focus = "candimppol")
d2 <- build("elecvspref_mar16_conjoint_v4.1.rds", a2, 8L, TRUE)
n2 <- d2[, .(pref = sum(!is.na(choice)), expect = sum(!is.na(choice_expect))), trial_election_level]
print(n2)
stopifnot(d2[attr_age == "35 Years Old" & attr_experience == "Incumbent (5 terms)", .N] == 0L)
fwrite(d2, file.path(out, "kato_2025_candidates_mar22.csv"))
