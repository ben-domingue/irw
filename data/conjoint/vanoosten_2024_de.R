##Politician-vignette experiment, EMMAVID Germany, from
##van Oosten, S., Mügge, L., Hakhverdian, A., van der Pas, D., & Vermeulen, F. (2024). German Ethnic
##Minority and Muslim Attitudes, Voting, Identity and Discrimination (EMMAVID) - EMMAVID Data Germany
##[Data set]. Harvard Dataverse. Analysed in van Oosten, S. (2023). Who favor in-group politicians?
##In-group voting in France, Germany and the Netherlands and the challenges to the descriptive and
##substantive representation of Muslims. OSF Preprints. https://doi.org/10.31219/osf.io/rkejd
##Replication data: Harvard Dataverse doi:10.7910/DVN/GT4N9J, CC0 1.0, no restricted files.
##Files read: DataDE_EMMAVID_vanOosten_etal_2024.sav (SPSS original; read with foreign::read.spss,
##haven cannot parse it), "Codebook - Germany - EMMAVID - Van Oosten et al 2024.pdf" (English
##questionnaire Part 3b, Table A1 name lists, OSF pre-registration), and the authors' "Code - van
##Oosten 2023 - OSF - Who Favor In-Group Politicians.R" read as text (not run) for the variable-to-
##profile mapping (L390-445) and the statement codes (L1615-1630).
##Sibling of vanoosten_2024_politicians_nl (data/conjoint/vanoosten_2024.R, same design, separate
##fielding and language): one table per country.
##Usage: Rscript vanoosten_2024_de.R <raw dir> <output dir>
##
##954 respondents of a German online panel (Kantar; respondents with Turkish and former-Soviet
##parents oversampled: V50041). Part 3b: three pairs of text vignettes (codebook: "<Politician> has
##a Turkish background and practices Islam. He says the tax rate for the rich must be higher");
##task = pair 1-3 (questionnaire profiles 3-4, 5-6, 7-8, in the order shown), profile = 1st / 2nd
##politician of the pair. Randomized per profile: background x religion (V40_k, 9 combinations),
##gender and first name (V10_k / V20_k, same code), surname (V30_k), policy statement (V2001-V2006,
##8 issues x 2 directions).
##attr_ text is GERMAN, as displayed (the .sav value labels are German): from the V40 labels
##"Der/die Politiker/in hat einen <X> Hintergrund und <Y>." -> attr_background = X (türkischen /
##sowjetischen / ausschließlich deutschen; the English codebook says Turkish / Former Soviet Union /
##German) and attr_religion = Y (praktiziert den Islam / praktiziert das Christentum / praktiziert
##keine Religion); attr_gender = V10 label, the pronoun of "<Sie/Er> sagt ..." (Sie / Er);
##attr_first_name / attr_surname = V20 / V30 labels; attr_statement = the German statement for codes
##1-16, taken from the .sav variable labels of V7101-V7116, whose order equals the authors' English
##list for idprofpp 1-16 (R code L1615-1630).
##Outcomes (codebook Part 3b, English questionnaire; respondents saw German; .sav value labels
##"0 - Überhaupt nicht", 1, ..., 9, "10 - Sehr"):
##  rating_represents "Do you think this politician represents you?" (V359_1, V369_1, ... _1)
##  rating_trust      "How much do you trust this politician?" (_2)
##  rating_capable    "How capable do you think this politician is to perform well on the job?" (_3)
##     each stored RAW as the .sav code 1-11 (code = displayed number + 1; higher = more favourable),
##     as in the NL sibling.
##  choice            "Which politician are you most likely to vote for?" (V380/V410/V440: 1 = first,
##                    2 = second politician of the pair; forced choice, no opt-out; every pair answered).
##trial_group = V50 ("Group 1" / "Group 2 (Control group)", not explained in the codebook);
##trial_block_order = V51 (statements first vs profiles first; the label text is Dutch).
##Names: first names and surnames come from the background's lists (codebook Table A1); the check
##below counts profiles whose first-name code lies outside its background's list block: 228 of the
##1,921 Turkish-background profiles carry a first name from the former-Soviet list (German names
##such as Christina, Thomas) with a Turkish surname, against Table A1. Kept as stored (the .sav
##records what was programmed; whether respondents saw it cannot be checked). Surnames always match.
##Dropped: Part 3a (profiles 1-2, outcome = expected policy position, a different design); free-text
##"why" answers; INTNR (panel interview number, re-keyed to integers in file order); other survey
##blocks. No survey weight is deposited (the authors' code builds a population weight w8eth from
##ethnic group shares; not in the deposit and not rebuilt here).
##Covariates: cov_gender (V640 "Gender": Männlich = male, Weiblich = female), cov_birth_year (V650
##"Age": values 1938-2001 are years of birth), cov_education_code (V680 "Education" codes: the
##.sav labels 20 options, 1 = Kein Abschluss ... 20 = Promotion, but the data hold only 1-9, i.e. no
##vocational or university degree at all, which is implausible for 954 adults, so the label mapping
##is not trusted and codes are kept), cov_parent_born (V50041, place of birth of mother or father,
##German label text: Türkei / Ehemalige Sowjetunion / Deutschland / Anderes), cov_region (V660
##Bundesland label), cov_duration_sec (INTTIME, interview duration in seconds).
##N: 954 in the deposit; the OSF preprint pools FR/DE/NL and was not checked for the DE count.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- suppressWarnings(foreign::read.spss(file.path(raw, "DataDE_EMMAVID_vanOosten_etal_2024.sav"), to.data.frame = FALSE,
                                         use.value.labels = FALSE, reencode = "UTF-8"))
vlab <- attr(s, "variable.labels")
lab <- function(v) { x <- s[[v]]; l <- attr(x, "value.labels"); out <- names(l)[match(x, l)]; stopifnot(all(is.na(x) | !is.na(out))); trimws(out) }
stmt <- trimws(unname(vlab[sprintf("V71%02d", 1:16)]))
stopifnot(startsWith(stmt[1], "Der Steuersatz für Reiche sollte höher"), startsWith(stmt[16], "Es sollte homosexuellen Paaren gestattet"))
rq <- c("V359", "V369", "V389", "V399", "V419", "V429"); cq <- c("V380", "V410", "V440")
n <- length(s$INTNR); stopifnot(n == 954, !anyDuplicated(s$INTNR)); rows <- list()
for (j in 1:6) {
  k <- j + 2L; t <- (j + 1L) %/% 2L; p <- 2L - j %% 2L
  bg <- lab(paste0("V40_", k)); g <- lab(paste0("V10_", k))
  stopifnot(!anyNA(bg), all(g %in% c("Sie", "Er")), all(s[[paste0("V10_", k)]] == s[[paste0("V20_", k)]]))
  m <- regmatches(bg, regexec("^Der/die Politiker/in hat einen (.*) Hintergrund und (.*)\\.$", bg))
  stopifnot(all(lengths(m) == 3))
  ch <- as.integer(s[[cq[t]]]); stopifnot(all(ch %in% 1:2))
  r <- lapply(1:3, function(q) as.integer(s[[paste0(rq[j], "_", q)]]))
  stopifnot(all(unlist(r) %in% 1:11), all(as.integer(s[[paste0("V200", j)]]) %in% 1:16))
  rows[[j]] <- data.table(id = seq_len(n), task = t, profile = p, choice = as.integer(ch == p),
    rating_represents = r[[1]], rating_trust = r[[2]], rating_capable = r[[3]],
    attr_first_name = lab(paste0("V20_", k)), attr_surname = lab(paste0("V30_", k)), attr_gender = g,
    attr_background = sapply(m, `[`, 2), attr_religion = sapply(m, `[`, 3),
    attr_statement = stmt[as.integer(s[[paste0("V200", j)]])],
    bgcode = as.integer(s[[paste0("V40_", k)]]), fncode = as.integer(s[[paste0("V20_", k)]]))
}
d <- rbindlist(rows)
stopifnot(!anyNA(d$attr_surname), !anyNA(d$attr_first_name), d[, sum(choice), .(id, task)][, all(V1 == 1)])
# first-name list blocks (codes): German 1-18, Turkish 19-34, former-Soviet list 35-54
d[, fnblock := cut(fncode, c(0, 18, 34, 54), labels = c("de", "tr", "su"))]
d[, bgblock := c("tr", "tr", "tr", "su", "su", "su", NA, NA, NA, "de", "de", "de")[bgcode]]
message("profiles whose first-name block differs from background: ", d[fnblock != bgblock, .N], " of ", nrow(d))
d[, c("bgcode", "fncode", "fnblock", "bgblock") := NULL]
stopifnot(all(s$V640 %in% 1:2))
cv <- data.table(id = seq_len(n), trial_group = lab("V50"), trial_block_order = lab("V51"),
                 cov_gender = c("male", "female")[as.integer(s$V640)], cov_birth_year = as.integer(s$V650),
                 cov_education_code = as.integer(s$V680), cov_parent_born = lab("V50041"), cov_region = lab("V660"),
                 cov_duration_sec = as.integer(s$INTTIME))
stopifnot(cv[, all(cov_birth_year %between% c(1900L, 2005L))])
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating_represents", "rating_trust", "rating_capable"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vanoosten_2024_politicians_de.csv"))
