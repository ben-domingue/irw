##Two forced-choice vs abstention replication conjoints (United States, MTurk) from
##Miller, D. R., & Ziegler, J. (2024). Preferential abstention in conjoint experiments. Research &
##Politics, 11(4). https://doi.org/10.1177/20531680241299329 (preprint OSF 4ws7m)
##Replication data: Harvard Dataverse doi:10.7910/DVN/JQOPNW, CC0 1.0, no restricted files.
##Files read: mummolo_data.csv and funckmccabe_data.csv (raw Qualtrics exports, three header rows).
##Read as text: README.txt, both codebooks, both survey PDFs (Qualtrics print-outs), and the
##authors' mummolo_code.R / funckmccabe_code.R (their task, profile and arm coding is followed).
##(miller_2024.R in this folder is a different paper, Miller & Smith 2024.)
##Usage: Rscript miller_2024_abstention.R <dir holding the two .csv files> <output dir>
##
##These are NEW data: the authors re-fielded two published designs on MTurk (2021) to compare a
##forced-choice arm with an arm that could choose neither profile. Two tables (different
##designs and samples):
##
##(1) miller_2024_news_selection (replication of Mummolo 2016; not the same data as
##    mummolo_2021_partisan_loyalty). "You will now be asked to consider 12 pairs of news articles
##    taken from various major online news providers." Two attributes per article, row order
##    randomized (F-<task>-<row> names the attribute in each row; attrpos_ stored): Headline (many
##    wordings of about 20 stories) and Source (Fox News / MSNBC / USA Today).
##    choice: "Would you prefer to read News Selection A or News Selection B?" Forced arm (FL_8_DO
##    = FL_15): News Selection A / B; abstention arm (FL_16): A / B / Neither (choice = 0 on both
##    profiles). Tasks 1-12 are in the respondent's arm. Task 13 re-shows the profiles of one
##    earlier task (FL_50_DO "AbstentionOption<k>" or FL_20_DO "ForcedChoice<k>") in the OTHER
##    format; it is stored as task 13 with the attributes of task k and trial_repeat_of = k.
##    trial_arm = the respondent's arm; trial_format = the format of this task (forced /
##    abstention). Respondents whose 13th block id is not an option block (BL_...) have no task 13.
##
##(2) miller_2024_scandal_candidates (replication of Funck & McCabe 2022). Six tasks of two
##    congressional candidates. Rows shown: Party (always first; Democrat vs Republican, the pair
##    order D-R or R-D set by the randomly drawn survey block), recent News (always second;
##    G-<task>-<profile>-1, 6 levels), then the candidate characteristics F-<task>-<row>
##    (abortion, age, gender, government spending, immigration, profession, race, religion; order
##    randomized). The information environment was randomized per task (block name): High shows
##    all 8 characteristics, Moderate the first 3 rows, Low none (survey print-out). Characteristics
##    not displayed are "(not shown)" (Ben's ruling); attrpos_ gives the row (1-8) of each
##    characteristic among the F rows, blank when not shown. trial_info_environment = High /
##    Moderate / Low.
##    Level shares are unequal for gender (Male about 2/3 of shown levels) and race (White about
##    1/2); not documented (observed restriction / weighting).
##    choice: "If this election were being held in your district, would you vote for Candidate A
##    or Candidate B?" (forced arm, FL_177_DO = FL_178) or "... Candidate A, Candidate B, or
##    neither candidate?" (abstention arm, FL_179; neither = 0 on both profiles). Blank when the
##    task's choice was skipped but ratings were given.
##    rating_shares_views / rating_good_morals / rating_cares: "Please indicate how much you agree
##    with the statements about Candidates A and B: Candidate A shares my views / has good morals /
##    cares about people like me", 1 = Strongly disagree ... 5 = Strongly agree.
##    Task 7 re-shows task 1's profiles in the other format (as in the authors' code: choice7 is
##    read from the other arm's task-1 columns); trial_repeat_of = 1.
##
##Both: rows are kept when the task has an answer; respondents who never reached the conjoint are
##omitted. No attention-check or IP filtering is applied (the authors' code applies none to the
##choice data). Covariates: the survey answers as given (age band or birth year, gender,
##education, race, Hispanic, income, ideology, party ID and strength/lean, issue items; the news
##design also health insurance, health job, student, losing weight, cigarettes).
##PII / identifiers dropped: Qualtrics ResponseId (re-keyed 1..n in file order), MTurk
##confirmation codes, IP_block, IP_country, dates, the free-text "other" boxes (Q4_3_TEXT,
##Q7_6_TEXT), the open-ended attention/manipulation answers (Q386, Q50).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) {
  f <- file.path(raw, f)
  h <- names(fread(f, nrows = 0))
  list(x = suppressWarnings(fread(f, skip = 3, header = FALSE, col.names = h, colClasses = "character")),
       lab = unlist(suppressWarnings(fread(f, nrows = 1, header = TRUE, colClasses = "character"))[1]))
}
cell <- function(x, cols, rows) vapply(seq_along(rows), function(i) if (is.na(cols[i])) NA_character_ else x[[cols[i]]][rows[i]], "")
## ---------- (1) news selection ----------
m <- rd("mummolo_data.csv"); x <- m$x
x[, id := .I]
fq <- c("Q23", "Q25", paste0("Q", seq(29, 45, 2)), "Q27"); aq <- paste0("Q", seq(52, 74, 2))
stopifnot(grepl("News Selection A or News Selection B", m$lab[c(fq, aq)]))
x <- x[FL_8_DO %in% c("FL_15", "FL_16")]
x[, arm := fifelse(FL_8_DO == "FL_15", "forced", "abstention")]
x[, rep := fifelse(arm == "forced", FL_50_DO, FL_20_DO)]
x[, repk := NA_integer_][grepl("Option[0-9]+$|ForcedChoice[0-9]+$", rep), repk := as.integer(sub(".*[^0-9]", "", rep))]
n <- nrow(x); ii <- seq_len(n)
nw <- rbindlist(lapply(1:13, function(t) {
  k <- if (t <= 12) rep(t, n) else x$repk
  fmt <- if (t <= 12) x$arm else ifelse(x$arm == "forced", "abstention", "forced")
  qc <- ifelse(is.na(k), NA_character_, ifelse(fmt == "forced", fq[pmax(k, 1L)], aq[pmax(k, 1L)]))
  ans <- cell(x, qc, ii)
  rbindlist(lapply(1:2, function(p) {
    r <- data.table(id = x$id, task = t, profile = p, ans = ans, trial_arm = x$arm, trial_format = fmt,
                    trial_repeat_of = if (t <= 12) NA_integer_ else k)
    for (an in c("Headline", "Source")) {
      v <- rep(NA_character_, n); pos <- rep(NA_integer_, n)
      for (j in 1:2) {
        nm <- cell(x, ifelse(is.na(k), NA, sprintf("F-%d-%d", k, j)), ii)
        lv <- cell(x, ifelse(is.na(k), NA, sprintf("F-%d-%d-%d", k, p, j)), ii)
        w <- which(nm == an); v[w] <- lv[w]; pos[w] <- j
      }
      r[, paste0("attr_", tolower(an)) := v][, paste0("attrpos_", tolower(an)) := pos]
    }
    r
  }))
}))
nw <- nw[!is.na(ans) & ans != ""]
stopifnot(nw$ans %in% c("News Selection A", "News Selection B", "Neither"),
          nw[trial_format == "forced", all(ans != "Neither")], !anyNA(nw$attr_headline), !anyNA(nw$attr_source),
          all(nw$attr_headline != ""), all(nw$attr_source != ""))
nw[, choice := as.integer(ans == c("News Selection A", "News Selection B")[profile])][, ans := NULL]
mc <- c(cov_birth_year = "Q2", cov_gender = "Q4", cov_education = "Q6", cov_race = "Q7", cov_hispanic = "Q8",
        cov_income = "Q9", cov_ideology = "Q11", cov_party_id = "Q12", cov_dem_strength = "Q13", cov_rep_strength = "Q14",
        cov_ind_lean = "Q15", cov_health_insurance = "Q16", cov_health_job = "Q17", cov_student = "Q18",
        cov_losing_weight = "Q19", cov_cigarettes = "Q20")
for (v in names(mc)) nw[, (v) := x[[mc[[v]]]][match(id, x$id)]]
nw[, cov_birth_year := suppressWarnings(as.integer(cov_birth_year))]
nw[, id := frank(id, ties.method = "dense")]
setcolorder(nw, c("id", "task", "profile", "choice"))
setorder(nw, id, task, profile)
fwrite(nw, file.path(out, "miller_2024_news_selection.csv"))
## ---------- (2) scandal candidates ----------
m <- rd("funckmccabe_data.csv"); y <- m$x; lab <- m$lab; hn <- names(lab)
y[, id := .I]
y <- y[FL_177_DO %in% c("FL_178", "FL_179")]
y[, arm := fifelse(FL_177_DO == "FL_178", "forced", "abstention")]
fc <- list(c(86, 92, 96, 104, 100, 108), seq(112, 132, 4), seq(136, 156, 4), c(162, 166, 170, 178, 174, 182),
           seq(186, 206, 4), c(210, 214, 218, 226, 222, 230))
ac <- lapply(0:5, function(t) seq(235, 255, 4) + 24L * t)
fc <- lapply(fc, function(v) paste0("Q", v)); ac <- lapply(ac, function(v) paste0("Q", v))
rl <- c("Candidate A shares my views", "Candidate B shares my views", "Candidate A has good morals",
        "Candidate B has good morals", "Candidate A cares about people like me", "Candidate B cares about people like me")
for (q in unlist(c(fc, ac))) {
  j <- match(q, hn)
  stopifnot(grepl("would you vote for Candidate A", lab[j]), sub(".*- ", "", lab[j + 1:6]) == rl)
}
stopifnot(grepl("neither", lab[unlist(ac)]), !grepl("neither", lab[unlist(fc)]))
sc <- c("Strongly disagree" = 1L, "Somewhat disagree" = 2L, "Neither agree nor disagree" = 3L, "Somewhat agree" = 4L, "Strongly agree" = 5L)
coal <- function(cols) {  # the one non-empty answer among the 6 block variants of a task
  v <- rep("", nrow(y))
  for (cc in cols) { z <- y[[cc]]; w <- z != ""; stopifnot(v[w] == ""); v[w] <- z[w] }
  v
}
fn <- c("Abortion" = "abortion", "Age" = "age", "Gender" = "gender", "Government Spending" = "government_spending",
        "Immigration" = "immigration", "Profession" = "profession", "Race" = "race", "Religion" = "religion")
fm <- y$arm == "forced"
sk <- rbindlist(lapply(1:7, function(t) {
  k <- if (t <= 6) t else 1L
  fmt <- if (t <= 6) y$arm else ifelse(fm, "abstention", "forced")
  isf <- fmt == "forced"
  pick <- function(off) {  # answers in the forced and abstention column sets, chosen by format
    f <- coal(hn[match(fc[[k]], hn) + off]); b <- coal(hn[match(ac[[k]], hn) + off])
    ifelse(isf, f, b)
  }
  ans <- pick(0L); rat <- lapply(1:6, pick)
  blk <- ifelse(fm, y[[sprintf("FL_%d_DO", 179 + k)]], y[[sprintf("FL_%d_DO", 185 + k)]])
  stopifnot(grepl(sprintf("^Task%d--(D-R|R-D)--(High|Moderate|Low)--", k), blk) | blk == "")
  env <- ifelse(blk == "", NA_character_, sub("^Task[0-9]+--[DR]-[DR]--([A-Za-z]+)--.*", "\\1", blk))
  ord <- ifelse(blk == "", NA_character_, sub("^Task[0-9]+--([DR]-[DR])--.*", "\\1", blk))
  nshow <- unname(c(High = 8L, Moderate = 3L, Low = 0L)[env])
  stopifnot(ans[blk == ""] == "", unlist(rat)[rep(blk == "", 6)] == "")
  rbindlist(lapply(1:2, function(p) {
    r <- data.table(id = y$id, task = t, profile = p, ans = ans,
                    rating_shares_views = unname(sc[rat[[p]]]), rating_good_morals = unname(sc[rat[[2 + p]]]),
                    rating_cares = unname(sc[rat[[4 + p]]]),
                    attr_party = ifelse(is.na(ord), NA_character_, ifelse(substr(ord, 2 * p - 1, 2 * p - 1) == "D", "Democrat", "Republican")),
                    attr_news = y[[sprintf("G-%d-%d-1", k, p)]],
                    trial_arm = y$arm, trial_format = fmt, trial_info_environment = env,
                    trial_repeat_of = if (t <= 6) NA_integer_ else 1L)
    for (an in names(fn)) {
      v <- rep("(not shown)", nrow(y)); pos <- rep(NA_integer_, nrow(y))
      for (j in 1:8) {
        w <- which(y[[sprintf("F-%d-%d", k, j)]] == an & !is.na(nshow) & j <= nshow)
        v[w] <- y[[sprintf("F-%d-%d-%d", k, p, j)]][w]; pos[w] <- j
      }
      r[, paste0("attr_", fn[[an]]) := v][, paste0("attrpos_", fn[[an]]) := pos]
    }
    r
  }))
}))
sk <- sk[ans != "" | !is.na(rating_shares_views) | !is.na(rating_good_morals) | !is.na(rating_cares)]
stopifnot(sk$ans %in% c("", "Candidate A", "Candidate B", "Neither candidate"), sk[trial_format == "forced", all(ans != "Neither candidate")],
          !anyNA(sk[, .SD, .SDcols = patterns("^attr_")]), sk[, all(unlist(.SD) != ""), .SDcols = patterns("^attr_")],
          sk[, .N, .(id, task)][, all(N == 2)])
sk[, choice := fifelse(ans == "", NA_integer_, as.integer(ans == c("Candidate A", "Candidate B")[profile]))][, ans := NULL]
fcv <- c(cov_age_band = "Q2", cov_gender = "Q4", cov_education = "Q6", cov_race = "Q7", cov_hispanic = "Q8", cov_income = "Q9",
         cov_ideology = "Q11", cov_party_id = "Q12", cov_dem_strength = "Q13", cov_rep_strength = "Q14", cov_ind_lean = "Q15",
         cov_abortion = "Q383", cov_gov_spending = "Q384", cov_immigration = "Q385")
for (v in names(fcv)) sk[, (v) := y[[fcv[[v]]]][match(id, y$id)]]
sk[, id := frank(id, ties.method = "dense")]
setcolorder(sk, c("id", "task", "profile", "choice"))
setorder(sk, id, task, profile)
fwrite(sk, file.path(out, "miller_2024_scandal_candidates.csv"))
