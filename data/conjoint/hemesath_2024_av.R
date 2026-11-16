##Autonomous-vehicle risk-regulation paired conjoint (Germany, Japan, US, 2020), from
##Hemesath, S., & Tepe, M. (2024). Multidimensional preference for technology risk regulation: The
##role of political beliefs, technology attitudes, and national innovation cultures. Regulation &
##Governance. https://doi.org/10.1111/rego.12578 (Wiley OA; not readable here: 403)
##Replication data: Harvard Dataverse doi:10.7910/DVN/VB1DKA, CC0 1.0. Files read:
##Hemesath_Tepe_RegGov_2024_Replication_AVConjoint.RDS; the authors' .R read as text, not run
##(attribute names, reference levels, English plot labels, analysis subsets).
##Usage: Rscript hemesath_2024_av.R <dir holding the .RDS> <output dir>
##
##3,464 respondents (sample DE 1,169, JP 1,126, US 1,169), Qualtrics panels, 6 tasks x 2 regulation
##packages (profile left = 1, right = 2), 6 attributes; 41,568 rows, exactly one selected per task
##(checked; agrees with the raw task<t> answer columns). One table with cov_country: the authors pool
##the three samples (pooled AMCEs/MMs, sample interactions) and the attribute codes are shared.
##Outcome choice = selected: which of two regulation packages the respondent prefers (forced choice;
##question wording not seen). Paper N not checked (article unreachable).
##CODED ATTRIBUTES (#3474). The deposit stores each level as the authors' short factor label, and
##respondents saw German, Japanese or English text that is in the article only (unreachable here).
##The short labels are kept as deposited in attr_<name>_code; the authors' own English plot labels
##(.R `lvl`) are given here for orientation only, not as displayed text:
##  attr_safety_standards_code  identical / stricter / much more strict  (vs. current standards)
##  attr_safety_approval_code   Self / Public / Independent  (self-regulation, public authority,
##                              independent body)
##  attr_moral_code             occupant / driver decides / others  (ethical prioritization: protect
##                              occupants, choice of driver, protect others)
##  attr_legal_code             Owner / Manufacturer  (liability for accidents)
##  attr_data_code              Driver / Pub. / Company  (access to telemetry data: only driver, public
##                              authorities, companies)
##  attr_supervision_code       none / warning / constant  (human supervision of autopilot)
##Randomization restrictions and attribute order: not documented in the deposit.
##The authors' subgroup analyses drop respondents with missing ideology (ecoLR/culLR bins) or restrict
##to party voters; no exclusion is applied here.
##Covariates (as deposited): cov_gender (Male = male, Female = female, Non-Binary = other), cov_age
##(years), cov_age_group, cov_education (country-specific answer text, mixed German/English labels
##as stored; latin1 bytes re-encoded to UTF-8), cov_vote (party vote intention text), cov_eco_lr / cov_cul_lr (1-10 economic / cultural
##left-right as stored), cov_climate_eco, cov_polsys_satisfaction (polsyssat), cov_democracy_rating
##(howdem), cov_income_code (country-specific bands, no labels), cov_social_class, cov_employment,
##cov_neighbourhood, cov_licence (driving licence), cov_tech1..9 and cov_adm_* (1-5 technology and
##automated-decision attitude items as stored; the .R reverses tech2/3/5, ADMpreferhuman and
##ADMuneasy for its index - not done here), cov_duration_sec (Qualtrics survey duration).
##PII dropped: Qualtrics ResponseId (re-keyed 1..n) and meta_LocationLatitude/Longitude (populated);
##also dropped: other meta_* paradata, region, and undocumented item batteries (disc*, grd*, grp*).
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(readRDS(file.path(raw, "Hemesath_Tepe_RegGov_2024_Replication_AVConjoint.RDS")))
# some strings (e.g. "Universit\xe4t") are latin1 bytes without a declared encoding: re-encode to UTF-8
for (v in names(k)) if (is.character(k[[v]])) { x <- k[[v]]; bad <- !is.na(x) & !validUTF8(x); if (any(bad)) { x[bad] <- iconv(x[bad], "latin1", "UTF-8"); set(k, j = v, value = x) } }
stopifnot(nrow(k) == 41568L, uniqueN(k$ResponseId) == 3464L, all(k$profile %in% c("left", "right")))
d <- data.table(id = match(k$ResponseId, unique(k$ResponseId)), task = as.integer(k$task),
                profile = fifelse(k$profile == "left", 1L, 2L), choice = as.integer(k$selected))
stopifnot(d[, .N, .(id, task)][, all(N == 2L)], d[, sum(choice), .(id, task)][, all(V1 == 1L)])
src <- c(safety_standards = "Safety.Standards", safety_approval = "Safety.Approval", moral = "Moral",
         legal = "Legal", data = "Data", supervision = "Supervision")
for (v in names(src)) { x <- as.character(k[[src[[v]]]]); stopifnot(!anyNA(x)); d[, paste0("attr_", v, "_code") := x] }
d[, cov_country := k$sample]
stopifnot(all(k$gender %in% c("Male", "Female", "Non-Binary")))
d[, cov_gender := c(Male = "male", Female = "female", `Non-Binary` = "other")[k$gender]]
num <- function(x) suppressWarnings(as.numeric(x))
d[, cov_age := as.integer(num(k$age))]
d[, cov_age_group := k$agegrp]
d[, cov_education := k$education]
d[, cov_vote := k$vote]
d[, cov_eco_lr := num(k$ecoLR)]
d[, cov_cul_lr := num(k$culLR)]
d[, cov_climate_eco := num(k$climateeco)]
d[, cov_polsys_satisfaction := num(k$polsyssat)]
d[, cov_democracy_rating := num(k$howdem)]
d[, cov_income_code := num(k$income)]
d[, cov_social_class := k$socclass]
d[, cov_employment := k$employment]
d[, cov_neighbourhood := k$neigh]
d[, cov_licence := k$license]
for (j in 1:9) d[, paste0("cov_tech", j) := num(k[[paste0("tech", j)]])]
for (v in c("ADMmakeeasy", "ADMpreferhuman", "ADMuneasy", "ADMlessdiscr"))
  d[, paste0("cov_adm_", tolower(sub("^ADM", "", v))) := num(k[[v]])]
d[, cov_duration_sec := num(k[["meta_Duration (in seconds)"]])]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hemesath_2024_av_regulation.csv"))
