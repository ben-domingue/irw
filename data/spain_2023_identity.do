*** This Stata Do File processes the spain_2023_identity study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2023_identity"

import delimited "3409_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

destring _all, replace force

rename *, lower

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename sexo cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2023_identity_master.dta", replace

**# Bookmark 1: identification

* ============================================================
* identification (P5_1 to P5_9)
* 1-5 identification scale, code 3 is a (NO LEER) volunteered midpoint
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols p5_1 p5_2 p5_3 p5_4 p5_5 p5_6 p5_7 p5_8 p5_9

keep id cov_* `survey_cols'

replace p5_1 = . if inlist(p5_1, 3, 8, 9)
replace p5_2 = . if inlist(p5_2, 3, 8, 9)
replace p5_3 = . if inlist(p5_3, 3, 8, 9)
replace p5_4 = . if inlist(p5_4, 3, 8, 9)
replace p5_5 = . if inlist(p5_5, 3, 8, 9)
replace p5_6 = . if inlist(p5_6, 3, 8, 9)
replace p5_7 = . if inlist(p5_7, 3, 8, 9)
replace p5_8 = . if inlist(p5_8, 3, 8, 9)
replace p5_9 = . if inlist(p5_9, 3, 8, 9)

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
export delimited using "spain_2023_identity_identification.csv", replace

**# Bookmark 2: territorial

* ============================================================
* territorial (P7_1 to P7_5)
* 0-10 identification with territorial units
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols p7_1 p7_2 p7_3 p7_4 p7_5

keep id cov_* `survey_cols'

replace p7_1 = . if inlist(p7_1, 98, 99)
replace p7_2 = . if inlist(p7_2, 98, 99)
replace p7_3 = . if inlist(p7_3, 98, 99)
replace p7_4 = . if inlist(p7_4, 98, 99)
replace p7_5 = . if inlist(p7_5, 98, 99)

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
export delimited using "spain_2023_identity_territorial.csv", replace

**# Bookmark 3: authenticity

* ============================================================
* authenticity (P8_1 to P8_5)
* importance scale coded 1, 2, 3, 7 where 7 (Ninguna) is a valid lowest category
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols p8_1 p8_2 p8_3 p8_4 p8_5

keep id cov_* `survey_cols'

replace p8_1 = . if inlist(p8_1, 8, 9)
replace p8_2 = . if inlist(p8_2, 8, 9)
replace p8_3 = . if inlist(p8_3, 8, 9)
replace p8_4 = . if inlist(p8_4, 8, 9)
replace p8_5 = . if inlist(p8_5, 8, 9)

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
replace resp = 4 if resp == 7
export delimited using "spain_2023_identity_authenticity.csv", replace

**# Bookmark 4: patriotism

* ============================================================
* patriotism (P9_1 to P9_3)
* agree/disagree, code 2 is a (NO LEER) volunteered midpoint
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols p9_1 p9_2 p9_3

keep id cov_* `survey_cols'

replace p9_1 = . if inlist(p9_1, 2, 9)
replace p9_2 = . if inlist(p9_2, 2, 9)
replace p9_3 = . if inlist(p9_3, 2, 9)

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
export delimited using "spain_2023_identity_patriotism.csv", replace

**# Bookmark 5: pride

* ============================================================
* pride (P11, P12)
* 1-4 pride in being Spanish / of the autonomous community
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols p11 p12

keep id cov_* `survey_cols'

replace p11 = . if inlist(p11, 8, 9)
replace p12 = . if inlist(p12, 8, 9)

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
export delimited using "spain_2023_identity_pride.csv", replace

**# Bookmark 6: state

* ============================================================
* state (P13, P14)
* territorial organization preference and functioning valuation, 1-5
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols p13 p14

keep id cov_* `survey_cols'

replace p13 = . if inlist(p13, 8, 9)
replace p14 = . if inlist(p14, 8, 9)

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
export delimited using "spain_2023_identity_state.csv", replace

**# Bookmark 7: centralism

* ============================================================
* centralism (ESCALACENTRALISMO_1 to ESCALACENTRALISMO_6)
* 1-10 party placement on centralism/decentralization
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols escalacentralismo_1 escalacentralismo_2 escalacentralismo_3 escalacentralismo_4 escalacentralismo_5 escalacentralismo_6

keep id cov_* `survey_cols'

replace escalacentralismo_1 = . if inlist(escalacentralismo_1, 98, 99)
replace escalacentralismo_2 = . if inlist(escalacentralismo_2, 98, 99)
replace escalacentralismo_3 = . if inlist(escalacentralismo_3, 98, 99)
replace escalacentralismo_4 = . if inlist(escalacentralismo_4, 98, 99)
replace escalacentralismo_5 = . if inlist(escalacentralismo_5, 98, 99)
replace escalacentralismo_6 = . if inlist(escalacentralismo_6, 98, 99)

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
export delimited using "spain_2023_identity_centralism.csv", replace

**# Bookmark 8: europe

* ============================================================
* europe (P16, P17)
* benefit/harm of EU membership, code 2 is a (NO LEER) volunteered midpoint
* ============================================================

use "spain_2023_identity_master.dta", clear

local survey_cols p16 p17

keep id cov_* `survey_cols'

replace p16 = . if inlist(p16, 2, 8, 9)
replace p17 = . if inlist(p17, 2, 8, 9)

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
export delimited using "spain_2023_identity_europe.csv", replace