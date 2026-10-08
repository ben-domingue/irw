##Israeli-Palestinian group-sympathy conjoints (two US studies) from
##Inouye, R., & Horiuchi, Y. (2026). Unraveling Americans' selective sympathies toward
##Israelis and Palestinians. International Studies Quarterly, 70(2), sqag027.
##Replication data: Harvard Dataverse doi:10.7910/DVN/CS7USS, CC0 1.0, no restricted files.
##Files read (from ISQ-2024-12-0761.R3_replication_package.zip): data/study1/study1.csv and
##data/study2/study2.csv (raw Qualtrics exports, answers as text, two header rows), and
##output/study1/cleaned_data.rds, output/study2/cleaned_data.rds (only their ResponseId column). Level
##text from documents/conjoint.php (the randomizer); wording and layout from
##documents/study1.pdf / study2.pdf (Qualtrics questionnaires) and the embedded-data fields
##group_choice_question / palestinian_similarity_question / israeli_similarity_question;
##sample filters from scripts/step01_read_data.R and step03_wrangle_data.R (read as text).
##Usage: Rscript inouye_2026.R <dir holding replication_package/> <output dir>
##
##TWO TABLES, one per study (separate fieldings 19 months apart; the paper reports them
##side by side, not pooled):
##  inouye_2026_sympathies_2023 (Study 1, fielded right after the October 2023 Gaza ground
##    invasion; 1,253 respondents, 1,198 in the authors' sample)
##  inouye_2026_sympathies_2025 (Study 2, May 2025; 1,104 respondents, 1,001 in the authors' sample)
##US online panel respondents (Qualtrics export with a supplier transaction id). Each saw two
##hypothetical groups "involved in a dispute" (Group A = profile 1, Group B = profile 2),
##described by 8 binary attributes: Majority religion (Judaism/Islam), Threats to civilians
##(Physical security and safety/Human rights violations), Territorial goal (Retain occupied
##territory/End territorial occupation), Alliance with the US (Yes/No), Controversial
##military actions (Indiscriminate air strikes killing civilians/Armed attacks on civilians
##and hostage-taking), Democracy (Yes/No), Economic development (High/Low), Military
##strength (Very strong/Weak).
##RESTRICTION (by construction, conjoint.php): within a task the two groups always take
##DIFFERENT levels on every attribute, so Group B is the mirror image of Group A (verified
##in every task). Attribute row order was shuffled once per respondent and kept for all
##tasks (attrpos_*, 1 = top row; verified constant across tasks).
##Tasks 1-10 are independent pairs; task 11 repeats task 1 with the groups swapped
##(Qualtrics block "8_att_symp_choice - 1 (repeated, flipped)"): it is stored as task 11
##with the displayed sides (profile 1 = task 1's Group B) and trial_repeat = 1. The authors
##use it (projoint) to correct for intra-respondent reliability.
##Outcomes:
##  choice = "Which side do you sympathize more with: Group A or Group B? Even if you are
##           not entirely sure, please indicate the answer you are more inclined towards."
##           Forced, no opt-out. Tasks 1-11, both studies.
##  Study 2 only, asked later in the survey about the SAME pairs (same randomized fields,
##  shown again):
##  choice_similar_palestinian = "Which group do you think is more similar to actual
##           Palestinian groups? Even if you are not entirely sure, please indicate the
##           answer you think is most accurate." Pairs of tasks 1-5 (shown in the order
##           2,1,3,4,5). Kept as asked: 1 = judged more similar to Palestinian groups (the
##           authors flip it to "similar to Israel").
##  choice_similar_israeli = "Which group do you think is more similar to the actual
##           Israeli government? ..." Pairs of tasks 6-10. Both forced, no opt-out.
##Sample: all panel completes (gc == 1; 1,253 in Study 1, 1,104 in Study 2), with
##cov_in_authors_sample = 1 for the authors' analysis sample (1,198 and 1,001), taken from
##the ResponseIds in the deposit's output/study<s>/cleaned_data.rds. Their step01 script
##describes the exclusion as Qualtrics fraud flags (RelevantID duplicate, duplicate score
##>= 75, fraud score >= 30, reCAPTCHA < 0.5) plus a missing prior-sympathy answer, but
##applying those rules to the deposited CSV removes only 32 / 80 respondents, not 55 / 103;
##the extra 23 per study cannot be explained from the deposit, so the authors' own kept-id
##list is used. Six / four respondents have no prior-sympathy answer (cov_perspective NA).
##Covariates (codes): cov_perspective (the authors' 6-point prior sympathy) 1=strongly
##pro-Palestinian .. 6=strongly pro-Israeli; cov_party (authors' coding) 1=strong
##Republican 2=not very strong Republican 3=leans Republican 4=leans Democratic 5=not very
##strong Democrat 6=strong Democrat (pure independents NA); cov_age_group 1=18-20 2=21-25
##3=26-35 4=36-45 5=46-55 6=56-65 7=66+; cov_gender 1=man 2=woman 3=other; cov_education
##1=did not graduate high school 2=high school 3=some college 4=two-year degree
##5=four-year degree 6=graduate degree; cov_race 1=White 2=Black 3=Hispanic 4=Asian
##5=Native American 6=Other.
##PII in the deposit (not read into the table): IP addresses, latitude/longitude, Qualtrics
##ResponseIds and panel transaction ids. Respondent ids are re-keyed to integers in file
##order. Dropped: open-ended answers, attribute-importance items, all other survey blocks.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c("Majority religion" = "majority_religion", "Threats to civilians" = "threats_to_civilians",
           "Territorial goal" = "territorial_goal", "Alliance with the US" = "alliance_us",
           "Controversial military actions" = "military_actions", "Democracy" = "democracy",
           "Economic development" = "economic_development", "Military strength" = "military_strength")
code <- function(x, lv) { i <- match(x, lv); stopifnot(all(is.na(x) | !is.na(i))); i }
build <- function(s) {
  r <- fread(file.path(raw, "replication_package", "data", paste0("study", s), paste0("study", s, ".csv")),
             colClasses = "character", na.strings = "")[-(1:2)]
  r <- r[gc == "1"]
  keep <- readRDS(file.path(raw, "replication_package", "output", paste0("study", s), "cleaned_data.rds"))$ResponseId
  stopifnot(all(keep %in% r$ResponseId))
  sy <- if (s == 1) c("Q3.15", "Q3.16", "Q3.17") else c("Q3.11", "Q3.12", "Q3.13")
  q <- if (s == 1) c(party1 = "Q3.10", party2 = "Q3.11", party3 = "Q3.12", age = "Q3.2", edu = "Q3.3", gender = "Q3.4", race = "Q3.5")
       else c(party1 = "Q3.7", party2 = "Q3.8", party3 = "Q3.9", age = "Q3.2", edu = "Q3.17", gender = "Q3.16", race = "Q3.3")
  g <- function(v) r[[q[[v]]]]
  persp <- fcase(r[[sy[1]]] == "Strongly sympathetic to the Israeli perspective.", 6L,
                 r[[sy[1]]] == "Not very strongly sympathetic to the Israeli perspective.", 5L,
                 r[[sy[2]]] == "More sympathetic to the Israeli perspective.", 4L,
                 r[[sy[2]]] == "More sympathetic to the Palestinian perspective.", 3L,
                 r[[sy[3]]] == "Not very strongly sympathetic to the Palestinian perspective.", 2L,
                 r[[sy[3]]] == "Strongly sympathetic to the Palestinian perspective.", 1L)
  party <- fcase(g("party1") == "Strong Democrat", 6L, g("party1") == "Not very strong Democrat", 5L,
                 g("party3") == "Closer to the Democratic Party", 4L, g("party3") == "Closer to the Republican Party", 3L,
                 g("party2") == "Not very strong Republican", 2L, g("party2") == "Strong Republican", 1L)
  cv <- data.table(id = seq_len(nrow(r)), cov_perspective = persp, cov_party = party,
    cov_age_group = code(g("age"), c("18-20 years old", "21-25 years old", "26-35 years old", "36-45 years old",
                                     "46-55 years old", "56-65 years old", "66 years old or older")),
    cov_gender = code(g("gender"), c("Man", "Woman", "Other")),
    cov_education = code(g("edu"), c("Did not graduate from high school", "High school", "Some college, no degree",
                                     "Two-year degree", "Four-year degree", "Graduate degree")),
    cov_race = code(tolower(g("race")), c("white", "black", "hispanic", "asian", "native american", "other")),
    cov_in_authors_sample = as.integer(r$ResponseId %in% keep))
  # attribute order: fixed per respondent
  an <- sapply(1:8, function(k) r[[sprintf("B-1-%d", k)]])
  for (t in 2:10) stopifnot(all(sapply(1:8, function(k) r[[sprintf("B-%d-%d", t, k)]]) == an))
  pos <- t(apply(an, 1, function(x) match(names(attrs), x)))
  stopifnot(!anyNA(pos))
  ans <- c(sym = sprintf("Q%d.2", 5:15))
  simp <- c(`2` = "Q18.2", `1` = "Q19.2", `3` = "Q20.2", `4` = "Q21.2", `5` = "Q22.2")
  simi <- setNames(sprintf("Q%d.2", 25:29), 6:10)
  d <- rbindlist(lapply(1:11, function(t) rbindlist(lapply(1:2, function(p) {
    src_t <- if (t == 11) 1L else t
    src_p <- if (t == 11) 3L - p else p
    lv <- sapply(1:8, function(k) r[[sprintf("B-%d-%d-%d", src_t, src_p, k)]])
    ch <- code(r[[ans[t]]], c("Group A", "Group B"))
    x <- data.table(id = seq_len(nrow(r)), task = t, profile = p, choice = as.integer(ch == p))
    if (s == 2) {
      x[, choice_similar_palestinian := if (as.character(t) %in% names(simp)) as.integer(code(r[[simp[[as.character(t)]]]], c("Group A", "Group B")) == p) else NA_integer_]
      x[, choice_similar_israeli := if (as.character(t) %in% names(simi)) as.integer(code(r[[simi[[as.character(t)]]]], c("Group A", "Group B")) == p) else NA_integer_]
    }
    for (j in seq_along(attrs)) {
      k <- pos[, j]
      x[, paste0("attr_", attrs[j]) := lv[cbind(seq_len(nrow(r)), k)]]
    }
    for (j in seq_along(attrs)) x[, paste0("attrpos_", attrs[j]) := pos[, j]]
    x[, trial_repeat := as.integer(t == 11)]
    x
  }))))
  # mirror-image restriction and one chosen per pair
  w <- dcast(d[, c("id", "task", "profile", paste0("attr_", attrs)), with = FALSE], id + task ~ profile, value.var = paste0("attr_", attrs))
  for (v in attrs) stopifnot(all(w[[paste0("attr_", v, "_1")]] != w[[paste0("attr_", v, "_2")]]))
  oc <- intersect(c("choice", "choice_similar_palestinian", "choice_similar_israeli"), names(d))
  for (o in oc) stopifnot(d[!is.na(get(o)), sum(get(o)), .(id, task)][, all(V1 == 1)])
  d <- d[d[, Reduce(`|`, lapply(.SD, Negate(is.na))), .SDcols = oc]]
  d <- merge(d, cv, by = "id")
  setorder(d, id, task, profile)
  d
}
d1 <- build(1); stopifnot(uniqueN(d1$id) == 1253, uniqueN(d1[cov_in_authors_sample == 1, id]) == 1198)
fwrite(d1, file.path(out, "inouye_2026_sympathies_2023.csv"))
d2 <- build(2); stopifnot(uniqueN(d2$id) == 1104, uniqueN(d2[cov_in_authors_sample == 1, id]) == 1001)
fwrite(d2, file.path(out, "inouye_2026_sympathies_2025.csv"))
