*** This Stata Do File processes the spain_2026_prostitution study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2026_prostitution"

**# Bookmark 1: import and clean

import delimited "3525_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* recover true variable names from quote wrapped headers

foreach v of varlist _all {
    local lbl : variable label `v'
    if "`lbl'" != "" {
        local newname = subinstr("`lbl'", char(34), "", .)
        local newname = strtrim("`newname'")
        capture rename `v' `newname'
    }
}

rename *, lower

destring _all, replace force

gen long id = _n

* rename covariates

rename sexo cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 999

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

order id cov_*, first

compress

save "spain_2026_prostitution_master.dta", replace

**# Bookmark 2: pornography

* ============================================================
* pornography (P1_1 to P1_5)
* ============================================================

use "spain_2026_prostitution_master.dta", clear

local survey_cols p1_1 p1_2 p1_3 p1_4 p1_5

keep id cov_* `survey_cols'

replace p1_1 = . if inlist(p1_1, 8, 9)
replace p1_2 = . if inlist(p1_2, 8, 9)
replace p1_3 = . if inlist(p1_3, 8, 9)
replace p1_4 = . if inlist(p1_4, 8, 9)
replace p1_5 = . if inlist(p1_5, 8, 9)

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
replace resp = . if resp == 3
drop if missing(resp)
sort id item
drop p1_1 p1_2 p1_3 p1_4 p1_5

* verification

count
tab item
tab resp

export delimited using "spain_2026_prostitution_pornography.csv", replace

**# Bookmark 3: prostitution

* ============================================================
* prostitution (P23_1 to P23_6)
* ============================================================

use "spain_2026_prostitution_master.dta", clear

local survey_cols p23_1 p23_2 p23_3 p23_4 p23_5 p23_6

keep id cov_* `survey_cols'

replace p23_1 = . if inlist(p23_1, 8, 9)
replace p23_2 = . if inlist(p23_2, 8, 9)
replace p23_3 = . if inlist(p23_3, 8, 9)
replace p23_4 = . if inlist(p23_4, 8, 9)
replace p23_5 = . if inlist(p23_5, 8, 9)
replace p23_6 = . if inlist(p23_6, 8, 9)

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
replace resp = . if resp == 3
drop if missing(resp)
sort id item
drop p23_1 p23_2 p23_3 p23_4 p23_5 p23_6

* verification

count
tab item
tab resp

export delimited using "spain_2026_prostitution_prostitution.csv", replace