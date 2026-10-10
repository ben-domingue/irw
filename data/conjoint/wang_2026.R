##Urban-green-space visit DCE under heat and humidity (Sapporo, Japan) from
##Wang, J., Mameno, K., Owake, T., Aikoh, T., & Shoji, Y. (2026). Extreme heat and humidity reduce
##the recreational value of urban green spaces. Communications Earth & Environment.
##https://doi.org/10.1038/s43247-026-03389-z
##Replication data: Zenodo record 18501408, doi:10.5281/zenodo.18501408, CC BY 4.0 (record licence;
##the zip's LICENSE file is an MIT software licence for the code, no stricter terms).
##Files read (from ugs_lossvalue_tcm_ce.zip): data/data_Nlogit/Derived_CE_Sapporo_2023.csv (NLOGIT
##input, no header) and Nlogit/Read.lim (its column names, 281 variables). Read as text, not run:
##Nlogit/CE_Command.lim, Ngene/CE_Design.ngs. Design facts from the article (Methods, "Discrete
##choice experiment" and "Data: web questionnaire survey"; open access, read online).
##Usage: Rscript wang_2026.R <raw dir> <output dir>
##
##Online survey (December 2023, survey-company panel, residents of the Sapporo metropolitan area aged
##20-69, language not stated, presumably Japanese). Each respondent answered 8 choice sets of one questionnaire version
##(pat = version 1-6, 6 versions x 8 sets = the 48-row Ngene D-efficient design: fixed blocked design,
##trial_version). Each set: two urban-green-space visit profiles + a "no UGS visit" option (the article:
##cancel the planned visit and reschedule it for another day). The no-visit alternative carries no
##displayed attributes (its rows hold the authors' model base values: 24, 0.5, absent, present, 0 min,
##asc = 1), so it is NOT a profile: choice = 0 on both profiles when it was chosen (opt-out).
##task = set (1-8), profile = choices (1, 2); recorded in the file. Exactly one of the three
##alternatives is chosen in every set (checked).
##Attributes (article Methods/Table 5): maximum daily temperature, six levels 24-34 °C (maxt, stored
##"24°C"); humidity 50/65/80% (hum 0.5/0.65/0.8 -> "50%"...); water-play facilities present/absent
##(wpf effect-coded 1/-1 -> "present"/"absent"); indoor air-conditioned facilities for temporary heat
##relief present/absent (ac 1/-1); one-way travel time 15/30/45/60/90 min (ttime -> "15 min"). The
##level text is the article's English rendering of quantities; the Japanese card wording is not
##deposited. The choice question wording is not deposited either (paraphrase in design_outcomes).
##The effect-code direction (1 = present) follows the article ("reference ... absent for both water-
##play facilities and indoor cooling spaces" and the opt-out row's "no water-play facilities, air
##conditioning available" = wpf -1, ac 1).
##Sample: 1,571 respondents in the file (the article: "1571 valid responses ... of which 1325 were used
##in the analysis"). The authors' exclusion flags reject_1, reject_2, reject_3 (0/1, constant within
##respondent; meaning not documented; CE_Command.lim drops reject_2 = 1, leaving 1,365, not 1,325;
##the main RPL output (Output_RPL_main.lim) also drops times = 0, leaving 8,024 sets = 1,003
##respondents) are kept as cov_reject_1..3. All 1,571 kept. The N discrepancy is the authors'.
##Covariates: cov_gender_code (column `male`, 1/0 as stored), cov_age_code (age, codes 2-6, unlabeled;
##probably age decade given the 20-69 sample, not verified), cov_income_code (inc, unlabeled numeric).
##Dropped: the ~250 unlabeled questionnaire items (q*, s*, d_*), derived dummies (yng_*, b_*, eld_*,
##mt*, hum65/80, asc, ln_*), CEID (row number), panel (constant 8), cell (undocumented), the 960
##empty trailing rows of the CSV.
##Spot check: a conditional logit over all three alternatives on the authors' numeric coding (maxt,
##hum, wpf, ac, ttime, asc; reject_2 = 0, 10,920 sets) reproduces the authors' CLOGIT in
##Nlogit/Output_continuous.lim to 3 decimals (MAXT -.317, HUM -2.300, WPF -.001, AC .204, TTIME -.020,
##ASC -2.922). Raw choice shares by water play are flat (the article reports a positive MXL effect).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
l <- readLines(file.path(raw, "Read.lim"), warn = FALSE)
i <- grep("names=", l)
nm <- trimws(sub(",$", "", sub("\\$.*", "", l[(i + 1):length(l)]))); nm <- nm[nm != ""]
x <- fread(file.path(raw, "Derived_CE_Sapporo_2023.csv"), header = FALSE)
stopifnot(length(nm) == 281, ncol(x) == 281)
setnames(x, nm)
x <- x[!is.na(ID)]
stopifnot(nrow(x) == 37704, uniqueN(x$ID) == 1571, x[, .N, ID][, all(N == 24)],
          x[, all(set == rep(1:8, each = 3) & choices == rep(1:3, 8)), ID][, all(V1)],
          x[, sum(choice), .(ID, set)][, all(V1 == 1)], all(x[choices == 3, asc] == 1), all(x[choices != 3, asc] == 0))
for (v in c("pat", "male", "age", "inc", "reject_1", "reject_2", "reject_3")) stopifnot(x[, uniqueN(get(v)), ID][, all(V1 == 1)])
p <- x[choices != 3]
stopifnot(all(p$maxt %in% seq(24, 34, 2)), all(p$hum %in% c(0.5, 0.65, 0.8)), all(p$wpf %in% c(-1, 1)),
          all(p$ac %in% c(-1, 1)), all(p$ttime %in% c(15, 30, 45, 60, 90)))
d <- p[, .(id = as.integer(ID), task = as.integer(set), profile = as.integer(choices), choice = as.integer(choice),
           attr_max_temperature = paste0(maxt, "°C"), attr_humidity = paste0(round(hum * 100), "%"),
           attr_water_play = fifelse(wpf == 1, "present", "absent"), attr_indoor_cooling = fifelse(ac == 1, "present", "absent"),
           attr_travel_time = paste(ttime, "min"), trial_version = as.integer(pat),
           cov_gender_code = as.integer(male), cov_age_code = as.integer(age), cov_income_code = as.integer(inc),
           cov_reject_1 = as.integer(reject_1), cov_reject_2 = as.integer(reject_2), cov_reject_3 = as.integer(reject_3))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wang_2026_green_space_heat.csv"))
cat("opt-out share:", x[choices == 3, mean(choice)], "\n")
print(d[, .(share = mean(choice)), attr_water_play]); print(d[, .(share = mean(choice)), keyby = attr_max_temperature])
