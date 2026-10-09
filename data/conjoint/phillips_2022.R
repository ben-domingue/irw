##Blended-care discrete choice experiment among German psychotherapists from
##Phillips, E. A., Himmler, S., & Schreyögg, J. (2022). Preferences of psychotherapists for
##blended care in Germany: A discrete choice experiment. BMC Psychiatry, 22, 112.
##https://doi.org/10.1186/s12888-022-03765-x
##Data: OSF project hy3ts (https://osf.io/hy3ts/), node licence CC BY 4.0, no other terms.
##Files read (from "Analysis repository DCE BC.zip"): fulldata.xlsx (sheet Data, one row per
##respondent), designmain.xlsx (sheet design: block, taskID, alt, the option text shown).
##Codebook: HCDR-0001-DC_Codebook_FINAL.xls (German question and answer labels); the authors'
##01_DCE_BC_merge_and_clean.do (read as text) gives the block and task mapping used here.
##Usage: Rscript phillips_2022.R <dir holding fulldata.xlsx and designmain.xlsx> <output dir>
##
##200 licensed psychotherapists (DocCheck online panel, July-August 2020), 16 forced choices
##each between OPTION A and OPTION B, two hypothetical blended-care application scenarios.
##A Bayesian D-efficient fixed design in blocks of 16 (fixed blocked design): trial_block = the
##authors' block. Block 1 is the design used before a programming change (v_70-v_85; 37
##respondents; the article: data collection paused after 30 respondents, pretest data used to
##refine the design); blocks 2 and 3 are the final design's two blocks (v_19 "ZUFALLSVERTEILUNG"
##= random allocation; v_20-v_35 and v_36-v_51; 79 and 84 respondents). The authors pool all
##200 with block dummies, so one table. task = position 1-16 within the block (the order the
##codebook lists the questions), profile = 1 for OPTION A, 2 for OPTION B. An unrelated warm-up
##task is not in the data.
##Attributes (German text as displayed, from the design file; the codebook shows the same
##text as the answer labels): attr_recommendation ("Empfehlung": keine / von Kollegen / von der
##Fachgesellschaft), attr_effectiveness ("Wirksamkeit von Online-Komponente": "7 von 10
##Klienten" etc.; two design cells read "9 von 10 von Klienten" / "8 von 10 von Klienten", a
##typo normalized here to "... von 10 Klienten"), attr_time_split ("Zeitliches Verhältnis
##Online vs. Face-to-Face": 20:80, 50:50, 80:20), attr_reimbursement ("Vergütung":
##"Proportional zu dem Zeitaufwand" / "... + Pauschale").
##Outcome: choice: "Bitte wählen Sie eines der beiden Anwendungsszenarien für Blended Care, das
##Sie bevorzugen würden:" OPTION A / OPTION B, forced (the article: no opt-out by design).
##Covariates (codes as in the codebook, -99/-66 = NA): cov_profession (v_3 answer text),
##cov_uses_online_tool (v_6: 1 ja, 2 nein), cov_experience_rating (v_7: 1 sehr gut ... 5 sehr
##schlecht), cov_likely_psychoeducation/_cbt_exercises/_diaries/_video/_games/_chatbots (v_8-v_13:
##1 sehr wahrscheinlich ... 5 sehr unwahrscheinlich; v_10's codebook swaps the labels of 4 and 5,
##kept as coded), cov_bc_format (v_15: 1 stepped care, 2 parallel, 3 aftercare),
##cov_time_new_clients/_existing_clients/_training/_leisure (v_16_1u-4u, percent),
##cov_bc_conceivable (v_52: 1 ja, 2 nein), cov_bc_relationship (v_54: 1 eher positiv, 2 weder
##noch, 3 eher negativ), cov_workplace (v_57: 1 eigene Praxis, 2 Klinik, 3 Sonstiges),
##cov_financial_satisfaction (v_58: 1 sehr zufrieden ... 5 sehr unzufrieden), cov_gender (v_59:
##weiblich -> female, männlich -> male), cov_age (v_60_1u, typed: whole numbers 18-99 only),
##cov_state (v_61 Bundesland text). Dropped: consent, all free-text answers (v_4_1u, v_5_1u,
##v_14_1u, v_53_1u, v_55_1u, v_56_1u, v_57_3u, v_62_1u), InterviewNumber (re-keyed in file
##order). N matches the article (200).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- as.data.table(read_excel(file.path(raw, "fulldata.xlsx"), sheet = "Data"))
g <- as.data.table(read_excel(file.path(raw, "designmain.xlsx"), sheet = "design"))[!is.na(Design), .(block, taskID, alt, Design)]
stopifnot(nrow(f) == 200L, nrow(g) == 96L)
pat <- "^(\\d) = OPTION ([AB]) Empfehlung: (.*?) Wirksamkeit von Online.Komponente: (.*?) Zeitliches Verhältnis Online vs\\. Face-to-Face: (.*?) Vergütung: (.*)$"
m <- regmatches(g$Design, regexec(pat, g$Design))
stopifnot(all(lengths(m) == 7L))
g[, `:=`(attr_recommendation = sapply(m, `[`, 4), attr_effectiveness = sub(" von Klienten", " Klienten", sapply(m, `[`, 5)),
         attr_time_split = sapply(m, `[`, 6), attr_reimbursement = sapply(m, `[`, 7))]
stopifnot(g$alt == as.integer(sapply(m, `[`, 2)), uniqueN(g$attr_effectiveness) == 3L)
num <- function(x) { x <- suppressWarnings(as.numeric(x)); x[x %in% c(-99, -66)] <- NA; x }
f[, id := seq_len(.N)]
f[, block := fifelse(num(v_19) %in% NA, 1L, fifelse(num(v_19) == 1, 2L, 3L))]
stopifnot(all(as.numeric(f$v_19) %in% c(-66, 1, 2)), f[, .N, block]$N[order(f[, .N, block]$block)] == c(37L, 79L, 84L))
cols <- list(`1` = paste0("v_", 70:85), `2` = paste0("v_", 20:35), `3` = paste0("v_", 36:51))
ch <- rbindlist(lapply(seq_len(nrow(f)), function(i) {
  b <- f$block[i]; v <- num(unlist(f[i, cols[[as.character(b)]], with = FALSE]))
  stopifnot(all(v %in% 1:2))
  data.table(id = f$id[i], block = b, task = 1:16, chosen = as.integer(v))
}))
d <- merge(ch[, .(id, block, task, chosen)][rep(seq_len(.N), each = 2)][, profile := rep(1:2, .N / 2)],
           g[, .(block = as.integer(block), task = as.integer(taskID), profile = as.integer(alt),
                 attr_recommendation, attr_effectiveness, attr_time_split, attr_reimbursement)],
           by = c("block", "task", "profile"))
d[, choice := as.integer(chosen == profile)][, chosen := NULL]
d[, trial_block := block][, block := NULL]
lab3 <- c("Psychologischer Psychotherapeut", "Ärztlicher Psychotherapeut", "Kinder- und Jugendpsychotherapeut",
          "Heilpraktiker für Psychotherapie", "Anderer")
st <- c("Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern",
        "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt",
        "Schleswig-Holstein", "Thüringen", "Außerhalb Deutschlands")
age <- trimws(as.character(f$v_60_1u)); age <- fifelse(grepl("^[0-9]+$", age), suppressWarnings(as.integer(age)), NA_integer_)
age[!(age %between% c(18, 99))] <- NA
cv <- f[, .(id, cov_profession = lab3[num(v_3)], cov_uses_online_tool = num(v_6), cov_experience_rating = num(v_7),
            cov_likely_psychoeducation = num(v_8), cov_likely_cbt_exercises = num(v_9), cov_likely_diaries = num(v_10),
            cov_likely_video = num(v_11), cov_likely_games = num(v_12), cov_likely_chatbots = num(v_13),
            cov_bc_format = num(v_15), cov_time_new_clients = num(v_16_1u), cov_time_existing_clients = num(v_16_2u),
            cov_time_training = num(v_16_3u), cov_time_leisure = num(v_16_4u), cov_bc_conceivable = num(v_52),
            cov_bc_relationship = num(v_54), cov_workplace = num(v_57), cov_financial_satisfaction = num(v_58),
            cov_gender = c("female", "male")[num(v_59)], cov_age = age, cov_state = st[num(v_61)])]
d <- merge(d, cv, by = "id")
stopifnot(nrow(d) == 6400L, d[, .(sum(choice), .N), .(id, task)][, all(V1 == 1 & N == 2)], !anyNA(d$attr_recommendation))
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "phillips_2022_blended_care.csv"))
