##Multilateral climate-policy conjoint (cost-path version) from
##Bechtel, M. M., Scheve, K. F., & van Lieshout, E. (2022). Improving public support for climate
##action through multilateralism. Nature Communications, 13, 6441.
##https://doi.org/10.1038/s41467-022-33830-8
##Replication data: Harvard Dataverse doi:10.7910/DVN/GCNO77, CC0 1.0, no restricted files, no terms.
##File read: pooled_touse.tab, in its Stata "original format" download (saved as pooled.dta; 10,081
##respondent rows x 1,453 columns, value labels kept). Not read: pooled_scenlevel_touse.dta (768 MB,
##the authors' scenario-level reshape, derived), the multilateralism vignette experiment (a separate
##experiment in the same deposit: treatment arms multilateral/unilateral x effectiveness information,
##not profiles; not built), the US-only "cost timing" conjoint (CPCT_*; no instructions, no question
##wording and no description of its Year attribute in the deposit or the paper; not built).
##Level text and wording: the paper (Europe PMC full text, PMC9616826) and Supplementary Fig. 5
##(Supplementary Information PDF: the conjoint instructions and an example profile pair, shown for
##the US). The authors' conjoint.do was read as text only (it needs the scenario-level file).
##Usage: Rscript bechtel_2022.R <raw dir> <output dir>   (raw dir holds pooled.dta)
##
##Sample: YouGov online panels (matched sampling) in the US (December 18 2018 - January 3 2019;
##4,075 respondents) and France, Germany, the UK (March 31 - April 4 2019; 2,000 each). The US
##sample was split between this cost-path conjoint (CPC_treatment = "Climate Policy Cost Path
##Conjoint", 2,075 respondents) and the cost-timing conjoint (2,000); all 6,000 European respondents
##saw the cost-path conjoint. 8,075 respondents in all, 8 tasks each. The authors pool the four countries in the main analysis (Fig. 3, N = 129,280
##task-profile rows reported = 8,080 respondents x 16; Supplementary Fig. 6 gives US N = 33,280 =
##2,080 x 16, so the paper counts 5 more US respondents than the 2,075 in the deposit; flagged,
##not fixed) and show country panels as a robustness check, so this is ONE table with cov_country.
##The instruction text is shared across countries; display languages were English (US, UK), French
##and German (translations not in the deposit), so labels are English.
##Design (Supplementary Fig. 5): each task shows two multilateral climate-policy scenarios (Scenario 1
##= profile 1, Scenario 2 = profile 2). Each scenario has two blocks of the same four attributes,
##"In the <own country>" and "In other major economies":
##  attr_*_cost       "Average household costs per month": one of four levels, in the respondent's
##                    currency (approx. 0.5, 1, 2, 2.5 percent of GDP): France 28/56/113/141 euros,
##                    Germany 39/77/154/193 euros, UK 15/30/60/75 pounds, US 53/107/213/267 dollars.
##                    The deposit stores the multi-currency label "Cost k: EUR/EUR/GBP/USD"; the
##                    amount for the respondent's country is stored here with its currency symbol
##                    (the order France, Germany, UK, US is confirmed by the paper's text: "low EUR 28
##                    in France, EUR 39 in Germany, GBP 15 in the UK and $53 in the US").
##                    Other economies' costs are shown in the respondent's own currency (Fig. 5).
##  attr_*_cost_path  "Distribution of costs over time": gradually increasing / constant over time /
##                    gradually decreasing
##  attr_*_adaptation "Adaptation (new technology, building dams, ...)": share of investment, 0-100%
##  attr_*_mitigation "Mitigation (reducing greenhouse gas emissions, removing greenhouse gases from the
##                    atmosphere)": 100 minus the adaptation share (checked: all 129,200 blocks sum to
##                    100), so the two are one randomized quantity shown twice.
##  with * = own (CPCP_Txx_B1_*, "IN COUNTRY") or other (B2, "OTHER COUNTRY").
##The experiment randomized whether the own-country or the other-economies block was listed first, once
##per respondent (trial_block_order = CPC_Country_Order, same for all tasks), and the on-screen order of
##the four attributes once per respondent (attrpos_*: CPCP_Distribution_Order, _Cost_Order, _Adapt_Order,
##_Mitigate_Order, 1 = listed first; the same position for the own and the other block; only 12 of the 24
##possible orders occur). "All attribute levels were fully and separately randomized" (Suppl. Fig. 5).
##Outcomes:
##  choice = "Which of these scenarios do you prefer?" (CPCP_Txx; Scenario 1 or 2). The instructions say
##           "You may like several alternatives similarly or may not like either of them at all.
##           Regardless of your overall evaluation, please indicate which alternative you prefer": forced
##           choice, no neither option, so opt-out no.
##  rating_effectiveness = CPCP_Txx_S1 / _S2, variable label "Scenario k Effectiveness": expected
##           effectiveness of the scenario, 1 "Not effective at all" ... 10 (top label not in the
##           deposit); "Don't know" (code 97) -> NA. Asked of US respondents only (all European
##           ratings are empty; 27,063 of the 33,200 US rows are rated, the rest are "Don't know" or
##           not asked). The question wording is not in the deposit (paraphrase).
##Weights: cov_survey_weight = mbweight (the authors' pooled weight used in conjoint.do, [pweight=mbweight]);
##NA for 70 respondents (6 US, 64 UK), kept with NA weight. Covariates: cov_country (country), cov_gender
##(DEMO_gender Male/Female/Other), cov_birth_year (DEMO_AGE, labelled "Birth Year"). Dropped: dates,
##timing, DEMO_inputzip (US ZIP code; PII), DEMO_inputstate, free text (DEMO_comments, reasons),
##the other experiments' variables, and all derived dummies/scales. Education/party questions are
##US-only or harmonised without a codebook, so not kept. Respondent id: caseid re-keyed to integers.
##Spot check: linear probability of choice on own cost level reproduces the paper (Fig. 3 text): medium own
##cost -6.3 pp (weighted; -6.0 unweighted), high -16.8 pp (-17.0), very high -23.6 pp (-23.0).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cols <- c("caseid", "country", "CPC_treatment", "CPC_Country_Order", "DEMO_gender", "DEMO_AGE", "mbweight",
          "CPCP_Distribution_Order", "CPCP_Cost_Order", "CPCP_Adapt_Order", "CPCP_Mitigate_Order")
tv <- c(sprintf("CPCP_T%02d", 1:8), unlist(lapply(1:8, function(t) unlist(lapply(c("B1", "B2"), function(b) unlist(lapply(c("S1", "S2"),
        function(s) sprintf("CPCP_T%02d_%s_%s_%s", t, b, s, c("Distribution", "Cost", "Adapt", "Mitigate")))))))),
        unlist(lapply(1:8, function(t) sprintf("CPCP_T%02d_S%d", t, 1:2))))
d <- as.data.table(read_dta(file.path(raw, "pooled.dta"), col_select = all_of(c(cols, tv))))
chr <- function(v) as.character(as_factor(d[[v]]))
d <- d[chr("CPCP_T01") != "not asked"]
stopifnot(nrow(d) == 8075, !anyDuplicated(d$caseid))
d[, id := .I]
ctry <- chr("country"); stopifnot(all(ctry %in% c("France", "Germany", "United Kingdom", "United States")))
cost <- list(France = list(sym = "€", v = c(28, 56, 113, 141)), Germany = list(sym = "€", v = c(39, 77, 154, 193)),
             `United Kingdom` = list(sym = "£", v = c(15, 30, 60, 75)), `United States` = list(sym = "$", v = c(53, 107, 213, 267)))
## check the deposit's own label "Cost k:<amounts in order FR/DE/UK/US>" against the paper's amounts
lab <- chr("CPCP_T01_B1_S1_Cost")
for (k in 1:4) {
  l <- unique(lab[grepl(paste0("^Cost ", k), lab, useBytes = TRUE)]); stopifnot(length(l) == 1)
  l <- iconv(l, "latin1", "ASCII", sub = "")   # the euro/pound signs are mis-encoded in the label
  amt <- as.numeric(gsub("[^0-9]", "", strsplit(sub("^[^:]*:", "", l), "/", fixed = TRUE)[[1]]))
  stopifnot(identical(amt, c(cost$France$v[k], cost$Germany$v[k], cost$`United Kingdom`$v[k], cost$`United States`$v[k])))
}
costtxt <- function(lbl, ctry) {
  k <- as.integer(sub("^Cost ([0-9]).*", "\\1", lbl, useBytes = TRUE)); stopifnot(!anyNA(k))
  mapply(function(k, c) paste0(cost[[c]]$sym, cost[[c]]$v[k]), k, ctry)
}
pos <- function(v) as.integer(as.character(as_factor(d[[v]])))
ordr <- data.table(attrpos_cost = pos("CPCP_Cost_Order"), attrpos_cost_path = pos("CPCP_Distribution_Order"),
                   attrpos_adaptation = pos("CPCP_Adapt_Order"), attrpos_mitigation = pos("CPCP_Mitigate_Order"))
stopifnot(!anyNA(ordr), all(apply(ordr, 1, function(x) setequal(x, 1:4))))
blk <- c(own = "B1", other = "B2")
res <- rbindlist(lapply(1:8, function(t) rbindlist(lapply(1:2, function(s) {
  x <- data.table(id = d$id, task = t, profile = s)
  ch <- chr(sprintf("CPCP_T%02d", t)); stopifnot(all(ch %in% c("Scenario 1", "Scenario 2")))
  x[, choice := as.integer(ch == paste("Scenario", s))]
  e <- as.integer(unclass(d[[sprintf("CPCP_T%02d_S%d", t, s)]])); e[e %in% 97:99] <- NA
  stopifnot(all(e %in% c(1:10, NA)))
  x[, rating_effectiveness := e]
  ad <- list()
  for (w in names(blk)) {
    p <- sprintf("CPCP_T%02d_%s_S%d_", t, blk[w], s)
    ap <- as.integer(as.character(as_factor(d[[paste0(p, "Adapt")]]))); mi <- as.integer(as.character(as_factor(d[[paste0(p, "Mitigate")]])))
    stopifnot(all(ap + mi == 100), all(ap >= 0 & ap <= 100))
    path <- chr(paste0(p, "Distribution")); stopifnot(all(path %in% c("gradually increasing", "constant over time", "gradually decreasing")))
    x[, (paste0("attr_", w, "_cost")) := costtxt(chr(paste0(p, "Cost")), ctry)]
    x[, (paste0("attr_", w, "_cost_path")) := path]
    x[, (paste0("attr_", w, "_adaptation")) := paste0(ap, "%")]
    x[, (paste0("attr_", w, "_mitigation")) := paste0(mi, "%")]
  }
  x
}))))
stopifnot(res[, sum(choice), .(id, task)][, all(V1 == 1)])
for (w in c("own", "other")) for (a in names(ordr)) res[, (sub("attrpos_", paste0("attrpos_", w, "_"), a)) := ordr[[a]][id]]
res[, trial_block_order := chr("CPC_Country_Order")[id]]
stopifnot(res[, all(trial_block_order %in% c("COUNTRY/OTHER MAJOR ECONOMIES", "OTHER MAJOR ECONOMIES/COUNTRY"))])
res[, trial_block_order := ifelse(trial_block_order == "COUNTRY/OTHER MAJOR ECONOMIES", "own country first", "other major economies first")]
gen <- c(Male = "male", Female = "female", Other = "other")
g <- chr("DEMO_gender"); stopifnot(all(g %in% names(gen)))
by <- as.integer(d$DEMO_AGE); by[by < 1900 | by > 2005] <- NA
cv <- data.table(id = d$id, cov_country = ctry, cov_gender = unname(gen[g]), cov_birth_year = by,
                 cov_survey_weight = as.numeric(d$mbweight))
res <- merge(res, cv, by = "id")
setorder(res, id, task, profile)
fwrite(res, file.path(out, "bechtel_2022_climate_multilateralism.csv"))
