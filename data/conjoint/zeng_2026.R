##Banning foreign social media apps: paired conjoint, US public (initial wave)
##Zeng, K., Raess, D., & Musgrave, P. (2026). Friending or Blocking? U.S. public attitudes toward restricting
##foreign social media apps. International Studies Quarterly. (no article DOI in the deposit)
##Replication data: Harvard Dataverse doi:10.7910/DVN/7Z6VRO, CC0 1.0. File read: "Replication 2.zip" ->
##Replication/data/input/Initial Wide 2026 07 22.dta (13 MB; saved as initial_wide.dta), plus README.txt and
##code/01_clean_initial_wave.do, code/04_analysis_conjoint.do (read as text: pipe-delimited level strings,
##question wording, programmed shares, constraint). The recontact-wave file (Recontact Wide) and the
##authors' 160-370 MB long files are not used; the recontact wave re-surveys a subset with new conjoint
##tasks and is not stored here.
##Usage: Rscript zeng_2026.R <dir holding initial_wide.dta> <output dir>
##
##1,494 US adult online respondents (vendor not stated in the deposit), each seeing 6 tasks of 2 hypothetical
##foreign social media apps described by 9 attributes, plus a 7th task that repeats task 1 with the two
##profiles in swapped positions (the authors' attention check; trial_repeat_of = 1 on task 7, profiles
##swapped: task 7 profile 1 is task 1 profile 2 and vice versa, verified on the data for all respondents).
##The attributes are in the wide file as pipe-delimited strings: orderK = the 9 attribute names in the order shown
##in task K (attribute order is randomized per task: attrpos_ columns), traitsKa / traitsKb = the levels of app
##A / B in the same order. Level text is the displayed text.
##Outcomes (do-file notes, Qualtrics question text):
##  choice  = "Which app would you most support the U.S. government banning?" (App A / App B); forced choice,
##            no opt-out; 2 respondents have an empty choice in task 1 (choice NA on both profiles of
##            that task, their ratings kept).
##  rating  = "Would you support or oppose the federal government banning each app from being used in the United
##            States?" asked for each app; 5-point, coded 1 Strongly oppose, 2 Somewhat oppose, 3 Neither
##            support nor oppose, 4 Somewhat support, 5 Strongly support (the authors' coding, do-file lines
##            ~250-265). Higher = more support for the ban.
##Randomization (do-file Table A3 code): programmed level shares are not uniform: risk to military/intel and risk
##to corporate interests High 10% / Moderate 70% / Low 20%; home-country regime Not democratic 30 / Partially 27 /
##Highly 43; reciprocity Bans all U.S. apps 20 / allows with restrictions 40 / without any restrictions 40;
##privacy 50/50, audience and employment uniform; owner not stated. Restriction seen in the data: "Owned by the
##government" never appears with "Highly democratic" (0 of 4,573 rows with that regime vs ~2,000 per other regime), all
##other pairs of levels occur. The authors' AMCE code also passes a constraint (constraints(cj_levels_4_num#
##cj_levels_9_num)) to the conjoint command; no document in the deposit describes the rule.
##Tasks whose attribute strings are empty (task 5 for 50 respondents, who nevertheless have a recorded choice) cannot
##be reconstructed and are dropped (not stored with blank levels).
##Covariates: cov_gender (Female/Male; prefer not to say and non-binary -> NA/other as below), cov_birth_year,
##cov_education (answer text), cov_party_id (partyidmain text), cov_party_id7 (pid7 label text), cov_use_tiktok
##(0/1 as recorded), cov_mobile (Desktop/Mobile), cov_duration_sec (Qualtrics survey duration, seconds).
##Dropped: personid and the Z#### panel ids (ids re-keyed to integers), start/end timestamps, timers, OS string,
##free text (race other, job other, marital other), seeds, income and all other items (not needed). No IP/lat-long.
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "initial_wide.dta")))
f <- function(s) as.character(as_factor(s))
x[, id := .I]
stopifnot(nrow(x) == 1494)
ratemap <- c("Strongly oppose" = 1L, "Somewhat oppose" = 2L, "Neither support nor oppose" = 3L, "Somewhat support" = 4L, "Strongly support" = 5L)
an <- c("Risk to US corporate and business interests" = "risk_corporate", "Owner of the app" = "owner", "Data privacy protections" = "privacy",
        "Effect of allowing app on US employment" = "employment", "Risk to US military and intelligence agencies" = "risk_military",
        "Target audience" = "audience", "App policies toward false or misleading content" = "moderation",
        "App home country policies toward US social media apps" = "reciprocity", "Type of government in app home country" = "regime")
res <- list()
for (t in 1:7) {
  ord <- if (t == 7) f(x$ordercheck) else f(x[[paste0("order", t)]])
  tr <- list(a = if (t == 7) f(x$traitschecka) else f(x[[paste0("traits", t, "a")]]),
             b = if (t == 7) f(x$traitscheckb) else f(x[[paste0("traits", t, "b")]]))
  ch <- f(x[[paste0("cj", t, "choice")]])
  O <- strsplit(ord, "|", fixed = TRUE)
  for (p in c("a", "b")) {
    r <- f(x[[if (t == 2) paste0("ch2rate_", p) else paste0("cj", t, "rate_", p)]])
    d <- data.table(id = x$id, task = t, profile = if (p == "a") 1L else 2L,
                    choice = ifelse(ch %in% c("App A", "App B"), as.integer(ch == paste("App", toupper(p))), NA_integer_),
                    rating = unname(ratemap[r]))
    L <- strsplit(tr[[p]], "|", fixed = TRUE)
    ok <- lengths(O) == 9 & lengths(L) == 9                      # tasks never shown (dropout) have empty strings
    O[!ok] <- list(rep(NA_character_, 9)); L[!ok] <- list(rep(NA_character_, 9))
    for (nm in names(an)) {
      pos <- vapply(O, function(o) { w <- which(trimws(o) == nm); if (length(w) == 1) w else NA_integer_ }, integer(1))
      d[, paste0("attr_", an[nm]) := mapply(function(l, i) if (is.na(i)) NA_character_ else trimws(l[i]), L, pos)]
      d[, paste0("attrpos_", an[nm]) := pos]
    }
    d[, trial_repeat_of := if (t == 7) 1L else NA_integer_]
    res[[length(res) + 1]] <- d
  }
}
d <- rbindlist(res)
cv <- x[, .(id, g = f(gender), cov_birth_year = as.integer(yearborn), cov_education = f(education), cov_party_id = f(partyidmain),
            cov_party_id7 = f(pid7), cov_use_tiktok = as.integer(use_tiktok), cov_mobile = f(mobile), cov_duration_sec = as.integer(duration))]
cv[, cov_gender := ifelse(g == "Female", "female", ifelse(g == "Male", "male", ifelse(g == "Non-binary / third gender", "other", NA_character_)))][, g := NULL]
cv[!(cov_birth_year >= 1920 & cov_birth_year <= 2010), cov_birth_year := NA_integer_]
d <- merge(d, cv, by = "id")
d <- d[!is.na(attr_regime)]                                       # tasks not shown
d <- d[!(is.na(choice) & is.na(rating))]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %in% c(1:5, NA))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zeng_2026_foreign_social_media.csv"))
