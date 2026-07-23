*** This Stata Do File processes the spain_2026_confidence study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2026_confidence"

import delimited "3565_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* header cells are "VARNAME: descriptive label"; recover the true variable name
foreach v of varlist _all {
    local lbl : variable label `v'
    local newname = trim(substr("`lbl'", 1, strpos("`lbl'", ":") - 1))
    rename `v' `newname'
}

destring _all, replace force

gen id = _n

* rename covariates

rename P19 cov_sex
rename P20 cov_age

* lower case everything
rename *, lower

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

save "spain_2026_master.dta", replace

**# Table 1: acquisition

* ============================================================
* acquisition (P1_1, P1_2, P1_3, P1_4)
* one yes/no item per good, rebuilt from one-hot dummy columns
* dummies coded 1 = selected, 2 = not selected
* item: 1 = acquired (self or household), 2 = no; N.S./N.C. left missing
* ============================================================

use "spain_2026_master.dta", clear

gen p1_1 = .
replace p1_1 = 1 if p1_1_1 == 1 | p1_1_2 == 1
replace p1_1 = 2 if p1_1_3 == 1

gen p1_2 = .
replace p1_2 = 1 if p1_2_1 == 1 | p1_2_2 == 1
replace p1_2 = 2 if p1_2_3 == 1

gen p1_3 = .
replace p1_3 = 1 if p1_3_1 == 1 | p1_3_2 == 1
replace p1_3 = 2 if p1_3_3 == 1

gen p1_4 = .
replace p1_4 = 1 if p1_4_1 == 1 | p1_4_2 == 1
replace p1_4 = 2 if p1_4_3 == 1

local survey_cols p1_1 p1_2 p1_3 p1_4

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
drop p1_1 p1_2 p1_3 p1_4
export delimited using "spain_2026_confidence_acquisition.csv", replace

**# Table 2: retrospect

* ============================================================
* retrospect (P3, P7, P7_1, P8, P8_1)
* retrospective mejor/igual/peor gradients
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p3 p7 p7_1 p8 p8_1

keep id cov_* `survey_cols'

replace p3 = . if inlist(p3, 8, 9)
replace p7 = . if inlist(p7, 8, 9)
replace p7_1 = . if inlist(p7_1, 8, 9)
replace p8 = . if inlist(p8, 8, 9)
replace p8_1 = . if inlist(p8_1, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
drop p3 p7 p7_1 p8 p8_1
export delimited using "spain_2026_confidence_retrospect.csv", replace

**# Table 3: prospect

* ============================================================
* prospect (P9, P9_1, P12, P14, P14_1)
* prospective mejor/igual/peor gradients
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p9 p9_1 p12 p14 p14_1

keep id cov_* `survey_cols'

replace p9 = . if inlist(p9, 8, 9)
replace p9_1 = . if inlist(p9_1, 8, 9)
replace p12 = . if inlist(p12, 8, 9)
replace p14 = . if inlist(p14, 8, 9)
replace p14_1 = . if inlist(p14_1, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
drop p9 p9_1 p12 p14 p14_1
export delimited using "spain_2026_confidence_prospect.csv", replace

**# Table 4: expectations

* ============================================================
* expectations (P6, P10, P11)
* personal change scales (more/same/less)
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p6 p10 p11

keep id cov_* `survey_cols'

replace p6 = . if inlist(p6, 8, 9)
replace p10 = . if inlist(p10, 8, 9)
replace p11 = . if inlist(p11, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
drop p6 p10 p11
export delimited using "spain_2026_confidence_expectations.csv", replace

**# Table 5: macro

* ============================================================
* macro (P15, P16, P17)
* inflation / interest rates / housing prices, up/same/down
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p15 p16 p17

keep id cov_* `survey_cols'

replace p15 = . if inlist(p15, 8, 9)
replace p16 = . if inlist(p16, 8, 9)
replace p17 = . if inlist(p17, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
drop p15 p16 p17
export delimited using "spain_2026_confidence_macro.csv", replace