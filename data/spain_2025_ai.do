*** This Stata Do File processes the spain_2025_ai study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_ai"

* import study dataset

import delimited "3495_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

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

save "spain_2025_ai_master.dta", replace

**# Bookmark 1: impact

* ============================================================
* impact (P1, P4)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p1 p4

keep id cov_* `survey_cols'

replace p1 = . if inlist(p1, 8, 9)
replace p4 = . if inlist(p4, 8, 9)

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
export delimited using "spain_2025_ai_impact.csv", replace

**# Bookmark 2: concern

* ============================================================
* concern (P5, P6)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p5 p6

keep id cov_* `survey_cols'

replace p5 = . if inlist(p5, 3, 6, 8, 9)
replace p6 = . if inlist(p6, 3, 6, 8, 9)

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
export delimited using "spain_2025_ai_concern.csv", replace

**# Bookmark 3: association

* ============================================================
* association (P3_1 to P3_12)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p3_1 p3_2 p3_3 p3_4 p3_5 p3_6 p3_7 p3_8 p3_9 p3_10 p3_11 p3_12

keep id cov_* `survey_cols'

replace p3_1 = . if inlist(p3_1, 98, 99)
replace p3_2 = . if inlist(p3_2, 98, 99)
replace p3_3 = . if inlist(p3_3, 98, 99)
replace p3_4 = . if inlist(p3_4, 98, 99)
replace p3_5 = . if inlist(p3_5, 98, 99)
replace p3_6 = . if inlist(p3_6, 98, 99)
replace p3_7 = . if inlist(p3_7, 98, 99)
replace p3_8 = . if inlist(p3_8, 98, 99)
replace p3_9 = . if inlist(p3_9, 98, 99)
replace p3_10 = . if inlist(p3_10, 98, 99)
replace p3_11 = . if inlist(p3_11, 98, 99)
replace p3_12 = . if inlist(p3_12, 98, 99)

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
export delimited using "spain_2025_ai_association.csv", replace

**# Bookmark 4: risk

* ============================================================
* risk (P7_1 to P7_6)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p7_1 p7_2 p7_3 p7_4 p7_5 p7_6

keep id cov_* `survey_cols'

replace p7_1 = . if inlist(p7_1, 8, 9)
replace p7_2 = . if inlist(p7_2, 8, 9)
replace p7_3 = . if inlist(p7_3, 8, 9)
replace p7_4 = . if inlist(p7_4, 8, 9)
replace p7_5 = . if inlist(p7_5, 8, 9)
replace p7_6 = . if inlist(p7_6, 8, 9)

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
export delimited using "spain_2025_ai_risk.csv", replace

**# Bookmark 5: datause

* ============================================================
* datause (P8_1 to P8_4)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p8_1 p8_2 p8_3 p8_4

keep id cov_* `survey_cols'

replace p8_1 = . if inlist(p8_1, 3, 8, 9)
replace p8_2 = . if inlist(p8_2, 3, 8, 9)
replace p8_3 = . if inlist(p8_3, 3, 8, 9)
replace p8_4 = . if inlist(p8_4, 3, 8, 9)

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
export delimited using "spain_2025_ai_datause.csv", replace

**# Bookmark 6: awareness

* ============================================================
* awareness (P10, P18_1_1 to P18_1_4)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p10 p18_1_1 p18_1_2 p18_1_3 p18_1_4

keep id cov_* `survey_cols'

replace p10 = . if inlist(p10, 8, 9)
replace p18_1_1 = . if inlist(p18_1_1, 0, 8, 9)
replace p18_1_2 = . if inlist(p18_1_2, 0, 8, 9)
replace p18_1_3 = . if inlist(p18_1_3, 0, 8, 9)
replace p18_1_4 = . if inlist(p18_1_4, 0, 8, 9)

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
export delimited using "spain_2025_ai_awareness.csv", replace

**# Bookmark 7: tools

* ============================================================
* tools (P12_1_1 to P12_1_5)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p12_1_1 p12_1_2 p12_1_3 p12_1_4 p12_1_5

keep id cov_* `survey_cols'

replace p12_1_1 = . if inlist(p12_1_1, 0, 8, 9)
replace p12_1_2 = . if inlist(p12_1_2, 0, 8, 9)
replace p12_1_3 = . if inlist(p12_1_3, 0, 8, 9)
replace p12_1_4 = . if inlist(p12_1_4, 0, 8, 9)
replace p12_1_5 = . if inlist(p12_1_5, 0, 8, 9)

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
export delimited using "spain_2025_ai_tools.csv", replace

**# Bookmark 8: frequency

* ============================================================
* frequency (P12_2_1 to P12_2_5)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p12_2_1 p12_2_2 p12_2_3 p12_2_4 p12_2_5

keep id cov_* `survey_cols'

replace p12_2_1 = . if inlist(p12_2_1, 0, 8, 9)
replace p12_2_2 = . if inlist(p12_2_2, 0, 8, 9)
replace p12_2_3 = . if inlist(p12_2_3, 0, 8, 9)
replace p12_2_4 = . if inlist(p12_2_4, 0, 8, 9)
replace p12_2_5 = . if inlist(p12_2_5, 0, 8, 9)

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
export delimited using "spain_2025_ai_frequency.csv", replace

**# Bookmark 9: comfort

* ============================================================
* comfort (P13_1 to P13_3, P19)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p13_1 p13_2 p13_3 p19

keep id cov_* `survey_cols'

replace p13_1 = . if inlist(p13_1, 0, 98, 99)
replace p13_2 = . if inlist(p13_2, 0, 98, 99)
replace p13_3 = . if inlist(p13_3, 0, 98, 99)
replace p19 = . if inlist(p19, 0, 98, 99)

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
export delimited using "spain_2025_ai_comfort.csv", replace

**# Bookmark 10: sectors

* ============================================================
* sectors (P14_1 to P14_8)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p14_1 p14_2 p14_3 p14_4 p14_5 p14_6 p14_7 p14_8

keep id cov_* `survey_cols'

replace p14_1 = . if inlist(p14_1, 0, 8, 9)
replace p14_2 = . if inlist(p14_2, 0, 8, 9)
replace p14_3 = . if inlist(p14_3, 0, 8, 9)
replace p14_4 = . if inlist(p14_4, 0, 8, 9)
replace p14_5 = . if inlist(p14_5, 0, 8, 9)
replace p14_6 = . if inlist(p14_6, 0, 8, 9)
replace p14_7 = . if inlist(p14_7, 0, 8, 9)
replace p14_8 = . if inlist(p14_8, 0, 8, 9)

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
export delimited using "spain_2025_ai_sectors.csv", replace

**# Bookmark 11: aspects

* ============================================================
* aspects (P15_1 to P15_4)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p15_1 p15_2 p15_3 p15_4

keep id cov_* `survey_cols'

replace p15_1 = . if inlist(p15_1, 0, 8, 9)
replace p15_2 = . if inlist(p15_2, 0, 8, 9)
replace p15_3 = . if inlist(p15_3, 0, 8, 9)
replace p15_4 = . if inlist(p15_4, 0, 8, 9)

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
export delimited using "spain_2025_ai_aspects.csv", replace

**# Bookmark 12: possibilities

* ============================================================
* possibilities (P16_1 to P16_5)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p16_1 p16_2 p16_3 p16_4 p16_5

keep id cov_* `survey_cols'

replace p16_1 = . if inlist(p16_1, 0, 3, 8, 9)
replace p16_2 = . if inlist(p16_2, 0, 3, 8, 9)
replace p16_3 = . if inlist(p16_3, 0, 3, 8, 9)
replace p16_4 = . if inlist(p16_4, 0, 3, 8, 9)
replace p16_5 = . if inlist(p16_5, 0, 3, 8, 9)

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
export delimited using "spain_2025_ai_possibilities.csv", replace

**# Bookmark 13: regulation

* ============================================================
* regulation (P17_1 to P17_5)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p17_1 p17_2 p17_3 p17_4 p17_5

keep id cov_* `survey_cols'

replace p17_1 = . if inlist(p17_1, 0, 3, 8, 9)
replace p17_2 = . if inlist(p17_2, 0, 3, 8, 9)
replace p17_3 = . if inlist(p17_3, 0, 3, 8, 9)
replace p17_4 = . if inlist(p17_4, 0, 3, 8, 9)
replace p17_5 = . if inlist(p17_5, 0, 3, 8, 9)

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
export delimited using "spain_2025_ai_regulation.csv", replace

**# Bookmark 14: eventsagree

* ============================================================
* eventsagree (P18_2_1 to P18_2_4)
* ============================================================

use "spain_2025_ai_master.dta", clear

local survey_cols p18_2_1 p18_2_2 p18_2_3 p18_2_4

keep id cov_* `survey_cols'

replace p18_2_1 = . if inlist(p18_2_1, 0, 3, 8, 9)
replace p18_2_2 = . if inlist(p18_2_2, 0, 3, 8, 9)
replace p18_2_3 = . if inlist(p18_2_3, 0, 3, 8, 9)
replace p18_2_4 = . if inlist(p18_2_4, 0, 3, 8, 9)

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
export delimited using "spain_2025_ai_eventsagree.csv", replace