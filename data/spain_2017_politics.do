*** This Stata Do File processes the spain_2017_politics study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2017_politics"

* import fixed-width ASCII using column positions from the CIS SPSS syntax file

infix P101 29-30 P102 31-32 P103 33-34 P104 35-36 P2 37-38 ///
    P401 41-42 P402 43-44 P403 45-46 P404 47-48 P405 49-50 P406 51-52 ///
    P601 54 P602 55 P603 56 P604 57 P605 58 P606 59 P607 60 P608 61 P609 62 ///
    P801 64 P802 65 P803 66 P804 67 P805 68 P806 69 P807 70 P808 71 ///
    P809 72 P810 73 P811 74 P812 75 P813 76 P814 77 P815 78 ///
    P10 83 P11 84 P12 85 P13 86 P16 89 P17 90 P18 91 P19 92 P20 93 ///
    P2301 99 P2302 100 P2303 101 P2304 102 P24 103 ///
    P2501 104 P2502 105 P2503 106 ///
    P2601 107 P2602 108 P2603 109 ///
    P34 146 P35 147-148 ///
    using "DA3184.", clear

rename *, lower

gen long id = _n

* rename covariates

rename p34 cov_sex
rename p35 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress
save "spain_2017_master.dta", replace

**# Table 1: wellbeing

* ============================================================
* wellbeing (P1, P2)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p101 p102 p103 p104 p2

keep id cov_* `survey_cols'

replace p101 = . if inlist(p101, 98, 99)
replace p102 = . if inlist(p102, 98, 99)
replace p103 = . if inlist(p103, 98, 99)
replace p104 = . if inlist(p104, 98, 99)
replace p2 = . if inlist(p2, 98, 99)

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
drop p101 p102 p103 p104 p2
export delimited using "spain_2017_politics_wellbeing.csv", replace

**# Table 2: citizenship

* ============================================================
* citizenship (P4)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p401 p402 p403 p404 p405 p406

keep id cov_* `survey_cols'

replace p401 = . if inlist(p401, 98, 99)
replace p402 = . if inlist(p402, 98, 99)
replace p403 = . if inlist(p403, 98, 99)
replace p404 = . if inlist(p404, 98, 99)
replace p405 = . if inlist(p405, 98, 99)
replace p406 = . if inlist(p406, 98, 99)

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
drop p401 p402 p403 p404 p405 p406
export delimited using "spain_2017_politics_citizenship.csv", replace

**# Table 3: services

* ============================================================
* services (P6)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p601 p602 p603 p604 p605 p606 p607 p608 p609

keep id cov_* `survey_cols'

replace p601 = . if inlist(p601, 8, 9)
replace p602 = . if inlist(p602, 8, 9)
replace p603 = . if inlist(p603, 8, 9)
replace p604 = . if inlist(p604, 8, 9)
replace p605 = . if inlist(p605, 8, 9)
replace p606 = . if inlist(p606, 8, 9)
replace p607 = . if inlist(p607, 8, 9)
replace p608 = . if inlist(p608, 8, 9)
replace p609 = . if inlist(p609, 8, 9)

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
drop p601 p602 p603 p604 p605 p606 p607 p608 p609
export delimited using "spain_2017_politics_services.csv", replace

**# Table 4: spending

* ============================================================
* spending (P801 to P815)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p801 p802 p803 p804 p805 p806 p807 p808 p809 p810 p811 p812 p813 p814 p815

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 8, 9)
}

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
drop p801 p802 p803 p804 p805 p806 p807 p808 p809 p810 p811 p812 p813 p814 p815
export delimited using "spain_2017_politics_spending.csv", replace

**# Table 5: burden

* ============================================================
* burden (P10, P11, P12, P13)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p10 p11 p12 p13

keep id cov_* `survey_cols'

replace p10 = . if inlist(p10, 8, 9)
replace p11 = . if inlist(p11, 8, 9)
replace p12 = . if inlist(p12, 8, 9)
replace p13 = . if inlist(p13, 4, 9)

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
export delimited using "spain_2017_politics_burden.csv", replace

**# Table 6: fraud

* ============================================================
* fraud (P18, P19, P20, P24)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p18 p19 p20 p24

keep id cov_* `survey_cols'

replace p18 = . if inlist(p18, 8, 9)
replace p19 = . if inlist(p19, 8, 9)
replace p20 = . if inlist(p20, 8, 9)
replace p24 = . if inlist(p24, 8, 9)

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
drop p18 p19 p20 p24
export delimited using "spain_2017_politics_fraud.csv", replace

**# Table 7: conscience

* ============================================================
* conscience (P16, P17)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p16 p17

keep id cov_* `survey_cols'

replace p16 = . if inlist(p16, 8, 9)
replace p17 = . if p17 == 9

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
drop p16 p17
export delimited using "spain_2017_politics_conscience.csv", replace

**# Table 8: agreement

* ============================================================
* agreement (P23)
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p2301 p2302 p2303 p2304

keep id cov_* `survey_cols'

replace p2301 = . if inlist(p2301, 8, 9)
replace p2302 = . if inlist(p2302, 8, 9)
replace p2303 = . if inlist(p2303, 8, 9)
replace p2304 = . if inlist(p2304, 8, 9)

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
drop p2301 p2302 p2303 p2304
export delimited using "spain_2017_politics_agreement.csv", replace

**# Table 9: attitudes

* ============================================================
* attitudes (P25) | code 3 is the volunteered (NO LEER) midpoint, recoded to missing
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p2501 p2502 p2503

keep id cov_* `survey_cols'

replace p2501 = . if inlist(p2501, 3, 8, 9)
replace p2502 = . if inlist(p2502, 3, 8, 9)
replace p2503 = . if inlist(p2503, 3, 8, 9)

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
drop p2501 p2502 p2503
export delimited using "spain_2017_politics_attitudes.csv", replace

**# Table 10: discussion

* ============================================================
* discussion (P26) | code 7 is volunteered (NO LEER) No procede, recoded to missing
* ============================================================

use "spain_2017_master.dta", clear

local survey_cols p2601 p2602 p2603

keep id cov_* `survey_cols'

replace p2601 = . if inlist(p2601, 7, 8, 9)
replace p2602 = . if inlist(p2602, 7, 8, 9)
replace p2603 = . if inlist(p2603, 7, 8, 9)

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
drop p2601 p2602 p2603
export delimited using "spain_2017_politics_discussion.csv", replace