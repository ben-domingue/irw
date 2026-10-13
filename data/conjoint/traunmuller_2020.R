##Religion-and-origin vignette experiment (Britain, 2015) from
##Traunmueller, R., & Helbling, M. (2020). Backlash to policy decisions: how citizens react to
##immigrants' rights to demonstrate. Political Science Research and Methods, 10(2), 279-297.
##https://doi.org/10.1017/psrm.2020.44
##Replication data: Harvard Dataverse doi:10.7910/DVN/NHSJMJ, CC0 1.0, no restricted files, no terms.
##File read: replication_backlash_data.tab, in its Stata "original format" download (saved as data.dta;
##4,468 rows x 199 columns, value labels kept). The authors' replication_backlash_recode.R, master and
##READ ME were read as text only. The same 4,468 respondents, vignette assignments and outcomes are in
##doi:10.7910/DVN/L2OZPI (Helbling & Traunmueller 2020, "What is Islamophobia?", BJPolS,
##doi:10.1017/S0007123418000054; a 48-column subset); that deposit is not built separately.
##Usage: Rscript traunmuller_2020.R <raw dir> <output dir>   (raw dir holds data.dta)
##
##4,468 British panel respondents (wave 5 of an online welfare-attitudes panel, 2015; the file holds
##country GB only although the paper's deposit title mentions a UK/NL panel). Each read ONE vignette:
##a 3 x 3 x 2 x 2 factorial, one vignette per respondent, between-subject (cell sizes 229-265).
##The deposit holds only the experimental factor labels (variable labels "Reli - Exp manipulation:
##..." and value labels), not the vignette sentences, so the levels are those labels:
##  attr_group_origin   E861 rel_country: native Britons / immigrants from Nigeria / immigrants from Bulgaria
##  attr_religiosity    E862 rel_devotion: devout / non-practising / radical
##  attr_religion       E863: Christians / Muslims
##  attr_proposal       E864: "Authorities propose to ban" / "Authorities propose to permit" (the
##                      sentence that follows, i.e. what is banned or permitted, is not in the deposit; the
##                      paper's title names the right to demonstrate)
##Task = profile = 1, id = row number (respid, a panel-wide respondent identifier, is not kept).
##Outcomes (all about "this group", the group described in the vignette; item wording is paraphrased from
##the variable labels; "Don't know" and not-asked codes -> NA; values are kept as coded):
##  rating_support_ban     E865 "Would you support or oppose the ban": 1 strongly support the ban .. 5
##                         strongly oppose the ban (LOWER = more support); asked only when the proposal is a ban
##  rating_support_permit  E866 "Would you support or oppose the permit": 1 strongly support the permit .. 5
##                         strongly oppose the permit (LOWER = more support); asked only when the proposal
##                         is to permit
##  rating_feeling         E867 feelings thermometer towards the group, 0-100 (anchors not documented);
##                         skipped (998) -> NA (348 respondents)
##  rating_deserving       E868 "How deserving is an unemployed single mother from this group": 0 very
##                         undeserving of help from the government .. 10 very deserving; Don't know (97) -> NA
##  rating_allow_vote      E869 "Should members of this group be allowed to vote in national elections":
##                         1 agree strongly .. 5 disagree strongly (LOWER = more agreement)
##  rating_allow_office    E870 "... allowed to hold public office": same coding
##No opt-out (no choice outcome). Dropped: response dates (E001GB/E002GB), free text (E141GB, E143GB), the
##~150 other panel items (welfare, immigration, politics attitudes), the authors' derived dummies and
##scales, and the weights other than E005GB. Covariates: cov_gender (E730 male/female), cov_age (E731, years
##as recorded), cov_left_right (leftright, authors' recode of E130: 1 very left-wing .. 7 very right-wing, don't
##know -> NA), cov_party_id (E140GB "Generally speaking, do you think of yourself as ...", answer text;
##"don't know" kept as text, not-asked -> NA), cov_survey_weight (E005GB "Original weight W5 GB"; the
##authors' replication code does not use it), cov_ethn_brit_code (authors' recode of E909GB ethnicity,
##1 = the group the authors keep for analysis, 4,053 of 4,468; codes not labelled in the deposit).
##All respondents with at least one outcome are kept (4,356 of 4,468), including those the authors exclude
##(ethn_brit = 0, 415 of 4,468).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(x) == 4468, !anyDuplicated(x$respid), all(as.character(as_factor(x$country)) == "GB"))
chr <- function(v) as.character(as_factor(x[[v]]))
num <- function(v) as.integer(x[[v]])
chk <- function(v, lv) { y <- chr(v); stopifnot(all(y %in% lv)); y }
cl <- function(v, ok) { y <- num(v); y[!y %in% ok] <- NA; y }
ban <- chk("E864", c("Authorities propose to ban", "Authorities propose to permit"))
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L,
  rating_support_ban = cl("E865", 1:5), rating_support_permit = cl("E866", 1:5),
  rating_feeling = cl("E867", 0:100), rating_deserving = cl("E868", 0:10),
  rating_allow_vote = cl("E869", 1:5), rating_allow_office = cl("E870", 1:5),
  attr_group_origin = chk("E861", c("native Britons", "immigrants from Nigeria", "immigrants from Bulgaria")),
  attr_religiosity = chk("E862", c("devout", "non-practising", "radical")),
  attr_religion = chk("E863", c("Christians", "Muslims")),
  attr_proposal = ban)
stopifnot(d[attr_proposal == "Authorities propose to ban", all(is.na(rating_support_permit))],
          d[attr_proposal == "Authorities propose to permit", all(is.na(rating_support_ban))],
          chr("rel_country") == d$attr_group_origin, chr("rel_devotion") == d$attr_religiosity)
age <- num("E731"); age[age < 18 | age > 100] <- NA
lr <- num("leftright"); lr[!lr %in% 1:7] <- NA
party <- chr("E140GB"); party[party == "not asked"] <- NA
cv <- data.table(id = d$id, cov_gender = chk("E730", c("male", "female")), cov_age = age, cov_left_right = lr,
                 cov_party_id = party, cov_survey_weight = as.numeric(x$E005GB), cov_ethn_brit_code = num("ethn_brit"))
d <- d[!(is.na(rating_support_ban) & is.na(rating_support_permit) & is.na(rating_feeling) & is.na(rating_deserving) &
         is.na(rating_allow_vote) & is.na(rating_allow_office))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "traunmuller_2020_religion_vignette.csv"))
