##Party-platform conjoint experiments from
##Tomz, M., Weeks, J. L. P., & Yarhi-Milo, K. (2020). Public opinion and decisions about military force in
##democracies. International Organization, 74(1), 119-143. https://doi.org/10.1017/S0020818319000341
##Replication data: Harvard Dataverse doi:10.7910/DVN/AUNLOB, CC0 1.0. File read: TWY-IO.zip (unzipped), the
##three survey files USPublic/USPublic.dta, USPublic2/USPublic2.dta, IsraelPublic/IsraelPublic.dta and their
##.do files (read as text; recode and labelling source for the covariates and the 0-100 preference recode).
##No codebook ships; the question wordings below are NOT in the deposit (paraphrases).
##Usage: Rscript tomz_2019.R <dir holding the unzipped TWY-IO folders> <output dir>
##Writes three tables (different attribute sets, populations and fieldings):
##  tomz_2019_us_party_apr  US public, April-May 2017, N = 2,051, 7 attributes incl. leader's home region
##  tomz_2019_us_party_sep  US public, Sept-Oct 2017, N = 1,580, attributes incl. the party (Dem/Rep)
##  tomz_2019_israel_party  Israeli public, March 2016, N = 1,277, Hebrew, 7 attributes
##Design (all three): each respondent compared FOUR pairs of hypothetical political parties/candidates
##(tasks 1-4 = the source pairings AB, CD, EF, GH in that order; profile 1 = A, 2 = B) described by seven
##attributes in a table whose ROW ORDER was randomized once per respondent (r0-r6 hold the row names; the same
##order is shown for all four pairs; recorded as attrpos_<name> = row, 1 = top). Per-pair attention checks
##(did attribute k differ between the two?) are summarised by the authors as % correct (ck); cov_attention_pass
##= 1 if ck >= 85 (the authors' own exclusion threshold; their analyses drop everyone below, this table keeps
##everyone). No survey weight in the files.
##Outcomes (same tasks, one table; wording not in the deposit, paraphrased):
##  choice: which of the two is preferred, derived from the 4-point preference question (prefAB: 1 = definitely
##    A, 2 = probably A, 3 = probably B, 4 = definitely B): profile A chosen if 1-2, profile B if 3-4 (the
##    authors' binary pick_a, pref > 50 on their 0-100 recode). No opt-out; exactly one chosen per task.
##  rating_pref: the authors' 0-100 recode of that preference question for THIS profile (A: 1 -> 100, 2 -> 67,
##    3 -> 33, 4 -> 0; B: 1 -> 0, 2 -> 33, 3 -> 67, 4 -> 100); higher = more preferred. The two profiles of a
##    task sum to 100.
##  rating_party: the 0-10 rating of this party/candidate (stored raw, 0 .. 10; the authors multiply by 10);
##    anchors not in the deposit (higher assumed more favourable; not stated).
##Attribute text is the displayed text as stored in the files (r*/a*..h* string columns). Attribute names are
##English labels from the authors' do files. Israel: levels are the Hebrew display text (label_language he).
##Randomization restrictions: none documented. US-Sep: the two profiles of a pair always have different parties
##(one Democrat, one Republican; never equal in 6,320 + 6,320 observations), and economic policy and role of
##religion were HELD CONSTANT across all profiles (one level each: "More capitalist ... than socialist" and
##"Religion should play a small role ..."), so they are not attributes here and are dropped. Level weights:
##levels of policy, region, race, party and gender are near-equal (observed shares within ~3 points); years in
##politics (0-30) is ~uniform, 31 levels.
##Covariates (mapped from the authors' do files): cov_gender (US: gender 1 = male, 0 = female per "rename
##gender male // 1 = male"; Israel: gender 1 = male, 2 = female per recode gender 1=1 2=0), cov_age (age + 17,
##per the do files), cov_education (authors' ed4 label of the 6-category education item: US HS or Less / Some
##Coll / Coll Deg / Advanced; Israel HS or less / Some college / College degree / Advanced deg), cov_party_id
##(US: authors' pid3 from pid_1: 2 Dem, 3-5 Ind, 1 Rep; Israel: closest party, the authors' value labels).
##Dropped: ideal points, state/region of residence, income, race, activism, time stamps, attention-check
##answers (all non-conjoint survey items); IsraelMK (87 members of the Knesset, < 100 respondents, not built) and
##IsraelMK_Frame (a sampling frame, no responses) are not read.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(path, name, rows, extra, cov) {
  s <- as.data.table(read_dta(path))
  s[, rid := seq_len(.N)]
  stopifnot(uniqueN(s$id) == nrow(s))
  chk <- function(p, q) { # attention % on one pair
    tot <- 0
    for (i in 1:7) tot <- tot + ((s[[paste0("ck", p, q, "_", i)]] == 1 & s[[paste0(p, i - 1)]] == s[[paste0(q, i - 1)]]) |
                                  (s[[paste0("ck", p, q, "_", i)]] == 2 & s[[paste0(p, i - 1)]] != s[[paste0(q, i - 1)]]))
    tot }
  ck <- 100 * (chk("a", "b") + chk("c", "d") + chk("e", "f") + chk("g", "h")) / 28
  L <- list()
  prs <- list(c("a", "b", "ab", 1L), c("c", "d", "cd", 2L), c("e", "f", "ef", 3L), c("g", "h", "gh", 4L))
  for (pr in prs) for (k in 1:2) {
    p <- pr[k]; nm <- pr[3]; pref <- s[[paste0("pref", nm)]]
    rate <- s[[paste0("rate", p, "_1")]]
    lab <- vapply(0:6, function(i) as.character(s[[paste0("r", i)]]), character(nrow(s)))  # rid x 7 row names
    val <- vapply(0:6, function(i) as.character(s[[paste0(p, i)]]), character(nrow(s)))
    x <- data.table(id = s$rid, task = as.integer(pr[4]), profile = k,
      choice = as.integer(if (k == 1) pref <= 2 else pref >= 3),
      rating_pref = c(100, 67, 33, 0)[if (k == 1) pref else 5 - pref],
      rating_party = as.integer(rate))
    for (j in seq_along(rows)) {
      pos <- apply(lab, 1, function(z) match(rows[[j]], z))
      v <- val[cbind(seq_len(nrow(s)), pos)]
      x[[paste0("attr_", names(rows)[j])]] <- trimws(v)
      x[[paste0("attrpos_", names(rows)[j])]] <- pos
    }
    x$cov_attention_pass <- as.integer(ck >= 85)
    for (n in names(cov)) x[[n]] <- cov[[n]]
    L[[length(L) + 1]] <- x
  }
  d <- rbindlist(L); setorder(d, id, task, profile)
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, grep("^attr_|^attrpos_", names(d)), with = FALSE]),
            !anyNA(d[, .(rating_pref, rating_party, choice)]))
  fwrite(d, file.path(out, paste0(name, ".csv")))
  cat(name, uniqueN(d$id), nrow(d), "\n")
}
usrows <- list(economic_policy = "Economic policy", foreign_policy = "Foreign policy", religion_role = "Role of religion",
  political_experience = "Years in politics", gender = "Gender", race = "Race")
edus <- c("HS or Less", "Some Coll", "Coll Deg", "Advanced")
uscov <- function(s) list(cov_gender = c("female", "male")[s$gender + 1L], cov_age = as.integer(s$age) + 17L,
  cov_education = edus[c(1, 1, 2, 3, 3, 4)[s$educ]], cov_party_id = c("Rep", "Dem", "Ind", "Ind", "Ind")[s$pid_1])
s <- as.data.table(read_dta(file.path(raw, "USPublic/USPublic.dta")))
build(file.path(raw, "USPublic/USPublic.dta"), "tomz_2019_us_party_apr", c(usrows, list(home_region = "Home region")), NULL, uscov(s))
s <- as.data.table(read_dta(file.path(raw, "USPublic2/USPublic2.dta")))
build(file.path(raw, "USPublic2/USPublic2.dta"), "tomz_2019_us_party_sep",
      list(foreign_policy = "Foreign policy", political_experience = "Years in politics", gender = "Gender", race = "Race", party = "Party"),
      NULL, uscov(s))
s <- as.data.table(read_dta(file.path(raw, "IsraelPublic/IsraelPublic.dta")))
pn <- c("likud", "zionist", "jhome", "shas", "utj", "meretz", "ihome", "kulanu", "yeshatid", "arablist", "yachad")
u <- function(h) paste0("<u>", h, "</u>")
isr <- list(economic_policy = paste0(u("מדיניות כלכלית"), " של המיפלגה"), religious_policy = paste0(u("מדיניות דתית"), " של המיפלגה"),
  foreign_policy = paste0(u("מדיניות חוץ וביטחון"), " של המיפלגה"), military_experience = paste0(u("ניסיונו הצבאי"), " של ראש המפלגה"),
  gender = paste0(u("המגדר"), " של ראש המפלגה"), large_party = paste0("אחת מ-3 המפלגות ", u("הגדולות ביותר"), "?"),
  political_experience = paste0(u("ניסיון פוליטי"), " של ראש המפלגה"))
build(file.path(raw, "IsraelPublic/IsraelPublic.dta"), "tomz_2019_israel_party", isr, NULL,
  list(cov_gender = c("male", "female")[s$gender], cov_age = as.integer(s$age) + 17L,
       cov_education = c("HS or less", "HS or less", "Some college", "College degree", "Advanced deg", "Advanced deg")[s$educ],
       cov_party_id = pn[as.integer(s$closest) - 3L]))
