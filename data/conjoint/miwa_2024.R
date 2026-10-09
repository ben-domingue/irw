##Candidate-attribute conjoints on perceived populism (Japan) from
##Miwa, H. (2024). Why voters prefer politicians with particular personal attributes: The role
##of voter demand for populists. Political Studies, 73(2), 725-752 (online 2024).
##https://doi.org/10.1177/00323217241263295
##Replication data: Harvard Dataverse doi:10.7910/DVN/71Y4GO, CC0 1.0, no restricted files.
##Files read (one row per respondent, conjoint in Qualtrics F-columns, UTF-8): data_Study1.csv,
##data_Study2_main.csv, data_Study2_pilot_1st.csv, data_Study2_pilot_2nd.csv,
##data_Study2_pilot_3rd.csv (saved as s1.csv, s2.csv, p1.csv, p2.csv, p3.csv). Question wording,
##scales and covariate codes: codebook_v2.pdf (English translation of the Japanese survey).
##Read as text: readme.txt, 2_Study1.R, 3_Study2_main.R, 4_Study2_pilot.R.
##Usage: Rscript miwa_2024.R <raw dir> <output dir>
##
##All five experiments: Lucid respondents in Japan rated pairs of hypothetical House of
##Representatives candidates shown as a table. Attribute text is the Japanese displayed level
##(F-task-candidate-k), attribute names from F-task-k: previous occupation (前の職業), Diet
##experience (国会議員経験), education (学歴), age (年齢), gender (性別), party (所属政党), relatives'
##political experience (近親者の政治家経験). Attribute order was randomized per respondent and
##fixed across tasks (codebook "F-x-z"): attrpos_* = the recorded row. Profile 1/2 = candidate
##[X]/[Y] (the y in the Qualtrics columns). No choice question; each candidate is rated.
##Ratings, 1-6, stored as answered (codebook):
##  rating_anti_elitism   (Qx_AE_*): "How do you feel about each of the Candidates [X] and [Y]
##      when you use the measure of 'desire to maintain the existing way of the society' as one
##      extreme and 'being active in breaking vested interests' as the other?" 1 = desire to
##      maintain ... 6 = being active in breaking vested interests.
##  rating_people_centrism (Qx_PC_*): same stem, 'placing importance on the opinions of
##      politicians and experts' (1) ... 'placing importance on the opinions of the general
##      public' (6).
##  rating (Study 2 main, Qx_M_* / Qx_N_*): same stem, 'being quite undesirable as a member of
##      the HoR' (1) ... 'being very desirable as a member of the HoR' (6).
##Tables (separate fieldings and attribute sets; the pilots each test a different set of notes):
##  miwa_2024_populist_study1: 1,000 respondents, 5 tasks, rating_anti_elitism +
##    rating_people_centrism. Arms (condition): trial_arm = "with party" (509; party shown) /
##    "without party" (491; attr_party = "(not shown)", 6 attribute rows). trial_question_order:
##    which rating was asked first (order: 0 people-centrism first, 1 anti-elitism first).
##  miwa_2024_populist_study2: 3,636 respondents, 2 tasks, rating (favourability). Arms:
##    "manipulated mediator" (Q_M answered, 2,425): each candidate also had a "special note"
##    (attr_note; the 4 notes are each used once per respondent, note-(2x+y-2)); "natural
##    mediator" (Q_N, 1,211): no note shown (attr_note = "(not shown)"; the dataset carries notes
##    for these respondents too, but the codebook says they were not shown).
##  miwa_2024_populist_pilot1 / _pilot2 / _pilot3: 406 / 432 / 410 respondents, 4 tasks,
##    rating_anti_elitism + rating_people_centrism, arms as in Study 2 (manipulated mediator:
##    8 notes each used once per respondent; natural mediator: "(not shown)"). Each pilot used
##    a different note set.
##Level weights: Study 1 levels follow the distribution of 2017 House of Representatives
##candidates (5_profile_distribution.R; e.g. 83% male, ages 34/42/53/64/70 at 10/20/40/20/10%);
##Study 2 and the pilots use two levels per attribute with near-equal shares.
##attr_note's position in the display is not recorded (no attrpos_note).
##Covariates (codebook): cov_gender from gender2 ("Please select your gender": Man = male,
##Woman = female, Non-binary/third gender = other, Prefer not to say = NA); cov_gender_lucid
##(Lucid's binary gender, codes 1 Man 2 Woman); cov_age (years); cov_education (codebook
##English label); cov_prefecture (codebook English name; -3105 = missing -> NA); cov_pop1-3,
##cov_ant1-3, cov_man1-3 (populist-attitude items, 1 = Strongly agree ... 7 = Strongly
##disagree; not asked in the pilots); cov_dq1-dq10 (directed and opinion questions, 1 = Agree
##... 5 = Disagree; DQ1/DQ2 are attention items everyone passed); Study 2: cov_lr (1 Liberal
##(left) ... 5 Conservative (right)), cov_block (blocked-randomization cell, codes per codebook).
##rid is a row ID (kept as id after re-keying in file order). Respondents whose ratings are all
##missing would be dropped (none are).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
an <- c("前の職業" = "previous_occupation", "国会議員経験" = "diet_experience", "学歴" = "education", "年齢" = "age",
        "性別" = "gender", "所属政党" = "party", "近親者の政治家経験" = "relatives_politicians")
edu <- c("Junior high school", "High school", "Technical college", "Vocational school", "Junior college", "University",
         "Graduate school (Master's course)", "Graduate school (Doctoral course)")
pref <- c("Aichi", "Akita", "Aomori", "Chiba", "Ehime", "Fukui", "Fukuoka", "Fukushima", "Gifu", "Gunma", "Hiroshima",
          "Hokkaido", "Hyogo", "Ibaraki", "Ishikawa", "Iwate", "Kagawa", "Kagoshima", "Kanagawa", "Kochi", "Kumamoto",
          "Kyoto", "Mie", "Miyagi", "Miyazaki", "Nagano", "Nagasaki", "Nara", "Niigata", "Oita", "Okayama", "Okinawa",
          "Osaka", "Saga", "Saitama", "Shiga", "Shimane", "Shizuoka", "Tochigi", "Tokushima", "Tokyo", "Tottori",
          "Toyama", "Wakayama", "Yamagata", "Yamaguchi", "Yamanashi")
covs <- function(s) {
  stopifnot(all(s$gender2 %in% 1:4), all(s$gender %in% 1:2), all(s$edu %in% 1:8), all(s$pref %in% c(1:47, -3105)))
  cv <- data.table(cov_gender = c("male", "female", "other", NA)[s$gender2], cov_gender_lucid = s$gender, cov_age = s$age,
                   cov_education = edu[s$edu], cov_prefecture = pref[ifelse(s$pref == -3105, NA, s$pref)])
  for (v in intersect(c(paste0(rep(c("POP", "ANT", "MAN"), each = 3), 1:3), paste0("DQ", 1:10), "LR", "block"), names(s)))
    cv[, paste0("cov_", tolower(v)) := s[[v]]]
  cv
}
build <- function(f, ntask, arms, outs, name, notes = FALSE) {
  # arms: list(label = list(code = arm letter in the Q column, note = notes shown?)); outs: c(rating column = Q-column stem)
  s <- fread(file.path(raw, f), encoding = "UTF-8")
  stopifnot(!anyDuplicated(s$rid))
  cv <- covs(s); cv[, id := seq_len(nrow(s))]
  d <- rbindlist(lapply(names(arms), function(arm) rbindlist(lapply(1:ntask, function(t) rbindlist(lapply(1:2, function(p) {
    cd <- arms[[arm]]$code
    r <- lapply(outs, function(o) s[[sprintf("Q%d_%s%s_%d", t, o, cd, p)]])
    keep <- Reduce(`|`, lapply(r, function(x) !is.na(x)))
    e <- data.table(id = seq_len(nrow(s)), task = t, profile = p, trial_arm = arm)
    for (o in names(outs)) e[, (o) := as.integer(r[[o]])]
    for (k in 1:7) {
      nm <- s[[sprintf("F-%d-%d", t, k)]]; lv <- s[[sprintf("F-%d-%d-%d", t, p, k)]]
      for (j in names(an)) {
        hit <- !is.na(nm) & nm == j
        e[hit, paste0("attr_", an[[j]]) := lv[hit]]
        e[hit, paste0("attrpos_", an[[j]]) := k]
      }
    }
    if (notes) e[, attr_note := if (arms[[arm]]$note) s[[paste0("note-", 2 * t + p - 2)]] else "(not shown)"]
    e[keep]
  }))))))
  if (!"attr_party" %in% names(d)) stop("no party")
  d[is.na(attr_party) & trial_arm == "without party", attr_party := "(not shown)"]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), !anyDuplicated(d[, .(id, task, profile)]),
            d[, all(unlist(lapply(.SD, function(x) all(x %in% c(NA, 1:6))))), .SDcols = names(outs)],
            d[, .N, .(id, task)][, all(N == 2)], d[, uniqueN(trial_arm), id][, all(V1 == 1)])
  d <- merge(d, cv, by = "id")
  if ("order" %in% names(s)) d[, trial_question_order := c("people-centrism first", "anti-elitism first")[s$order[id] + 1L]]
  setcolorder(d, c("id", "task", "profile", names(outs), sort(grep("^attr_", names(d), value = TRUE)),
                   sort(grep("^attrpos_", names(d), value = TRUE)), grep("^trial_", names(d), value = TRUE)))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
ae_pc <- c(rating_anti_elitism = "AE_", rating_people_centrism = "PC_")
build("s1.csv", 5, list(`with party` = list(code = "A"), `without party` = list(code = "B")), ae_pc, "miwa_2024_populist_study1")
mm <- list(`manipulated mediator` = list(code = "A", note = TRUE), `natural mediator` = list(code = "B", note = FALSE))
build("s2.csv", 2, list(`manipulated mediator` = list(code = "M", note = TRUE), `natural mediator` = list(code = "N", note = FALSE)),
      c(rating = ""), "miwa_2024_populist_study2", notes = TRUE)
for (k in 1:3) build(sprintf("p%d.csv", k), 4, mm, ae_pc, sprintf("miwa_2024_populist_pilot%d", k), notes = TRUE)
