##Green-investment conjoint (Netherlands) from
##Beaucousin, J., Kantorowicz, J. J., & Moszoro, M. W. (2025). Building support for green
##investments. Applied Economics Letters. https://doi.org/10.1080/13504851.2025.2585154
##Replication data: Harvard Dataverse doi:10.7910/DVN/K7TEBA, CC0 1.0, no restricted files.
##File read: green_investments.RDS (long, one row per respondent x task x profile, built by the
##authors from a Qualtrics export; Dutch level text, attribute row positions *.rowpos). Read as
##text, not run: replication.Rmd (English relabelling for the figures). The article (closed access)
##was not read; the deposit description gives the design summary.
##Usage: Rscript beaucousin_2025.R <raw dir> <output dir>
##
##1,541 quota-representative Dutch respondents (deposit description), 8 tasks of two proposed green
##investments each (task, profile recorded), 4 attributes with 4 levels each, Dutch text as shown:
##  attr_type (Soort investering): Aanpassing van gebouwen / Duurzaam openbaar vervoer / Duurzame
##    landbouw / Schone elektrische stroom (authors: building retrofitting, sustainable public
##    transportation, sustainable farming, clean electricity)
##  attr_effect (Effect van de investeringen): Creëert banen / Toename in economische groei /
##    Verbetert de biodiversiteit / Vermindert de CO2 uitstoot
##  attr_place (Plaats van investering): Ethiopië / Nederland / Polen / Suriname
##  attr_financing (Financiering van investeringen): Verhoging van de brandstofbelasting / van de
##    BTW / van de inkomstenbelasting in Nederland / Verhoging van de Nederlandse staatsschuld
##Attribute row order (attrpos_*, from the *.rowpos columns, 1 = top) was randomized once per
##respondent (constant across a respondent's tasks and profiles: checked).
##Outcome: choice = `selected`; exactly one of two chosen in every answered task, so no opt-out was
##recorded. The question wording is not in the deposit (design_outcomes gives a paraphrase).
##Dropped: 33 tasks with no answer (selected NA on both profiles); Qualtrics Response.ID (the
##authors' sequential `respondent` is the id); the authors' derived respondentIndex. No covariates
##or survey weight are deposited. Restrictions and level weights are not documented; level shares
##are 24.6-25.4% and every pair of levels occurs.
##N = 1,541 respondents, as in the deposit description. Spot check (the authors' AMCEs are not in
##the deposit): OLS of choice on the four attributes, SEs clustered by id: vs Nederland, Polen -0.326
##(0.009), Ethiopie -0.282, Suriname -0.222; vs building retrofitting, sustainable farming +0.152
##(largest type effect); vs VAT, public debt +0.106 (largest financing effect); the pattern the
##deposit description reports (local investment, sustainable farming, public debt preferred).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "green_investments.RDS")))
stopifnot(nrow(s) == 24656, uniqueN(s$respondent) == 1541, s[, uniqueN(Response.ID), respondent][, all(V1 == 1)])
d <- s[, .(id = as.integer(respondent), task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_type = as.character(Soort.investering), attr_effect = as.character(Effect.van.de.investeringen),
           attr_place = as.character(Plaats.van.investering), attr_financing = as.character(Financiering.van.investeringen),
           attrpos_type = as.integer(Soort.investering.rowpos), attrpos_effect = as.integer(Effect.van.de.investeringen.rowpos),
           attrpos_place = as.integer(Plaats.van.investering.rowpos),
           attrpos_financing = as.integer(Financiering.van.investeringen.rowpos))]
stopifnot(d[, uniqueN(paste(attrpos_type, attrpos_effect, attrpos_place, attrpos_financing)), id][, all(V1 == 1)],
          d[, all(sort(c(attrpos_type, attrpos_effect, attrpos_place, attrpos_financing)) == 1:4), .(id, task, profile)]$V1)
d <- d[!is.na(choice)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 1541)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "beaucousin_2025_green_investments.csv"))
