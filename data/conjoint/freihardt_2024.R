##Flood-protection funding conjoint (US and Germany) from
##Freihardt, J., Buntaine, M. T., & Bernauer, T. (2024). Choosing to protect: public support for
##flood defense over relocation in climate change adaptation. Environmental Research Letters,
##19(10), 104012. https://doi.org/10.1088/1748-9326/ad6781
##Replication data: Zenodo doi:10.5281/zenodo.13253754 (version DOI; concept DOI 10.5281/zenodo.8408711),
##CC BY 4.0, no restricted files. Files read: Full_conjoint_raw_data_GER.csv and
##Full_conjoint_raw_data_US.csv (raw Qualtrics exports; only the columns listed below are read),
##Code_data_cleaning_and_analysis.R and "Survey instrument.pdf" as text (English survey, US
##version; the German wording is read from the data).
##Usage: Rscript freihardt_2024.R <dir holding the two csv files> <output dir>
##  writes freihardt_2024_flood_us.csv and freihardt_2024_flood_de.csv
##
##PII FOUND in both raw exports (dropped, never read into the output): IPAddress, LocationLatitude,
##LocationLongitude (every respondent), plus empty RecipientLastName/FirstName/Email/ExternalReference,
##panel ids pid/psid and the Qualtrics ResponseId (replaced by integers).
##
##Design: pairs of mid-sized communities applying for flood-protection funding; 7 attributes
##(frequency of floods, economic vitality = job change in the last 10 years, use of funds,
##lives lost in a large flood, property damage in a large flood, political position of the mayor,
##location relative to the respondent), 6 tasks (rounds) per respondent. Round 6 repeats round 1 with
##communities A and B swapped (checked for every respondent: same levels, A/B exchanged);
##kept as task 6 with trial_repeat_of = 1. The authors analyse rounds 1-5 only (n_rounds <- 5).
##Attribute order is randomized per respondent (embedded field AttributeOrder, constant across
##rounds - checked on the Qualtrics table of round 1 vs round 3); stored as attrpos_*.
##Two outcomes about the same tasks, both per community:
##  rating_allocation = dollars (euros in the German sample), in whole millions, allocated to this
##    community out of a $10 million grant ("Please distribute the $10 million grant between
##    community A and community B", any split summing to 10 allowed incl. 0 / 10); 0-10, higher =
##    more funding. The two profiles of a task sum to 10 (checked).
##  rating_support = "How much do you support or oppose funding for community A and community B?"
##    asked independently of the allocation, 1 Strongly oppose ... 5 Strongly support (the authors'
##    coding, code lines 'resp_support_coded').
##There is no choice column (no pick among profiles; allocations are continuous) and no opt-out.
##Level text = the authors' English recodes of the displayed text (code lines 'Re-code German
##conjoint attributes to English'): Every 5/10/20/50 years; 10% job loss / 5% job loss / No job
##growth or loss / 5% job growth / 10% job growth; Flood control infrastructure / Incentives to
##relocate; 10/50/100/500 lives; property damage $50/$250/$500 million/$2.5 billion (US) or
##EUR 50/250/500 million/2.5 billion (DE, displayed as '250 Millionen EUR'); Far-left /
##Center-left / Center / Center-right / Far-right; Within your county / Not in your county, but within
##your state / In another state (US 'In another US state' and German 'In einem anderen Bundesland',
##which the authors also pool as 'In another state'; German 'Landkreis' is 'county').
##Two tables, not one pooled table: although the authors stack the samples in their code, the
##displayed text differs (language, currency, county/state vs Landkreis/Bundesland), so one table
##per sample (cov_country is therefore absent). Quota samples (gender, age, education, region).
##Processing: only respondents with fertig == 1 (the authors' completion filter: 2,400 DE; the US
##count is in the return). In the German export a few cells carry US wording ('$', 'In another US
##state') or English strings for respondents with Q_Language DE/EN: the English strings are
##harmonised by the same recode; respondents with ANY '$' / 'US state' cell in the German sample
##are dropped (they saw the US instrument text). Tasks with a missing allocation or support answer
##are dropped (count in the return). Attention-check flags (fail_*) are not used by the authors'
##filter and are not stored.
##Covariates: cov_gender (quota_q1: Male/Female/Non-binary / other -> male/female/other), cov_age_group
##(quota_q2, text), cov_education (quota_q3, answer text in the survey's own categories),
##cov_birth_year (cov_q21, free-typed, plausible 1900-2010 whole numbers else NA),
##cov_party_id (cov_q19 answer text: US 'Strong Republican'...'Something else'; DE party list),
##cov_left_right (cov_q20 answer text), cov_language (Q_Language). Dropped: all other covariates,
##timers, attention items, rankings of attributes, durations. No survey weight in the exports.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rs <- 1:6
attrs <- c(freq = "Freq", econ = "Econ", use = "Use", lives = "Lives", prop = "Prop", pol = "Pol", loc = "Loc")
nm <- c(freq = "flood_frequency", econ = "economic_vitality", use = "funding_use", lives = "lives_lost",
        prop = "property_damage", pol = "political_position", loc = "location")
rc <- function(x, map) { y <- unname(map[trimws(x)]); y }
lvl <- list(
  freq = c("Alle 5 Jahre" = "Every 5 years", "Alle 10 Jahre" = "Every 10 years", "Alle 20 Jahre" = "Every 20 years", "Alle 50 Jahre" = "Every 50 years",
           "Every 5 years" = "Every 5 years", "Every 10 years" = "Every 10 years", "Every 20 years" = "Every 20 years", "Every 50 years" = "Every 50 years"),
  econ = c("10% weniger Arbeitsplätze" = "10% job loss", "5% weniger Arbeitsplätze" = "5% job loss", "Kein Arbeitsplatz-Verlust oder -Zuwachs" = "No job growth or loss",
           "5% mehr Arbeitsplätze" = "5% job growth", "10% mehr Arbeitsplätze" = "10% job growth", "10% job loss" = "10% job loss", "5% job loss" = "5% job loss",
           "No job growth or loss" = "No job growth or loss", "5% job growth" = "5% job growth", "10% job growth" = "10% job growth"),
  use = c("Anreize zur Umsiedlung" = "Incentives to relocate", "Infrastruktur für den Hochwasserschutz" = "Flood control infrastructure",
          "Incentives to relocate" = "Incentives to relocate", "Flood control infrastructure" = "Flood control infrastructure"),
  lives = c("10 Todesopfer" = "10 lives", "50 Todesopfer" = "50 lives", "100 Todesopfer" = "100 lives", "500 Todesopfer" = "500 lives",
            "10 lives" = "10 lives", "50 lives" = "50 lives", "100 lives" = "100 lives", "500 lives" = "500 lives"),
  pol = c("Weit links" = "Far-left", "Mitte-links" = "Center-left", "Mitte" = "Center", "Mitte-rechts" = "Center-right", "Weit rechts" = "Far-right",
          "Far-left" = "Far-left", "Center-left" = "Center-left", "Center" = "Center", "Center-right" = "Center-right", "Far-right" = "Far-right"),
  loc = c("In Ihrem Landkreis" = "Within your county", "Nicht in Ihrem Landkreis, aber in Ihrem Bundesland" = "Not in your county, but within your state",
          "In einem anderen Bundesland" = "In another state", "In another German state" = "In another state", "In another US state" = "In another state",
          "In another state" = "In another state", "Within your county" = "Within your county",
          "Not in your county, but within your state" = "Not in your county, but within your state"))
prop_us <- c("$50 million" = "$50 million", "$250 million" = "$250 million", "$500 million" = "$500 million", "$2.5 billion" = "$2.5 billion")
prop_de <- c("50 Millionen €" = "EUR 50 million", "250 Millionen €" = "EUR 250 million", "500 Millionen €" = "EUR 500 million", "2.5 Milliarden €" = "EUR 2.5 billion",
             "50 million €" = "EUR 50 million", "250 million €" = "EUR 250 million", "500 million €" = "EUR 500 million", "2.5 billion €" = "EUR 2.5 billion")
supp <- c("Strongly oppose" = 1L, "Somewhat oppose" = 2L, "Neutral" = 3L, "Somewhat support" = 4L, "Strongly support" = 5L)
build <- function(file, country, outname) {
  h <- names(fread(file, nrows = 0))
  comm <- unique(unlist(lapply(rs, function(r) as.vector(t(outer(c("A", "B"), attrs, function(ab, at) paste0("Round", r, "Comm", ab, at)))))))
  q <- unlist(lapply(rs, function(r) c(paste0("cj_r", r, "_q1_1_", 1:2), paste0("cj_r", r, "_q2_", 1:2))))
  cols <- c("ResponseId", "fertig", "Q_Language", "AttributeOrder", "quota_q1", "quota_q2", "quota_q3", "cov_q19", "cov_q20", "cov_q21", comm, q)
  stopifnot(all(cols %in% h))
  x <- fread(file, select = cols, colClasses = "character")[-(1:2)]
  x <- x[fertig == "1"]
  cat(country, "finished:", nrow(x), "\n")
  if (country == "DE") {
    bad <- x[, Reduce(`|`, lapply(.SD, function(v) grepl("\\$|US state", v))), .SDcols = comm]
    cat("DE respondents with US wording dropped:", sum(bad), "\n")
    x <- x[!bad]
  }
  x[, id := .I]
  pm <- if (country == "US") prop_us else prop_de
  L <- list()
  for (r in rs) for (ab in 1:2) {
    ch <- c("A", "B")[ab]
    d <- data.table(id = x$id, task = r, profile = ab)
    for (a in names(attrs)) {
      v <- x[[paste0("Round", r, "Comm", ch, attrs[[a]])]]
      set(d, j = paste0("attr_", nm[[a]]), value = if (a == "prop") rc(v, pm) else rc(v, lvl[[a]]))
    }
    ord <- strsplit(x$AttributeOrder, "-", fixed = TRUE)
    for (a in names(attrs)) set(d, j = paste0("attrpos_", nm[[a]]), value = vapply(ord, function(o) match(a, o), 1L))
    set(d, j = "rating_allocation", value = as.numeric(x[[paste0("cj_r", r, "_q1_1_", ab)]]))
    set(d, j = "rating_support", value = unname(supp[trimws(x[[paste0("cj_r", r, "_q2_", ab)]])]))
    set(d, j = "trial_repeat_of", value = if (r == 6) 1L else NA_integer_)
    L[[length(L) + 1]] <- d
  }
  d <- rbindlist(L)
  a_cols <- grep("^attr_", names(d), value = TRUE)
  ok <- d[, .(ok = !anyNA(.SD) && !anyNA(rating_allocation) && !anyNA(rating_support)), by = .(id, task), .SDcols = c(a_cols, "rating_allocation", "rating_support")]
  cat(country, "tasks dropped (missing level/answer):", sum(!ok$ok), "of", nrow(ok), "\n")
  d <- merge(d, ok[ok == TRUE, .(id, task)], by = c("id", "task"))
  d <- d[d[, .N, .(id, task)][N == 2, .(id, task)], on = c("id", "task")]
  s <- d[, .(s = sum(rating_allocation)), .(id, task)]
  cat(country, "allocation sums:", paste(names(table(s$s)), table(s$s), collapse = "; "), "\n")
  d <- d[s[s == 10, .(id, task)], on = c("id", "task")]
  # repeat check: round 6 = round 1 with A/B swapped
  r1 <- d[task == 1, c("id", "profile", a_cols), with = FALSE]; r6 <- d[task == 6, c("id", "profile", a_cols), with = FALSE]
  r6[, profile := 3L - profile]
  m <- merge(r1, r6, by = c("id", "profile"), suffixes = c("", ".6"))
  same <- Reduce(`&`, lapply(a_cols, function(v) m[[v]] == m[[paste0(v, ".6")]]))
  cat(country, "round 6 equals round 1 with A/B swapped:", sum(same), "of", nrow(m), "profile pairs\n")
  # covariates
  g <- c("Male" = "male", "Female" = "female", "Non-binary / other" = "other")
  cv <- x[, .(id, cov_gender = unname(g[quota_q1]), cov_age_group = quota_q2, cov_education = quota_q3,
              cov_birth_year = suppressWarnings(as.integer(cov_q21)), cov_party_id = cov_q19, cov_left_right = cov_q20,
              cov_language = Q_Language)]
  cv[!(cov_birth_year %in% 1900:2010), cov_birth_year := NA_integer_]
  for (v in c("cov_age_group", "cov_education", "cov_party_id", "cov_left_right")) cv[get(v) == "", (v) := NA_character_]
  d <- merge(d, cv, by = "id")
  d[, id := as.integer(factor(id))]
  setcolorder(d, c("id", "task", "profile", "rating_allocation", "rating_support"))
  setorder(d, id, task, profile)
  cat(country, "rows", nrow(d), "respondents", uniqueN(d$id), "\n")
  fwrite(d, file.path(out, outname))
  invisible(d)
}
de <- build(file.path(raw, "Full_conjoint_raw_data_GER.csv"), "DE", "freihardt_2024_flood_de.csv")
if (file.exists(file.path(raw, "Full_conjoint_raw_data_US.csv"))) us <- build(file.path(raw, "Full_conjoint_raw_data_US.csv"), "US", "freihardt_2024_flood_us.csv")
