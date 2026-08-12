*** This Stata Do File processes the spain_2025_ageism study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_ageism"

import delimited "3493_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* recover variable names from labels where Stata mangled the quoted headers

foreach var of varlist _all {
    local lab : variable label `var'
    if "`lab'" != "" {
        local newname = subinstr("`lab'", char(34), "", .)
        local newname = trim("`newname'")
        capture rename `var' `newname'
    }
}

rename *, lower

destring _all, replace force

* clean covariates

rename sexo cov_sex
rename edad cov_age

replace cov_age = . if cov_age == 999

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

gen long id = _n

order id cov_*, first

compress

save "spain_2025_ageism_master.dta", replace

**# Bookmark 1: problems

* ============================================================
* problems (P1, P2)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p1 p2

keep id cov_* `survey_cols'

replace p1 = . if inlist(p1, 3, 8, 9)
replace p2 = . if inlist(p2, 3, 8, 9)

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
drop p1 p2
export delimited using "spain_2025_ageism_problems.csv", replace

**# Bookmark 2: agreement

* ============================================================
* agreement (P5_1 to P5_4)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p5_1 p5_2 p5_3 p5_4

keep id cov_* `survey_cols'

replace p5_1 = . if inlist(p5_1, 3, 8, 9)
replace p5_2 = . if inlist(p5_2, 3, 8, 9)
replace p5_3 = . if inlist(p5_3, 3, 8, 9)
replace p5_4 = . if inlist(p5_4, 3, 8, 9)

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
drop p5_1 p5_2 p5_3 p5_4
export delimited using "spain_2025_ageism_agreement.csv", replace

**# Bookmark 3: elderpriority

* ============================================================
* elderpriority (P6_1 to P6_7)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p6_1 p6_2 p6_3 p6_4 p6_5 p6_6 p6_7

keep id cov_* `survey_cols'

replace p6_1 = . if inlist(p6_1, 98, 99)
replace p6_2 = . if inlist(p6_2, 98, 99)
replace p6_3 = . if inlist(p6_3, 98, 99)
replace p6_4 = . if inlist(p6_4, 98, 99)
replace p6_5 = . if inlist(p6_5, 98, 99)
replace p6_6 = . if inlist(p6_6, 98, 99)
replace p6_7 = . if inlist(p6_7, 98, 99)

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
drop p6_1 p6_2 p6_3 p6_4 p6_5 p6_6 p6_7
export delimited using "spain_2025_ageism_elderpriority.csv", replace

**# Bookmark 4: youthpriority

* ============================================================
* youthpriority (P7_1 to P7_7)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p7_1 p7_2 p7_3 p7_4 p7_5 p7_6 p7_7

keep id cov_* `survey_cols'

replace p7_1 = . if inlist(p7_1, 98, 99)
replace p7_2 = . if inlist(p7_2, 98, 99)
replace p7_3 = . if inlist(p7_3, 98, 99)
replace p7_4 = . if inlist(p7_4, 98, 99)
replace p7_5 = . if inlist(p7_5, 98, 99)
replace p7_6 = . if inlist(p7_6, 98, 99)
replace p7_7 = . if inlist(p7_7, 98, 99)

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
drop p7_1 p7_2 p7_3 p7_4 p7_5 p7_6 p7_7
export delimited using "spain_2025_ageism_youthpriority.csv", replace

**# Bookmark 5: comparison

* ============================================================
* comparison (P8, P9, P10)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p8 p9 p10

keep id cov_* `survey_cols'

replace p8 = . if inlist(p8, 3, 8, 9)
replace p9 = . if inlist(p9, 3, 8, 9)
replace p10 = . if inlist(p10, 3, 8, 9)

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
drop p8 p9 p10
export delimited using "spain_2025_ageism_comparison.csv", replace

**# Bookmark 6: bureaucracy

* ============================================================
* bureaucracy (P11_1 to P11_6)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p11_1 p11_2 p11_3 p11_4 p11_5 p11_6

keep id cov_* `survey_cols'

replace p11_1 = . if inlist(p11_1, 0, 6, 8, 9)
replace p11_2 = . if inlist(p11_2, 0, 6, 8, 9)
replace p11_3 = . if inlist(p11_3, 0, 6, 8, 9)
replace p11_4 = . if inlist(p11_4, 0, 6, 8, 9)
replace p11_5 = . if inlist(p11_5, 0, 6, 8, 9)
replace p11_6 = . if inlist(p11_6, 0, 6, 8, 9)

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
drop p11_1 p11_2 p11_3 p11_4 p11_5 p11_6
export delimited using "spain_2025_ageism_bureaucracy.csv", replace

**# Bookmark 7: difficulty

* ============================================================
* difficulty (P12_1 to P12_5)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p12_1 p12_2 p12_3 p12_4 p12_5

keep id cov_* `survey_cols'

replace p12_1 = . if inlist(p12_1, 0, 3, 6, 8, 9)
replace p12_2 = . if inlist(p12_2, 0, 3, 6, 8, 9)
replace p12_3 = . if inlist(p12_3, 0, 3, 6, 8, 9)
replace p12_4 = . if inlist(p12_4, 0, 3, 6, 8, 9)
replace p12_5 = . if inlist(p12_5, 0, 3, 6, 8, 9)

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
drop p12_1 p12_2 p12_3 p12_4 p12_5
export delimited using "spain_2025_ageism_difficulty.csv", replace

**# Bookmark 8: elderslights

* ============================================================
* elderslights (P13_1 to P13_6)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p13_1 p13_2 p13_3 p13_4 p13_5 p13_6

keep id cov_* `survey_cols'

replace p13_1 = . if inlist(p13_1, 0, 8, 9)
replace p13_2 = . if inlist(p13_2, 0, 8, 9)
replace p13_3 = . if inlist(p13_3, 0, 8, 9)
replace p13_4 = . if inlist(p13_4, 0, 8, 9)
replace p13_5 = . if inlist(p13_5, 0, 8, 9)
replace p13_6 = . if inlist(p13_6, 0, 8, 9)

* code 7 is the lowest ordered category (Ninguna vez), recode to 4 for a contiguous 1 to 4 scale

replace p13_1 = 4 if p13_1 == 7
replace p13_2 = 4 if p13_2 == 7
replace p13_3 = 4 if p13_3 == 7
replace p13_4 = 4 if p13_4 == 7
replace p13_5 = 4 if p13_5 == 7
replace p13_6 = 4 if p13_6 == 7

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
drop p13_1 p13_2 p13_3 p13_4 p13_5 p13_6
export delimited using "spain_2025_ageism_elderslights.csv", replace

**# Bookmark 9: youthslights

* ============================================================
* youthslights (P16_1 to P16_4)
* ============================================================

use "spain_2025_ageism_master.dta", clear

local survey_cols p16_1 p16_2 p16_3 p16_4

keep id cov_* `survey_cols'

replace p16_1 = . if inlist(p16_1, 0, 3, 8, 9)
replace p16_2 = . if inlist(p16_2, 0, 3, 8, 9)
replace p16_3 = . if inlist(p16_3, 0, 3, 8, 9)
replace p16_4 = . if inlist(p16_4, 0, 3, 8, 9)

* code 7 is the lowest ordered category (Ninguna vez), recode to 5

replace p16_1 = 5 if p16_1 == 7
replace p16_2 = 5 if p16_2 == 7
replace p16_3 = 5 if p16_3 == 7
replace p16_4 = 5 if p16_4 == 7

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
drop p16_1 p16_2 p16_3 p16_4
export delimited using "spain_2025_ageism_youthslights.csv", replace