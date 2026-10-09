##Occupation-choice conjoint among Swiss 8th graders from
##Bajka, S. M., Combet, B., Emmenegger, P., & Seufert, S. (2025). Skill requirements versus
##workplace characteristics: Exploring the drivers of occupational gender segregation.
##Socio-Economic Review. https://doi.org/10.1093/ser/mwaf034
##Replication data: Harvard Dataverse doi:10.7910/DVN/MEYKYI, CC0 1.0, no restricted files.
##File read: GenderSegVET_Data_Maintext.xlsx (one sheet, long: ResponseId, Choice_Number,
##Profile, 8 attributes as the authors' one-word labels, Choice, Pref, var_class, var_gen).
##Read as text, not run: GenderSegVET_Analaysis_and_Figures_Appendix_20250508.R. Design facts and
##the attribute text are from the article (Table 1 and the data section; read online).
##Usage: Rscript bajka_2025.R <raw dir> <output dir>
##
##2,144 lower-secondary students (mostly 14-year-olds, 8th grade) in schools of the German-speaking
##cantons Luzern and St.Gallen, Oct-Dec 2022, online survey taken in class. Each made 4 choices
##between two juxtaposed occupational profiles (task = Choice_Number, profile = Profile, both
##recorded) described by 8 two-level attributes, 5 skill requirements and 3 workplace
##characteristics. Outcome: choice, forced (exactly one chosen per task). The verbatim question is
##in the article's Supplementary Appendix 2a (not read); design_outcomes carries a paraphrase.
##Attribute text: the deposit has only the authors' one-word labels; each is replaced by the level
##text of the article's Table 1 (English, as published; the survey language is not stated, the
##cantons are German-speaking). Mapping (deposit label -> Table 1): IT_Reliance Strong/Weak ->
##"Strong IT reliance, use of new technologies"/"Weak IT reliance, use of standard applications";
##Social_Interactions Often/Few -> "Many/Few social interactions in this occupation";
##Creative_Tasks Central/Irrelevant -> "Creativity required for work tasks"/"Creativity rarely
##required for work tasks"; Routinized_Tasks Routine/Non-routine -> "Routine work, clear
##instructions for tasks"/"Requires to constantly find new solutions"; Entrepreneurial_Tasks
##More/Fewer -> "Entrepreneurial work, can involve risks"/"Dependent employment, no entrepreneurial
##risk"; Salary_Expectations High/Low -> "Very important, the higher the better"/"Not so important,
##as long as it is enough"; Family_Friendliness Part-time/Full-time -> "Part-time work is possible
##and common"/"Full-time work is expected, overtime can occur"; Meaningful_Work Important/
##Unimportant -> "Very important, makes contribution to society"/"Not so important, the work needs
##to suit me". The two-level design makes the match unambiguous.
##Randomization: the article says levels were randomly assigned (full factorial, no profile
##excluded) and attribute order randomized ("in a randomized sequence"; per respondent or per task
##not stated, not recorded). Level shares 49-51%.
##Covariates: cov_gender (var_gen Female -> female, Male -> male; the authors' gender split),
##cov_school_class (var_class, the deposit's class code, e.g. "S2a"; meaning of the code not
##documented). Dropped: Qualtrics ResponseId (re-keyed), row number, Pref (the number of the chosen
##profile: identical to Choice, checked).
##N = 2,144 respondents, 17,152 profiles, as in the article. Spot check (direction only, the
##article's numbers were not read): share chosen for strong IT reliance is 0.48 among girls and 0.54
##among boys, the gender gap the article reports.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_excel(file.path(raw, "GenderSegVET_Data_Maintext.xlsx"), col_types = "text"))
stopifnot(nrow(s) == 17152, uniqueN(s$ResponseId) == 2144, s[, .N, ResponseId][, all(N == 8)])
stopifnot(all(as.integer(s$Choice) == as.integer(s$Profile == s$Pref)))
mp <- list(IT_Reliance = c(Strong = "Strong IT reliance, use of new technologies", Weak = "Weak IT reliance, use of standard applications"),
           Social_Interactions = c(Often = "Many social interactions in this occupation", Few = "Few social interactions in this occupation"),
           Creative_Tasks = c(Central = "Creativity required for work tasks", Irrelevant = "Creativity rarely required for work tasks"),
           Routinized_Tasks = c(Routine = "Routine work, clear instructions for tasks", "Non-routine" = "Requires to constantly find new solutions"),
           Entrepreneurial_Tasks = c(More = "Entrepreneurial work, can involve risks", Fewer = "Dependent employment, no entrepreneurial risk"),
           Salary_Expectations = c(High = "Very important, the higher the better", Low = "Not so important, as long as it is enough"),
           Family_Friendliness = c("Part-time" = "Part-time work is possible and common", "Full-time" = "Full-time work is expected, overtime can occur"),
           Meaningful_Work = c(Important = "Very important, makes contribution to society", Unimportant = "Not so important, the work needs to suit me"))
nm <- c(IT_Reliance = "it_reliance", Social_Interactions = "social_interactions", Creative_Tasks = "creative_tasks",
        Routinized_Tasks = "routine_tasks", Entrepreneurial_Tasks = "entrepreneurial_tasks", Salary_Expectations = "salary",
        Family_Friendliness = "family_friendliness", Meaningful_Work = "meaningful_work")
ids <- sort(unique(s$ResponseId))
d <- data.table(id = match(s$ResponseId, ids), task = as.integer(s$Choice_Number), profile = as.integer(s$Profile),
                choice = as.integer(s$Choice))
for (v in names(mp)) { stopifnot(all(s[[v]] %in% names(mp[[v]]))); d[, paste0("attr_", nm[[v]]) := unname(mp[[v]][s[[v]]])] }
stopifnot(all(s$var_gen %in% c("Female", "Male")))
d[, cov_gender := fifelse(s$var_gen == "Female", "female", "male")][, cov_school_class := s$var_class]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bajka_2025_occupation_choice.csv"))
