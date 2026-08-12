*** This Stata Do File processes the spain_2025_democracy study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_democracy"

* import study dataset

import delimited "3497_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* convert column names to lowercase

rename *, lower

* destring

destring _all, replace force

* clean covariates

rename sexo cov_sex
rename edad cov_age

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

* generate id

gen long id = _n

order id cov_*, first

compress

save "spain_2025_democracy_master.dta", replace

**# Bookmark 1: system

* ============================================================
* system (P2, P7, P11)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p2 p7 p11

keep id cov_* `survey_cols'

replace p2 = . if inlist(p2, 3, 8, 9)
replace p7 = . if inlist(p7, 8, 9)
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
keep id cov_* item resp
export delimited using "spain_2025_democracy_system.csv", replace

**# Bookmark 2: parties

* ============================================================
* parties (P3P_1 to P3P_5)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p3p_1 p3p_2 p3p_3 p3p_4 p3p_5

keep id cov_* `survey_cols'

replace p3p_1 = . if inlist(p3p_1, 3, 8, 9)
replace p3p_2 = . if inlist(p3p_2, 3, 8, 9)
replace p3p_3 = . if inlist(p3p_3, 3, 8, 9)
replace p3p_4 = . if inlist(p3p_4, 3, 8, 9)
replace p3p_5 = . if inlist(p3p_5, 3, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2025_democracy_parties.csv", replace

**# Bookmark 3: internal

* ============================================================
* internal (P3AP_1 to P3AP_5)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p3ap_1 p3ap_2 p3ap_3 p3ap_4 p3ap_5

keep id cov_* `survey_cols'

replace p3ap_1 = . if inlist(p3ap_1, 3, 8, 9)
replace p3ap_2 = . if inlist(p3ap_2, 3, 8, 9)
replace p3ap_3 = . if inlist(p3ap_3, 3, 8, 9)
replace p3ap_4 = . if inlist(p3ap_4, 3, 8, 9)
replace p3ap_5 = . if inlist(p3ap_5, 3, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2025_democracy_internal.csv", replace

**# Bookmark 4: judiciary

* ============================================================
* judiciary (P4JU_1 to P4JU_4)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p4ju_1 p4ju_2 p4ju_3 p4ju_4

keep id cov_* `survey_cols'

replace p4ju_1 = . if inlist(p4ju_1, 3, 8, 9)
replace p4ju_2 = . if inlist(p4ju_2, 3, 8, 9)
replace p4ju_3 = . if inlist(p4ju_3, 3, 8, 9)
replace p4ju_4 = . if inlist(p4ju_4, 3, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2025_democracy_judiciary.csv", replace

**# Bookmark 5: media

* ============================================================
* media (P5ME_1 to P5ME_4)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p5me_1 p5me_2 p5me_3 p5me_4

keep id cov_* `survey_cols'

replace p5me_1 = . if inlist(p5me_1, 3, 8, 9)
replace p5me_2 = . if inlist(p5me_2, 3, 8, 9)
replace p5me_3 = . if inlist(p5me_3, 3, 8, 9)
replace p5me_4 = . if inlist(p5me_4, 3, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2025_democracy_media.csv", replace

**# Bookmark 6: efficacy

* ============================================================
* efficacy (P8DE_1 to P8DE_4)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p8de_1 p8de_2 p8de_3 p8de_4

keep id cov_* `survey_cols'

replace p8de_1 = . if inlist(p8de_1, 3, 8, 9)
replace p8de_2 = . if inlist(p8de_2, 3, 8, 9)
replace p8de_3 = . if inlist(p8de_3, 3, 8, 9)
replace p8de_4 = . if inlist(p8de_4, 3, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2025_democracy_efficacy.csv", replace

**# Bookmark 7: trust

* ============================================================
* trust (P10GR_1 to P10GR_10)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p10gr_1 p10gr_2 p10gr_3 p10gr_4 p10gr_5 p10gr_6 p10gr_7 p10gr_8 p10gr_9 p10gr_10

keep id cov_* `survey_cols'

replace p10gr_1 = . if inlist(p10gr_1, 98, 99)
replace p10gr_2 = . if inlist(p10gr_2, 98, 99)
replace p10gr_3 = . if inlist(p10gr_3, 98, 99)
replace p10gr_4 = . if inlist(p10gr_4, 98, 99)
replace p10gr_5 = . if inlist(p10gr_5, 98, 99)
replace p10gr_6 = . if inlist(p10gr_6, 98, 99)
replace p10gr_7 = . if inlist(p10gr_7, 98, 99)
replace p10gr_8 = . if inlist(p10gr_8, 98, 99)
replace p10gr_9 = . if inlist(p10gr_9, 98, 99)
replace p10gr_10 = . if inlist(p10gr_10, 98, 99)

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
keep id cov_* item resp
export delimited using "spain_2025_democracy_trust.csv", replace

**# Bookmark 8: priorities

* ============================================================
* priorities (P12_1 to P12_8)
* ============================================================

use "spain_2025_democracy_master.dta", clear

local survey_cols p12_1 p12_2 p12_3 p12_4 p12_5 p12_6 p12_7 p12_8

keep id cov_* `survey_cols'

replace p12_1 = . if inlist(p12_1, 8, 9)
replace p12_2 = . if inlist(p12_2, 8, 9)
replace p12_3 = . if inlist(p12_3, 8, 9)
replace p12_4 = . if inlist(p12_4, 8, 9)
replace p12_5 = . if inlist(p12_5, 8, 9)
replace p12_6 = . if inlist(p12_6, 8, 9)
replace p12_7 = . if inlist(p12_7, 8, 9)
replace p12_8 = . if inlist(p12_8, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2025_democracy_priorities.csv", replace