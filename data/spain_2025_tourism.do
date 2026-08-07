*** This Stata Do File processes the spain_2025_tourism study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_tourism"

**# Bookmark 1: import and clean

import delimited "3521_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

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

save "spain_2025_tourism_master.dta", replace

**# Bookmark 2: importance

* ============================================================
* importance (GRADOIMPOR1_1 to GRADOIMPOR1_5, P5)
* ============================================================

use "spain_2025_tourism_master.dta", clear

local survey_cols gradoimpor1_1 gradoimpor1_2 gradoimpor1_3 gradoimpor1_4 gradoimpor1_5

keep id cov_* `survey_cols'

replace gradoimpor1_1 = . if inlist(gradoimpor1_1, 8, 9)
replace gradoimpor1_2 = . if inlist(gradoimpor1_2, 8, 9)
replace gradoimpor1_3 = . if inlist(gradoimpor1_3, 8, 9)
replace gradoimpor1_4 = . if inlist(gradoimpor1_4, 8, 9)
replace gradoimpor1_5 = . if inlist(gradoimpor1_5, 8, 9)

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
drop gradoimpor1_1 gradoimpor1_2 gradoimpor1_3 gradoimpor1_4 gradoimpor1_5

* verification

count
tab item
tab resp

export delimited using "spain_2025_tourism_importance.csv", replace