##Economic-sanctions factorial vignette (US public, paper booklet) from
##McLean, E. V., & Roblyer, D. (2017). Public support for economic sanctions: An experimental
##analysis. Foreign Policy Analysis, 13(1), 233-254. https://doi.org/10.1093/fpa/orw014
##Replication data: Harvard Dataverse doi:10.7910/DVN/BSAARV, CC0 1.0. Files read: "dataset_FPA.tab"
##(Dataverse "original format" download = Stata dataset_FPA.dta, 158 rows, variable labels), the
##authors' "replication_dofile.do" and "research procedures.docx" (read as text, not run), which gives the
##vignette wording.
##Usage: Rscript mclean_2017.R <dir holding dataset_FPA.dta saved as data.dta> <output dir>
##
##158 participants (paper booklet, in person), each reading ONE vignette: a US president proposes
##sanctions against "Erqat" to stop uranium enrichment. 2 x 2 x 2 between-subject factorial (cells of 19-20):
##  attr_sanction_type: type = C "Comprehensive trade embargo" (broad sanctions, 12-month horizon, harm to
##    the lower classes) / T "Tailored sanctions" (targeted at elites, 24-36 month horizon);
##  attr_expected_effectiveness: effect = H "Highly effective" / M "Moderately effective" (expert assessment:
##    85% or 60% chance of success; the percentage is the same effect level in either frame);
##  attr_effectiveness_frame: frame = P "Positive frame (chance of success stated)" / N "Negative frame
##    (chance of failing stated)" (85% success vs 15% failing; 60% success vs 40% failing).
##The level text is the authors' condition names as described in the procedures document; the full
##paragraph shown also depends on the combination (e.g. the time horizon follows the sanction type).
##Presentation is text; profile = 1, task = 1 for every respondent, id = row number (no respondent id).
##Outcomes (procedures document; labels in the .dta):
##  choice = spt: "Should the U.S. impose the sanctions recommended by the President? (Yes / No)", 1 = yes.
##    A single-profile accept/reject, so opt_out = yes.
##  rating_success = q7 "How likely do you think the sanctions are to succeed?" 0-100.
##  rating_pain_public = q8 "How painful do you think the sanctions will be for the Erqatan public?" 1-10
##    (1 = Not Painful, 10 = Very Painful).   rating_pain_leaders = q9, same for the Erqatan leaders.
##Dropped: cond and ref (condition and row numbers), q4 (recall of the stated probability: a manipulation
##check). Missing: q7 1, q8 4, q9 4 (rows kept, NA). No respondent covariates in the deposit.
##Restrictions: none (balanced 2x2x2, condition counts 19-20); level_weights near-uniform.
##N check: the paper's sample size was not looked up; 158 = 8 cells of 19-20.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(r) == 158, all(r$type %in% c("C", "T")), all(r$effect %in% c("H", "M")), all(r$frame %in% c("P", "N")),
          all(r$spt %in% 0:1), uniqueN(r[, .(type, effect, frame)]) == 8)
d <- data.table(id = seq_len(nrow(r)), task = 1L, profile = 1L, choice = as.integer(r$spt),
                rating_success = as.integer(r$q7), rating_pain_public = as.integer(r$q8), rating_pain_leaders = as.integer(r$q9),
                attr_sanction_type = c(C = "Comprehensive trade embargo", T = "Tailored sanctions")[r$type],
                attr_expected_effectiveness = c(H = "Highly effective", M = "Moderately effective")[r$effect],
                attr_effectiveness_frame = c(P = "Positive frame (chance of success stated)", N = "Negative frame (chance of failing stated)")[r$frame])
stopifnot(all(d$rating_success %in% c(0:100, NA)), all(d$rating_pain_public %in% c(1:10, NA)), all(d$rating_pain_leaders %in% c(1:10, NA)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mclean_2017_sanctions.csv"))
