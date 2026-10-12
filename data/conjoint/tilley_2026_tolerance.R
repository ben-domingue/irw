##Three paired conjoints on political tolerance (Britain), Brexit panel wave 4, from
##Tilley, J., Bejan, T., & Hobolt, S. B. (2026). Partisan (in)tolerance and affective polarization. British
##Journal of Political Science, 56, e36. https://doi.org/10.1017/S0007123426101550
##Replication data: Harvard Dataverse doi:10.7910/DVN/S0J0BZ, CC0 1.0. File read: BrexitPanel4only (04-08-23).sav
##(Dataverse "original format" download, saved as brexit.sav; read with foreign::read.spss because haven cannot parse
##it); Tolerance conjoints - main paper.Rmd read as text for the outcome coding.
##Usage: Rscript tilley_2026_tolerance.R <dir holding brexit.sav> <output dir>
##
##4,127 respondents of the wave-4 file, each with THREE separate paired conjoints of 3 tasks x 2 profiles (A = 1, B = 2),
##different attribute sets, so three tables (one experiment each, per the one-experiment rule):
##  tilley_2026_protest_tolerance (C2, 8 attributes): two protests; party of the politicians associated with the protest,
##    number of people, police presence, road closures, share of the population who agree with the aim, duration, noise
##    level, likely type of protest.
##  tilley_2026_platform_ban (C3, 6 attributes): two politicians; party, how many people are offended, whether the
##    politician holds office, years in politics, share of the population who agree with a ban, threatening language.
##  tilley_2026_school_speaker (C4, 6 attributes): two politicians; party, how many people are offended, years in
##    politics, current position, protest outside the school, social-media record.
##Outcome (one per table, TolCJ{1,2,4}_screen{1,2,3}, value labels): "Which of the two protests do you think should go
##ahead?" (1 Only protest A, 2 Only protest B, 3 Both, 4 Neither), "Which of the two politicians do you think should
##be banned?" (1 Only A, 2 Only B, 3 Both, 4 Neither) and "Which of the two politicians do you think should be allowed
##to speak [at the school]?" (same four answers). Because BOTH or NEITHER can be the answer, the answer is not a pick
##among profiles: it is stored per profile as rating (1 = this protest should go ahead / this politician should be
##banned / this politician should be allowed to speak, 0 = not). The authors' own `newchoice` recodes the same
##answers in the restricting direction for the protest and speaker tables (1 = restrict); here the raw direction of the
##question wording is kept. 8 = "Skipped" is dropped.
##Level text is the SPSS value label of each C{2,3,4}_src_<screen>_attr<k>_<profile> column. In the deposit the variable
##labels of C3 attr3/attr4 are swapped relative to their value labels; the value labels (office / years in politics) are
##used. The order in which attributes were listed is randomised per respondent (C{2,3,4}_attr_order holds a
##permutation) but what the permutation indexes is not documented, so no attrpos_ columns are kept. The HTML of the
##screens (C*_screen*_table) is cut by the SPSS reader and not used. Randomization restrictions are not documented.
##Covariates: cov_gender (profile_gender: 1 Male, 2 Female), cov_age (age), cov_education (profile_education_level
##value-label text; Skipped/Prefer not to say -> NA), cov_party_id (pid1 value-label text: Conservative, Labour,
##Liberal Democrat, SNP, Plaid Cymru, Green, Other party, None, Don't know; Skipped -> NA). The file's W8 (mean 1.0, no
##label) is probably a weight but is undocumented, so no weight is kept. Dropped: all postcode/constituency/local-authority
##geography, panel IDs (ID_W1..W4), timestamps, free-text fields, the respondent's other tolerance items and
##thermometers. id = row number.
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
suppressMessages(library(data.table))
x <- as.data.table(suppressWarnings(foreign::read.spss(file.path(raw, "brexit.sav"), to.data.frame = TRUE,
                                      use.value.labels = TRUE, reencode = "UTF-8")))
stopifnot(nrow(x) == 4127)
x[, id := .I]
chr <- function(v) { v <- trimws(as.character(v)); v[v %in% c("Skipped", "Not Asked", "")] <- NA; v }
cov <- data.table(id = x$id,
  cov_gender = c(Male = "male", Female = "female")[chr(x$profile_gender)],
  cov_age = as.integer(as.character(x$age)),
  cov_education = {e <- chr(x$profile_education_level); e[e == "Prefer not to say"] <- NA; e},
  cov_party_id = chr(x$pid1))
build <- function(prefix, tol, nattr, names, outcome_lab, file) {
  L <- list()
  for (s in 1:3) {
    ans <- chr(x[[sprintf("TolCJ%s_screen%d", tol, s)]])
    for (p in 1:2) {
      d <- data.table(id = x$id, task = s, profile = p)
      for (k in 1:nattr) d[[paste0("attr_", names[k])]] <- chr(x[[sprintf("%s_src_%d_attr%d_%d", prefix, s, k, p)]])
      yes <- grepl("^Both", ans) | grepl(if (p == 1) "^Only (protest|politician) A " else "^Only (protest|politician) B ", ans)
      stopifnot(all(grepl("^(Both|Neither|Only)", ans[!is.na(ans)])))
      d$rating <- ifelse(is.na(ans), NA_integer_, as.integer(yes))
      L[[length(L) + 1]] <- d
    }
  }
  d <- rbindlist(L)
  d <- d[!is.na(rating)]
  ac <- grep("^attr_", names(d), value = TRUE)
  stopifnot(!anyNA(d[, ..ac]))
  stopifnot(d[, .N, .(id, task, profile)][, all(N == 1)])
  d <- merge(d, cov, by = "id")
  setcolorder(d, c("id", "task", "profile", "rating"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, file))
  cat(file, nrow(d), uniqueN(d$id), "\n"); print(d[, mean(rating), .(profile)])
}
build("C2", 1, 8, c("party", "attendance", "police", "roads_closed", "public_agreement", "duration", "noise", "protest_type"),
      "", "tilley_2026_protest_tolerance.csv")
build("C3", 2, 6, c("party", "offence", "office", "years_in_politics", "public_support_ban", "threats"),
      "", "tilley_2026_platform_ban.csv")
build("C4", 4, 6, c("party", "offence", "years_in_politics", "position", "school_protest", "social_media"),
      "", "tilley_2026_school_speaker.csv")
