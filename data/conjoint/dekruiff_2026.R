##Forest landscape change in Slovakia and Poland: choice experiments from the Zenodo deposit "Data (code and survey responses)
##for paper Value pluralism and the economic valuation of landscape change: Evidence on the suitability of stated preference
##methods" (De Kruiff, 2026). No article DOI in the deposit (doi = "").
##Deposit: doi:10.5281/zenodo.20538567 (concept doi 10.5281/zenodo.20538566), CC BY 4.0 (record licence cc-by-4.0).
##Files read: database_SK.csv, database_PL.csv, and the Apollo scripts "Hybrid LC - Slovakia.r" / "Hybrid LC - Poland.r" (read as
##text, never run) for the level coding. NOT built: database_NL.csv (Netherlands river-landscape experiment, a different
##attribute set; HELD because its two status-quo alternatives show attribute levels that are only partly stored); the
##attitudes_*.csv and posterior_*.csv files (latent-class output).
##Usage: Rscript dekruiff_2026.R <dir holding database_SK.csv and database_PL.csv> <output dir>
##
##Two tables, one per country: the authors estimate separate country models and the level sets differ (forest management share
##0/20/40/70% in Slovakia vs 0/20/40/50% in Poland; fee scales 10-100 vs 50-500), so the level text is not shared.
##  dekruiff_2026_forests_slovakia: 846 respondents x 8 choice sets;  dekruiff_2026_forests_poland: 933 respondents x 8 sets.
##Design: each choice set has two forest-landscape alternatives (alt1, alt2 = profile 1, 2) with four attributes, plus a third
##alternative (choice = 3, the status quo / "neither": the authors' model gives it only a constant, with no attribute
##values stored, and it was never given attribute levels in the data) = opt-out, no profile row. Exactly one of the three
##is chosen per set. Choice counts: SK 1725 / 2092 / 2951 (alt1 / alt2 / status quo of 6,768); PL 1881 / 2103 / 3480 (of 7,464).
##Attributes (names and codes from the files and the Apollo script; the deposit has no codebook and the article was not found):
##  forestmanagement: share 0 / 0.2 / 0.4 / 0.7 (SK) or 0 / 0.2 / 0.4 / 0.5 (PL), stored as "0%", "20%", ... ; what the share
##    refers to is not stated in the deposit (script: b_forestmanagement_0/20/40/70).
##  access: 0 = "Current access", 1 = "Closed for 5 years", 2 = "Closed for 10 years", 3 = "Closed permanently"
##    (script parameter names b_access_current, _closed5years, _closed10years, _closedpermanently).
##  tours: 0 = "Current tours", 1 = "Free tours" (b_tours_current, b_tours_free).
##  fee: number as stored (SK 10-100, PL 50-500); currency and period not stated.
##LABELS: partial -- the level wording is built from the authors' script parameter names, not from the questionnaire; the
##forest management share's meaning and the fee currency are unknown. Flagged for Ben.
##Task = choice_set 1-8 (the design's set index; presentation order not documented). Restrictions/level probabilities: not
##stated (the level shares are near equal). Attribute order: unknown.
##Covariates: cov_gender_code (female: 1 = female, 0 = otherwise per the variable name; no codebook), cov_age (respAge, years),
##cov_higher_education (highereduc 0/1, definition not documented), cov_urban (urban 0/1, definition not documented).
##Dropped: the 11 Likert value-indicator items (vpn*, 7-point), used only for the authors' latent-variable model.
##No survey weight. No identifying columns (respID is a counter).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lev_access <- c("Current access", "Closed for 5 years", "Closed for 10 years", "Closed permanently")
lev_tours <- c("Current tours", "Free tours")
build <- function(file, nresp, fm_levels) {
  d <- fread(file.path(raw, file))
  stopifnot(nrow(d) == nresp * 8, uniqueN(d$respID) == nresp, d[, .N, respID][, all(N == 8)], all(d$choice %in% 1:3),
            d[, all(choice_set == 1:8), respID][, all(V1)])
  d[, id := match(respID, unique(respID))]
  mk <- function(k) {
    p <- function(v) d[[paste0("alt", k, ".", v)]]
    fm <- p("forestmanagement")
    stopifnot(all(fm %in% fm_levels), all(p("access") %in% 0:3), all(p("tours") %in% 0:1), !anyNA(p("fee")))
    data.table(id = d$id, task = as.integer(d$choice_set), profile = k, choice = as.integer(d$choice == k),
      attr_forest_management_share = paste0(round(fm * 100), "%"), attr_access = lev_access[p("access") + 1L],
      attr_tours = lev_tours[p("tours") + 1L], attr_fee = as.character(p("fee")),
      cov_gender_code = as.integer(d$female), cov_age = as.integer(d$respAge), cov_higher_education = as.integer(d$highereduc),
      cov_urban = as.integer(d$urban))
  }
  o <- rbind(mk(1L), mk(2L))
  setorder(o, id, task, profile)
  stopifnot(o[, sum(choice), .(id, task)][, all(V1 <= 1)], !anyNA(o[, .SD, .SDcols = patterns("^attr_")]))
  o
}
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(build("database_SK.csv", 846, c(0, 0.2, 0.4, 0.7)), file.path(out, "dekruiff_2026_forests_slovakia.csv"))
fwrite(build("database_PL.csv", 933, c(0, 0.2, 0.4, 0.5)), file.path(out, "dekruiff_2026_forests_poland.csv"))
