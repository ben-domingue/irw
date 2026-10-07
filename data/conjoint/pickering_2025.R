##Two conjoint experiments (UK and Japan) from
##Pickering, S. (2025). Replication data for: Peacekeeping by any other name: A conjoint
##experiment evaluating support for peacekeeping, diplomatic and humanitarian missions in
##Japan and the UK [Data set]. Harvard Dataverse. https://doi.org/10.7910/DVN/XKSZCU
##No published article was found (Crossref, web search, 2026-10-07); the authors' earlier
##deposit of the same study is doi:10.7910/DVN/ZI4PBD (CC BY 4.0, Pickering; Stata code by
##Han Dorussen). Deposit used here: doi:10.7910/DVN/XKSZCU, CC BY 4.0, no restricted files.
##Files read: replication_data_jp.csv and replication_data_uk.csv (Dataverse "original
##format" downloads). Usage: Rscript pickering_2025.R <raw dir> <output dir>
##
##THE TWO FILE NAMES ARE SWAPPED IN THE DEPOSIT. replication_data_jp.csv (646 respondents,
##6 tasks, outcomes Q1-Q6 / Q*_effective_*) is the UK sample and replication_data_uk.csv
##(1,511 respondents, 4 tasks, outcomes exp*_1 / exp*_2a,b) is the Japan sample. Evidence:
##(a) the deposit's own replication_code.r builds its `uk` object with 6 tasks and Q1-Q6 and
##its `jp` object with 4 tasks and exp*; (b) the earlier deposit ZI4PBD has UK_wave20_final
##with 646 x 12 rows and Japan_wave20_final with 1,511 x 8 rows; (c) every respondent's set
##of 12 (resp. 8) attribute profiles in the "jp" (resp. "uk") file matches a respondent in
##ZI4PBD's UK (resp. Japan) file (100% match).
##
##Design: each task shows two missions (A = profile 1, B = profile 2) with 5 attributes, all
##levels fully randomized as far as the data show: mission (Peacekeeping / Diplomatic /
##Humanitarian), personnel type (Civilian only / Military only / Civilian and military),
##size (5 / 50 / 500 personnel), lead (UN / USA / NATO / China), location (Sub-Saharan Africa
##/ South America / Central Asia / Middle East). Task and profile come from the wide column
##names (src_<task>_attribute<k>_<profile>), not from row order.
##LEVEL TEXT: no questionnaire is deposited. Level labels are the authors' English labels,
##taken from the string columns of ZI4PBD ("Civilian only", "Military only", "USA",
##"Sub-saharan" written out as "Sub-Saharan Africa"); XKSZCU's replication_code.r uses the
##shorter "Civilian", "Military", "US" for the same codes. Japanese respondents saw Japanese
##text, which is not available.
##Outcomes (exact question wording not deposited):
##  choice = which mission the respondent preferred (A or B), forced choice, no opt-out.
##           UK: 7 task answers coded 8 (non-substantive) -> choice NA on both profiles.
##           Japan: 237 tasks unanswered -> NA.
##  rating = perceived effectiveness of each mission, 1 = Not at all effective, 2 = Not very
##           effective, 3 = Somewhat effective, 4 = Effective, 5 = Extremely effective
##           (labels from replication_code.r). UK code 8 (non-substantive) -> NA.
##Rows with neither outcome are omitted. Respondent IDs are already sequential integers.
##No covariates or weights are in XKSZCU (ZI4PBD has them, including postcode district and
##constituency, which would need stripping; not merged here).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv <- list(mission = c("Peacekeeping", "Diplomatic", "Humanitarian"),
           personnel = c("Civilian only", "Military only", "Civilian and military"),
           size = c("5", "50", "500"),
           lead = c("UN", "USA", "NATO", "China"),
           location = c("Sub-Saharan Africa", "South America", "Central Asia", "Middle East"))
build <- function(w, nt, chv, rtv) {
  d <- rbindlist(lapply(1:nt, function(t) rbindlist(lapply(1:2, function(p) {
    x <- data.table(id = as.integer(w$ID), task = t, profile = p)
    ch <- as.integer(w[[chv(t)]]); ch[!ch %in% 1:2] <- NA
    x[, choice := as.integer(ch == p)]
    r <- as.integer(w[[rtv(t, p)]]); r[!r %in% 1:5] <- NA
    x[, rating := r]
    for (k in 1:5) x[, paste0("attr_", names(lv)[k]) := lv[[k]][w[[sprintf("src_%d_attribute%d_%d", t, k, p)]]]]
    x
  }))))
  d <- d[!(is.na(choice) & is.na(rating))]
  stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile); d
}
uk <- fread(file.path(raw, "replication_data_jp.csv"))   # sic: this file is the UK sample
jp <- fread(file.path(raw, "replication_data_uk.csv"))   # sic: this file is the Japan sample
stopifnot(nrow(uk) == 646, "Q6" %in% names(uk), nrow(jp) == 1511, "exp4_1" %in% names(jp))
fwrite(build(uk, 6, function(t) paste0("Q", t), function(t, p) sprintf("Q%d_effective_%d", t, p)),
       file.path(out, "pickering_2025_peacekeeping_uk.csv"))
fwrite(build(jp, 4, function(t) sprintf("exp%d_1", t), function(t, p) sprintf("exp%d_2%s", t, c("a", "b")[p])),
       file.path(out, "pickering_2025_peacekeeping_japan.csv"))
