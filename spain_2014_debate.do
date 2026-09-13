*** This Stata Do File processes the spain_2014_debate study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2014_debate"

* fixed-width ASCII import, column positions taken from the SPSS syntax file Es3016

infix ///
    estudio 1-5 cues 6-10 ccaa 11-12 prov 13-14 tamuni 15 mun 16-18 ///
    p0a 19 p1 20 p2 21 p3 22 p4 23 p5a 24 ///
    p5b 25 p5c 26 p5d 27 p5e 28 p6_1 29 p6_2 30 ///
    p6_3 31 p6_4 32 p6_5 33 p6_9 34 p6a 35 p7_1 36 ///
    p7_2 37 p7_3 38 p7_4 39 p7_5 40 p7_6 41 p7_9 42 ///
    p8 43 p9 44 p10 45-46 p10a 47-48 p11 49 p12 50 ///
    p13_1 51 p13_2 52 p13_3 53 p13_4 54 p13_5 55 p13_6 56 ///
    p13_7 57 p13_8 58 p13_9 59 p13_10 60 p13_11 61 p13_12 62 ///
    p13_13 63 p13_14 64 p13_15 65 p13_16 66 p13_17 67 p13a_1 68 ///
    p13a_2 69 p13a_3 70 p13a_4 71 p13a_5 72 p13a_6 73 p13a_7 74 ///
    p13a_8 75 p13a_9 76 p13a_10 77 p13a_11 78 p13a_12 79 p13a_13 80 ///
    p13a_14 81 p13a_15 82 p13a_16 83 p13a_17 84 p14a 85 p14b 86 ///
    p14c 87 p14d 88 p15a 89 p15b 90 p15c 91 p15d 92 ///
    p16a 93 p16b 94 p16c 95 p16d 96 p16e 97 p16f 98 ///
    p16g 99 p16h 100 p17a 101 p17b 102 p17c 103 p17d 104 ///
    p17e 105 p17f 106 p17g 107 p17h 108 p18 109-110 p19 111-112 ///
    p20 113 p20a 114-115 recuerdo 116-117 p0b 118 p0c 119-120 p21 121 ///
    p22 122 p23 123 ///
    using "Da3016.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p0b cov_sex
rename p0c cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2014_debate_master.dta", replace

**# Bookmark 1: general

* ============================================================
* general (P2, P3)
* 1-4 interest of state of the nation debates for people and degree to which they address issues that worry Spaniards
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p2 p3

keep id cov_* `survey_cols'

replace p2 = . if inlist(p2, 8, 9)
replace p3 = . if inlist(p3, 8, 9)

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
label values resp .
export delimited using "spain_2014_debate_general.csv", replace

**# Bookmark 2: media

* ============================================================
* media (P5A to P5E)
* 1-5 frequency of following political news in press, television, radio, Internet and conversation
* five read frequency categories, no NO LEER code, only 9 recoded (no 8 code on these items)
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p5a p5b p5c p5d p5e

keep id cov_* `survey_cols'

replace p5a = . if inlist(p5a, 9)
replace p5b = . if inlist(p5b, 9)
replace p5c = . if inlist(p5c, 9)
replace p5d = . if inlist(p5d, 9)
replace p5e = . if inlist(p5e, 9)

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
label values resp .
export delimited using "spain_2014_debate_media.csv", replace

**# Bookmark 3: debate

* ============================================================
* debate (P8, P11, P12)
* 1-4 evaluation of the 2014 debate: interest in following it, treatment of issues that worry citizens, conflict level
* asked only to respondents who knew of the debate (P1 = 1); blanks are structural and stay missing
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p8 p11 p12

keep id cov_* `survey_cols'

replace p8 = . if inlist(p8, 8, 9)
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
label values resp .
export delimited using "spain_2014_debate_debate.csv", replace

**# Bookmark 4: leaders

* ============================================================
* leaders (P13_1 to P13_17)
* 1-5 rating of each leader's performance in the debate, muy bien to muy mal
* code 3 (Regular) is marked (No leer) and is recoded to missing per the NO LEER rule
* code 7 (No leer) does not know the leader is a non-scale code, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p13_1 p13_2 p13_3 p13_4 p13_5 p13_6 p13_7 p13_8 p13_9 p13_10 p13_11 p13_12 p13_13 p13_14 p13_15 p13_16 p13_17

keep id cov_* `survey_cols'

replace p13_1 = . if inlist(p13_1, 3, 7, 8, 9)
replace p13_2 = . if inlist(p13_2, 3, 7, 8, 9)
replace p13_3 = . if inlist(p13_3, 3, 7, 8, 9)
replace p13_4 = . if inlist(p13_4, 3, 7, 8, 9)
replace p13_5 = . if inlist(p13_5, 3, 7, 8, 9)
replace p13_6 = . if inlist(p13_6, 3, 7, 8, 9)
replace p13_7 = . if inlist(p13_7, 3, 7, 8, 9)
replace p13_8 = . if inlist(p13_8, 3, 7, 8, 9)
replace p13_9 = . if inlist(p13_9, 3, 7, 8, 9)
replace p13_10 = . if inlist(p13_10, 3, 7, 8, 9)
replace p13_11 = . if inlist(p13_11, 3, 7, 8, 9)
replace p13_12 = . if inlist(p13_12, 3, 7, 8, 9)
replace p13_13 = . if inlist(p13_13, 3, 7, 8, 9)
replace p13_14 = . if inlist(p13_14, 3, 7, 8, 9)
replace p13_15 = . if inlist(p13_15, 3, 7, 8, 9)
replace p13_16 = . if inlist(p13_16, 3, 7, 8, 9)
replace p13_17 = . if inlist(p13_17, 3, 7, 8, 9)

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
label values resp .
export delimited using "spain_2014_debate_leaders.csv", replace

**# Bookmark 5: agreement

* ============================================================
* agreement (P13A_1 to P13A_17)
* 1-4 agreement with what each leader said in the debate, from most to nothing
* asked only about leaders the respondent rated; four read categories, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p13a_1 p13a_2 p13a_3 p13a_4 p13a_5 p13a_6 p13a_7 p13a_8 p13a_9 p13a_10 p13a_11 p13a_12 p13a_13 p13a_14 p13a_15 p13a_16 p13a_17

keep id cov_* `survey_cols'

replace p13a_1 = . if inlist(p13a_1, 8, 9)
replace p13a_2 = . if inlist(p13a_2, 8, 9)
replace p13a_3 = . if inlist(p13a_3, 8, 9)
replace p13a_4 = . if inlist(p13a_4, 8, 9)
replace p13a_5 = . if inlist(p13a_5, 8, 9)
replace p13a_6 = . if inlist(p13a_6, 8, 9)
replace p13a_7 = . if inlist(p13a_7, 8, 9)
replace p13a_8 = . if inlist(p13a_8, 8, 9)
replace p13a_9 = . if inlist(p13a_9, 8, 9)
replace p13a_10 = . if inlist(p13a_10, 8, 9)
replace p13a_11 = . if inlist(p13a_11, 8, 9)
replace p13a_12 = . if inlist(p13a_12, 8, 9)
replace p13a_13 = . if inlist(p13a_13, 8, 9)
replace p13a_14 = . if inlist(p13a_14, 8, 9)
replace p13a_15 = . if inlist(p13a_15, 8, 9)
replace p13a_16 = . if inlist(p13a_16, 8, 9)
replace p13a_17 = . if inlist(p13a_17, 8, 9)

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
label values resp .
export delimited using "spain_2014_debate_agreement.csv", replace

**# Bookmark 6: government

* ============================================================
* government (P14A to P14D)
* 1-4 degree to which the Government conveyed confidence in the economic and political future, resolve to keep promises, and strength
* four read categories mucho to nada, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p14a p14b p14c p14d

keep id cov_* `survey_cols'

replace p14a = . if inlist(p14a, 8, 9)
replace p14b = . if inlist(p14b, 8, 9)
replace p14c = . if inlist(p14c, 8, 9)
replace p14d = . if inlist(p14d, 8, 9)

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
label values resp .
export delimited using "spain_2014_debate_government.csv", replace

**# Bookmark 7: opposition

* ============================================================
* opposition (P15A to P15D)
* 1-4 degree to which the opposition leader has real proposals, constructive opposition, inspires confidence, is ready to govern
* four read categories mucho to nada, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p15a p15b p15c p15d

keep id cov_* `survey_cols'

replace p15a = . if inlist(p15a, 8, 9)
replace p15b = . if inlist(p15b, 8, 9)
replace p15c = . if inlist(p15c, 8, 9)
replace p15d = . if inlist(p15d, 8, 9)

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
label values resp .
export delimited using "spain_2014_debate_opposition.csv", replace

**# Bookmark 8: rajoy

* ============================================================
* rajoy (P16A to P16H)
* yes/no whether Mariano Rajoy showed each of eight political qualities in the debate
* yes/no selected response, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p16a p16b p16c p16d p16e p16f p16g p16h

keep id cov_* `survey_cols'

replace p16a = . if inlist(p16a, 8, 9)
replace p16b = . if inlist(p16b, 8, 9)
replace p16c = . if inlist(p16c, 8, 9)
replace p16d = . if inlist(p16d, 8, 9)
replace p16e = . if inlist(p16e, 8, 9)
replace p16f = . if inlist(p16f, 8, 9)
replace p16g = . if inlist(p16g, 8, 9)
replace p16h = . if inlist(p16h, 8, 9)

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
label values resp .
export delimited using "spain_2014_debate_rajoy.csv", replace

**# Bookmark 9: rubalcaba

* ============================================================
* rubalcaba (P17A to P17H)
* yes/no whether Alfredo Perez Rubalcaba showed each of eight political qualities in the debate
* yes/no selected response, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_debate_master.dta", clear

local survey_cols p17a p17b p17c p17d p17e p17f p17g p17h

keep id cov_* `survey_cols'

replace p17a = . if inlist(p17a, 8, 9)
replace p17b = . if inlist(p17b, 8, 9)
replace p17c = . if inlist(p17c, 8, 9)
replace p17d = . if inlist(p17d, 8, 9)
replace p17e = . if inlist(p17e, 8, 9)
replace p17f = . if inlist(p17f, 8, 9)
replace p17g = . if inlist(p17g, 8, 9)
replace p17h = . if inlist(p17h, 8, 9)

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
label values resp .
export delimited using "spain_2014_debate_rubalcaba.csv", replace
