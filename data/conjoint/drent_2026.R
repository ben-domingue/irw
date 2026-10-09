##Teacher-expectation vignette experiment (Netherlands) from
##Drent, N., Timmermans, A. C., & Strijbos, J. W. (2026). Dataset: Beyond achievement: A vignette
##experiment on how intersecting student characteristics shape teachers' expectations and
##recommendations [Data set]. DANS Data Station Social Sciences and Humanities.
##(No article DOI in the deposit.)
##Data: DANS doi:10.17026/SS/KGD30Q, CC BY 4.0, no restricted files, no terms.
##Files read: "Teacher expectations and recommendation vignettes dataset.sav" (original SPSS,
##read via its value labels) and the deposit's codebook (.docx, read as text).
##Usage: Rscript drent_2026.R <raw dir> <output dir>   (raw dir holds the .sav as data.sav)
##
##140 secondary-school teachers in heterogeneous grade 7/8 classes (convenience sample recruited
##via school leaders, teacher-education programmes and LinkedIn; Qualtrics, April-July 2025).
##Each teacher evaluated 6 vignettes drawn at random from 32, a full 2^5 factorial of five binary
##student characteristics; the student was shown in "a fictional interactive environment modeled
##after Magister (a digital student tracking system)" (DANS metadata), in Dutch. The Dutch display
##text is NOT deposited: levels are the codebook's English category labels (gender Male/Female,
##SES Low/High, ethnicity "Turkish/Moroccan"/Dutch (codebook spelling; the .sav label reads
##"Turkish/Morrocan"), work effort Low/High, class type "Lowest (PV-SG class)"/"Highest (SG-PU
##class)"). Gender and ethnicity were probably carried by the student's name (a teacher's comment
##names the student "Farah"); not documented.
##Outcomes, both per vignette (single profile, profile = 1):
##  rating_recommendation: "Transfer recommendation" 0 = Lowest track, 1 = Highest track
##    (the codebook's "primary outcome"; a classification, not a pick among profiles, so a rating).
##  rating_expectation: "How likely do you think it is that this student will graduate from the
##    highest attainble track?" (.sav label, English translation; codebook: "...obtain a diploma at
##    the higher track?") 1 = Unlikely .. 5 = Highly likely.
##Task: the display order is not documented. task = rank of RespondentXvignet (the deposit's
##row key, contiguous within teacher) -- INFERRED, not a recorded order.
##Most teachers have 6 vignettes; 34 have 1-5 (partial completions kept by the authors) and two
##have 8 and 12 rows (ids 34 with 12 and 116 with 8: possibly two sessions under one id; kept as deposited).
##One row (RespondentXvignet 208, vignette 7) has all five characteristics missing; they are filled
##from vignette 7's levels elsewhere in the file (each vignette number is one fixed combination;
##checked below).
##Covariate: cov_progress (Qualtrics survey progress, %). Dropped: the optional free-text
##explanation (Toelichting; teachers' comments) and the row key.
##N: 140 teachers, 722 rows (codebook says 721 usable evaluations and 721 rows; the extra row is
##not identified). No weighting (DANS metadata).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_sav(file.path(raw, "data.sav"))))
s[, Toelichting := NULL]
f <- c("GenderV", "SESV", "EthnicityV", "Workeffort", "Tracklevel")
key <- unique(na.omit(s[, c("VignetNr", f), with = FALSE]))
stopifnot(nrow(key) == 32, !anyDuplicated(key$VignetNr), nrow(unique(key[, ..f])) == 32)
miss <- !complete.cases(s[, ..f]); stopifnot(sum(miss) == 1)
s[miss, (f) := key[match(s$VignetNr[miss], key$VignetNr), f, with = FALSE]]
setorder(s, RespondentID, RespondentXvignet)
d <- s[, .(id = as.integer(RespondentID), task = seq_len(.N), profile = 1L,
           rating_recommendation = as.integer(Recommendation), rating_expectation = as.integer(Teacherexpectation),
           attr_gender = c("Male", "Female")[GenderV + 1], attr_ses = c("Low", "High")[SESV + 1],
           attr_ethnicity = c("Turkish/Moroccan", "Dutch")[EthnicityV + 1], attr_work_effort = c("Low", "High")[Workeffort + 1],
           attr_class_type = c("Lowest (PV-SG class)", "Highest (SG-PU class)")[Tracklevel + 1],
           cov_progress = as.integer(Progress)), by = RespondentID][, RespondentID := NULL]
stopifnot(all(d$rating_recommendation %in% 0:1), all(d$rating_expectation %in% 1:5), uniqueN(d$id) == 140)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "drent_2026_teacher_expectations.csv"))
