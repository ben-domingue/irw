##Discrete choice experiment on outcomes of a home-visiting programme for teenage mothers (Family
##Nurse Partnership), UK general public, from
##Stamuli, E., Richardson, G., Robling, M., et al. (2020). A discrete-choice experiment to capture
##public preferences on the benefits of home-visiting programme for teenage mothers. F1000Research,
##9, 677. https://doi.org/10.12688/f1000research.23966.1
##Replication data: Harvard Dataverse doi:10.7910/DVN/DUL9KT ("FNP Discrete Choice experiment"),
##CC0 1.0, no restricted files. Extended data, also CC0 1.0, no restricted files: designs
##doi:10.7910/DVN/GK4TPV ("Designs A to D.docx", the displayed choice sets), variables key
##doi:10.7910/DVN/L8QOKC, patient information sheet doi:10.7910/DVN/JBVRTZ (survey intro).
##Files read: "Final pooled DCE data_difference in variables.dta" (Dataverse "original format"
##download), "Designs A to D.docx" (parsed here: document.xml, one table cell per scenario).
##"Variables key.docx" and "Patient information sheet.docx" read by hand. Article read online
##(F1000Research, open access).
##Usage: Rscript stamuli_2020.R <raw dir> <output dir>
##
##Dynata (Research Now) UK online panel, adults 18+, 1,008 respondents (article and variables key:
##200 design A, 201 design B, 200 design C, 200 design D, and 207 who completed all four designs).
##Fixed blocked designs (SAS, D-efficient main-effects fractional factorials): every design has
##the two common attributes (second pregnancy, A&E attendance) plus three design-specific ones;
##A-C have 15 choice sets, D 16. Each choice set = 2 scenarios (A left = profile 1, B right =
##profile 2), each a list of 5 outcome statements; no opt-out (the information sheet: "make a
##choice between Scenario A and Scenario B. Place a tick in one box from each set").
##FOUR TABLES, one per design (stamuli_2020_fnp_outcomes_a/_b/_c/_d): the designs have different
##attribute sets and the article estimates one model per design, pooling the single-design
##respondents with the all-four respondents (407-408 per design), as here.
##  choice = choice (1 = Scenario A, 2 = Scenario B; equals the key's Choice, checked):
##           information sheet: "We would like you to choose which scenario you prefer out of a
##           choice of two."
##task = Choiceset, the choice-set number of the fixed design (1-15/16). The order in which sets
##(and, for the all-four group, designs) were shown is not recorded; task is the set number, not
##the display position. trial_group = "one design" or "all four designs".
##Attribute text = the statements of "Designs A to D.docx" for that design, choice set and
##scenario; each statement is assigned to its attribute by its wording. The script checks that
##the docx and the .dta codes agree one-to-one for every attribute (e.g. pregnancy_a = 1 always
##with "Mother had another pregnancy ...") and that every respondent of a design saw the same
##sets. The mother's health attribute (design D, health_a 0-3, EQ-5D values 1/.848/.883/.812) has 4
##levels, the others 2. Statements are listed in the same order in every set (checked): fixed
##attribute order.
##Covariates (panel profile, text as stored, "N/A" -> NA): cov_age, cov_gender (Male/Female ->
##male/female), cov_education (Education, the panel's answer text), cov_region (GOR region),
##cov_social_grade, cov_occupation, cov_marital_status, cov_guardian, cov_home_status,
##cov_tobacco_interest, cov_smoking_history. Dropped: SubsIDUniqueId (panel member ID), the
##Confirmit project number, constant wave/country fields, region generalizations, tobacco
##products purchased, the design-version bookkeeping (dVrsn*, append*, Designs, dummy_*), the
##authors' A-minus-B difference variables and EQ-5D weights (derived). No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
# --- displayed choice sets from the designs docx ---
td <- tempfile(); unzip(file.path(raw, "Designs A to D.docx"), "word/document.xml", exdir = td)
x <- paste(readLines(file.path(td, "word/document.xml"), warn = FALSE, encoding = "UTF-8"), collapse = "")
para <- function(ch) { p <- strsplit(ch, "</w:p>", fixed = TRUE)[[1]]; p <- gsub("<[^>]+>", "", p)
  p <- gsub("&amp;", "&", p, fixed = TRUE); p <- gsub("&apos;|’", "'", p); p <- trimws(gsub("\\s+", " ", p)); p[p != ""] }
design <- NA; cs <- NA; state <- 0; L <- list()
for (ch in strsplit(x, "</w:tc>", fixed = TRUE)[[1]]) {
  ps <- para(ch)
  for (q in ps) {
    if (grepl("^Design [A-D]$", q)) design <- sub("Design ", "", q)
    if (grepl("^Choice set\\s*[0-9]+$", q)) { cs <- as.integer(sub("\\D+", "", q)); state <- 1 }
  }
  if (state == 1 && length(ps) && ps[1] == "Scenario A") { state <- 2; next }
  if (state == 2 && length(ps) && ps[1] == "Scenario B") { state <- 3; next }
  if (state %in% 3:4) { L[[length(L) + 1]] <- data.table(design, set = cs, profile = state - 2L, pos = seq_along(ps), text = ps)
                        state <- if (state == 3) 4 else 0 }
}
dx <- rbindlist(L)
stopifnot(dx[, .N, .(design, set, profile)][, all(N == 5)], dx[, uniqueN(set), design]$V1 == c(15, 15, 15, 16))
pat <- c(pregnancy = "another pregnancy", AandE = "accident and emergency", education = "in education", smoking = "smoke",
         breastfeeding = "breastfe", employment = "employed", attachment = "emotional bond", vaccines = "vaccinations",
         confidence = "confident", child_needs = "child's needs", birth_weight = "weight", relationship = "relationship",
         language = "spoken language", health = "problems with mobility")
dx[, attr := names(pat)[sapply(text, function(t) { m <- which(sapply(pat, grepl, x = t, fixed = TRUE)); stopifnot(length(m) == 1); m })]]
stopifnot(dx[, uniqueN(attr), .(design, pos)][, all(V1 == 1)])  # same statement order in every set
# --- responses ---
s <- as.data.table(zap_labels(read_dta(file.path(raw, "Final pooled DCE data_difference in variables.dta"))))
s[, design := fifelse(!is.na(education_a), "A", fifelse(!is.na(employment_a), "B", fifelse(!is.na(confidence_a), "C",
                fifelse(!is.na(relationship_a), "D", NA_character_))))]
stopifnot(!anyNA(s$design), s[, .N, .(id, design, Choiceset)][, all(N == 1)], all(s$choice %in% 1:2),
          all((s$choice == 1) == (s$Choice == 1)), s[, uniqueN(Designs), id][, all(V1 == 1)])
attrs <- list(A = c("pregnancy", "AandE", "education", "smoking", "breastfeeding"), B = c("pregnancy", "AandE", "employment", "attachment", "vaccines"),
              C = c("pregnancy", "AandE", "confidence", "child_needs", "birth_weight"), D = c("pregnancy", "AandE", "relationship", "language", "health"))
anm <- c(pregnancy = "second_pregnancy", AandE = "ae_attendance", education = "education", smoking = "smoking", breastfeeding = "breastfeeding",
         employment = "employment", attachment = "prenatal_attachment", vaccines = "vaccinations", confidence = "self_efficacy",
         child_needs = "child_centeredness", birth_weight = "birth_weight", relationship = "partner_relationship",
         language = "language_development", health = "mother_health")
na <- function(v) fifelse(v %in% c("", "N/A"), NA_character_, v)
stopifnot(all(s$Gender %in% c("Male", "Female")))
for (g in names(attrs)) {
  x <- s[design == g]
  d <- rbindlist(lapply(1:2, function(p) data.table(id = as.integer(x$id), task = as.integer(x$Choiceset), profile = p,
                                                     choice = as.integer(x$choice == p), row = seq_len(nrow(x)))))
  for (k in attrs[[g]]) {
    code <- c(x[[paste0(k, "_a")]], x[[paste0(k, "_b")]])
    txt <- dx[design == g & attr == k][d, on = c(set = "task", profile = "profile"), text]
    stopifnot(!anyNA(code), !anyNA(txt), data.table(code, txt)[, uniqueN(txt), code][, all(V1 == 1)],
              data.table(code, txt)[, uniqueN(code), txt][, all(V1 == 1)])
    d[, paste0("attr_", anm[[k]]) := txt]
  }
  d[, trial_group := fifelse(x$Designs[row] == 5, "all four designs", "one design")]
  d[, `:=`(cov_age = as.integer(x$Age[row]), cov_gender = tolower(x$Gender[row]), cov_education = na(x$Education[row]),
           cov_region = na(x$GORRegion[row]), cov_social_grade = na(x$SocialGradeUKClassification[row]),
           cov_occupation = na(x$Occupation[row]), cov_marital_status = na(x$MaritalStatus[row]), cov_guardian = na(x$Guardian[row]),
           cov_home_status = na(x$HomeStatus[row]), cov_tobacco_interest = na(x$TOBACCOInterestinTobaccoPr[row]),
           cov_smoking_history = na(x$TOBACCOSmokinghistoryandhab[row]))][, row := NULL]
  # fixed design: every respondent of this design saw the same sets
  stopifnot(d[, uniqueN(do.call(paste, .SD)), .(task, profile), .SDcols = patterns("^attr_")][, all(V1 == 1)],
            d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("stamuli_2020_fnp_outcomes_", tolower(g), ".csv")))
}
