##Electric-vehicle purchase conjoint (canton of Zurich) from
##Bernauer, T., Brückmann, G., Quoß, F., & Wicki, M. (2022). Registered design for survey experiment:
##Decision behaviour when purchasing electric vehicles [Data set]. Harvard Dataverse.
##https://doi.org/10.7910/DVN/NAAVVP (pre-registration deposited 2020-03-17, data added in version 3,
##2022-11-28; no journal article is linked, so the deposit is cited; the deposit also holds the
##project's final report, FP-1.26_EFZ_Layout_Schlussbericht_def (1).pdf, not read).
##Replication data: CC0 1.0, no restricted files, no terms.
##Files read: evzh_conjoint.RData (df_conj), evzh_sociodemographics.RData (df_resp). Also read as
##text: conjoint_EVZH_english.R (level order, models), 20200317_preregistration_EVZH.pdf (design,
##question wording) and final_survey.pdf (Qualtrics print of the fielded German survey).
##Usage: Rscript bernauer_2022.R <raw dir> <output dir>
##
##Random sample of adult residents of the canton of Zurich invited by the cantonal Statistical Office
##(pre-registration), online, fielded Aug-Sep 2020. Respondents were randomized to Experiment 1 (this
##conjoint) or Experiments 2-5; 1,021 did the conjoint: 4 comparisons (task = round) of two cars
##(profile 1 = Auto A, 2 = Auto B; source `car`), 10 attributes, levels randomized independently
##("[RANDOMISE ATTRIBUTE]" per cell in the pre-registration; no constraints in the authors' cjoint
##design, makeDesign(constraints = list())). Display language German; level text as stored (German
##number formats). The survey's attribute overview spells charging times "15 Minuten" etc.; the
##data store "15 min" (the per-task cells were piped Qualtrics fields, not printed).
##Attributes (German row label in the survey -> column): Reichweite bei vollgeladener Batterie ->
##attr_range; Kaufpreis -> attr_purchase_price; Jährliche Unterhaltskosten (Versicherung, Service,
##Ersatzteile, Reparaturen) -> attr_maintenance_cost; Energiekosten pro 100km (Strom) ->
##attr_energy_cost; Garantierte Lademöglichkeit an öffentlicher Ladestation im Umkreis Ihres
##Haushalts von -> attr_charging_guarantee; Laden der Batterie von 0 auf 80% dauert ->
##attr_charging_time; Elektroauto kann für Fr. ... pro Tag gegen ein Benzin- oder Dieselauto
##eingetauscht werden -> attr_car_exchange; ... gegen eine SBB-Tageskarte 2. Klasse eingetauscht
##werden -> attr_pt_day_pass; Garantieperiode (gratis Ersatz) für die Batterie, falls deren
##Kapazität unter 80% der Neukapazität fällt -> attr_battery_warranty; Staatlicher Förderbeitrag an
##den Autokauf (Kaufprämie) -> attr_subsidy.
##Attribute rows are piped per task (T<t>R<r>C1 fields), so row order may have been randomized; it
##is not in the deposit.
##Outcomes (final_survey.pdf):
##  choice  "Wenn Sie sich für eines der beiden Autos entscheiden müssten, welches Auto würden Sie
##          kaufen?" Vorschlag A / Vorschlag B; forced ("Auch wenn Ihnen keines der beiden Autos
##          wirklich gefällt, wählen Sie bitte dasjenige, welches Sie weniger ablehnen"), no opt-out.
##  rating  `buy`: "Würden Sie Auto A kaufen?" / "Würden Sie Auto B kaufen?" Ja = 1, Nein = 0.
##trial_group = the source `group` (1/2), constant within respondent. The survey has two versions
##of the conjoint block, "Conjoint Pos" and "Conjoint Neg"; elsewhere the survey's pos/neg versions
##reverse the order of answer options. Which group is which, and what differs in the conjoint, is
##not documented.
##Dropped: the Qualtrics ResponseId (re-keyed); from df_resp ExternalReference (the panel/invitation
##reference code), start/end times, progress, experiment (all "1" here) and the Q45_* items (reasons
##not to buy an EV, a separate question).
##Covariates (df_resp): cov_gender (GESCHLECHT maennlich/weiblich -> male/female), cov_age (ALTER,
##years as stored), cov_education (Q3, "Bitte geben Sie Ihre höchste abgeschlossene Ausbildung an.",
##answer text as stored), cov_pt_subscription (abo, "Besitzen Sie ein Abonnement des öffentlichen
##Verkehrs (ÖV)?" Ja/Nein), cov_duration_sec (whole-survey duration). No survey weight.
##N: 1,021 respondents x 4 tasks, every task with one choice (8,168 rows as deposited).
##Spot check: lm(choice ~ 10 attributes), SEs clustered by respondent, as the authors' cjoint::amce
##call: purchase price CHF 40'000 / 60'000 / 80'000 / 100'000 vs 20'000 = -0.055 / -0.148 / -0.222 /
##-0.304 (SE 0.017); monotone as expected. The final report's figures were not compared.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "evzh_conjoint.RData"), envir = e); x <- as.data.table(as.data.frame(e$df_conj))
e2 <- new.env(); load(file.path(raw, "evzh_sociodemographics.RData"), envir = e2); s <- as.data.table(e2$df_resp)
stopifnot(x[, .(n = .N, c = sum(choice)), .(ResponseId, round)][, all(n == 2 & c == 1)], all(x$buy %in% 0:1),
          x[, uniqueN(group), ResponseId][, all(V1 == 1)], all(x$ResponseId %in% s$ResponseId))
# some Q3 factor labels are latin1 strings; write UTF-8
utf8 <- function(v) ifelse(validUTF8(v), v, iconv(v, "latin1", "UTF-8"))
ids <- unique(x$ResponseId)
d <- data.table(id = match(x$ResponseId, ids), task = as.integer(x$round), profile = as.integer(x$car),
                choice = as.integer(x$choice), rating = as.integer(x$buy),
                attr_range = x$Reichweite, attr_purchase_price = x$Kaufpreis, attr_maintenance_cost = x$Unterhaltskosten,
                attr_energy_cost = x$Energiekosten, attr_charging_guarantee = x$Ladegarantie, attr_charging_time = x$Ladedauer,
                attr_car_exchange = x$Verbrennertausch, attr_pt_day_pass = x$Tageskarte, attr_battery_warranty = x$Garantie,
                attr_subsidy = x$Beitrag, trial_group = as.integer(x$group))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(nzchar(d[[v]])))
s <- s[match(x$ResponseId, s$ResponseId)]
stopifnot(all(s$experiment == "1"), all(s$GESCHLECHT %in% c("maennlich", "weiblich")), all(s$group == x$group))
d[, `:=`(cov_gender = c(maennlich = "male", weiblich = "female")[s$GESCHLECHT], cov_age = as.integer(s$ALTER),
         cov_education = utf8(as.character(s$Q3)), cov_pt_subscription = as.character(s$abo),
         cov_duration_sec = as.integer(s$duration))]
d[, cov_gender := unname(cov_gender)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bernauer_2022_ev_purchase_zurich.csv"))
cat(nrow(d), uniqueN(d$id), "\n")
