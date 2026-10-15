##Gulf of Alaska commercial salmon permit holders: discrete choice experiment on whether to keep fishing.
##Data: Schwoerer, T. (2022). A discrete choice survey with Gulf of Alaska commercial salmon permit
##holders conducted in 2022. NSF Arctic Data Center. https://doi.org/10.18739/A2GF0MX8D, CC BY 4.0
##(EML intellectualRights; checked on the DataONE metadata record). The associated article could not be
##identified (the record lists none), so the article N cannot be compared; the deposit text says 462
##filtered respondents, which is what is kept here.
##Files read: OAsalmonCBC_2con_data051122.csv (Sawtooth export, one row per respondent),
##OAsalmonCBC_2con_CBC_Design2.csv (the 300-version design of the random tasks),
##SupplementaryFile1.pdf (the survey print-out: displayed level text) and SupplementaryFile3.docx
##(fixed-task settings, image text), SupplementaryFile4.Rmd (how the design was built), all read as text/images.
##Usage: Rscript schwoerer_2022.R <dir holding the files above> <output dir>
##
##706 Sawtooth records; 462 answered at least one choice task and are kept (the same count as the
##"Filtered respondent count 462" in SupplementaryFile3). 418 answered all 12 tasks. Respondents are
##Alaska commercial salmon permit holders (4 areas x 4 gear classes, mailed + text invitation, online,
##Mar-May 2022). Each respondent saw 12 tasks of 5 alternatives: TWO described fisheries (profiles) plus
##three alternatives WITHOUT attributes: "wait out a year", "sell permit" and "NONE: I wouldn't choose
##any of the above. I would do something else". The three are opt-outs (no profile rows).
##Outcome (choice): "If you had a choice between the two fisheries, waiting out a year, or selling
##your permit, which one would you choose?" (plus the NONE option). Choice = 1 on the chosen fishery;
##0 on both when an opt-out was chosen; which opt-out is in trial_optout_chosen.
##Design: 10 tasks drawn at random from 300 versions of an alternative-specific Sawtooth design (version =
##sys_CBCVersion_CBC, joined on version + task) plus 2 FIXED tasks shown to everybody (positions 5 and 10).
##The two fixed tasks are DROPPED: the design settings give algal blooms = "full season" for both
##fisheries but the survey print-out shows no algal-bloom row in them, so the displayed text cannot be
##stated; the authors also exclude them from estimation. Task = position shown (1-4 random, 5 fixed,
##6-9 random, 10 fixed, 11-12 random), so tasks 5 and 10 are absent. The random task k is design Task k
##(random tasks are CBC_Random1..10 in order).
##Attributes (level text from the survey print-out SF1 and the fixed-task images, mapping verified by
##matching the printed example tasks to design version 1: the printed levels match codes exactly):
##  species (sockeye/chum/pink: the fishery's target species; alternative-specific, code in Att 1),
##  harvest ("5-year-average"/"half of 5-year-average"/"10% of 5-year-average", codes 1/2/3),
##  lbs per fish (species-specific: pink 1.5/2/2.5, sockeye 3.5/4/4.5, chum 5.5/6/6.5 lbs, codes 1/2/3),
##  price per lb (pink $0.06/$0.15/$0.24, sockeye $0.40/$0.66/$0.91, chum $0.10/$0.22/$0.35),
##  algal blooms and jellyfish (none / half season / full season, codes 1/2/3; code 3 = full season is
##  confirmed by the fixed-task settings, 1 and 2 by the printed task of version 1).
##Restrictions: the two fisheries of a task target different species and size and price levels are
##species-specific (nested); other combinations appear to be balanced. Attribute order fixed.
##Level weights: Sawtooth balanced design, no probabilities stated.
##Covariates: cov_fishery (permitText: permit/fishery code and name as stored), cov_age_group (Age, text
##of the answer bands). Dropped: Password (individual access code), timestamps, browser/OS, all other
##survey answers, free text (Openended etc.). No IP/name/geo fields exist in the file.
##Weights: the authors' post-stratification weights are computed in SupplementaryFile2.Rmd from population
##counts, not stored in the data file (not kept).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "OAsalmonCBC_2con_data051122.csv"))
des <- fread(file.path(raw, "OAsalmonCBC_2con_CBC_Design2.csv"))
setnames(des, c("ver", "task", "concept", "alt", "harv", "chs", "red", "pks", "pkp", "chp", "skp", "alg"))
des <- des[concept <= 2]
cols <- c("CBC_Random1","CBC_Random2","CBC_Random3","CBC_Random4","CBC_Random5","CBC_Random6","CBC_Random7","CBC_Random8","CBC_Random9","CBC_Random10")
pos <- c(1:4, 6:9, 11:12)
r <- r[rowSums(!is.na(r[, ..cols])) > 0 | !is.na(CBC_Fixed1) | !is.na(CBC_Fixed2)]
stopifnot(nrow(r) == 462, !anyNA(r$sys_CBCVersion_CBC))
r[, id := .I]
ch <- melt(r[, c("id", "sys_CBCVersion_CBC", cols), with = FALSE], id.vars = c("id", "sys_CBCVersion_CBC"),
           variable.name = "v", value.name = "pick")
ch[, task := as.integer(sub("CBC_Random", "", v))][, pos := pos[task]]
ch <- ch[!is.na(pick)]
setnames(ch, "sys_CBCVersion_CBC", "ver")
d <- merge(ch, des, by = c("ver", "task"), allow.cartesian = TRUE)
stopifnot(d[, .N, .(id, task)][, all(N == 2)])
sp <- c("sockeye", "chum", "pink")
d[, attr_species := sp[alt]]
d[, attr_harvest := c("5-year-average", "half of 5-year-average", "10% of 5-year-average")[harv]]
size <- list(sockeye = c("3.5 lbs", "4 lbs", "4.5 lbs"), chum = c("5.5 lbs", "6 lbs", "6.5 lbs"), pink = c("1.5 lbs", "2 lbs", "2.5 lbs"))
price <- list(sockeye = c("$0.40", "$0.66", "$0.91"), chum = c("$0.10", "$0.22", "$0.35"), pink = c("$0.06", "$0.15", "$0.24"))
d[, sz := fcase(alt == 1, red, alt == 2, chs, alt == 3, pks)]
d[, pr := fcase(alt == 1, skp, alt == 2, chp, alt == 3, pkp)]
d[, attr_lbs_per_fish := mapply(function(s, k) size[[s]][k], attr_species, sz)]
d[, attr_price_per_lb := mapply(function(s, k) price[[s]][k], attr_species, pr)]
d[, attr_algal_blooms_jellyfish := c("none", "half season", "full season")[alg]]
stopifnot(!anyNA(d[, .(attr_species, attr_harvest, attr_lbs_per_fish, attr_price_per_lb, attr_algal_blooms_jellyfish)]))
d[, profile := concept][, choice := as.integer(pick == concept)]
d[, trial_optout_chosen := fcase(pick == 3, "wait out a year", pick == 4, "sell permit", pick == 5, "none of the above", default = NA_character_)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], all(d$pick %in% 1:5))
ag <- c("under 20", "between 20 and 30", "between 30 and 40", "between 40 and 50", "between 50 and 60", "between 60 and 70", "older than 70")
cv <- r[, .(id, cov_fishery = trimws(permitText), cov_age_group = ag[Age])]
d <- merge(d, cv, by = "id")
d[, task := pos]
d <- d[, .(id, task, profile, choice, attr_species, attr_harvest, attr_lbs_per_fish, attr_price_per_lb,
           attr_algal_blooms_jellyfish, cov_fishery, cov_age_group, trial_optout_chosen)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "schwoerer_2022_salmon_permits.csv"))
