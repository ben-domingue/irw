##Ethnic-minority candidate conjoint (British Election Study Internet Panel, wave 11) from
##Martin, N. S., & Blinder, S. (2021). Biases at the ballot box: How multiple forms of voter
##discrimination impede the descriptive and substantive representation of ethnic minority groups.
##Political Behavior, 43(4), 1487-1510. https://doi.org/10.1007/s11109-020-09596-4
##Replication data: Harvard Dataverse doi:10.7910/DVN/SUDLEG, CC0 1.0, no restricted files.
##File read: replicationdata.tab ("original format" Stata 14 download, saved as data.dta; 15,806
##rows, one per profile; value labels = the authors' short level names). Read as text:
##replication code.do and the article (Springer HTML via the Internet Archive; vignette template,
##"Study Design" section and notes).
##Usage: Rscript martin_2021_minority.R <raw dir> <output dir>
##
##7,903 BESIP wave 11 respondents (YouGov online panel, Great Britain, 24 April-3 May 2017; a
##random subsample of the wave), ONE task of two candidate vignettes shown on the same page
##(presentation = text). Template (article): "[Name] is a candidate in your area from the
##[Conservative party/Labour party], who comes from a [white British/Pakistani/black Caribbean]
##background. [He/She] is in favour of [letting skilled migrants enter the country to fill jobs in
##sectors with skill shortages/accepting more refugees who are fleeing war or persecution/strongly
##limiting migration to the UK]. [He/She] thinks that [race equality laws/laws against anti-social
##behaviour] should be more strictly enforced, with greater penalties for those found guilty of
##[harassment and discrimination/disturbing the public order]. [Name] became a candidate after
##[being included on a list of candidates from under-represented backgrounds/getting involved in the
##political party]." The law-enforcement brackets are one variable (article note).
##attr_ text = the bracketed text for each value-label code (party, ethnicity, immigration, law
##enforcement as the full clause from "race equality laws"/"laws against anti-social behaviour" to
##the end of the sentence, route into politics), mapped from the .dta value labels (gender 1 Male
##2 Female; ethnic 1 white British 2 Pakistani 3 black Caribbean; immigPolicy 1 Skilled
##immigration 2 Refugees 3 Strictly limited; equality 1 Anti-social behaviour 2 Race equality laws;
##list 1 Getting involved 2 List of underrepresented candidates; party 1 Conservatives 2 Labour).
##attr_gender = the pronoun shown, "He"/"She". The first name (not saved) followed from ethnicity x
##gender (Oliver/Emily, Omar/Fatima, Joshua/Gabrielle; an alternate name when both candidates
##shared ethnicity and gender; article) and is not stored.
##The file has NO respondent or task column: rows come in consecutive pairs, one pair per
##respondent (all respondent covariates agree within each pair and no two neighbouring pairs agree;
##in the forced-choice arm exactly one profile per pair is chosen), so id = pair number, task = 1
##and profile = position in the pair (INFERRED from row order; which was shown first is not
##documented). 7,903 respondents / 15,806 rows, as in the article.
##Outcome: choice = select, "Which of these candidates would you rather have as your MP?" The answer
##options were randomized ("the 'Neither' experiment"): trial_neither_offered = 1 when an explicit
##"neither" option was shown (3,960 respondents, 1,603 of whom chose neither: choice = 0 on both
##profiles), 0 for a forced choice (3,943). OPT-OUT only in that arm.
##Covariates (BESIP items, value-label text): cov_ethnicity (respondent ethnicity), cov_religion,
##cov_religion_denomination, cov_vote_intention (general election vote intention), cov_ft_asian,
##cov_ft_black (0-100 feeling thermometers), cov_immig_enriches_culture (1 undermines - 7 enriches,
##raw). Label text is Windows-1252 in the .dta (en dashes) and is converted to UTF-8. "Prefer not to say", "Skipped", "Not Asked" -> NA. Dropped: the authors' derived scales
##and recodes (mcp, missingness, socialDesScale, *_m imputed scales, ethnicity_small).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "data.dta"))
x <- as.data.table(zap_labels(k))
stopifnot(nrow(x) == 15806)
x[, id := (seq_len(.N) + 1L) %/% 2L][, profile := 2L - seq_len(.N) %% 2L]
cv <- c("warmAsian", "warmBlack", "profile_ethnicity", "profile_religion", "profile_religion_denom", "mcp", "missingness", "immenrichcult", "vi", "neither")
same <- x[, lapply(.SD, function(v) uniqueN(v) == 1), id, .SDcols = cv]
stopifnot(all(as.matrix(same[, -1])))
stopifnot(x[neither == 0, sum(select), id][, all(V1 == 1)], x[neither == 1, sum(select), id][, all(V1 <= 1)])
chk <- function(v, lv) { l <- attr(k[[v]], "labels"); stopifnot(all(unname(l) == seq_along(lv)), length(l) == length(lv), identical(names(l), lv)) }
chk("gender", c("Male", "Female")); chk("ethnic", c("white British", "Pakistani", "black Caribbean"))
chk("immigPolicy", c("Skilled immigration", "Refugees", "Strictly limited")); chk("equality", c("Anti-social behaviour", "Race equality laws"))
chk("list", c("Getting involved", "List of underrepresented candidates")); chk("party", c("Conservatives", "Labour"))
na_t <- function(v) { s <- iconv(as.character(as_factor(k[[v]], levels = "labels")), "CP1252", "UTF-8"); s[s %in% c("Prefer not to say", "Skipped", "Not Asked")] <- NA; s }
d <- x[, .(id, task = 1L, profile, choice = as.integer(select),
           attr_party = c("Conservative party", "Labour party")[party],
           attr_ethnicity = c("white British", "Pakistani", "black Caribbean")[ethnic],
           attr_gender = c("He", "She")[gender],
           attr_immigration = c("letting skilled migrants enter the country to fill jobs in sectors with skill shortages",
                                "accepting more refugees who are fleeing war or persecution",
                                "strongly limiting migration to the UK")[immigPolicy],
           attr_law_enforcement = c("laws against anti-social behaviour should be more strictly enforced, with greater penalties for those found guilty of disturbing the public order",
                                    "race equality laws should be more strictly enforced, with greater penalties for those found guilty of harassment and discrimination")[equality],
           attr_route = c("getting involved in the political party", "being included on a list of candidates from under-represented backgrounds")[list],
           trial_neither_offered = as.integer(neither))]
d[, `:=`(cov_ethnicity = na_t("profile_ethnicity"), cov_religion = na_t("profile_religion"),
         cov_religion_denomination = na_t("profile_religion_denom"), cov_vote_intention = na_t("vi"),
         cov_ft_asian = as.numeric(x$warmAsian), cov_ft_black = as.numeric(x$warmBlack),
         cov_immig_enriches_culture = fifelse(x$immenrichcult == 9999, NA_real_, as.numeric(x$immenrichcult)))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), uniqueN(d$id) == 7903)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "martin_2021_minority_candidates.csv"))
