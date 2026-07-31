*** This Stata Do File processes the spain_2026_love study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2026_love"

import delimited "3508_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* recover true variable names from the CIS header labels

foreach var of varlist _all {
    local lab : variable label `var'
    local newname = substr("`lab'", 1, strpos("`lab'", ":") - 1)
    rename `var' `newname'
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

compress

save "spain_2026_love_master.dta", replace

**# Bookmark 1: importance

* ============================================================
* importance (P1_1 to P1_10)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p1_1 p1_2 p1_3 p1_4 p1_5 p1_6 p1_7 p1_8 p1_9 p1_10

keep id cov_* `survey_cols'

replace p1_1 = . if inlist(p1_1, 8, 9)
replace p1_2 = . if inlist(p1_2, 8, 9)
replace p1_3 = . if inlist(p1_3, 8, 9)
replace p1_4 = . if inlist(p1_4, 8, 9)
replace p1_5 = . if inlist(p1_5, 8, 9)
replace p1_6 = . if inlist(p1_6, 8, 9)
replace p1_7 = . if inlist(p1_7, 8, 9)
replace p1_8 = . if inlist(p1_8, 8, 9)
replace p1_9 = . if inlist(p1_9, 8, 9)
replace p1_10 = . if inlist(p1_10, 8, 9)

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
drop p1_1 p1_2 p1_3 p1_4 p1_5 p1_6 p1_7 p1_8 p1_9 p1_10
export delimited using "spain_2026_love_importance.csv", replace

**# Bookmark 2: association

* ============================================================
* association (P3_1 to P3_9)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p3_1 p3_2 p3_3 p3_4 p3_5 p3_6 p3_7 p3_8 p3_9

keep id cov_* `survey_cols'

replace p3_1 = . if inlist(p3_1, 8, 9)
replace p3_2 = . if inlist(p3_2, 8, 9)
replace p3_3 = . if inlist(p3_3, 8, 9)
replace p3_4 = . if inlist(p3_4, 8, 9)
replace p3_5 = . if inlist(p3_5, 8, 9)
replace p3_6 = . if inlist(p3_6, 8, 9)
replace p3_7 = . if inlist(p3_7, 8, 9)
replace p3_8 = . if inlist(p3_8, 8, 9)
replace p3_9 = . if inlist(p3_9, 8, 9)

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
drop p3_1 p3_2 p3_3 p3_4 p3_5 p3_6 p3_7 p3_8 p3_9
export delimited using "spain_2026_love_association.csv", replace

**# Bookmark 3: attitudes

* ============================================================
* attitudes (P4_1 to P4_8)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p4_1 p4_2 p4_3 p4_4 p4_5 p4_6 p4_7 p4_8

keep id cov_* `survey_cols'

replace p4_1 = . if inlist(p4_1, 8, 9)
replace p4_2 = . if inlist(p4_2, 8, 9)
replace p4_3 = . if inlist(p4_3, 8, 9)
replace p4_4 = . if inlist(p4_4, 8, 9)
replace p4_5 = . if inlist(p4_5, 8, 9)
replace p4_6 = . if inlist(p4_6, 8, 9)
replace p4_7 = . if inlist(p4_7, 8, 9)
replace p4_8 = . if inlist(p4_8, 8, 9)

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
drop p4_1 p4_2 p4_3 p4_4 p4_5 p4_6 p4_7 p4_8
export delimited using "spain_2026_love_attitudes.csv", replace

**# Bookmark 4: apps

* ============================================================
* apps (P16_1 to P16_7)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p16_1 p16_2 p16_3 p16_4 p16_5 p16_6 p16_7

keep id cov_* `survey_cols'

replace p16_1 = . if inlist(p16_1, 0, 8, 9)
replace p16_2 = . if inlist(p16_2, 0, 8, 9)
replace p16_3 = . if inlist(p16_3, 0, 8, 9)
replace p16_4 = . if inlist(p16_4, 0, 8, 9)
replace p16_5 = . if inlist(p16_5, 0, 8, 9)
replace p16_6 = . if inlist(p16_6, 0, 8, 9)
replace p16_7 = . if inlist(p16_7, 0, 8, 9)

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
drop p16_1 p16_2 p16_3 p16_4 p16_5 p16_6 p16_7
export delimited using "spain_2026_love_apps.csv", replace

**# Bookmark 5: gestures

* ============================================================
* gestures (P7, P8, P9)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p7 p8 p9

keep id cov_* `survey_cols'

replace p7 = . if inlist(p7, 8, 9)
replace p8 = . if inlist(p8, 8, 9)
replace p9 = . if inlist(p9, 8, 9)

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
drop p7 p8 p9
export delimited using "spain_2026_love_gestures.csv", replace

**# Bookmark 6: conceptions

* ============================================================
* conceptions (P10, P11, P12, P13)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p10 p11 p12 p13

keep id cov_* `survey_cols'

replace p10 = . if inlist(p10, 8, 9)
replace p11 = . if inlist(p11, 8, 9)
replace p12 = . if inlist(p12, 8, 9)
replace p13 = . if inlist(p13, 8, 9)

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
drop p10 p11 p12 p13
export delimited using "spain_2026_love_conceptions.csv", replace

**# Bookmark 7: usage

* ============================================================
* usage (P15, P15A, P15B)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p15 p15a p15b

keep id cov_* `survey_cols'

replace p15 = . if inlist(p15, 8, 9)
replace p15a = . if inlist(p15a, 0, 8, 9)
replace p15b = . if inlist(p15b, 0, 8, 9)

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
drop p15 p15a p15b
export delimited using "spain_2026_love_usage.csv", replace

**# Bookmark 8: desire

* ============================================================
* desire (P19, P22A)
* ============================================================

use "spain_2026_love_master.dta", clear

local survey_cols p19 p22a

keep id cov_* `survey_cols'

replace p19 = . if inlist(p19, 0, 8, 9)
replace p22a = . if inlist(p22a, 0, 8, 9)

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
drop p19 p22a
export delimited using "spain_2026_love_desire.csv", replace