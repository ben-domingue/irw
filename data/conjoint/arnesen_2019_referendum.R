##Perceived legitimacy of an EU-membership referendum result, single-profile text vignette in the
##Norwegian Citizen Panel, from
##Arnesen, S., Broderstad, T. S., Johannesson, M. P., & Linde, J. (2019). Conditional legitimacy: How
##turnout, majority size, and outcome affect perceptions of legitimacy in European Union membership
##referendums. European Union Politics, 20(2), 176-197. https://doi.org/10.1177/1465116518820163
##Replication data: Harvard Dataverse doi:10.7910/DVN/KOKLPH, CC0 1.0 (the compendium's own LICENSE
##file is MIT and covers its R package code, not the data). Files read:
##analysis/data/wiggle.csv (1,065 rows, one per respondent) and analysis/raw/wiggle_treatments.csv
##(144 design cells, for the displayed sentence). Also read as documentation: README.md,
##analysis/01_data.R, analysis/output/tbls/tbl_wording.txt, analysis/raw/docs/
##"Codebook NCP w07 - EN.pdf".
##Usage: Rscript arnesen_2019_referendum.R <raw dir> <output dir>
##  (<raw dir> holds wiggle.csv and wiggle_treatments.csv)
##
##LICENCE NOTE. The README states that the raw Norwegian Citizen Panel (NCP) wave 7 file cannot be
##shared openly under data-protection law, so the authors deposited a PREPARED analysis file instead.
##The CC0 1.0 licence and this table cover that prepared file; the raw panel file is not in the deposit
##and is not used here. Researchers obtain the raw NCP from Sikt (formerly NSD).
##
##Design: a factorial survey (single-profile conjoint, presentation = text). Each respondent read ONE
##sentence describing a hypothetical advisory referendum on Norwegian EU membership, assembled from
##three randomised attributes, and said whether the government must follow the result. One task, one
##profile. Codebook r7padpilot2_ran: "A vignette is randomly selected from a population of 145
##vignettes" - the deposited treatment table enumerates 144 cells, and 144 is what the data use.
##  attr_turnout  share of the population that voted: 35%, 47%, 53%, 85%
##  attr_majority share of the vote the winning side got: 51%, 55%, 70%
##  attr_outcome  which side won: "For EU Membership won", "Against EU Membership won"
##Each attribute also has the reserved `(not shown)`, which here means the clause was left out of the
##sentence altogether. For turnout and majority that is literal. For the outcome it needs stating: when
##the outcome is withheld the sentence names the winner only generically, as "den vinnende siden" ("the
##winning side"), which is the placeholder the sentence needs to state a majority share at all, not a
##disclosed level - so it is recorded as `(not shown)` rather than as displayed text. In the cell where
##all three are withheld the respondent saw no sentence at all (treat_text is empty for those 85 rows,
##and trial_vignette_no is NA there).
##Outcome: choice = post, 1 = Yes / 0 = No, with opt_out = yes. Codebook r7padpilot2 -
##  pre-question: "We are interested in examining what mandate the government needs to make important
##    choices on behalf of the people. Imagine a new debate regarding EU membership for Norway and that
##    an advisory referendum was held regarding the issue." [then the vignette sentence]
##  literal question: "In such a case the government must act according to the result of the referendum
##    even if the majority in the Storting disagree?" Values 1 = Yes (817), 2 = No (248).
##This is a yes/no on whether the single profile should be acted on, which the layout treats as a
##single-profile accept/reject `choice` with opt_out = yes (as for chilton_2020_fdi_reciprocity_*,
##"should the Chinese government prevent the proposed transaction?"), not a `rating`.
##The 38 respondents the codebook records as "No answer" (97) have no outcome and are absent from the
##prepared file, as are the 3,586 panellists not asked (the experiment ran on a random third, u=3).
##task / profile: one each by design, both recorded.
##Respondent id: rsp_id is the real NCP respondent id, kept, so it links the same people to
##arnesen_2019_candidate_choice and arnesen_2019_attitude_prediction (864 respondents in common with
##the former, which is NCP wave 6).
##Covariates, as the authors' prepared file labels them (01_data.R maps the NCP codes; where their
##mapping differs from the codebook's own categories it is said so):
##  cov_age_group    <- rsp_age. Despite its name this is NOT age in years: 01_data.R sets it from
##                      r7P5_1, which the codebook defines as age in SEVEN BANDS, and the column holds
##                      codes 1-7. Mapped here to the codebook's band text (18-25 ... "75 and above"),
##                      the same labels as arnesen_2019_candidate_choice, so the three NCP tables are
##                      comparable on age. The file's own rsp_age_cat is a DIFFERENT panel variable
##                      (r7P5_2, three bands: "18-29 years", "30-59 years", "60 and above"), relabelled
##                      by the authors as "18-29 yrs" etc. It is not carried: it is coarser, it is not
##                      nested in the seven bands, and a second age banding under a near-identical name
##                      invites misreading. Recover it from the raw NCP if needed.
##  cov_gender       <- rsp_gender (r7P1), mapped to IRW's female/male
##  cov_education    <- rsp_edu: "Lower or intermediate" / "Higher". The authors COLLAPSE the
##                      codebook's three r7P4_1 categories, merging "No education/elementary school"
##                      and "Upper secondary eduction" into the first; the three-way split is not
##                      recoverable from the prepared file.
##  cov_vote_intent  <- rsp_party (r7k204), the authors' labels VERBATIM, including their bloc letters
##                      in parentheses and their typo "Christian Democracts (C)". This is VOTE CHOICE
##                      ("Which party would you vote for if there were a parliamentary election
##                      tomorrow?"), so deliberately not cov_party_id, which the standard reserves for
##                      party identification.
##  cov_eu_position  <- rsp_eu (r7padpilot1), the respondent's own position before the vignette: "For
##                      EU Membership", "Against EU Membership", "Don't know" (kept as answer text, per
##                      the rule that "don't know" is an answer and only refusals are NA).
##trial_vignette_id (treat_id, the design cell 1-144) and trial_vignette_no (treat_text, the sentence
##as displayed, in Norwegian) are kept so a user can recover exactly what was read.
##Dropped as derived: treat_outcome_match (favourable/unfavourable, built from cov_eu_position crossed
##with the outcome), treat_outcome_shown / treat_turnout_shown / treat_majority_shown (indicators of
##whether each clause appeared, recoverable from the attr_ columns), and treat_*_raw (the pre-label
##strings behind the three attributes).
##Language: the vignette and the question were in Norwegian. The sentence is kept verbatim in
##trial_vignette_no; the attribute LEVELS are the authors' English labels (the percentages are
##language-neutral, the outcome labels are translations of "ja-siden"/"nei-siden"). So
##display_language = no, label_language = en.
##Restrictions and level frequencies - READ THIS BEFORE ESTIMATING. The design is the full crossing of
##the three attributes plus each one's withheld state: 5 turnout x 4 majority x 3 outcome = 60 cells,
##and all 60 appear in wiggle_treatments.csv. But the deposit enumerates those 60 cells as 144
##`treat_id` lottery tickets, UNEVENLY: 36 cells hold one ticket, 12 hold three, 9 hold four, and the
##three cells with both turnout and majority withheld hold TWELVE each. The codebook draws uniformly
##over the 144 tickets (r7padpilot2_ran, range 1-144; all 144 are observed here), so the withheld
##states are over-sampled by construction, not by chance: attr_turnout is "(not shown)" in 531 of
##1,065 rows (50%) against 125-141 for each disclosed level, and attr_majority in 504 (47%) against
##180-195. Level frequencies are therefore recorded as `observed` rather than `uniform`, and anything
##that treats the levels as equiprobable will be wrong.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "wiggle.csv"), encoding = "UTF-8", na.strings = c("NA", ""))
tr <- fread(file.path(raw, "wiggle_treatments.csv"), encoding = "UTF-8", na.strings = c("NA", ""))
stopifnot(nrow(d) == 1065, uniqueN(d$rsp_id) == 1065, nrow(tr) == 144,
          all(d$post %in% c(0, 1)), sum(d$post) == 817)
##The three attributes carry the authors' "Not shown" string; map it to the reserved value.
ns <- function(x) { v <- ifelse(x == "Not shown", "(not shown)", as.character(x))
                    stopifnot(!is.na(v)); v }
##rsp_age is r7P5_1, age in seven bands (codes 1-7), not years: see the header.
AGE <- c("1" = "18-25", "2" = "26-35", "3" = "36-45", "4" = "46-55", "5" = "56-65",
         "6" = "66-75", "7" = "75 and above")
stopifnot(all(as.character(d$rsp_age) %in% c(names(AGE), NA)))
t <- d[, .(id = as.integer(rsp_id), task = 1L, profile = 1L, choice = as.integer(post),
           attr_turnout = ns(treat_turnout), attr_majority = ns(treat_majority),
           attr_outcome = ns(treat_outcome),
           trial_vignette_id = as.integer(treat_id),
           trial_vignette_no = ifelse(treat_text == "", NA_character_, treat_text),
           cov_age_group = unname(AGE[as.character(rsp_age)]),
           cov_gender = tolower(rsp_gender), cov_education = rsp_edu,
           cov_vote_intent = rsp_party, cov_eu_position = rsp_eu)]
ac <- grep("^attr_", names(t), value = TRUE)
stopifnot(!anyNA(t[, ..ac]), !any(t[, ..ac] == ""), !anyNA(t$choice),
          all(t$cov_gender %in% c("female", "male", NA)),
          t[, .N, .(id, task)][, all(N == 1)])
setorder(t, id, task, profile)
fwrite(t, file.path(out, "arnesen_2019_referendum_mandate.csv"))
