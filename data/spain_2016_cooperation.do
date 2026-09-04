*** This Stata Do File processes the spain_2016_cooperation study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2016_cooperation"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES3130

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    capital 18 distr 19-20 seccion 21-23 entrev 24-27 p1 28 p201 29 ///
    p202 30 p203 31 p204 32 p205 33 p206 34 p207 35 ///
    p208 36 p301 37 p302 38 p401 39 p402 40 p5 41 ///
    p6 42 p7 43 p801 44 p802 45 p9 46 p10 47 ///
    p11 48 p12 49 p13 50 p1401 51-52 p1402 53-54 p15 55 ///
    p16 56 p17 57 p1801 58-59 p1802 60-61 p1803 62-63 p1901 64-65 ///
    p1902 66-67 p1903 68-69 p2001 70 p2002 71 p21 72 p22 73 ///
    p23 74 p24 75 p2501 76 p2502 77 p2503 78 p2504 79 ///
    p2505 80 p2506 81 p2507 82 p2508 83 p26 84 p27 85 ///
    p28 86 p29 87 p30 88 p30a 89-90 p31 91-92 p32 93 ///
    p32a 94-95 p33 96 p34 97-98 p35 99 p35a 100-101 p36 102 ///
    p36a 103 p37 104 p38 105 p39 106-108 p40 109 p40a 110 ///
    p41 111-113 p42 114 p42a 115 p42b 116-118 p42c 119 p42d 120 ///
    p43 121 p4401 122 p4402 123 p4403 124 p4404 125 str3 p4501 126-128 ///
    str3 p4502 129-131 str3 p4503 132-134 str3 p4504 135-137 str3 p4505 138-140 str3 p4601 141-143 str3 p4602 144-146 ///
    str3 p4603 147-149 str3 p4604 150-152 str3 p4605 153-155 p47 156 p48 157 p49 158 ///
    p50 159 i1 160-162 i2 163-165 i3 166-168 i4 169-171 i5 172-174 ///
    i6 175-177 i7 178-180 i8 181-183 i9 184-186 e101 187-188 e102 189-190 ///
    e103 191-192 e2 193 e3 194-196 e4 197 c1 198 c1a 199-200 ///
    c2 201 c2a 202 c2b 203-204 c3 205 c4 206-207 p2509 208 ///
    p32ar 209-210 recuerdo 211-212 estudios 213 ocumar11 214-215 rama09 216 condicion11 217-218 ///
    estatus 219 ///
    using "DA3130.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p33 cov_sex
rename p34 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2016_cooperation_master.dta", replace

**# Bookmark 1: interest

* ============================================================
* interest (P1, P201 to P208)
* 1-4 attention to international issues (P1) and interest in world regions (P201 to P208), Mucho to Ninguno
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2016_cooperation_master.dta", clear

local survey_cols p1 p201 p202 p203 p204 p205 p206 p207 p208

keep id cov_* `survey_cols'

replace p1 = . if inlist(p1, 8, 9)
replace p201 = . if inlist(p201, 8, 9)
replace p202 = . if inlist(p202, 8, 9)
replace p203 = . if inlist(p203, 8, 9)
replace p204 = . if inlist(p204, 8, 9)
replace p205 = . if inlist(p205, 8, 9)
replace p206 = . if inlist(p206, 8, 9)
replace p207 = . if inlist(p207, 8, 9)
replace p208 = . if inlist(p208, 8, 9)

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
export delimited using "spain_2016_cooperation_interest.csv", replace

**# Bookmark 2: duty

* ============================================================
* duty (P5, P13)
* yes/no on whether Spain has a duty to cooperate internationally and to dedicate 0.7 percent of GDP
* P5 code 3 (NO LEER, No estoy seguro/a) is an off-scale volunteered code, recoded to missing
* ============================================================

use "spain_2016_cooperation_master.dta", clear

local survey_cols p5 p13

keep id cov_* `survey_cols'

replace p5 = . if inlist(p5, 3, 8, 9)
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
keep id cov_* item resp
label values resp .
export delimited using "spain_2016_cooperation_duty.csv", replace

**# Bookmark 3: awareness

* ============================================================
* awareness (P10, P12, P17)
* yes/no awareness of development cooperation facts (aid cuts, 0.7 percent target, Sustainable Development Goals)
* two-category scale, only 9 recoded
* ============================================================

use "spain_2016_cooperation_master.dta", clear

local survey_cols p10 p12 p17

keep id cov_* `survey_cols'

replace p10 = . if inlist(p10, 9)
replace p12 = . if inlist(p12, 9)
replace p17 = . if inlist(p17, 9)

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
export delimited using "spain_2016_cooperation_awareness.csv", replace

**# Bookmark 4: funding

* ============================================================
* funding (P2001, P2002)
* yes/no belief that the autonomous community and the municipality dedicate resources to development cooperation
* two-category scale, 8/9 recoded
* ============================================================

use "spain_2016_cooperation_master.dta", clear

local survey_cols p2001 p2002

keep id cov_* `survey_cols'

replace p2001 = . if inlist(p2001, 8, 9)
replace p2002 = . if inlist(p2002, 8, 9)

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
export delimited using "spain_2016_cooperation_funding.csv", replace
