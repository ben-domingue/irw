##Refugee-facility conjoint (Greece), citizens and municipal councilors, from
##Fabbe, K., Kyrkopoulou, E., & Vidali, M. E. (2025). Between human dignity and security:
##Identifying citizen and elite preferences and concerns over refugee reception. Comparative
##Political Studies. https://doi.org/10.1177/00104140251381741
##Replication data: Harvard Dataverse doi:10.7910/DVN/5CSZWG, CC0 1.0. Files read:
##citizens_level.dta (citizens, one row per respondent, raw Qualtrics conjoint columns) and
##councilors_full.dta (councilors, same layout). Read as text, not run: READme.pdf,
##citizens_profile.do, citizens_profile_without_outcome.R, step1_councilors.R,
##step2_councilors.do, citizens_level.do, Appendix_AandB.R. No questionnaire ships and the article
##could not be read: outcome wording is a PARAPHRASE.
##Usage: Rscript fabbe_2025.R <dir holding the two .dta files> <output dir>
##
##TWO TABLES, one per population, as the authors analyse them separately (different samples,
##different displayed text, different choice wording):
##  fabbe_2025_refugee_sites_citizens: 5,916 Greek adults (nationally representative online survey,
##    README), 3 tasks x 2 proposals for an asylum-seeker host site in the respondent's municipality.
##  fabbe_2025_refugee_sites_councilors: municipal councilors (README: 586 elites; the file holds 651
##    rows, 626 with conjoint answers -- all kept, count flagged).
##Attributes (5): Proximity, Size, Type, Run by, Public goods (councilors' Greek row names: Απόσταση
##Δομής από αστικό κέντρο, Μέγεθος Δομής, Είδος Δομής, Φορέας διαχείρισης Δομής, Αντισταθμιστικά
##οφέλη για το Δήμο σας; trailing carriage returns trimmed). Qualtrics layout: F<t><p><a> = level of
##attribute in row a, task t, profile p (1 = Proposal A, 2 = B); F<t><a> = name of the attribute in
##row a. Attribute row order was randomized ONCE per respondent (F1a = F2a = F3a for every
##respondent; stopifnot) and is stored as attrpos_* (1-5). task/profile RECORDED.
##Citizens' levels are stored in ENGLISH in the export (e.g. "Closed (exit allowed by permission of
##authorities only for a specified amount of time)") although the answer options are Greek; the
##councilors' export holds the Greek text (e.g. "Πλήρως Κλειστή"). Both stored as exported.
##Outcomes (per task):
##  rating: each proposal rated on a 0-7 scale (Q8_a_1/Q8_a_4, Q9_a_1/2, Q10_a_1/2, labelled
##    "cj-Scenario t/Proposal A|B- Likert"; anchors not deposited; the authors' do-files rescale it
##    as 0-7 (citizens) and as both 1-7 and 0-7 (councilors); stored raw).
##  choice (citizens): "Τον Υποψήφιο που στηρίζει την Πρόταση A/B" = the [mayoral] candidate who
##    supports Proposal A/B, i.e. which candidate the respondent would vote for (paraphrase).
##  choice (councilors): "Την Πρόταση A/B" = which proposal the councilor prefers (paraphrase).
##  Forced choice, no opt-out. NOTE: for councilors' task 3 the authors' step2_councilors.do
##  REPLACES the answered Q10_b by the higher-rated proposal; this table keeps the answered Q10_b.
##Tasks with no choice answer keep their ratings with choice NA; rows with no outcome are omitted;
##councilors with blank attribute cells have no outcomes and drop out.
##Covariates (answer text from the export; codes only where the export has none):
##  cov_gender (Γυναίκα -> female, Άντρας -> male, Άλλο -> other, "Δε γνωρίζω/ Δεν απαντώ" -> NA),
##  cov_birth_year (Q24), cov_education (Q26_edu, Greek text; blank -> NA), cov_party_id (Q17
##  "Which party do you think most closely represents your political beliefs now?", Greek text;
##  blank -> NA), cov_left_right (Q16_1, 0-10 as stored), cov_region (Q26_residence_1, NUTS2
##  periphery), cov_income (Q29_income, Greek text; citizens only),
##  cov_survey_weight (citizens only: the authors' entropy-balancing weight `webal`, used in their
##  "Weighted model"; the councilors' weight lives only in an .xlsx not read).
##Dropped (PII / free text): Qualtrics ResponseId (re-keyed 1..N), Q15_postcode (zip code),
##Q26_residence_2 / Q11_born_in_2 (municipality), Q28_job / job / profession, Q30 and Q_Feedback
##open text, and all derived indices and dummies.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
nm <- c("Proximity" = "proximity", "Size" = "size", "Type" = "type", "Run by" = "run_by", "Public goods" = "public_goods",
        "Απόσταση Δομής από αστικό κέντρο" = "proximity", "Μέγεθος Δομής" = "size", "Είδος Δομής" = "type",
        "Φορέας διαχείρισης Δομής" = "run_by", "Αντισταθμιστικά οφέλη για το Δήμο σας" = "public_goods")
blank <- function(v) { v <- trimws(as.character(v)); v[v == ""] <- NA; v }
build <- function(x, choice_pat) {
  x[, id := seq_len(.N)]
  stopifnot(x[, all(F11 == F21 & F21 == F31 & F12 == F22 & F13 == F23 & F14 == F24 & F15 == F25 & F22 == F32 & F23 == F33 & F24 == F34 & F25 == F35)])
  rt <- list(c("Q8_a_1", "Q8_a_4"), c("Q9_a_1", "Q9_a_2"), c("Q10_a_1", "Q10_a_2")); ch <- c("Q8_b", "Q9_b", "Q10_b")
  d <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
    y <- x[, .(id, task = t, profile = p, rating = as.integer(get(rt[[t]][p])), ans = blank(get(ch[t])))]
    for (k in 1:5) {
      an <- blank(x[[paste0("F", t, k)]]); lv <- blank(x[[paste0("F", t, p, k)]])
      y[, paste0("a", k) := an][, paste0("l", k) := lv]
    }
    y
  }))))
  last <- chartr("ΑΒ", "AB", substring(d$ans, nchar(d$ans)))
  d[, choice := fifelse(is.na(ans), NA_integer_, as.integer(last == c("A", "B")[profile]))]
  stopifnot(d[!is.na(ans), all(grepl(paste0(choice_pat, "[ABΑΒ]$"), ans))])
  d <- d[!(is.na(choice) & is.na(rating))]
  for (k in 1:5) d[, paste0("a", k) := nm[get(paste0("a", k))]]
  stopifnot(!anyNA(d[, paste0("l", 1:5), with = FALSE]), !anyNA(d[, paste0("a", 1:5), with = FALSE]))
  L <- melt(d[, c("id", "task", "profile", paste0("a", 1:5), paste0("l", 1:5)), with = FALSE],
            id.vars = c("id", "task", "profile"), measure.vars = list(paste0("a", 1:5), paste0("l", 1:5)), value.name = c("attr", "level"))
  L[, pos := as.integer(variable)]
  A <- dcast(L, id + task + profile ~ attr, value.var = "level"); P <- dcast(L, id + task + profile ~ attr, value.var = "pos")
  setnames(A, names(A)[-(1:3)], paste0("attr_", names(A)[-(1:3)])); setnames(P, names(P)[-(1:3)], paste0("attrpos_", names(P)[-(1:3)]))
  d <- merge(d[, .(id, task, profile, choice, rating)], A, by = c("id", "task", "profile"))
  d <- merge(d, P, by = c("id", "task", "profile"))
  stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)])
  d
}
cov <- function(x) {
  g <- blank(x$Q25_gender)
  x[, .(id, cov_gender = unname(c("Γυναίκα" = "female", "Άντρας" = "male", "Άλλο" = "other")[g]),
        cov_birth_year = as.integer(Q24), cov_education = blank(Q26_edu), cov_party_id = blank(Q17),
        cov_left_right = suppressWarnings(as.integer(as.character(Q16_1))), cov_region = blank(Q26_residence_1))]
}
x <- as.data.table(read_dta(file.path(raw, "citizens_level.dta")))
stopifnot(nrow(x) == 5916, uniqueN(x$ResponseId) == 5916)
d <- build(x, "Τον Υποψ[ήη]φιο που στηρίζει την Πρόταση ")
cv <- cov(x)[, `:=`(cov_income = blank(x$Q29_income), cov_survey_weight = as.numeric(x$webal))]
d <- merge(d, cv, by = "id"); setorder(d, id, task, profile)
cat("citizens rows", nrow(d), "resp", uniqueN(d$id), "tasks w/o choice", d[is.na(choice), uniqueN(paste(id, task))], "\n")
m <- lm(choice ~ attr_proximity + attr_size + attr_type + attr_run_by + attr_public_goods, d)
print(round(coef(m), 3))
fwrite(d, file.path(out, "fabbe_2025_refugee_sites_citizens.csv"))
y <- as.data.table(read_dta(file.path(raw, "councilors_full.dta")))
stopifnot(nrow(y) == 651, uniqueN(y$ResponseId) == 651)
y <- y[!is.na(blank(F111))]
e <- build(y, "Την Πρόταση ")
e <- merge(e, cov(y), by = "id"); setorder(e, id, task, profile)
cat("councilors rows", nrow(e), "resp", uniqueN(e$id), "tasks w/o choice", e[is.na(choice), uniqueN(paste(id, task))], "\n")
fwrite(e, file.path(out, "fabbe_2025_refugee_sites_councilors.csv"))
