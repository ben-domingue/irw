##Contact-tracing-app vignette experiment (US, June 2020) from
##Zhang, B., Kreps, S., McMurry, N., & McCain, R. M. (2020). Americans' perceptions of privacy and
##surveillance in the COVID-19 pandemic. PLOS ONE, 15(12), e0242652.
##https://doi.org/10.1371/journal.pone.0242652
##Replication data: Harvard Dataverse doi:10.7910/DVN/5UEFP6, CC0 1.0, no restricted files.
##File read: survey_data_june_24_25_2020.RData (object d, 2,703 x 411, with haven value labels).
##Read as text only: README.md, covid_privacy_analysis_code.R. Design and wording from the article
##(Methods, Table 1). Not read: the six *.tab population margins (inputs for the authors' weights).
##Usage: Rscript zhang_2020.R <dir holding survey_data_june_24_25_2020.RData> <output dir>
##
##Lucid quota sample, June 24-25 2020 (100-person pilot on June 24 included). 2,703 started; the
##2,057 who reached the conjoint block each read ONE short news article about a hypothetical app
##(task = profile = 1), shown as prose (presentation = text). The source stores, per respondent,
##the article HTML as displayed (ca_nographic / ca_graphic) and each randomized slot:
##  attr_developer: "Apple and Google" / "The Centers for Disease Control and Prevention (CDC)" /
##    "Your state government" / "A group of researchers at leading universities" (source slot text
##    minus its trailing verb "are"/"is", e.g. "Apple and Google are building a ...")
##  attr_app_name: "contact tracing" / "exposure notification" ("... building a contact tracing app")
##  attr_technology: "GPS data that track users’ location" / "Bluetooth data that does not track users’
##    location" / "Bluetooth data that does not track users’ locations, with an illustration of how
##    the app works" (third level: the source slot is blank and the displayed article reads "The app
##    uses Bluetooth data that does not track users’ locations. ... Here is how the app works:"
##    followed by a BBC graphic; the article's Table 1 level 3; explainer_graphic == 1 exactly)
##  attr_users_needed: "at least 60%" / "at least 80%" ("Public health experts say that at least 80%
##    of US smartphone users need to use this app ...")
##  attr_data_storage: the three sentences shown together (storage, costs/benefits, how it runs),
##    one of two blocks (decentralized / centralized), joined with a space as displayed
##  attr_expiration: "The app would expire after a successful vaccine for COVID-19 has been
##    discovered." / "The app would expire after the Centers for Disease Control and Prevention
##    (CDC) declares the COVID-19 Pandemic is over." / "(not shown)" (no sentence; Table 1 "no
##    expiration date information given"; the displayed article has an empty paragraph)
##Every level was checked against the displayed article HTML of every respondent (stopifnot below).
##Outcomes (one row per respondent who answered at least one; all ratings, stored as in the source
##with refusals -99 and Don't know -88 set to NA):
##  rating_download (0-100): "On a 0 to 100 scale, how likely are you to download this app a[nd use
##    it]..." (source label truncated); asked only of smartphone owners; in a random half preceded by
##    "Suppose that you got a notification on your phone to download this app." (trial_notification = 1)
##  rating_report (0-100): "On a 0 to 100 scale, How likely are you to report to this app if you tested
##    positive for COVID-19..." (truncated); smartphone owners only
##  rating_guess_perc (0-100): "By your best guess, what percentage of people in your town or city
##    would use this app?"
##  rating_consequence_<k> (1 Yes, 0 No; Don't know -> NA): "If enough people in the US population
##    were to use this app, do you think it would...": 1 Help limit the spread of COVID-19, 2 Improve
##    the economy, 3 Make it safer for workers to return to work, 4 ... students to return to school,
##    5 ... for me to visit friends and family, 6 Violate people's privacy, 7 Violate people's civil
##    liberties, 8 Threaten US democracy, 9 Make tech companies too powerful
##  rating_confident_data (0 Not confident at all .. 3 Very confident)
##  rating_require_government, rating_auto_install, rating_require_employers, rating_require_worship,
##    rating_choice_to_report: five statements, -2 Strongly disagree .. 2 Strongly agree; the
##    government statement names "The federal government" or "Your state government" at random
##    (trial_government_level).
##The authors' mean-imputation of missing outcomes is not applied (NAs stay NA).
##Other randomizations recorded: trial_notification (above); trial_government_level. Earlier,
##unrelated survey experiments (priming, policy blocks) are not kept.
##Covariates (survey answers; value labels in the .RData): cov_gender (gen: Male/Female/Other;
##refused -99 -> NA), cov_birth_year (bornyear label text), cov_age (the `age` column, Lucid's
##record, in years), cov_education (edu label text), cov_party_id (pid label text: Republican,
##Democrat, Independent, Other party), cov_ideology_code (1 Very conservative .. 5 Very liberal),
##cov_income_code (1 < $20,000 .. 9 > $160,000), cov_state (label text), cov_cellphone_type_code
##(1 Android, 2 iPhone, 3 Windows, 4 Blackberry, 5 Basic non-smartphone, 6 Other; NA = no cellphone
##or not asked).
##Dropped: Qualtrics metadata (V1 ResponseId, V8/V9 timestamps, IP-free) and Lucid rid (re-keyed to
##integers in source order), open-ended text, comprehension checks, Lucid's own demographics, the
##646 respondents who never reached the conjoint block. No weight is deposited: the authors rake
##weights in their code from the *.tab margins (survey_weight = not_kept).
##N: 2,057 respondents saw the article; the article reports N = 1,883 for the download question
##(smartphone owners, after mean-imputing refusals); here rating_download has fewer non-missing
##values (refusals kept as NA).
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "survey_data_june_24_25_2020.RData"), envir = e); s <- e$d
s <- s[s$ca_nographic != "", ]
stopifnot(nrow(s) == 2057)
lab <- function(x) { l <- attr(x, "labels"); v <- as.character(zap_labels(x)); r <- setNames(names(l), l)[v]; r[!is.na(v) & as.numeric(v) < 0] <- NA; unname(r) }
num <- function(x) { x <- as.numeric(zap_labels(x)); x[x %in% c(-99, -88)] <- NA; x }
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L)
d[, attr_developer := sub(" (is|are)$", "", s$app_developer)]
d[, attr_app_name := sub("^an? ", "", s$app_name)]
d[, attr_technology := fifelse(s$tech_used == "", "Bluetooth data that does not track users’ locations, with an illustration of how the app works", s$tech_used)]
d[, attr_users_needed := paste0("at least ", s$percent_needed, "%")]
d[, attr_data_storage := paste(s$data_storage, s$costs_benefits, s$actual_use)]
d[, attr_expiration := fifelse(s$expire_app == "", "(not shown)", s$expire_app)]
## checks against the displayed article
html <- gsub("&nbsp;", " ", s$ca_nographic)
gh <- gsub("&nbsp;", " ", s$ca_graphic)
stopifnot(all(mapply(grepl, paste(s$app_developer, "building", s$app_name, "app"), html, fixed = TRUE)),
          all(mapply(grepl, paste0("at least ", s$percent_needed, "% of US smartphone users"), html, fixed = TRUE)),
          all(mapply(grepl, s$data_storage, html, fixed = TRUE)), all(mapply(grepl, s$costs_benefits, html, fixed = TRUE)),
          all(mapply(grepl, s$actual_use, html, fixed = TRUE)),
          all(mapply(grepl, s$expire_app, html, fixed = TRUE)), !any(grepl("would expire", html[s$expire_app == ""])),
          all((s$tech_used == "") == (s$explainer_graphic == "1")),
          all(grepl("Bluetooth data that does not track users’ locations. The app will not reveal the identity of infected persons. Here is how the app works:", gh[s$tech_used == ""], fixed = TRUE)),
          all(grepl("<img", gh[s$tech_used == ""], fixed = TRUE)),
          all(mapply(grepl, paste0("The app uses ", s$tech_used[s$tech_used != ""]), html[s$tech_used != ""], fixed = TRUE)))
d[, rating_download := num(s$download_likely)]
d[, rating_report := num(s$report_likely)]
d[, rating_guess_perc := num(s$guess_perc)]
for (k in 1:9) d[, paste0("rating_consequence_", k) := num(s[[paste0("app_outcome_", k)]])]
d[, rating_confident_data := num(s$confident_data)]
d[, rating_require_government := num(s$gov_use_app)]
d[, rating_auto_install := num(s$auto_install_app)]
d[, rating_require_employers := num(s$empl_use_app)]
d[, rating_require_worship := num(s$rel_use_app)]
d[, rating_choice_to_report := num(s$obligation_report)]
d[, trial_notification := as.integer(s$notification_download != "")]
d[, trial_government_level := s$government_level_q]
d[, cov_gender := c("male", "female", "other")[match(as.numeric(zap_labels(s$gen)), 1:3)]]
d[, cov_birth_year := as.integer(lab(s$bornyear))]
d[, cov_age := as.integer(s$age)]
d[, cov_education := lab(s$edu)]
d[, cov_party_id := lab(s$pid)]
d[, cov_ideology_code := num(s$pol_ideology)]
d[, cov_income_code := num(s$income)]
d[, cov_state := lab(s$state)]
d[, cov_cellphone_type_code := num(s$cellphone_type)]
rc <- grep("^rating_", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..rc])) > 0]
d[, id := seq_len(.N)]
stopifnot(all(d$rating_download %between% c(0, 100), na.rm = TRUE), all(d$rating_require_government %in% c(-2:2, NA)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhang_2020_contact_tracing_app.csv"))
