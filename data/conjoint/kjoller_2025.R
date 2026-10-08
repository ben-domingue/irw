##Political-job choice conjoint among Danish local-election candidates from
##Kjoller, F. K., & Pedersen, L. H. (2025). The gendered cost of politics. British Journal of
##Political Science, 55, e59. https://doi.org/10.1017/S0007123424000310
##Replication data: Harvard Dataverse doi:10.7910/DVN/SOLAAJ, CC0 1.0. File read:
##data_genderedcost_wide.rdata (one data frame `df_wide`, loaded into its own environment; SPSS
##labels from the survey firm Epinion carry the Danish text shown). The authors' recode
##(0_cleaning_n_pivoting.R, read as text) gives English labels; this table keeps the Danish text.
##Usage: Rscript kjoller_2025.R <dir holding the .rdata> <output dir>
##
##Candidates in the 16 Nov 2021 Danish municipal elections (survey 2-21 Dec 2021), 7 paired
##choices between two hypothetical council positions, 4 attributes with 3 levels each:
##  position (Post): ordinary member / chair with little / with large political influence. The
##    wording depended on the municipality type, stored per respondent in
##    conjoint_attr_1_lvl_<k>_Text: Copenhagen ("Menigt medlem af Borgerrepraesentationen",
##    "Borgmester med lille/stor politisk indflydelse"), magistrate municipalities ("Raadmand ...")
##    and all others ("Udvalgsformand ..."); the respondent's own text is stored.
##  remuneration (Vederlag compared with normal pay): 10% lower / same / 10% higher.
##  workload (Arbejdstid compared with what the post normally requires): 10% less / same / 10% more.
##  environment (Arbejdsmiljoeet as described by council members): "Praeget af ligevaerd" /
##    "Flere har vaeret udsat for graenseoverskridende adfaerd og chikane" / "Flere har vaeret
##    udsat for sexisme og/eller seksuelt graenseoverskridende adfaerd".
##  HTML underline tags (<u>) are stripped from the level text.
##Outcome: choice = "Forestil dig, at du tilbydes foelgende to poster som medlem af byraadet. Saet
##  dig venligst godt ind i de to poster. Hvilken post vil du vaelge?" (Mulighed A / Mulighed B;
##  forced choice, no opt-out; the stored label is cut off after "Bemaerk, at posterne er
##  identiske i alle andre henseender end").
##Randomization: the article says simple randomization, every level with probability 1/3
##  (restrictions none). Position is always the top attribute; the order of the other three
##  was randomized between respondents and held fixed across their 7 tasks
##  (conjoint_attr_order_record, e.g. "0,1,3,2,4"): attrpos_* = rank in that record (position = 1).
##Sample: 2,391 survey records; 250 made no choice (149 never reached the experiment) and are
##  dropped; 2,141 respondents keep every task they answered (191 partial respondents answered
##  1-6 tasks). The article analyses 1,938 candidates who completed in time (27,132 profile rows):
##  cov_in_authors_sample = 1 for SurveyStatus Complete and SurveyEndTime <= 2021-12-20 21:49:52,
##  the authors' filter (3_fig3.R). That filter gives 1,939 respondents and 27,146 rows (men 18,214)
##  in the authors' own long file too; the article reports 1,938 / 27,132 (men 18,200), one man
##  fewer. Not resolved.
##Covariates (numeric codes; Danish labels in the SPSS file): cov_female (c_Koen == "Kvinde"),
##  cov_birth_year, cov_education (uddannelse 1-8), cov_elected_2021 (kom_valg: 1 first-time
##  elected, 2 re-elected, 3 not elected but previously, 4 never elected), cov_marital (1 married,
##  2 in a relationship, 3 single, 4 prefer not to say), cov_left_right (0-10, 0 = very
##  left-wing), cov_political_hours (weekly hours on political work), cov_harassed_1..5 (five
##  experiences of sexism/harassment: 1 yes, 2 no, 3 prefer not to say),
##  cov_harassment_risk (1 very low .. 5 very high, 6 don't know), cov_survey_status (1 partial,
##  2 complete, 4 refused). Dropped: Epinion respondent Id (re-keyed to integers), timestamps,
##  send/reminder dates, time zone, design-version strings, the authors' derived dummies. The
##  deposit already omits name, email, municipality and party (GDPR, per _readme.pdf).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "data_genderedcost_wide.rdata"), envir = e)
w <- as.data.table(lapply(e$df_wide, function(x) { attributes(x)[c("label", "format.spss", "display_width")] <- NULL; x }))
lab <- function(v) { l <- attr(e$df_wide[[v]], "labels"); setNames(names(l), l) }
clean <- function(x) trimws(gsub("\\s+", " ", gsub("<[^>]+>", "", x)))
w <- w[!is.na(conjoint_1_Concept_1_attribute_1)]
w[, nid := .I]
posl <- lapply(1:3, function(k) lab(paste0("conjoint_attr_1_lvl_", k, "_Text")))
lv <- lapply(2:4, function(k) lab(paste0("conjoint_1_Concept_1_attribute_", k)))
ord <- strsplit(w$conjoint_attr_order_record, ",")
rows <- list()
for (t in 1:7) for (p in 1:2) {
  g <- function(k) w[[sprintf("conjoint_%d_Concept_%d_attribute_%d", t, p, k)]]
  pc <- g(1)
  ptxt <- vapply(seq_len(nrow(w)), function(i) if (is.na(pc[i])) NA_character_ else posl[[pc[i]]][as.character(w[[paste0("conjoint_attr_1_lvl_", pc[i], "_Text")]][i])], "")
  ch <- w[[sprintf("conjoint_%d_choice", t)]]
  rows[[length(rows) + 1]] <- data.table(nid = w$nid, task = t, profile = p,
    choice = as.integer(ch == p),
    attr_position = clean(ptxt), attr_remuneration = clean(lv[[1]][as.character(g(2))]),
    attr_workload = clean(lv[[2]][as.character(g(3))]), attr_environment = clean(lv[[3]][as.character(g(4))]))
}
d <- rbindlist(rows)[!is.na(choice)]
stopifnot(!anyNA(d[, .(attr_position, attr_remuneration, attr_workload, attr_environment)]),
          d[, uniqueN(attr_remuneration)] == 3, d[, uniqueN(attr_workload)] == 3, d[, uniqueN(attr_environment)] == 3,
          d[, uniqueN(attr_position)] == 8)
stopifnot(d[, .(s = sum(choice), n = .N), .(nid, task)][, all(s == 1 & n == 2)])
pos <- t(vapply(ord, function(o) match(c("1", "2", "3", "4"), o) - 1L, integer(4)))
stopifnot(all(pos[, 1] == 1L), !anyNA(pos))
cv <- w[, .(nid, attrpos_position = pos[, 1], attrpos_remuneration = pos[, 2], attrpos_workload = pos[, 3],
            attrpos_environment = pos[, 4],
            cov_female = as.integer(c_Koen == "Kvinde"), cov_birth_year = as.integer(alder_o1),
            cov_education = as.integer(uddannelse), cov_elected_2021 = as.integer(kom_valg),
            cov_marital = as.integer(civilstatus), cov_left_right = as.integer(politik_skala),
            cov_political_hours = as.numeric(arbejdstid),
            cov_harassed_1 = as.integer(kraenkelser_1_resp), cov_harassed_2 = as.integer(kraenkelser_2_resp),
            cov_harassed_3 = as.integer(kraenkelser_3_resp), cov_harassed_4 = as.integer(kraenkelser_4_resp),
            cov_harassed_5 = as.integer(kraenkelser_5_resp), cov_harassment_risk = as.integer(risiko),
            cov_survey_status = as.integer(SurveyStatus),
            cov_in_authors_sample = as.integer(SurveyStatus == 2 & SurveyEndTime <= as.POSIXct("2021-12-20 21:49:52", tz = attr(SurveyEndTime, "tzone"))))]
d <- merge(d, cv, by = "nid")
used <- sort(unique(d$nid)); d[, id := match(nid, used)][, nid := NULL]
stopifnot(uniqueN(d$id) == 2141, d[cov_in_authors_sample == 1, uniqueN(id)] == 1939, d[cov_in_authors_sample == 1, .N] == 27146)
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kjoller_2025_council_positions.csv"))
