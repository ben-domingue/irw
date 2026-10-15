##Beach recreation stated-choice experiment on jellyfish blooms (Catalonia, Spain) from
##Nunes, P. A. L. D., Loureiro, M. L., Pinol, L., Sastre, S., Voltaire, L., & Canepa, A. (2015). Analyzing beach
##recreationists' preferences for the reduction of jellyfish blooms: Economic results from a stated-choice
##experiment in Catalonia, Spain. PLOS ONE, 10(6), e0126681. https://doi.org/10.1371/journal.pone.0126681
##Data: figshare doi:10.6084/m9.figshare.1372408 (v1), CC BY 4.0 (figshare API). File read: CE_database.xls (the
##figshare upload carries a multipart-form header before the OLE2 bytes; the script strips everything before the
##OLE2 signature and reads sheet 1). Usage: Rscript nunes_2015.R <dir holding CE_database.xls> <output dir>
##
##644 adult beach recreationists interviewed face to face at eight Catalan beaches, 14 Jun-15 Sep 2012. Two survey
##types (A: 4 choice cards, B: 5 cards; one type per respondent, trial_survey_type). Each card: Beach A, Beach B and
##a third option "stay at home or do any recreational activity other than going to the beach" (status quo), which
##has no attributes: opt-out (opt_out = yes; its rows are dropped, choice is 0 on both profiles when chosen, 106
##of 2,395 answered cards). Outcome: choice among the three options (exact card wording not in the deposit).
##Profile 1 = Beach A, 2 = Beach B; task = choice_card (assumed in the order shown).
##Attributes (deposit tags -> level text of the paper's Table 2):
##  attr_jellyfish_risk: low/high -> "Low risk (<=2 days/week)" / "High risk (> 5 days/week)"
##  attr_water_transparency: average/above -> "Average (as regulated by the law)" / "Above average"
##  attr_services: pt/ptc/ptcs -> "Parking and toilets" / "Parking, toilets and children play area" /
##     "Parking, toilets, children's play area and first aid centre"
##  attr_extra_travel_time: LABELS: codes only. The deposit stores the proportion 0.2/0.3/0.4 (nom_time = time x the
##     respondent's reported travel minutes), the paper's Table 2 lists +5%/+10%/+15%; the two cannot be reconciled
##     from the files, so the stored value is kept as text ("0.2" = 0.2 x the reported travel time).
##Restrictions: none documented (36 profiles from a 2^2 x 3^2 design, orthogonal); level weights unknown.
##Choices are missing (all three rows NA) for 497 of the 2,892 cards, including 4 respondents with none and 136
##with only their first card answered (the paper does not say why); those cards are omitted (no outcome). One card
##(id 196, card 1) has two options marked chosen and is dropped. Respondents kept: those with >= 1 answered card.
##Covariates: cov_gender (sexe: man/woman -> male/female), cov_age (years, as recorded), cov_site (beach, case
##harmonised: Blanes, Barceloneta, Bogatell, De Castell, De la Fosca, Del Golfet, Gran de Palamos, Sabanell).
##Dropped: all other survey columns (interviewer name, interview date, place of birth/residence, postal-style
##residence codes, nationality, income, education with mixed spellings, etc.). id = deposit id (1..644 integers).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
bytes <- readBin(file.path(raw, "CE_database.xls"), "raw", file.size(file.path(raw, "CE_database.xls")))
sig <- as.raw(c(0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1, 0x1a, 0xe1))
i <- which(bytes[1:2000] == sig[1] & c(bytes[2:2000], as.raw(0)) == sig[2])[1]
stopifnot(identical(bytes[i:(i + 7)], sig))
tf <- tempfile(fileext = ".xls"); writeBin(bytes[i:length(bytes)], tf)
x <- as.data.table(suppressMessages(read_excel(tf, sheet = 1, guess_max = 1e5)))
x <- x[, .(id, site, sexe, age, survey, choice_card, beaches, choice, risk = `risk...113`, water = `water...115`,
  environ = `environ...117`, time)]
stopifnot(nrow(x) == 8676, uniqueN(x$id) == 644, x[, .N, .(id, choice_card)][, all(N == 3)])
cs <- x[, .(n1 = sum(choice, na.rm = TRUE), nna = sum(is.na(choice))), .(id, choice_card)]
stopifnot(cs[, all(nna %in% c(0, 3))], cs[n1 > 1, .N] == 1)
bad <- cs[n1 > 1]; x <- x[!(id == bad$id & choice_card == bad$choice_card)]
x <- x[!is.na(choice)]
stopifnot(x[, sum(choice), .(id, choice_card)][, all(V1 == 1)])
stopifnot(x[beaches == "SQ", all(risk == "0" & time == 0)], x[beaches != "SQ", !any(risk == "0" | time == 0)])
cov <- unique(x[, .(id, sexe = sexe, age = age, site = site)][, .(sexe = sexe[!is.na(sexe)][1], age = age[!is.na(age)][1], site = site[1]), id])
sitefix <- c(barceloneta = "Barceloneta", blanes = "Blanes", bogatell = "Bogatell", sabanell = "Sabanell", `de castell` = "De Castell",
  `de la fosca` = "De la Fosca", `del golfet` = "Del Golfet", `gran de palamos` = "Gran de Palamos")
cov[, site := unname(sitefix[tolower(site)])]
stopifnot(!anyNA(cov$site), cov[, uniqueN(id)] == uniqueN(x$id))
p <- x[beaches != "SQ"]
d <- p[, .(id, task = as.integer(choice_card), profile = ifelse(beaches == "A", 1L, 2L), choice = as.integer(choice),
  attr_jellyfish_risk = c(low = "Low risk (<=2 days/week)", high = "High risk (> 5 days/week)")[risk],
  attr_water_transparency = c(average = "Average (as regulated by the law)", above = "Above average")[water],
  attr_services = c(pt = "Parking and toilets", ptc = "Parking, toilets and children play area",
    ptcs = "Parking, toilets, children's play area and first aid centre")[environ],
  attr_extra_travel_time = format(time, nsmall = 1), trial_survey_type = survey)]
d <- merge(d, cov[, .(id, cov_gender = c(man = "male", woman = "female")[sexe], cov_age = ifelse(age >= 15 & age <= 100, as.integer(age), NA_integer_), cov_site = site)], by = "id")
d[, id := match(id, sort(unique(id)))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nunes_2015_jellyfish_beach.csv"))
