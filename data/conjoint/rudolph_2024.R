##Arms-export conjoint (Germany and France) from
##Rudolph, L., Freitag, M., & Thurner, P. W. (2024). Deontological and consequentialist
##preferences towards arms exports: A comparative conjoint experiment in France and Germany.
##European Journal of Political Research, 63(2), 705-728. https://doi.org/10.1111/1475-6765.12617
##Replication data: Harvard Dataverse doi:10.7910/DVN/C6PTYD, CC0 1.0, no restricted files.
##File read: arms_conjoint.RDS (one data.frame, 6,617 rows, one per respondent).
##Level text: the authors' English labels (their theme_helpers.R conjoint_reshape(), read as
##text, and article Table 1); wording checked against the German master questionnaire
##(OSF rj89e, Rudolph-Freitag-Thurner-2020-SurveyDesign.pdf). Respondents saw German or French
##text, so the shared English master labels are used.
##Usage: Rscript rudolph_2024.R <raw dir> <output dir>
##
##6,617 respondents (Kantar opt-in online panel, quota sample on age, education, gender, region;
##Oct 2020-Jan 2021): Germany 3,250, France 3,367. The authors analyse the two countries pooled
##(main AMCEs) and compare them, with the same design and English master labels, so this is ONE
##table with cov_country. Each respondent saw 6 pairs (task 1-6) of hypothetical arms deliveries
##("Waffenlieferung 1/2" = profile 1/2), 9 attributes, levels drawn uniformly, no restrictions.
##Outcomes, both on the same screen as each pair:
##  choice: "If you had to decide between the two arms deliveries, which one would you personally
##    prefer and approve?" Forced choice, no opt-out (Q15A).
##  rating: "On a scale from 1 to 7, where 1 means the arms delivery should definitely be rejected
##    and 7 means it should definitely be approved: how would you assess the two arms
##    deliveries?" 1 = definitely reject .. 7 = definitely approve (Q15B r1/r2).
##Attributes (question -> levels): regime ("Government elected democratically?") Democratically
##elected / Not democratically elected; human_rights ("Human rights situation in the country?")
##Human rights respected / Freedom of expression suppressed / Dissidents persecuted/incarcerated/
##tortured; conflict ("Military conflicts in the country?") Peace in the country / Conflict with
##terrorists / Civil war with rebels / Country at war, under attack (German "verteidigt sich
##gegen Angriff", defending) / Country at war, attacks (German "greift selbst an"); article Table 1
##omits "Conflict with terrorists" but the questionnaire, code and text have it;
##security_partner ("Is country important for security of Germany/France?") Important partner /
##Not an important partner; trade ("Does country trade goods with Germany/France?") A lot of
##trade of goods / Little trade of goods; economic_value ("Economic profits for Germany/France in
##million Euro in total?") 1 m / 10 m / 100 m / 1000 m (1 bn); jobs ("How many jobs in
##Germany/France will be lost without delivery?") 100 / 1000 / 5000; weapon ("What is to be
##delivered?") Military protective equipment / Small arms (e.g. rifles, pistols) / Large weapons
##(e.g. tanks, aircraft, ships) / Military reconnaissance and surveillance systems (German shows
##"Militaerische Aufklaerungssysteme (z.B. Satellitentechnologie)"); other_suppliers ("Do other
##countries already supply weapons?") Unknown / <other country> / China and Russia / NATO partners
##(USA, UK, <other country>), where <other country> is France for German respondents and Germany
##for French respondents (the authors' "{France/Germany}" placeholder resolved per respondent, as
##the questionnaire specifies).
##Attribute row order was randomized per respondent (1/3 fully random, 2/3 by thematic blocks,
##fixed across that respondent's pairs; hidden variable CONJOINTORDER) but is not in the deposit.
##Covariates: cov_country; cov_gender Male/Female/Other; cov_age_group (bands 18-24..65-120);
##cov_education Low/Middle/High (authors' ISCED bands of the country question); cov_region
##(Bundesland or Region); cov_job; cov_household_income (authors' 7 collapsed net monthly bands;
##"don't know"/no answer missing; raw 15-band answer not deposited); cov_party (vote intention,
##country-specific party labels; "no answer" missing); cov_restrict_arms_exports (Q20C, "Should
##arms exports be restricted much more or much less than now?" 1 = much more .. 7 = much less);
##cov_arms_sometimes_necessary (Q20D, "Under certain conditions arms deliveries are necessary to
##help a country fend off an enemy or maintain internal security", 1 = not at all .. 7 = fully
##applies); cov_arms_trade_never (Q20E, "Trade in or transfer of weapons between states should in
##principle not be allowed", 1 = strongly disagree .. 7 = fully agree); cov_trade_for_economy (Q20F,
##"Trade in goods, weapons or other, should happen if it benefits the economy of Germany/France,
##regardless of other effects", same scale); cov_war_1..5 (Q21r6..r10, war subscale of the 10-item
##war/peace battery, 1 = strongly disagree .. 7 = strongly agree: 1 "There is no conceivable
##justification for war", 2 "War is sometimes the best way to solve a conflict", 3 "War is a
##futile struggle resulting in self-destruction", 4 "Under some conditions, war is necessary to
##maintain justice", 5 "Although war is terrible, it has some value"). The r6..r10 -> item mapping
##is INFERRED from the questionnaire's printed order (peace items r1-r5 are not deposited).
##Dropped: the vignette experiment that followed the conjoint (VIGNETTE, Q17, Choice,
##pipe_Choice_Pipe, Q19r1) and its free-text justification Q18; the party-position split
##experiment (Q20A, Q20B, ParteDisplay_*); raw party codes Q13/Q13_FR (= cov_party); per-task
##timers (CJ_3_timer equals CJ_4_timer in every row, so they are not trustworthy); the Kantar
##uuid (re-keyed to integers 1..6617 in file order). No survey weight is deposited.
##N = 6,617 (3,250 / 3,367) matches the article. Spot check (OLS of choice on all attributes,
##clustered by id): Not democratically elected -0.105, freedom of expression suppressed -0.148,
##dissidents persecuted -0.192, war/attacks -0.164, 1 bn 0.071, 5000 jobs 0.014, large weapons
##-0.075, China and Russia -0.023 all equal the article's text; NATO partners 0.087 vs 0.084 in the
##text. Mean rating is 3.20 (article: 3.23).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "arms_conjoint.RDS")))
stopifnot(nrow(s) == 6617, uniqueN(s$uuid) == 6617)
s[, rid := .I]
ctry <- as.character(s$hCountry); other <- ifelse(ctry == "Germany", "France", "Germany")
labs <- list(
  regime = c("Democratically elected", "Not democratically elected"),
  human_rights = c("Human rights respected", "Freedom of expression suppressed", "Dissidents persecuted/incarcerated/tortured"),
  conflict = c("Peace in the country", "Conflict with terrorists", "Civil war with rebels", "Country at war, under attack",
               "Country at war, attacks"),
  security_partner = c("Important partner", "Not an important partner"),
  trade = c("A lot of trade of goods", "Little trade of goods"),
  economic_value = c("1 m", "10 m", "100 m", "1000 m (1 bn)"),
  jobs = c("100", "1000", "5000"),
  weapon = c("Military protective equipment", "Small arms (e.g. rifles, pistols)", "Large weapons (e.g. tanks, aircraft, ships)",
             "Military reconnaissance and surveillance systems"),
  other_suppliers = NULL)
rows <- list()
for (t in 1:6) for (p in 1:2) {
  ch <- s[[sprintf("Q15A%dr1", t)]]; stopifnot(all(ch %in% 1:2))
  rt <- s[[sprintf("Q15B%dr%d", t, p)]]; stopifnot(all(rt %in% 1:7))
  d <- data.table(id = s$rid, task = t, profile = p, choice = as.integer(ch == p), rating = as.integer(rt))
  for (k in 1:9) {
    x <- s[[sprintf("CJ%dATT%dCH%d", t, k, p)]]
    if (k < 9) { l <- labs[[k]]; stopifnot(all(x %in% seq_along(l))); v <- l[x] }
    else { stopifnot(all(x %in% 1:4))
      v <- c("Unknown", NA, "China and Russia", NA)[x]
      v[x == 2] <- other[x == 2]; v[x == 4] <- paste0("NATO partners (USA, UK, ", other[x == 4], ")") }
    d[, paste0("attr_", names(labs)[k]) := v]
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
fc <- function(x) { x <- as.character(x); bad <- !is.na(x) & !validUTF8(x); x[bad] <- iconv(x[bad], "latin1", "UTF-8"); x } # Windows latin1 labels
cv <- s[, .(id = rid, cov_country = ctry, cov_gender = fc(Gender), cov_age_group = fc(Age), cov_education = fc(Education),
            cov_region = ifelse(ctry == "Germany", fc(region_de), fc(region_fr)), cov_job = fc(Job_situation),
            cov_household_income = fc(Household_Income),
            cov_party = ifelse(ctry == "Germany", fc(party_choice_de), fc(party_choice_fr)),
            cov_restrict_arms_exports = as.integer(Q20C), cov_arms_sometimes_necessary = as.integer(Q20D),
            cov_arms_trade_never = as.integer(Q20E), cov_trade_for_economy = as.integer(Q20F),
            cov_war_1 = as.integer(Q21r6), cov_war_2 = as.integer(Q21r7), cov_war_3 = as.integer(Q21r8),
            cov_war_4 = as.integer(Q21r9), cov_war_5 = as.integer(Q21r10))]
d <- merge(d, cv, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 6617 * 12, d[cov_country == "Germany", uniqueN(id)] == 3250)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rudolph_2024_arms_exports.csv"))
