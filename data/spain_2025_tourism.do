*** This Stata Do File processes the spain_2026_disinformation study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2026_disinformation"

import delimited "3563_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* header cells are "VARNAME: descriptive label"; recover the true variable name
foreach v of varlist _all {
    local lbl : variable label `v'
    local newname = trim(substr("`lbl'", 1, strpos("`lbl'", ":") - 1))
    rename `v' `newname'
}

destring _all, replace force

gen id = _n

* rename covariates

rename SEXO cov_sex
rename EDAD cov_age

* lower case everything
rename *, lower

* clean covariates

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

save "spain_2026_master.dta", replace

**# Table 1: concern

* ============================================================
* concern (P1, DESINFOR_1 to DESINFOR_4, P12_1 to P12_5)
* mucho/bastante/poco/nada severity of disinformation's harm
* to institutions and society
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p1 desinfor_1 desinfor_2 desinfor_3 desinfor_4 p12_1 p12_2 p12_3 p12_4 p12_5

keep id cov_* `survey_cols'

replace p1 = . if inlist(p1, 8, 9)
replace desinfor_1 = . if inlist(desinfor_1, 8, 9)
replace desinfor_2 = . if inlist(desinfor_2, 8, 9)
replace desinfor_3 = . if inlist(desinfor_3, 8, 9)
replace desinfor_4 = . if inlist(desinfor_4, 8, 9)
replace p12_1 = . if inlist(p12_1, 8, 9)
replace p12_2 = . if inlist(p12_2, 8, 9)
replace p12_3 = . if inlist(p12_3, 8, 9)
replace p12_4 = . if inlist(p12_4, 8, 9)
replace p12_5 = . if inlist(p12_5, 8, 9)

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
drop p1 desinfor_1 desinfor_2 desinfor_3 desinfor_4 p12_1 p12_2 p12_3 p12_4 p12_5
export delimited using "spain_2026_disinformation_concern.csv", replace

**# Table 2: hostility

* ============================================================
* hostility (P10_1 to P10_4)
* mucho/bastante/poco/nada contribution of disinformation to
* intolerance and hatred toward groups
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p10_1 p10_2 p10_3 p10_4

keep id cov_* `survey_cols'

replace p10_1 = . if inlist(p10_1, 8, 9)
replace p10_2 = . if inlist(p10_2, 8, 9)
replace p10_3 = . if inlist(p10_3, 8, 9)
replace p10_4 = . if inlist(p10_4, 8, 9)

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
drop p10_1 p10_2 p10_3 p10_4
export delimited using "spain_2026_disinformation_hostility.csv", replace

**# Table 3: regulation

* ============================================================
* regulation (P3, P4, P5, P6)
* support for countermeasures against disinformation
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p3 p4 p5 p6

keep id cov_* `survey_cols'

replace p3 = . if inlist(p3, 3, 8, 9)
replace p6 = . if inlist(p6, 3, 8, 9)
replace p4 = . if inlist(p4, 8, 9)
replace p5 = . if inlist(p5, 8, 9)

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
drop p3 p4 p5 p6
export delimited using "spain_2026_disinformation_regulation.csv", replace

**# Table 4: memes

* ============================================================
* memes (P14, P15_1 to P15_6)
* frequency of receiving memes/jokes overall and by topic
* P15 battery uses 0 for filtered non-recipients
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p14 p15_1 p15_2 p15_3 p15_4 p15_5 p15_6

keep id cov_* `survey_cols'

replace p14 = . if inlist(p14, 8, 9)
replace p15_1 = . if inlist(p15_1, 0, 8, 9)
replace p15_2 = . if inlist(p15_2, 0, 8, 9)
replace p15_3 = . if inlist(p15_3, 0, 8, 9)
replace p15_4 = . if inlist(p15_4, 0, 8, 9)
replace p15_5 = . if inlist(p15_5, 0, 8, 9)
replace p15_6 = . if inlist(p15_6, 0, 8, 9)

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
drop p14 p15_1 p15_2 p15_3 p15_4 p15_5 p15_6
export delimited using "spain_2026_disinformation_memes.csv", replace

**# Table 5: offense

* ============================================================
* offense (P23_1 to P23_4)
* how much humor about sensitive topics bothers the respondent
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p23_1 p23_2 p23_3 p23_4

keep id cov_* `survey_cols'

replace p23_1 = . if inlist(p23_1, 8, 9)
replace p23_2 = . if inlist(p23_2, 8, 9)
replace p23_3 = . if inlist(p23_3, 8, 9)
replace p23_4 = . if inlist(p23_4, 8, 9)

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
drop p23_1 p23_2 p23_3 p23_4
export delimited using "spain_2026_disinformation_offense.csv", replace

**# Table 6: personalhumor

* ============================================================
* personalhumor (P16, P17, P18, P20, P21, P25)
* respondent's own relationship to humor
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p16 p17 p18 p20 p21 p25

keep id cov_* `survey_cols'

replace p16 = . if inlist(p16, 8, 9)
replace p17 = . if inlist(p17, 8, 9)
replace p18 = . if inlist(p18, 8, 9)
replace p20 = . if inlist(p20, 8, 9)
replace p21 = . if inlist(p21, 8, 9)
replace p25 = . if inlist(p25, 8, 9)

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
drop p16 p17 p18 p20 p21 p25
export delimited using "spain_2026_disinformation_personalhumor.csv", replace

**# Table 7: humorlimits

* ============================================================
* humorlimits (P13, P24)
* normative limits on humor
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p13 p24

keep id cov_* `survey_cols'

replace p13 = . if inlist(p13, 3, 8, 9)
replace p24 = . if inlist(p24, 3, 8, 9)

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
drop p13 p24
export delimited using "spain_2026_disinformation_humorlimits.csv", replace

**# Table 8: humorclimate

* ============================================================
* humorclimate (P29, P30)
* freedom and change in Spain's humor environment
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p29 p30

keep id cov_* `survey_cols'

replace p29 = . if inlist(p29, 8, 9)
replace p30 = . if inlist(p30, 8, 9)

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
drop p29 p30
export delimited using "spain_2026_disinformation_humorclimate.csv", replace

**# Table 9: humorperception

* ============================================================
* humorperception (P26, P27, P28)
* perception of Spaniards and Spain regarding humor
* ============================================================

use "spain_2026_master.dta", clear

local survey_cols p26 p27 p28

keep id cov_* `survey_cols'

replace p26 = . if inlist(p26, 8, 9)
replace p27 = . if inlist(p27, 8, 9)
replace p28 = . if inlist(p28, 8, 9)

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
drop p26 p27 p28
export delimited using "spain_2026_disinformation_humorperception.csv", replace