##Eye-tracking candidate conjoint (Duke lab, US) from
##Jenke, L., Bansak, K., Hainmueller, J., & Hangartner, D. (2021). Using eye-tracking to
##understand decision-making in conjoint experiments. Political Analysis, 29(1), 75-101.
##https://doi.org/10.1017/pan.2020.11 (CC BY 4.0 article)
##Replication data: Harvard Dataverse doi:10.7910/DVN/TISLDL, CC0 1.0, no restricted files,
##no terms. File read: replication_materials.zip -> replication_materials/data/individual/
##ind_<subjid>.csv (122 files, one row per eye fixation, trial and respondent variables repeated
##on every row) and data/variable_codebook_individual.rtf (value labels). The authors' processing
##code (1_process_individual_data.R, helper_functions/preprocess_conj_data.R) read as text.
##Not built: data/bansaketal2019_replication_data (re-host of Bansak et al. 2019, already in IRW
##as bansak_2019_satisficing_*), the fixation-level eye-tracking measures.
##Usage: Rscript jenke_2021.R <dir holding the ind_*.csv files> <output dir>
##
##122 subjects (Duke Behavioral Research pool, 5-31 July 2019; article section 3.3), six blocks
##of 20 decision tasks (120 tasks), block order random per subject. Each block has 5, 8 or 11
##attributes and 2 or 3 candidate profiles side by side in a conjoint table (Figure 1); the
##attributes of a block are drawn at random from 11, with party and gender always included, and
##their row order is random per subject-block and fixed within the block (article 3.1).
##choice: instructions "Your task is to decide which of the candidates you would vote for, for
##  President, if you had to cast a vote. If you prefer candidate 1, the leftmost candidate,
##  press the '1' key ... The candidates are always numbered from left to right." (three-candidate
##  wording; "appropriately modified" for two). candpref 1-3; no opt-out.
##task = trialnums (1-120, recorded, in the order shown); profile = candidate number = position
##  from the left (article). trial_block = the design ("5atts2cands" etc.), trial_block_iter =
##  the block's position in the subject's sequence (1-6).
##attr_ text: codebook value labels, which match the Figure 1 screenshot ("Weakly support",
##  "Served in the Air Force", "No prior political experience"); article Table 1 gives "Support/
##  Oppose" and age 37 where the codebook has "Weakly support/oppose" and age 36 (codebook kept).
##  Attributes the block did not show are "(not shown)": the individual files carry values for
##  all 11 attributes on every trial, and the shown set and row order come from the `order`
##  variable (first 66 rows of each file: 11 slots per block in block_iter order, 0 = empty
##  slot). Checked: every block has exactly numatts nonzero slots including party (2) and gender
##  (6), and the not-shown set equals the authors' NA pattern in pooled_processed/
##  resp-trial_conj.csv for every trial both files hold.
##attrpos_<attr>: row of the attribute in the table (1 = top), NA when not shown.
##Trials: the individual files hold 14,616 trials (110 subjects with all 120, 12 with 115-119;
##  the missing trials are absent from the source). The authors' pooled conjoint file has 14,605:
##  it drops 11 trials with no valid fixation; those are kept here and flagged
##  trial_fixation_data = 0 (1 elsewhere).
##Randomization: level weights NONUNIFORM: "for some attributes - including race, military
##  service, and religion - weights were adjusted to give a higher probability to more common
##  groups" (article; probabilities in Appendix A, not read). No combination restrictions stated.
##Covariates (codebook mappings): cov_birth_year (born), cov_gender (1 Male, 2 Female, 3 Other),
##  cov_education, cov_income, cov_race, cov_party_id (pid: Democrat / Republican / Independent /
##  Other party), cov_party_lean (pid_indp), cov_party_strength (dem_str / rep_str: Strong / Not
##  very strong), cov_ideology, cov_ideology_economic, cov_ideology_social (7-point answer text),
##  cov_political_interest, cov_political_understanding, cov_student_status (student),
##  cov_ssmar_position, cov_tax_position, cov_gun_position (0-100, 100 = strongly support),
##  cov_know_speaker, cov_know_senate_term, cov_know_roberts (answer text; -99 -> NA).
##Dropped: fixation-level variables (et_rois), order/orderall (turned into attrpos_ and
##  trial_block_iter).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fs <- list.files(raw, pattern = "^ind_[0-9]+\\.csv$", full.names = TRUE)
stopifnot(length(fs) == 122)
an <- c("age", "party", "race", "occupation", "military", "gender", "same_sex_marriage", "tax_wealthy",
        "gun_control", "political_experience", "religion")
src <- c("age", "party", "race", "prof", "military", "gender", "ssmar", "taxes", "guns", "polex", "relig")
pos4 <- c("Strongly support", "Weakly support", "Weakly oppose", "Strongly oppose")
lev <- list(age = c("36", "45", "53", "61", "77"), party = c("Republican", "Democrat", "Independent"),
            race = c("White", "Hispanic/Latino", "Black", "Asian American", "Native American"),
            prof = c("Business executive", "College professor", "Lawyer", "Doctor", "Activist"),
            military = c("Did not serve", "Served in the Army", "Served in the Navy", "Served in the Marine Corps", "Served in the Air Force"),
            gender = c("Male", "Female"), ssmar = pos4, taxes = pos4, guns = pos4,
            polex = c("Mayor", "Governor", "U.S. Senator", "U.S. Representative", "No prior political experience"),
            relig = c("Catholic", "Evangelical Protestant", "Mainline Protestant", "Mormon", "Jewish"))
rows <- list(); resp <- list()
for (f in fs) {
  x <- fread(f)
  o <- x$order[1:66]; stopifnot(!anyNA(o))
  tr <- x[!duplicated(trialnums)]
  tr[, block_iter := (trialnums - 1L) %/% 20L + 1L]
  for (b in unique(tr$block_iter)) {
    sl <- o[(b - 1) * 11 + 1:11]; sh <- sl[sl != 0]
    tb <- tr[block_iter == b]
    stopifnot(uniqueN(tb$numatts) == 1, length(sh) == tb$numatts[1], all(c(2, 6) %in% sh), !anyDuplicated(sh))
    for (p in 1:3) {
      tp <- tb[numcand >= p]
      if (!nrow(tp)) next
      r <- tp[, .(subjid, task = trialnums, profile = p, choice = as.integer(candpref == p),
                  trial_block = paste0(numatts, "atts", numcand, "cands"), trial_block_iter = block_iter)]
      for (k in 1:11) {
        v <- lev[[src[k]]][tp[[paste0(src[k], p)]]]
        stopifnot(!anyNA(v))
        r[, (paste0("attr_", an[k])) := if (k %in% sh) v else "(not shown)"]
        r[, (paste0("attrpos_", an[k])) := if (k %in% sh) match(k, sh) else NA_integer_]
      }
      rows[[length(rows) + 1]] <- r
    }
  }
  resp[[length(resp) + 1]] <- x[1]
}
d <- rbindlist(rows)
stopifnot(d[, sum(choice), .(subjid, task)][, all(V1 == 1)], nrow(unique(d[, .(subjid, task)])) == 14616)
## check against the authors' processed file
pp <- file.path(dirname(raw), "pooled_processed", "resp-trial_conj.csv")
if (file.exists(pp)) {
  q <- fread(pp)
  qq <- rbindlist(lapply(1:3, function(p) q[numcand >= p, c(list(subjid = subjid, task = trialnums, profile = p),
                                                           lapply(setNames(src, an), function(s) is.na(get(paste0(s, p)))))]))
  m <- merge(qq, d, by = c("subjid", "task", "profile"))
  stopifnot(nrow(m) == nrow(qq))
  for (k in an) stopifnot(all(m[[paste0(k, ".x")]] == (m[[paste0("attr_", k)]] == "(not shown)")))
  d[, trial_fixation_data := as.integer(paste(subjid, task) %in% paste(q$subjid, q$trialnums))]
}
r <- rbindlist(resp, use.names = TRUE, fill = TRUE)
cb <- function(v, labs) { v[v %in% c(-99)] <- NA; labs[v] }
ideo <- c("Extremely liberal", "Liberal", "Slightly liberal", "Moderate; middle of the road", "Slightly conservative",
          "Conservative", "Extremely conservative")
cv <- r[, .(subjid, cov_birth_year = as.integer(born),
            cov_gender = cb(gender, c("male", "female", "other")),
            cov_education = cb(educ, c("Less than a high school degree or equivalent", "High school degree or equivalent",
                                       "Some college, but no degree", "2-year college degree / Associate's degree",
                                       "4-year college degree / Bachelor's degree", "Postgraduate degree (MA, MBA, MA, JD, PhD, etc)")),
            cov_income = cb(income, c("Less than $10,000", "$10,000 - $19,999", "$20,000 - $29,999", "$30,000 - $39,999",
                                      "$40,000 - $49,999", "$50,000 - $59,999", "$60,000 - $69,999", "$70,000 - $79,999",
                                      "$80,000 - $89,999", "$90,000 - $99,999", "$100,000 - $149,999", "More than $150,000")),
            cov_race = cb(race, c("White", "Black or African-American", "American Indian or Alaska Native", "Asian",
                                  "Native Hawaiian or Pacific Islander", "Hispanic", "Other")),
            cov_party_id = cb(pid, c("Democrat", "Republican", "Independent", "Other party")),
            cov_party_lean = cb(pid_indp, c("Closer to the Republicans", "Closer to the Democrats", "Neither")),
            cov_party_strength = cb(fcoalesce(as.integer(dem_str), as.integer(rep_str)), c("Strong", "Not very strong")),
            cov_ideology = cb(ideo, ideo), cov_ideology_economic = cb(ideo_econ, ideo),
            cov_ideology_social = cb(ideo_ideo_soc, ideo),
            cov_political_interest = cb(polint, c("very interested", "somewhat interested", "not very interested", "not interested at all")),
            cov_political_understanding = cb(polund, c("Agree strongly", "Agree somewhat", "Neither agree nor disagree",
                                                       "Disagree somewhat", "Disagree strongly")),
            cov_student_status = cb(student, c("Duke Undergraduate student", "Duke Graduate student", "Duke staff",
                                               "Durham community member", "Other")),
            cov_ssmar_position = as.integer(ssmarpos), cov_tax_position = as.integer(taxpos), cov_gun_position = as.integer(gunpos),
            cov_know_speaker = cb(polknow1, c("Nancy Pelosi", "Harry Reid", "Marco Rubio", "Paul Ryan", "Don't know")),
            cov_know_senate_term = cb(polknow2, c("2 years", "4 years", "6 years", "8 years", "Don't know")),
            cov_know_roberts = cb(polknow3, c("Chair of the Democratic National Committee", "Senate Majority Leader",
                                              "Chief Justice of the Supreme Court", "Chair of the Republican National Committee", "Don't know")))]
stopifnot(uniqueN(cv$subjid) == 122)
d <- merge(d, cv, by = "subjid")
d[, id := match(subjid, sort(unique(subjid)))][, subjid := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jenke_2021_eyetracking_candidates.csv"))
