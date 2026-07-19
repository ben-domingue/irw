*** This Stata Do File processes the spain_2025_sex study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_sex"

* read raw data (semicolon-delimited; variable names are wrapped in double quotes)

import delimited "3515_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

foreach v of varlist _all {
    local lbl : variable label `v'
    if strpos("`lbl'", ":") > 0 {
        local newname = trim(substr("`lbl'", 1, strpos("`lbl'", ":") - 1))
        local newname = subinstr("`newname'", `"""', "", .)
        capture rename `v' `newname'
    }
}

rename *, lower

* destring
destring _all, replace force

* row id
gen long id = _n

* ============================================================
* Clean covariates
* ============================================================

rename sexo cov_sex
rename edad cov_age

replace cov_age = . if cov_age >= 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

* compress and save master
compress
save "spain_2025_sex_master.dta", replace

**# Table 1: attitudes

* ============================================================
* attitudes (A5_1 to A5_5), agreement scale 1-5, sentinel 8/9
* ============================================================

use "spain_2025_sex_master.dta", clear

local survey_cols a5_1 a5_2 a5_3 a5_4 a5_5

keep id cov_* `survey_cols'

replace a5_1 = . if inlist(a5_1, 8, 9)
replace a5_2 = . if inlist(a5_2, 8, 9)
replace a5_3 = . if inlist(a5_3, 8, 9)
replace a5_4 = . if inlist(a5_4, 8, 9)
replace a5_5 = . if inlist(a5_5, 8, 9)

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
drop a5_1 a5_2 a5_3 a5_4 a5_5
export delimited using "spain_2025_sex_attitudes.csv", replace

**# Table 2: frequency

* ============================================================
* frequency (B2_1 to B2_6), frequency scale 1-4, sentinel 8/9
* B2_3 to B2_6 also carry 0 = filtered N.P.
* ============================================================

use "spain_2025_sex_master.dta", clear

local survey_cols b2_1 b2_2 b2_3 b2_4 b2_5 b2_6

keep id cov_* `survey_cols'

replace b2_1 = . if inlist(b2_1, 8, 9)
replace b2_2 = . if inlist(b2_2, 8, 9)
replace b2_3 = . if inlist(b2_3, 0, 8, 9)
replace b2_4 = . if inlist(b2_4, 0, 8, 9)
replace b2_5 = . if inlist(b2_5, 0, 8, 9)
replace b2_6 = . if inlist(b2_6, 0, 8, 9)

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
drop b2_1 b2_2 b2_3 b2_4 b2_5 b2_6
export delimited using "spain_2025_sex_frequency.csv", replace

**# Table 3: identity

* ============================================================
* identity (A7, A9, A10, A13) - mixed scales, sentinels per item
* A7  yes/no (1/2), sentinel 8/9
* A9  yes/no (1/2), sentinel 0 (filter N.P.), 9
* A10 satisfaction 1-5, sentinel 8/9
* A13 yes/no (1/2), sentinel 8/9
* ============================================================

use "spain_2025_sex_master.dta", clear

local survey_cols a7 a9 a10 a13

keep id cov_* `survey_cols'

replace a7 = . if inlist(a7, 8, 9)
replace a9 = . if inlist(a9, 0, 9)
replace a10 = . if inlist(a10, 8, 9)
replace a13 = . if inlist(a13, 8, 9)

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
drop a7 a9 a10 a13
export delimited using "spain_2025_sex_identity.csv", replace

**# Table 4: condom

* ============================================================
* condom (D6, D7), condom-use frequency 1-5, sentinel 0/7/9
* 0 = filtered N.P., 7 = only oral relations (non-scale), 9 = N.C.
* ============================================================

use "spain_2025_sex_master.dta", clear

local survey_cols d6 d7

keep id cov_* `survey_cols'

replace d6 = . if inlist(d6, 0, 7, 9)
replace d7 = . if inlist(d7, 0, 7, 9)

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
drop d6 d7
export delimited using "spain_2025_sex_condom.csv", replace