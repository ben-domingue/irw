*** This Do File creates tables from the Uruguay Technology survey ***

* clear
clear

* import study dataset
import delimited "EUTIC2022.csv", clear varnames(1) case(lower)

* compress
compress

* convert column names to lowercase
rename *, lower

* clean covariates
rename c7 cov_sex
rename edad_tramos cov_age

label define sex_lbl 1 "Male" 2 "Female"
label values cov_sex sex_lbl

* generate new id
drop id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned household covariate dataset
save "uruguay_2022_technology.dta", replace

**# Bookmark #1: Access and Ownership of ICT

use "uruguay_2022_technology.dta", clear

local survey_cols b_2_1_1 b_2_1_2 b3 b3_1 b4 b4_1 b5_1 b5_2 b5_3 b5_4 b6 b6_1

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_access.csv", replace

**# Bookmark #2: Internet Use and Devices

use "uruguay_2022_technology.dta", clear

local survey_cols c9 c9_1 c10 c11 c12_1_1 c12_1 c12_2_a c12_2_1 c12_2 c12_3_1_1 c12_3_3 c12_3_4 c12_3 c12_4

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_devices.csv", replace

**# Bookmark #3: Internet Access Points

use "uruguay_2022_technology.dta", clear

local survey_cols c13_1 c13_2 c13_3 c13_4 c13_5 c13_6 c13_7 c13_8

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_places.csv", replace

**# Bookmark #4: Digital Skills

use "uruguay_2022_technology.dta", clear

local survey_cols c14_1 c14_2 c14_3 c14_4 c14_5 c14_6 c14_6_b c14_7 c14_8 c14_9 c14_10 c14_11 c14_12 c14_13 c14_14 c14_15 c14_16 c14_17 c14_18

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_skills.csv", replace

**# Bookmark #5: Information Search Activities

use "uruguay_2022_technology.dta", clear

local survey_cols c15_1 c15_3 c15_2 c15_4 c15_5 c15_6 c15_7 c15_8 c15_9

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_information.csv", replace

**# Bookmark #6: Work and Study Activities

use "uruguay_2022_technology.dta", clear

local survey_cols c16_1 c16_2 c16_3 c16_4 c16_5 c16_6 c16_7

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_work.csv", replace

**# Bookmark #7: Communication and Participation Activities

use "uruguay_2022_technology.dta", clear

local survey_cols c17_1 c17_2 c17_3 c17_4 c17_5 c17_6 c17_7

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_communication.csv", replace

**# Bookmark #8: Social Media Frequency of Use

use "uruguay_2022_technology.dta", clear

local survey_cols c18_1 c18_2 c18_3 c18_4 c18_10 c18_11 c18_5 c18_6

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_socialmedia.csv", replace

**# Bookmark #9: Safety and Security Risks

use "uruguay_2022_technology.dta", clear

local survey_cols c25 c26 c27

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    if "`var'" == "c27" {
        replace resp = . if inlist(resp, 4)
    }
    else {
        replace resp = . if inlist(resp, 3, 4)
    }
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_safety.csv", replace

**# Bookmark #10: Entertainment Activities

use "uruguay_2022_technology.dta", clear

local survey_cols c19_a c19_c c19_d c19_e

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_entertainment.csv", replace

**# Bookmark #11: Streaming Services

use "uruguay_2022_technology.dta", clear

local survey_cols c19_1_1 c19_1_2 c19_1_7 c19_1_8 c19_1_9 c19_1_3 c19_1_4 c19_1_5 c19_1_6

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_streaming.csv", replace

**# Bookmark #12: Transactions and Commerce Activities

use "uruguay_2022_technology.dta", clear

local survey_cols c20_1 c20_2 c20_3 c20_4 c20_5 c20_6 c20_7 c20_8 c20_9 c20_10 c20_11 c20_12 c20_13

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_transactions.csv", replace

**# Bookmark #13: Barriers to Online Shopping

use "uruguay_2022_technology.dta", clear

local survey_cols c21_a_2 c21_a_3 c21_a_4 c21_a_5 c21_a_6 c21_a_7 c21_a_9

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_barriers.csv", replace

**# Bookmark #14: Government Services Online

use "uruguay_2022_technology.dta", clear

local survey_cols c22_a_1 c22_a_2 c22_a_3 c22_a_4 c22_a_5 c22_a_6 c22_a_7 c22_a_8 c22_a_9 c22_a_11 c22_a_12

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 3, 4, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_govservices.csv", replace

**# Bookmark #15: Perception of Government Online Services

use "uruguay_2022_technology.dta", clear

local survey_cols c23_1 c23_2 c23_3 c23_4 c23_5 c23_6 c23_7

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
	replace resp = . if inlist(resp, 5)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_govperception.csv", replace

**# Bookmark #16: ICT Ownership (Household)

use "uruguay_2022_technology.dta", clear

local survey_cols d21_4 d21_5 d21_6 d21_20 d21_7 d21_15 d21_15_1 d21_15_3 d21_15_5 d21_16 d21_16_1 d21_16_2 d21_21 d21_17

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    destring `var', replace force
}

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 0, 3, 4)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

keep id cov_* item resp

export delimited using "uruguay_2022_technology_ownership.csv", replace