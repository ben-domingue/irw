##Politician-vignette experiment, EMMAVID France, from
##van Oosten, S., et al. (2024). French Ethnic Minority and Muslim Attitudes, Voting, Identity and
##Discrimination (EMMAVID) - EMMAVID Data France [Data set]. Harvard Dataverse. Analysed in
##van Oosten, S. (2023). Who favor in-group politicians? In-group voting in France, Germany and the
##Netherlands and the challenges to the descriptive and substantive representation of Muslims.
##OSF Preprints. https://doi.org/10.31219/osf.io/rkejd
##Replication data: Harvard Dataverse doi:10.7910/DVN/ULQEAY, CC0 1.0, no restricted files.
##Files read: DataFR_EMMAVID_vanOosten_etal_2024.sav (SPSS original; read with foreign::read.spss as
##in the DE sibling), "Codebook - France - EMMAVID - Van Oosten et al 2024.pdf" (English questionnaire
##Part 3b, Table A1 name lists), and the authors' "Code - van Oosten 2023 - OSF - Who Favor In-Group
##Politicians.R" read as text (not run) for the variable-to-profile mapping (L280-325: V40_k/V10_k for
##profiles 3-8, V2001-V2006 statement codes, V359/V369/V389/V399/V419/V429 _1/_2/_3 ratings).
##Sibling of vanoosten_2024_politicians_nl (vanoosten_2024.R) and vanoosten_2024_politicians_de
##(vanoosten_2024_de.R): same design, separate fielding and language, one table per country.
##Usage: Rscript vanoosten_2024_fr.R <raw dir> <output dir>
##
##1,199 respondents of a French online panel (respondents with Turkish, North-African and Sub-Saharan
##African parents oversampled: V50041). Part 3b: three pairs of text vignettes (codebook: "Politician
##3 has a Turkish background and practices Islam. He says the tax rate for the rich must be higher");
##task = pair 1-3 (questionnaire profiles 3-4, 5-6, 7-8, in the order shown), profile = 1st / 2nd
##politician of the pair. Randomized per profile: background x religion (V40_k, 12 combinations),
##gender and first name (V10_k / V20_k, same code), surname (V30_k), policy statement (V2001-V2006,
##8 issues x 2 directions).
##attr_ text is FRENCH, as displayed (the .sav value labels are French; HTML entities &apos; decoded):
##from the V40 labels "est d'origine <X> et <Y>." -> attr_background = X (turque / nord-africaine /
##africaine subsaharienne / entièrement français) and attr_religion = Y (pratique l'Islam /
##pratique le christianisme / ne pratique aucune religion; the label capitalises "l'Islam" for
##Turkish and North-African profiles and writes "l'islam" otherwise, kept as stored);
##attr_gender = the V10 label, the pronoun (Il / Elle); attr_first_name / attr_surname = V20 / V30
##labels; attr_statement = the French statement for codes 1-16, from the .sav variable labels of
##V7101-V7116 (same order as the DE/NL siblings and the authors' list).
##Outcomes (codebook Part 3b, English; respondents saw French; 11-point scales 0-10):
##  rating_represents "Do you think this politician represents you?" (V359_1, V369_1, ... _1; No-Yes)
##  rating_trust      "How much do you trust this politician?" (_2; not at all - very much)
##  rating_capable    "How capable do you think this politician is to perform well on the job?" (_3)
##     each stored RAW as the .sav code 1-11 (code = displayed number + 1; .sav labels "1 = 0 - Pas
##     du tout" ... "11 = 10 Oui, tout à fait" on all three, i.e. the represents anchors reused;
##     higher = more favourable), as in the siblings.
##  choice            "Which politician are you most likely to vote for?" (V380/V410/V440: 1 = first,
##                    2 = second politician of the pair; forced choice, no opt-out; every pair answered).
##trial_group = V50 ("Group 1" / "Group 2 (Control group)", not explained in the codebook);
##trial_block_order = V51 (statements first vs profiles first; the label text is Dutch).
##Names: the check below counts profiles whose first-name code lies outside its background's block
##(codes 1-18 French, 19-34 Turkish, 35-54 North-African, 55-80 Sub-Saharan; codebook Table A1 lumps
##Turkish and North-African names under "French North-African"): 182 of the 1,433 Turkish-background
##profiles carry a North-African first name (e.g. Mohammed, Fatima); all other profiles match. Kept
##as stored (consistent with Table A1's lumped list). Surnames are not checked (lists overlap).
##Level weights are unequal: background "africaine subsaharienne" is 2,968 of 7,194 profiles (V40
##codes 7-9 drawn about twice as often as each other background), the others 1,362-1,433.
##Dropped: Part 3a (profiles 1-2, a different design); free-text "why" answers and comments; INTNR
##(panel interview number; id = row order 1..1199); V41/V42 programme helper strings; other blocks.
##No survey weight is deposited (the authors' code builds w8eth; not in the deposit).
##Covariates: cov_gender (V640: Un homme = male, Une femme = female), cov_birth_year (V650 "Age":
##values 1910-2001 are years of birth; the authors compute age as 2020 - V650), cov_education_code
##(V680: the .sav labels 11 French options but the data hold only 1-9 plus 186 missing, and the
##authors scale 1-9 linearly, so the label mapping is not trusted and codes are kept), cov_parent_born
##(V50041 label, French), cov_region (V660 label), cov_duration_sec (INTTIME, seconds).
##N: 1,199 in the deposit; the OSF preprint pools FR/DE/NL and was not checked for the FR count.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- suppressWarnings(foreign::read.spss(file.path(raw, "DataFR_EMMAVID_vanOosten_etal_2024.sav"), to.data.frame = FALSE,
                                         use.value.labels = FALSE, reencode = "UTF-8"))
ent <- function(x) trimws(gsub("&apos;", "'", gsub("&lt;", "<", gsub("&gt;", ">", x, fixed = TRUE), fixed = TRUE), fixed = TRUE))
vlab <- attr(s, "variable.labels")
lab <- function(v) { x <- s[[v]]; l <- attr(x, "value.labels"); out <- names(l)[match(x, l)]; stopifnot(all(is.na(x) | !is.na(out))); ent(out) }
stmt <- ent(unname(vlab[sprintf("V71%02d", 1:16)]))
stopifnot(startsWith(stmt[1], "Le taux d'imposition des riches doit être plus élevé"), startsWith(stmt[16], "Les couples homosexuels devraient être autorisés"))
rq <- c("V359", "V369", "V389", "V399", "V419", "V429"); cq <- c("V380", "V410", "V440")
n <- length(s$INTNR); stopifnot(n == 1199, !anyDuplicated(s$INTNR)); rows <- list()
for (j in 1:6) {
  k <- j + 2L; t <- (j + 1L) %/% 2L; p <- 2L - j %% 2L
  bg <- lab(paste0("V40_", k)); g <- lab(paste0("V10_", k))
  stopifnot(!anyNA(bg), all(g %in% c("Il", "Elle")), all(s[[paste0("V10_", k)]] == s[[paste0("V20_", k)]]))
  m <- regmatches(bg, regexec("^est d'origine (.*) et (.*)\\.$", bg))
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
stopifnot(!anyNA(d$attr_surname), !anyNA(d$attr_first_name), d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[, uniqueN(attr_background)] == 4, d[, uniqueN(tolower(attr_religion))] == 3)
d[, fnblock := cut(fncode, c(0, 18, 34, 54, 80), labels = c("fr", "tr", "na", "ss"))]
d[, bgblock := rep(c("tr", "na", "ss", "fr"), each = 3)[bgcode]]
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
fwrite(d, file.path(out, "vanoosten_2024_politicians_fr.csv"))
