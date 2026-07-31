*** This Stata Do File processes the spain_2025_fears study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_fears"

import delimited "3534_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

destring _all, replace force

rename *, lower

gen long id = _n

* rename covariates

rename sexo cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 999

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2025_fears_master.dta", replace

**# Bookmark 1: prospect

* ============================================================
* prospect (P10, P11)
* ============================================================

use "spain_2025_fears_master.dta", clear

local survey_cols p10 p11

keep id cov_* `survey_cols'

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
drop p10 p11
export delimited using "spain_2025_fears_prospect.csv", replace

**# Bookmark 2: leaders

* ============================================================
* leaders (VALORALIDERES_1 to VALORALIDERES_4)
* ============================================================

use "spain_2025_fears_master.dta", clear

local survey_cols valoralideres_1 valoralideres_2 valoralideres_3 valoralideres_4

keep id cov_* `survey_cols'

replace valoralideres_1 = . if inlist(valoralideres_1, 0, 98, 99)
replace valoralideres_2 = . if inlist(valoralideres_2, 0, 98, 99)
replace valoralideres_3 = . if inlist(valoralideres_3, 0, 98, 99)
replace valoralideres_4 = . if inlist(valoralideres_4, 0, 98, 99)

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
drop valoralideres_1 valoralideres_2 valoralideres_3 valoralideres_4
export delimited using "spain_2025_fears_leaders.csv", replace