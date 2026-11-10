##Swedish private forest owners' choices among biodiversity conservation contracts, from the replication package
##"Private forest owners prefer public involvement in financing biodiversity conservation" (authors withheld during review; no article located 2026-11-10)
##(Zenodo doi:10.5281/zenodo.23674088, CC BY 4.0; replication_v4 zip).
##Files read: replication_v4/data/raw/dataversion_2025.xlsx (sheet Rawdata; row 1 under the header holds the Swedish question text, which for
##Q8_1-Q31_1 contains the full text of the two contract alternatives shown), replication_v4/data/raw/attribute_map_update_1.csv (design map,
##used to verify the parsed text), replication_v4/R/00_prepare_master.R, 01_mnl.R, schema_checks.R and results/Table_S7/S9/S10 (read as text, code labels).
##Usage: Rscript svensson_2026.R <dir holding the unzipped replication_v4 folder> <output dir>
##
##Swedish private forest owners (1,912 workbook rows, 1,674 answered at least one choice set; online/survey through four distribution channels).
##Discrete choice experiment: 24 choice sets (Choice_Set 8-31 = columns Q8_1-Q31_1); each respondent answered 6 of them (random subset; 1,603 answered
##all 6, 71 answered 1-5). Each set shows two contract alternatives side by side, Resultatsbaserat (result-based, profile 1) and Atgardsbaserat
##(action-based, profile 2), described by 5 rows: Naturvardsaktivitet (conservation activity), Ersattningsniva per ar (annual compensation level),
##Avtalslangd (contract length), Finansiar (financier), plus the column label (attr_contract_type). Level text is the Swedish text displayed (label_language sv).
##A third option, coded 3, is the opt-out (asc_no in the authors' MNL, alternative-specific constant only); no text for it is in the file, so the wording is unknown.
##Choice: Q<k>_1 = 1 chosen alternative 1, 2 chosen alternative 2, 3 opt-out (choice = 0 on both profiles). The question wording is the first line of the
##question text ("Vilket av foljande val foredrar du? Markera en av cirklarna." = which of the following do you prefer? mark one of the circles).
##The text in the label row ends the financier cell of alternative 2 with " - Ditt val" ("your choice"): this is the radio-button caption, not part of the
##level, and is removed. Fixed blocked random design: each respondent got a random 6 of 24 sets; levels fixed per set (attribute_map_update_1.csv; text parsed
##here matches its Price, Length and financier columns for all 24 sets, checked in the script). Restrictions: none documented; the 24 sets are a fixed
##fractional design.
##Task order: the file does not record the order the 6 sets were shown; task = rank of the set number within respondent (task_source inferred) and
##trial_choice_set holds the set number (8-31). Position of the alternatives (result-based left) is as in the label text.
##Authors' analysis samples: the master sample is every respondent with at least one choice (1,674 respondents, 9,794 choices: reproduced exactly); the authors also
##use a Q2-complete sample (1,673 respondents) and a gender sample (1,547 respondents with all 6 tasks and gender code 1 or 2). No exclusion is applied here;
##reproduce them with cov_forest_size missing and with cov_gender_code in male/female and 6 tasks.
##Covariates (code labels from the package's own tables S7, S9, S10): cov_gender (Male -> male, Female -> female, Other -> other, "I don't want to say" -> NA),
##cov_age_group (S9 band text, "Younger than 30" ...), cov_forest_size (S7 band of productive forest hectares, text). Dropped: all other survey items (forest
##attitudes, income, free text Q6_14_TEXT/Q32_8_TEXT/Q33_1_TEXT, open text Q36/Q39 are empty in the file), county, distribution channel, the Random ID (re-keyed).
##No weights. PII FOUND: none (Random ID is a random survey id; free-text fields emptied by the depositors).
##Respondent count vs paper: 1,674 respondents / 9,794 choices equals the package's own master sample (paper not located).
suppressMessages({library(data.table); library(readxl)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
wb <- file.path(raw, "replication_v4/data/raw/dataversion_2025.xlsx")
s <- as.data.table(read_excel(wb, sheet = "Rawdata", col_types = "text"))
lab <- unlist(s[1]); r <- s[-1]
r <- r[!is.na(`Random ID`) & trimws(`Random ID`) != ""]
stopifnot(nrow(r) == 1912)
sets <- 8:31
parse_set <- function(q) {
  l <- trimws(strsplit(lab[[paste0("Q", q, "_1")]], "\n")[[1]]); l <- l[l != ""]
  i <- which(l == "Resultatsbaserat"); stopifnot(length(i) == 1, l[i + 1] == "Åtgärdsbaserat")
  stopifnot(l[i + 2] == "Naturvårdsaktivitet", l[i + 5] == "Ersättningsnivå per år", l[i + 8] == "Avtalslängd", l[i + 11] == "Finansiär", length(l) == i + 13)
  f2 <- sub(" - Ditt val$", "", l[i + 13]); stopifnot(f2 != l[i + 13])
  data.table(Choice_Set = q, profile = 1:2, attr_contract_type = c("Resultatsbaserat", "Åtgärdsbaserat"),
             attr_conservation_activity = l[i + 3:4], attr_compensation = l[i + 6:7],
             attr_contract_length = l[i + 9:10], attr_financier = c(l[i + 12], f2))
}
des <- rbindlist(lapply(sets, parse_set))
# verify against the authors' attribute map
am <- fread(file.path(raw, "replication_v4/data/raw/attribute_map_update_1.csv"))
chk <- merge(des, rbind(am[, .(Choice_Set, profile = 1L, price = Price_1, len = Length_1, pr = Private_Sector_1, st = Swedish_State_1, pp = Public_Private_1)],
                        am[, .(Choice_Set, profile = 2L, price = Price_2, len = Length_2, pr = Private_Sector_2, st = Swedish_State_2, pp = Public_Private_2)]), by = c("Choice_Set", "profile"))
num <- function(x) as.numeric(gsub("\\.", "", sub("^([0-9.]+) .*$", "\\1", x)))
stopifnot(nrow(chk) == 48, all(num(chk$attr_compensation) == chk$price),
          all(as.numeric(sub(" år$", "", chk$attr_contract_length)) == chk$len),
          all((chk$attr_financier == "Privata sektorn") == (chk$pr == 1)),
          all((chk$attr_financier == "Svenska staten") == (chk$st == 1)))
ch <- melt(r[, c("Random ID", paste0("Q", sets, "_1")), with = FALSE], id.vars = "Random ID", variable.name = "q", value.name = "ans")
ch <- ch[!is.na(ans) & ans != ""]
ch[, Choice_Set := as.integer(sub("^Q([0-9]+)_1$", "\\1", q))]
stopifnot(all(ch$ans %in% c("1", "2", "3")), nrow(ch) == 9794, ch[, uniqueN(`Random ID`)] == 1674)
ch[, id := as.integer(factor(`Random ID`))]
setorder(ch, id, Choice_Set); ch[, task := seq_len(.N), id]
x <- merge(ch[, .(`Random ID`, id, task, Choice_Set, ans)], des, by = "Choice_Set", allow.cartesian = TRUE)
x[, choice := as.integer(as.integer(ans) == profile)]
stopifnot(x[, sum(choice), .(id, task)][, all(V1 <= 1)], x[, uniqueN(id)] == 1674)
gl <- c("1" = "male", "2" = "female", "3" = "other")
age <- c("Younger than 30", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90 and above")
fs <- c("Less than 5 ha", "5-20 ha", "21-50 ha", "51-100 ha", "101-200 ha", "201-400 ha", "401-1000 ha", "1001-5000 ha", "More than 5000 ha")
cv <- r[, .(`Random ID`, cov_gender = unname(gl[Q40]), cov_age_group = age[as.integer(Q41)], cov_forest_size = fs[as.integer(Q2)])]
x <- merge(x, cv, by = "Random ID")
x[, trial_choice_set := Choice_Set]
x <- x[, .(id, task, profile, choice, attr_contract_type, attr_conservation_activity, attr_compensation, attr_contract_length, attr_financier,
           cov_gender, cov_age_group, cov_forest_size, trial_choice_set)]
setorder(x, id, task, profile)
stopifnot(!anyNA(x[, 5:9]))
fwrite(x, file.path(out, "svensson_2026_forest_biodiversity.csv"))
cat(nrow(x), x[, uniqueN(id)], "\n")
