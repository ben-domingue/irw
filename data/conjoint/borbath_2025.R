##Party-brand conjoints (Austria, Hungary, Italy): a new party's name/organization/action form, and a rebranding of the
##respondent's own party, from
##Borbath, E., & Hutter, S. (2025). Brand transformation in European politics: The rise and limits of nonclassical names.
##Perspectives on Politics. https://doi.org/10.1017/S1537592725103319
##Replication data: Harvard Dataverse doi:10.7910/DVN/WGATQF, CC0 1.0. Files read: AU_survey.Rdata, HU_IT_survey.Rdata
##(DE_survey.Rdata inspected, see below), README.md and step8_experiment_analysis.Rmd (as text). Value labels are haven labels
##inside the .Rdata (loaded into new environments). Usage: Rscript borbath_2025.R <dir with the .Rdata files> <output dir>
##
##Online surveys fielded Feb 2023 (Austria, n = 2,110), Jul-Aug 2023 (Italy 2,129 and Hungary 2,160; 4,289 together, matching
##the 4,289 respondents of HU_IT_survey.Rdata) and Dec 2023 (Germany, n = 2,936). Each respondent rated and compared
##described political groups (Study 2 of the article): THREE tasks of TWO profiles (A and B) in each of two experiments:
##  1. new-party branding (CJ1): name {"New [country]", "Party for a new [country]", "Movement for a new [country]"} x
##     organization {No organization, Strong leader, Close links to CSOs} x action form {No action form, Parliament,
##     Demonstrations};
##  2. rebranding (CJ2): what the respondent's OWN party does: name change {No name change, Takes-up party, Deletes party,
##     Takes-up movement, Deletes movement} x organization (same 3 levels) x action form (same 3 levels).
##Level text is the authors' English labels (value labels in the Rdata; the pooled analysis in step8 recodes the country-specific
##names to the "[country]" placeholders, as used here). Respondents saw the local language (German/Hungarian/Italian;
##the questionnaire is not in the deposit).
##Outcomes (from the article text, not the deposit): rating = "How much do you support the described group/scenario A/B?"
##(0-10 in the article; the file stores 1-11, which looks like a +1 shift; kept raw, higher = more support), and choice (file
##column CJxTradeOff) = "Which of the two organizations/scenarios would you be more likely to vote for?" Forced choice, no opt-out.
##Both outcomes in one table per experiment (same tasks).
##Structure. The file is long: six rows per respondent. In the Austrian and Hungarian/Italian files the rows of a respondent are
##contiguous and each consecutive pair (1,2), (3,4), (5,6) has exactly one chosen profile in BOTH experiments (checked below, 100%),
##so task = (row+1)%/%2 and profile = 1/2 by row order are INFERRED (task_source/profile_source = inferred). In the German file
##the rows are not in task order: no pairing of the six rows gives one choice per pair more often than chance (59-62%, chance 60%
##given three choices among six), so tasks cannot be rebuilt; GERMANY IS HELD (2,936 respondents) and not in the tables.
##Respondents with no party to rebrand (party_in_CJ2 missing: 42 in Austria, 458 in Italy/Hungary) have no CJ2 outcome and are
##omitted from the rebranding table only.
##Covariates: cov_country (AT/HU/IT, ISO; Italy vs Hungary from the CJ1 name labels, which agree with the pid_IT/pid_HU
##columns), cov_party_id (pid / pid_IT / pid_HU label text; "Other" and "None" kept as text), cov_left_right (lrscale 0-10,
##0 = Left, 10 = Right). The rebranded party is trial_party_rebranded (party_in_CJ2 label text, constant per respondent).
##Dropped: ID (rewritten to an integer; it is a panel number, not a platform ID), membership/populism/trust scales, imp_issue,
##the authors' derived factors. No survey weight in the deposit.
##Randomization restrictions. New-party table: none documented, all three attributes have near-equal level shares. Rebranding
##table: the name-change levels are CONDITIONAL on the party's current name (restrictions = observed): a party whose name has
##neither "party" nor "movement" in it (e.g. Gruene, NEOS, Forza Italia) gets {No name change, Takes-up movement, Takes-up
##party}; a party named a "party" (SPOe, OEVP, FPOe, BIER, LMP, MKKP, MSZP) gets {Deletes party, No name change, Takes-up
##movement}; a "movement" (Mi Hazanak, Momentum) gets {Deletes movement, No name change, Takes-up party}. Each allowed level
##is about 1/3, so within a party the draws are uniform; organization and action form are independent of it.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ld <- function(f) { e <- new.env(); load(file.path(raw, f), envir = e); as.data.table(e[[ls(e)[1]]]) }
txt <- function(x) as.character(as_factor(x))
au <- ld("AU_survey.Rdata"); hi <- ld("HU_IT_survey.Rdata")
std <- function(d, cty, pidcol, partycol) {
  d <- copy(d); d[, k := seq_len(.N), by = ID]
  stopifnot(d[, .N, ID][, all(N == 6)])
  ## rows of a respondent must be contiguous and pairs complementary
  stopifnot(!anyNA(d$CJ1TradeOff), d[, sum(CJ1TradeOff), .(ID, g = (k + 1L) %/% 2L)][, all(V1 == 1)])
  ok <- d[!is.na(CJ2TradeOff), sum(CJ2TradeOff), .(ID, g = (k + 1L) %/% 2L)]
  stopifnot(ok[, all(V1 == 1)])
  data.table(src = d$ID, task = (d$k + 1L) %/% 2L, profile = 2L - d$k %% 2L,
             cj1_name = txt(d$CJ1Name), cj1_org = txt(d$CJ1Organization), cj1_form = txt(d$CJ1Form),
             cj1_scale = as.integer(d$CJ1Scale), cj1_choice = as.integer(d$CJ1TradeOff),
             cj2_name = txt(d$CJ2Name), cj2_org = txt(d$CJ2Organization), cj2_form = txt(d$CJ2Form),
             cj2_scale = as.integer(d$CJ2Scale), cj2_choice = as.integer(d$CJ2TradeOff),
             party = txt(d[[partycol]]), pid = txt(d[[pidcol]]), lr = as.integer(d$lrscale), cty = cty)
}
hi_it <- hi[grepl("Italy|Italt", txt(CJ1Name))]; hi_hu <- hi[grepl("Hungary", txt(CJ1Name))]
stopifnot(nrow(hi_it) + nrow(hi_hu) == nrow(hi), nrow(hi_it) == 2129 * 6, nrow(hi_hu) == 2160 * 6)
hi_it[, party_in_CJ2 := party_in_CJ2_IT]; hi_hu[, party_in_CJ2 := party_in_CJ2_HU]
hi_it[, pid := pid_IT]; hi_hu[, pid := pid_HU]
x <- rbindlist(list(std(au, "AT", "pid", "party_in_CJ2"), std(hi_it, "IT", "pid", "party_in_CJ2"), std(hi_hu, "HU", "pid", "party_in_CJ2")))
x[, src := paste(cty, src)]
x[, id := match(src, unique(src))]
x[, pid := fifelse(is.na(pid) | pid == "", NA_character_, pid)]
nm <- function(s) fifelse(grepl("^Party for", s), "Party for a new [country]", fifelse(grepl("^Movement for", s), "Movement for a new [country]", fifelse(grepl("^New ", s), "New [country]", NA_character_)))
build <- function(cj) {
  y <- copy(x)
  if (cj == 1) { y[, `:=`(attr_name = nm(cj1_name), attr_organization = cj1_org, attr_action_form = cj1_form, rating = cj1_scale, choice = cj1_choice)]
  } else { y[, `:=`(attr_name_change = cj2_name, attr_organization = cj2_org, attr_action_form = cj2_form, rating = cj2_scale, choice = cj2_choice)]
           y <- y[!is.na(choice)] }
  y[, `:=`(cov_country = cty, cov_party_id = pid, cov_left_right = lr)]
  if (cj == 2) y[, trial_party_rebranded := party]
  keep <- c("id", "task", "profile", "choice", "rating", grep("^attr_", names(y), value = TRUE), grep("^cov_", names(y), value = TRUE), grep("^trial_", names(y), value = TRUE))
  y <- y[, ..keep]
  y[, id := match(id, unique(id))]
  setorder(y, id, task, profile)
  y
}
t1 <- build(1); t2 <- build(2)
for (t in list(t1, t2)) { ac <- grep("^attr_", names(t), value = TRUE); stopifnot(!anyNA(t[, ..ac]), t[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(t$rating)) }
stopifnot(t1[, uniqueN(id)] == 2110 + 4289, t1[, uniqueN(attr_name)] == 3)
stopifnot(sum(t2$cov_country == "AT") == (2110 - 42) * 6)
fwrite(t1, file.path(out, "borbath_2025_new_party_brand.csv"))
fwrite(t2, file.path(out, "borbath_2025_party_rebranding.csv"))
