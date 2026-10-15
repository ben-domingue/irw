##Electric-motorcycle stated choice experiment (Solo, Indonesia) from
##Guerra, E. (2019). Electric vehicles, air pollution, and the motorcycle city: A stated preference survey of
##consumers' willingness to adopt electric motorcycles in Solo, Indonesia. Transportation Research Part D, 68, 52-64.
##https://doi.org/10.1016/j.trd.2017.07.027
##Data: Mendeley Data doi:10.17632/3xyf8kvkr2.1, CC BY-NC 3.0 (Mendeley public API, data_licence). File read:
##solo_moto_wide.RDa (one data.frame "dat", 6,040 rows = 1,208 respondents x 5 choice tasks, wide per task).
##Usage: Rscript guerra_2019.R <dir holding solo_moto_wide.RDa> <output dir>
##
##1,208 consumers in Solo (Surakarta), Indonesia, 2015 survey (N 1,208 matches the paper's 1,208 surveys).
##Each of 5 tasks: choose among a gasoline motorcycle, an electric motorcycle, or no motorcycle (NOM). The
##data code the choice as GAS / ELE / NOM. NOM has no attributes: opt_out = yes, no profile row, choice 0 on both.
##Profiles: profile 1 = electric motorcycle, profile 2 = gasoline motorcycle (fixed by construction; the on-screen
##position is unknown, profile_source = unknown). attr_mode holds the label.
##Electric motorcycle attributes (six, randomized): down payment, monthly payment, fuel (electricity) price, maximum
##range, charge time, maximum speed. Gasoline motorcycle: only the fuel price varies; the paper (Table 1, via
##search summary, full text not read) says its other levels were fixed, but the fixed levels are not in the deposit,
##so those cells hold the text "(fixed level, not in deposit)" rather than a guess. They are not randomized.
##Level text: the deposit stores numbers only. Units and wording are inferred: prices in rupiah ("Rp 400,000"),
##range in km, charge time in hours, maximum speed in km/h (units from the article abstract: premium for 10 km more
##range, 10 km/h more speed, one hour shorter charge time; the on-screen wording was not seen, and whether fuel price
##is per litre is not stated, so fuel prices carry no unit). Down payment / monthly payment shown as Rp amounts.
##Restrictions: none documented; level weights: appear near-uniform but no source states them (unknown).
##Attribute order fixed (assumed; no position column).
##Respondent id: the file has no respondent column and its rows are not grouped by person; ids are rebuilt from the
##data.frame row names ("143" = task 1 of respondent 143; "<id><k-1>" for later tasks; two make.unique collisions
##for respondent 143 are repaired by hand), then verified: every respondent has choice.id 1..5 once and constant
##age/gender/income. task = choice.id (assumed order shown).
##Covariates kept: cov_age (years; the one value 422 and nothing else implausible -> NA), cov_gender (Laki-laki =
##male, Perempuan = female; translated from Indonesian, no codebook), cov_income_monthly_rp (answer text as stored),
##cov_n_motorcycles.
##Dropped: kelurahan (neighbourhood), phone, travel mode, environmental concern, smoking, e-bike items, all text columns.
##N vs paper: 1,208 respondents x 5 tasks, as in the paper.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(list.files(raw, pattern = "[.]RDa$", full.names = TRUE)[1], e)
d <- e$dat; x <- as.data.table(d); x[, rn := rownames(d)]
x[, rni := as.integer(rn)]
x[, sid := ifelse(choice.id == 1, rni, (rni - (choice.id - 1)) %/% 10L)]
x[rn %in% c("14310", "14314"), sid := 143L]
stopifnot(x[, .N, sid][, all(N == 5)], x[, all(sort(choice.id) == 1:5), sid][, all(V1)],
  x[, uniqueN(paste(age, gender, inc.monthly, n.motorcycles)), sid][, all(V1 == 1)], uniqueN(x$sid) == 1208)
x[, id := match(sid, sort(unique(sid)))]
rp <- function(v) paste0("Rp ", formatC(v, format = "d", big.mark = ","))
fx <- "(fixed level, not in deposit)"
mk <- function(prof) {
  if (prof == 1) x[, .(id, task = as.integer(choice.id), profile = 1L, choice = as.integer(choice == "ELE"),
    attr_mode = "Electric motorcycle", attr_down_payment = rp(el.downpayment), attr_monthly_payment = rp(el.monthlypayment),
    attr_fuel_price = rp(el.fuelprice), attr_max_range = paste(as.integer(el.maxrange), "km"),
    attr_charge_time = paste(as.integer(el.chargetime), ifelse(el.chargetime == 1, "hour", "hours")),
    attr_max_speed = paste(as.integer(el.maxspeed), "km/h"))]
  else x[, .(id, task = as.integer(choice.id), profile = 2L, choice = as.integer(choice == "GAS"),
    attr_mode = "Gasoline motorcycle", attr_down_payment = fx, attr_monthly_payment = fx,
    attr_fuel_price = rp(gas.fuelprice), attr_max_range = fx, attr_charge_time = fx, attr_max_speed = fx)]
}
cv <- x[, .(id, task = as.integer(choice.id), cov_age = ifelse(age >= 15 & age <= 100, as.integer(age), NA_integer_),
  cov_gender = ifelse(gender == "Laki-laki", "male", ifelse(gender == "Perempuan", "female", NA_character_)),
  cov_income_monthly_rp = as.character(inc.monthly), cov_n_motorcycles = as.integer(n.motorcycles))]
dd <- rbind(mk(1), mk(2))
dd <- merge(dd, cv, by = c("id", "task"), sort = FALSE)
stopifnot(!anyNA(dd[, .SD, .SDcols = patterns("^attr_|^task$|^profile$")]), dd[, .N, .(id, task)][, all(N == 2)],
  dd[, sum(choice), .(id, task)][, all(V1 <= 1)], nrow(dd) == 12080)
setorder(dd, id, task, profile)
fwrite(dd, file.path(out, "guerra_2019_electric_motorcycle.csv"))
