##Interest-group trade-agreement conjoint from
##Dür, A., Huber, R. A., Mateo, G., & Spilker, G. (2023). Interest group preferences towards
##trade agreements: Institutional design matters. Interest Groups & Advocacy, 12(1), 48-72.
##https://doi.org/10.1057/s41309-022-00174-z
##Replication data: Harvard Dataverse doi:10.7910/DVN/UJGMAW, CC0 1.0, no restricted files.
##File read: survey_clean.rds. Design and wording from the article (CC BY 4.0, open access via
##KOPS, Konstanz), section "Choice experiment" and Table 1; the authors' preparing_experimental_
##data.R (read as text) gives the column layout (a1/b1 = round 1 agreements A/B, a2/b2 = round 2).
##Usage: Rscript dur_2023.R <raw dir> <output dir>
##
##609 interest groups (business associations, citizen groups, labour unions) from a worldwide
##online survey (2,841 invited; one representative answered per group); each compared two
##proposed trade agreements side by side, two times (task 1-2; agreement A = profile 1). Four
##binary attributes, shown as rows "The agreement includes provisions..." with Yes/No cells
##(Table 1): ...liberalising services (attr_services), ...protecting intellectual property
##rights (attr_ipr), ...protecting the environment (attr_environment), ...protecting labour
##rights (attr_labour). Levels "Yes"/"No" as displayed (source 1/0).
##Outcomes:
##  choice = which agreement the group prefers ("choose the design they prefer more"; options
##     Agreement A / Agreement B / Neither; wording not deposited, paraphrase). Opt-out: "Neither"
##     (footnote 6, indifference allowed) -> choice 0 on both profiles; 411 of 1,213 tasks.
##  rating = each agreement rated "on a scale from 1 (not favourably at all) to 10 (very
##     favourably)" (paraphrase of the article); higher = more favourable.
##Restrictions: none stated ("we randomly vary whether it includes (Yes) or excludes (No)");
##the data hold all 16 combinations.
##Respondents: the 609 with a round-1 answer (as the authors' code; 82 others in the file never
##reached the experiment). Tasks with no choice and no rating are omitted; a missing
##rating on an otherwise answered task stays NA (4 profile ratings); 5 round-2 tasks with neither were omitted.
##Covariates (group descriptors, the authors' manual coding, source text/values): cov_group_type
##(type: Business groups / Citizen groups / Labour union / Professional association),
##cov_group_type3 (gen_type: professional associations merged into business groups),
##cov_bus_sector, cov_ngo_type, cov_export_orientation (shr: exports / (exports + imports) of
##the group's sector in its home country, from Comtrade/BaTiS; NA for non-business and
##economy-wide groups), cov_knowledge_intensive, cov_services_tradeable, cov_general_business
##(0/1), cov_non_eu_oecd_focus (No/Yes), cov_focus_region (country or region the group works
##in). Dropped: seed (randomization seed). No survey weight. No IDs in the deposit; id = row
##order among the 609.
##N = 609 matches the article (2,436 profile observations). Spot check: mean rating by group
##type, citizen groups 4.19 and labour unions 3.96, as in the article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "survey_clean.rds")))
s <- s[!is.na(exp1)]
s[, rid := .I]
yn <- function(x) { stopifnot(all(x %in% 0:1)); fifelse(x == 1, "Yes", "No") }
d <- rbindlist(lapply(1:2, function(t) rbindlist(lapply(1:2, function(p) {
  k <- paste0(c("a", "b")[p], t); ch <- s[[paste0("exp", t)]]
  stopifnot(all(ch %in% c("Agreement A", "Agreement B", "Neither", NA)))
  data.table(id = s$rid, task = t, profile = p,
             choice = fifelse(ch == paste("Agreement", c("A", "B")[p]), 1L, 0L),
             rating = as.integer(s[[paste0("exp", t, "_favourably_", c("A", "B")[p])]]),
             attr_services = yn(s[[paste0("ser_", k)]]), attr_ipr = yn(s[[paste0("ipr_", k)]]),
             attr_environment = yn(s[[paste0("env_", k)]]), attr_labour = yn(s[[paste0("lab_", k)]]))
}))))
cv <- s[, .(id = rid, cov_group_type = as.character(type), cov_group_type3 = as.character(gen_type),
            cov_bus_sector = as.character(bus_sector), cov_ngo_type = as.character(ngo_type), cov_export_orientation = shr,
            cov_knowledge_intensive = as.integer(knowledge_intensive), cov_services_tradeable = as.integer(services_tradeable),
            cov_general_business = as.integer(general_business), cov_non_eu_oecd_focus = as.character(non_EU_OECD_focus),
            cov_focus_region = focus_region1)]
d <- merge(d, cv, by = "id")
d[, keep := !(all(is.na(choice)) & all(is.na(rating))), .(id, task)]
d <- d[keep == TRUE][, keep := NULL]
stopifnot(all(d$rating %in% c(1:10, NA)), d[, sum(choice), .(id, task)][, all(V1 <= 1 | is.na(V1))], uniqueN(d$id) == 609L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dur_2023_trade_agreement_groups.csv"))
