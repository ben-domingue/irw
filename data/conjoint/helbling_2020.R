##Climate-change-migrant vignette experiment (Germany) from
##Helbling, M. (2020). Attitudes towards climate change migrants. Climatic Change, 160(1), 89-102.
##https://doi.org/10.1007/s10584-020-02697-3
##Replication data: Harvard Dataverse doi:10.7910/DVN/MJIVGR, CC0 1.0, no restricted files. Files read:
##DataClimateChangeMigrantsReplication.tab (1,102 rows), CodebookClimateChangeMigrants.pdf (pdftotext),
##SyntaxClimateChangeMigrantsReplication.do (as text). Usage: Rscript helbling_2020.R <dir holding data.tab> <out dir>
##
##German adults (online survey, n = 1,102); each saw ONE vignette about a migrant and was asked "Do you think Germany
##should let him immigrate?" (1 Yes, 2 No). The vignette is one of 6 reasons x 2 religions x 2 education levels = 24
##cells, stored as 24 wide columns (v_4, v_29-v_38, v_40-v_52; -77 = not shown); the cell a respondent answered is
##the one with a 1/2. Cell order and labels are from the codebook ("Vig1_1a political/muslim/education high" ...,
##variable name printed just above its label; the pairing was cross-checked against the authors' reason recode in the
##.do file). The deposit holds only these short cell labels, not the vignette wording, so attribute levels are the
##codebook labels: reason political / economic / droughts / droughts - climate change / sea level / sea level -
##climate change; religion muslim / christian; education high / low. The .do file's `muslim` dummy lists v_40 where
##the codebook points to v_46; the dummy is dropped here.
##Outcome (choice, single-profile accept/reject, so opt_out = yes): choice = 1 if Yes, 0 if No. One task, one profile
##per respondent; id = row number (no respondent id in the file).
##NOT built: the second vignette block (low/high migration numbers x morality / corrective justice / capacity
##argument; outcome agreement with the argument) -- the arguments are messages, not attributes of an evaluated
##profile, and their wording is not in the deposit. Held.
##Covariates: cov_gender (v_1: 1 male, 2 female; codebook), cov_birth_year (v_2), cov_education (v_3, codebook
##German school-leaving categories as English text; 0 = missing -> NA), cov_left_right (v_67, 1 left .. 11 right,
##0 missing -> NA). Dropped: environmental behaviour items, climate-belief items, income, second-vignette columns.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.tab"))
cells <- c(4, 29:34, 35:38, 40, 41:46, 47:52)  # 1a..1f, 2a..2f, 3a..3f, 4a..4f
stopifnot(length(cells) == 24)
cn <- paste0("v_", cells)
reasons <- c("political", "economic", "droughts", "droughts - climate change", "sea level", "sea level - climate change")
grid <- data.table(cn = cn, attr_reason = rep(reasons, 4),
                   attr_religion = rep(rep(c("muslim", "christian"), each = 6), 2),
                   attr_education = rep(c("high", "low"), each = 12))
m <- as.matrix(s[, ..cn]); ans <- m %in% c(1, 2); dim(ans) <- dim(m)
stopifnot(all(rowSums(ans) <= 1))
cat("respondents with an answer:", sum(rowSums(ans) == 1), "of", nrow(s), "\n")
k <- apply(ans, 1, function(z) if (any(z)) which(z) else NA_integer_)
ok <- !is.na(k)
resp <- m[cbind(seq_len(nrow(s)), k)]
edu <- c("1" = "school finished without certificate", "2" = "Hauptschulabschluss", "3" = "Volksschulabschluss",
         "4" = "Realschulabschluss / Mittlere Reife", "6" = "Fachschulreife or Abschluss der polytechnischen Oberschule, 10. Klasse",
         "7" = "Fachhochschulreife", "8" = "Abitur (A levels)", "9" = "Still pupil")
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L, choice = ifelse(resp == 1, 1L, 0L),
                grid[k, .(attr_reason, attr_religion, attr_education)],
                cov_gender = c("male", "female")[s$v_1], cov_birth_year = as.integer(s$v_2),
                cov_education = unname(edu[as.character(s$v_3)]),
                cov_left_right = ifelse(s$v_67 == 0, NA, as.integer(s$v_67)))
d <- d[ok]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "helbling_2020_climate_migrants.csv"))
