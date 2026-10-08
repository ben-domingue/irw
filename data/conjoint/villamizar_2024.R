##Reserved-seat district choice conjoint (Afro-Colombians) from
##Villamizar-Chaparro, M., & Echeverri-Pineda, C. (2025). Group consciousness, organizational
##membership, and district choice: Evidence from the Afro-Colombian reserved seats. Political
##Behavior, 47, 825-846 (online 2024). https://doi.org/10.1007/s11109-024-09972-4
##Replication data: Harvard Dataverse doi:10.7910/DVN/D5YYHO, CC0 1.0. Files read: afro_replic.csv
##(one row per district profile) and distrito_afro_regs.csv (one row per respondent; age, gender).
##Design from the article (open access, CC BY), Table 1 and pp. 832-834. The authors' .Rmd was read
##as text, not run.
##Usage: Rscript villamizar_2024.R <dir holding the two CSVs> <output dir>
##
##1,200 self-identified Afro-Colombian adults (online convenience sample recruited through a survey
##firm, October-November 2021), 3 tasks of 2 hypothetical electoral districts, 7 attributes. Matches
##the article's N. The file has NO task or profile column: each respondent has exactly 6 contiguous
##rows, and consecutive row pairs form a task (exactly one profile chosen in all 3,600 pairs), so
##task and profile are INFERRED from row order.
##Outcome: choice = chosen_you. Respondents were "prompted to select their preferred district for
##voting" (paraphrase; the verbatim Spanish question is not in the deposit or the article). Forced
##choice, no opt-out.
##Attribute text: respondents presumably saw Spanish (not stated in the article or deposit). The deposit stores the authors' short English labels,
##used as is (attr_district_type Afro/Territorial; attr_num_candidates; attr_experience;
##attr_vote_buying Clientelistic/Not Clientelistic; attr_candidate_ethnicity Majority Black/Majority
##White; attr_projects; attr_networks). The article's Table 1 gives longer English renderings (e.g.
##"Most candidates are Afro Colombians", "Politicians usually buy votes") but does not match the
##deposit everywhere: its Networks attribute lists "Both family and the community usually vote in
##this district" where the deposit has "No community or family", and its candidate count says "More
##than 15" where the deposit says "More than 14". So the deposit labels are kept rather than mapped.
##Levels were "randomly assigned"; attribute order fixed (article p.834). No restrictions are stated.
##Covariates (distrito_afro_regs.csv): cov_age (years, as recorded; max 100), cov_female (1 = female),
##cov_department (department of residence). Dropped: the authors' derived group-consciousness and
##organization indicators and their survey-item sources. Source ids are survey numbers (not
##platform ids), kept.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "afro_replic.csv"))
r <- fread(file.path(raw, "distrito_afro_regs.csv"))
rl <- rle(s$id); stopifnot(all(rl$lengths == 6), !anyDuplicated(rl$values), nrow(s) == 7200)
s[, k := seq_len(.N), id]
d <- s[, .(id = as.integer(id), task = as.integer((k + 1L) %/% 2L), profile = as.integer(2L - k %% 2L), choice = as.integer(chosen_you),
           attr_district_type = FeatCirc, attr_num_candidates = FeatNumcand, attr_experience = FeatExp,
           attr_vote_buying = FeatClient, attr_candidate_ethnicity = FeatEth, attr_projects = FeatLegis, attr_networks = FeatFam)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d))
cv <- r[, .(id = as.integer(id), cov_age = as.integer(edad), cov_female = as.integer(female), cov_department = departamento)]
stopifnot(!anyDuplicated(cv$id), all(d$id %in% cv$id))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "villamizar_2024_afro_districts.csv"))
