##Syrian-refugee conjoint (Turkey) from
##Getmansky, A., Matakos, K., & Sinmazdemir, T. (2024). Diversity without adversity? Ethnic
##bias toward refugees in a co-religious society. International Studies Quarterly, 68(2),
##sqae031. https://doi.org/10.1093/isq/sqae031
##Replication data: Harvard Dataverse doi:10.7910/DVN/NUMV0I, CC0 1.0, no restricted files.
##File read: ProfileDataset.csv (Dataverse "original format" download of ProfileDataset.tab).
##Level text and question wording are from the authors' pre-analysis plan (OSF z6cjh,
##20181108AA_PAP_anon_20200714.docx, English survey instrument); design facts from the
##article's online appendix. The deposit itself has no codebook.
##Usage: Rscript getmansky_2024.R <raw dir> <output dir>
##
##2,362 respondents from an online panel in Turkey (Benderimki/IPSOS, fielded after the 2018-11-08 pre-registration; 22
##provinces with oversampling of refugee-hosting provinces). Each saw 3 pairs (task 1-3) of
##Syrian-refugee profiles (A = profile 1, B = profile 2) with 9 attributes. For each of three
##outcomes the respondent rated both profiles of a pair 1-7 and then chose one of the two;
##outcome blocks came one after another over the same three pairs, block order randomized
##(trial_outcome_order = the source's sys_block_set_1, e.g. "2,1,3"; the deposit does not
##say which number is which block). Attribute row order was randomized per respondent (fixed
##across that respondent's pairs) but is not in the data.
##ONE TABLE, getmansky_2024_refugees, with the three outcomes as named columns
##(choice_/rating_ + neighbor, work_permit, citizenship):
##  neighbor: "...where 1 indicates that you definitely don't want the refugee to be your
##     neighbor, and 7 indicates that you definitely want the refugee to be your neighbor, how
##     would you rate each of the refugee profiles described above?" and "Now, imagine if you
##     had to choose between these two people, which one of these two people would you want
##     to be your neighbor? Even if you aren't entirely sure, please indicate which of the two
##     you prefer."
##  work_permit: same, "...to be given a work permit" / "which ... should be given a work
##     permit?"
##  citizenship: same, "...to be granted Turkish citizenship" / "which ... should be granted
##     Turkish citizenship?"
##rating 1 = definitely don't want .. 7 = definitely want; choice forced, no opt-out. About
##2-3% of pairs have a choice that contradicts the ratings (the authors' logical_* flags,
##appendix G.3); kept as answered.
##Task and profile come from ROW ORDER: rows are sorted by respondent and profileid, 6 per
##respondent; rows 1-2, 3-4, 5-6 are pairs 1-3 (verified: every pair has exactly one chosen
##profile on each outcome, and the deposit's ProfileDataset_task1 holds exactly rows 1-2 of
##every respondent). Which row of a pair was "Profile A" is assumed from order.
##Attributes (source codes -> instrument text; reconstructed from the authors' dummies,
##which agree 100%): gender Male/Female; age 18-30/31-50/Over 50; ethnicity Turcoman/Kurd/
##Arab; religion Sunni/Alawite/Christian; education "Literate but not graduated from primary
##school"/Primary school/Middle school/High school/"Graduated from university in Syria";
##Turkish friends; language; civil war "Was not involved in the war himself/herself"/"Fought
##in the civil war with Free Syrian Army forces before coming to Turkey"/"Fought in the civil
##war with pro-Assad forces before coming to Turkey"; torture. Respondents saw Turkish text.
##Covariates (codes per the instrument; only those whose coding could be confirmed):
##  cov_female 0/1; cov_age years; cov_province Turkish plate code (34 = Istanbul);
##  cov_party June 2018 vote 1=AKP 2=CHP 3=MHP 4=HDP 5=Iyi Parti 6=other 7=didn't vote 8=no
##  answer; cov_religion 1=none 2=Muslim 3=Christian 4=Jewish 5=other; cov_pray (Muslims)
##  1=no 2=only during Ramadan 3=every Friday 4=5 times a day; cov_proud_turkish 1=very
##  proud..4=not at all proud 5=I am not Turkish; cov_identity_* ("I see myself as part of
##  the Muslim community / the Turkish nation / my local community / a world citizen / an
##  autonomous individual") 1=strongly disagree..5=strongly agree; cov_syrians_estimate
##  (refugees in Turkey) 1=<100,000 2=~250,000 3=~1,000,000 4=~3,500,000 5=~10,000,000;
##  cov_contact_* 0/1 (had conversations / shopped / has Syrian friends / dated / argument /
##  saw them walking in groups / was cheated); cov_knows_<language> 0/1; cov_mother_born_
##  turkey, cov_father_born_turkey, cov_lived_refugee_province (lived in one of the 10 main
##  host provinces in the last 7 years), cov_has_kids, cov_owns_<item> 0/1; cov_home 1=owner
##  2=tenant 3=subsidized 4=no rent.
##Dropped: education, employment, occupation, socio-economic status, household-earner block,
##income, hair covering, dishwasher (their codes do not match the pre-registered instrument
##and no codebook is deposited); mother-tongue items (asked only of speakers); the authors'
##derived variables (dummies, 0-1 rescaled ratings, binary-ness flags, akp_supporter,
##religion2/education2/ethnicity composites, scale differences, testdifference) and the
##design `version` column. No survey weight is deposited.
##N = 2,362 matches the article. Spot check: OLS of the 0-1 rescaled neighbor rating on the
##attribute dummies reproduces appendix Table B.1 col. 1 (Arab -0.065, Kurd -0.069).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "ProfileDataset.csv"))
stopifnot(all(diff(s$profileid) > 0), s[, .N, idnumbernew][, all(N == 6)])
s[, r := seq_len(.N), idnumbernew]
d <- data.table(id = as.integer(s$idnumbernew), task = (s$r + 1L) %/% 2L, profile = 2L - s$r %% 2L)
lv <- function(x, l) { stopifnot(all(x %in% seq_along(l))); l[x] }
d[, `:=`(attr_gender = ifelse(s$female == 1, "Female", "Male"),
         attr_age = lv(s$age, c("18-30", "31-50", "Over 50")),
         attr_ethnicity = lv(s$ethnicity, c("Turcoman", "Kurd", "Arab")),
         attr_religion = lv(s$religion, c("Sunni", "Alawite", "Christian")),
         attr_education = lv(s$education, c("Literate but not graduated from primary school", "Primary school", "Middle school",
                                            "High school", "Graduated from university in Syria")),
         attr_turkish_friends = ifelse(s$turkishfriends == 1, "Has Turkish friends", "Doesn't have Turkish friends"),
         attr_language = ifelse(s$knowsturkish == 1, "Speaks Turkish", "Doesn't speak Turkish"),
         attr_civil_war = lv(s$fighter, c("Was not involved in the war himself/herself",
                                          "Fought in the civil war with Free Syrian Army forces before coming to Turkey",
                                          "Fought in the civil war with pro-Assad forces before coming to Turkey")),
         attr_torture = ifelse(s$tortured == 1, "Was tortured during the civil war", "Was not tortured during the civil war"))]
# the codes agree with the authors' dummies
stopifnot(s[, all((arab == 1) == (ethnicity == 3) & (kurd == 1) == (ethnicity == 2) & (young == 1) == (age == 1) & (old == 1) == (age == 3) &
                  (alawite == 1) == (religion == 2) & (christian == 1) == (religion == 3) & (university == 1) == (education == 5) &
                  (primary == 1) == (education == 2) & (foughtwithfsa == 1) == (fighter == 2) & (foughtwithasad == 1) == (fighter == 3))])
d[, trial_outcome_order := s$sys_block_set_1]
cmap <- c(respondent_female = "female", respondent_age = "age", QIL = "province", D17 = "party", respondent_religion = "religion",
          pray = "pray", proud_turkish = "proud_turkish", mem_muslim_community = "identity_muslim_community",
          mem_turkish_nation = "identity_turkish_nation", mem_local_community = "identity_local_community",
          world_citizen = "identity_world_citizen", auto_individual = "identity_autonomous_individual",
          howmany_syrians = "syrians_estimate", conversations = "contact_conversations", shopped = "contact_shopped",
          friends = "contact_friends", dated = "contact_dated", argument = "contact_argument", walkingroups = "contact_saw_in_groups",
          cheated = "contact_cheated", motherborninturkey = "mother_born_turkey", fatherborninturkey = "father_born_turkey",
          livedinrefprovince = "lived_refugee_province", havekids = "has_kids", landline = "owns_landline", washer = "owns_washer",
          creditcard = "owns_creditcard", plasmatv = "owns_flatscreen_tv", internet = "owns_internet", homestatus = "home")
for (v in names(cmap)) d[, paste0("cov_", cmap[[v]]) := s[[v]]]
for (l in c("kurd", "arab", "bulgarian", "macedonian", "bosnian", "laz", "circassian", "georgian", "armenian", "greek", "albanian"))
  d[, paste0("cov_knows_", l) := s[[paste0("respondent_", l, "_lang")]]]
outs <- list(neighbor = c("neighborscale", "neighborbinary"), work_permit = c("workpermitscale", "workpermitbinary"),
             citizenship = c("citizenshipscale", "citizenshipbinary"))
for (o in names(outs)) {
  d[, paste0("choice_", o) := as.integer(s[[outs[[o]][2]]])][, paste0("rating_", o) := as.integer(s[[outs[[o]][1]]])]
  stopifnot(d[, sum(get(paste0("choice_", o))), .(id, task)][, all(V1 == 1)], all(d[[paste0("rating_", o)]] %in% 1:7))
}
setcolorder(d, c("id", "task", "profile", paste0(rep(c("choice_", "rating_"), 3), rep(names(outs), each = 2))))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "getmansky_2024_refugees.csv"))
