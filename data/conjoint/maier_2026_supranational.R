##Supranational governance paired conjoint (Germany and Poland) from the figshare deposit
##Maier, F. (2026). Supranational governance preferences [Data set]. figshare,
##doi:10.6084/m9.figshare.32252061, CC BY 4.0. No article or codebook is linked.
##Files read: con_de.csv (77 MB), con_po.csv (71 MB), read with fread(select = ...) only; the
##survey files de_final.csv / po_final.csv are the same respondents' wide data and are not used.
##Usage: Rscript maier_2026_supranational.R <dir holding con_de.csv and con_po.csv> <output dir>
##Writes two tables (separate samples: attribute text is in German and in Polish and the deposit
##gives no shared coding, so one table per sample, not pooled):
##  maier_2026_supranational_de: 1,027 German respondents, display and labels German.
##  maier_2026_supranational_pl: 1,051 Polish respondents, display and labels Polish.
##Both: 6 tasks x 2 profiles (A, B -> profile 1, 2), 4 attributes, same design. Task and profile
##columns are recorded; the deposit's `choice` (1/2) names the chosen profile and `chosen` (0/1)
##flags it; they agree on every row and exactly one profile is chosen in each task (verified).
##Forced choice, no opt-out. Each profile also has `rating`, an integer 1-7, kept raw in
##`rating`. The QUESTION WORDING and the rating anchors are NOT in the deposit (design_outcomes:
##unknown); the direction of the rating is not documented (a higher rating presumably means
##more favourable, not verified).
##Attributes (text as stored): feature1 = the legislature (a world parliament / the European
##Parliament), feature2 = further actors involved (experts, civil-society organisations, business,
##citizens, no further actors), feature3 = role of nation states (their agreement not necessary /
##the majority must agree / all must agree), feature4 = financing (equal contribution by all
##citizens / richer citizens pay more / citizens in richer countries pay more). Names are my
##descriptive labels for feature1-4; the deposit does not name them. Attribute order and
##restrictions are not documented; level shares are near-equal.
##Covariates: no codebook, so codes are kept with a _code suffix: cov_gender_code (1-4),
##cov_income_code, cov_education_code; cov_birth_year (the deposit's `year`, range 1958-2005 in
##Germany, 1960-2005 in Poland, consistent with birth year; not verified).
##cov_education_code is NA for 60 (DE) and 48 (PL) rows (missing in source).
##Dropped (PII FOUND): IPAddress, LocationLatitude, LocationLongitude, RecipientLastName, RecipientFirstName, RecipientEmail,
##ExternalReference, ResponseId (re-keyed), all dates, timing and survey items. `timing` (seconds
##on the task) is also dropped.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cols <- c("ResponseId", "task", "profile", "feature1", "feature2", "feature3", "feature4", "rating", "choice", "chosen", "gender", "year", "income", "education")
one <- function(f, nm, nexp) {
  s <- fread(file.path(raw, f), select = cols)
  stopifnot(uniqueN(s$ResponseId) == nexp, s[, .N, ResponseId][, all(N == 12)], s[, all(profile %in% c("A", "B"))])
  s[, id := as.integer(factor(ResponseId, levels = unique(ResponseId)))]
  s[, profile_n := match(profile, c("A", "B"))]
  stopifnot(s[, all((profile_n == choice) == (chosen == 1))], s[, sum(chosen), .(id, task)][, all(V1 == 1)],
            s[, all(rating %in% 1:7)], !anyNA(s[, !"education"]))
  d <- s[, .(id, task = as.integer(task), profile = as.integer(profile_n), choice = as.integer(chosen), rating = as.integer(rating),
    attr_legislature = feature1, attr_other_actors = feature2, attr_nation_state_role = feature3, attr_financing = feature4,
    cov_gender_code = as.integer(gender), cov_birth_year = as.integer(year), cov_income_code = as.integer(income),
    cov_education_code = as.integer(education))]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(nm, ".csv")))
}
one("con_de.csv", "maier_2026_supranational_de", 1027)
one("con_po.csv", "maier_2026_supranational_pl", 1051)
