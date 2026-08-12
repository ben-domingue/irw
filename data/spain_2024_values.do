*** This Stata Do File processes the spain_2024_values study (CIS 3473) ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2024_values"

* import raw data (semicolon delimited, quote-wrapped plain variable names)

import delimited "3473_num.csv", delimiter(";") varnames(1) case(lower) encoding("UTF-8") clear

* destring

destring _all, replace force

* generate row id

gen long id = _n

* rename covariates (locked set: cov_sex, cov_age)

rename sexo cov_sex
rename edad cov_age

* clean covariates
* edad is true age (18 to 97 observed), no sentinel codes present

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

* save master

compress

save "spain_2024_values_master.dta", replace

**# Bookmark 1: institutions

* ============================================================
* institutions (P6_1 to P6_4), 1-5 agreement scale
* ============================================================

use "spain_2024_values_master.dta", clear

local survey_cols p6_1 p6_2 p6_3 p6_4

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace p6_1 = . if inlist(p6_1, 8, 9)
replace p6_2 = . if inlist(p6_2, 8, 9)
replace p6_3 = . if inlist(p6_3, 8, 9)
replace p6_4 = . if inlist(p6_4, 8, 9)

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
keep id item resp cov_*
export delimited using "spain_2024_values_institutions.csv", replace

**# Bookmark 2: meaning

* ============================================================
* meaning (P5, P7_1 to P7_4), 1-5 agreement scale
* ============================================================

use "spain_2024_values_master.dta", clear

local survey_cols p5 p7_1 p7_2 p7_3 p7_4

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace p5 = . if inlist(p5, 8, 9)
replace p7_1 = . if inlist(p7_1, 8, 9)
replace p7_2 = . if inlist(p7_2, 8, 9)
replace p7_3 = . if inlist(p7_3, 8, 9)
replace p7_4 = . if inlist(p7_4, 8, 9)

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
keep id item resp cov_*
export delimited using "spain_2024_values_meaning.csv", replace

**# Bookmark 3: values

* ============================================================
* values (P8_1 to P8_3), 1-5 agreement scale
* ============================================================

use "spain_2024_values_master.dta", clear

local survey_cols p8_1 p8_2 p8_3

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace p8_1 = . if inlist(p8_1, 8, 9)
replace p8_2 = . if inlist(p8_2, 8, 9)
replace p8_3 = . if inlist(p8_3, 8, 9)

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
keep id item resp cov_*
export delimited using "spain_2024_values_values.csv", replace

**# Bookmark 4: difficulty

* ============================================================
* difficulty (P10, P11), 1-5 easy to difficult scale
* ============================================================

use "spain_2024_values_master.dta", clear

local survey_cols p10 p11

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

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
replace resp = . if resp == 3
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_values_difficulty.csv", replace

**# Bookmark 5: political

* ============================================================
* political (ESCIDEOL 1-10, PROBVOTO 0-10)
* sentinels differ by item, recoded separately
* ============================================================

use "spain_2024_values_master.dta", clear

local survey_cols escideol probvoto

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data
* probvoto code 96 is not documented in the codebook but matches the
* not-applicable cases exactly, so it is treated as missing

replace escideol = . if inlist(escideol, 98, 99)
replace probvoto = . if inlist(probvoto, 96, 98, 99)

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
keep id item resp cov_*
export delimited using "spain_2024_values_political.csv", replace