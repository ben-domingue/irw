*** This Stata Do File processes the spain_2012_gender study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2012_gender"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES2968

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    area 18 distr 19-20 seccion 21-23 entrev 24-27 p1 28 p201 29 ///
    p202 30 p203 31 p204 32 p205 33 p206 34 p207 35 ///
    p208 36 p301 37 p302 38 p303 39 p304 40 p305 41 ///
    p306 42 p307 43 p308 44 p309 45 p310 46 p311 47 ///
    p312 48 p4 49-50 p501 51 p502 52 p503 53 p504 54 ///
    p505 55 p506 56 p507 57 p508 58 p509 59 p510 60 ///
    p511 61 p601 62 p602 63 p603 64 p604 65 p7 66 ///
    p8 67 p901 68 p902 69 p903 70 p904 71 p905 72 ///
    p906 73 p1001 74 p1002 75 p1003 76 p1004 77 p1005 78 ///
    p1101 79 p1102 80 p1103 81 p1104 82 p1105 83 p1201 84 ///
    p1202 85 p1203 86 p1204 87 p1205 88 p1206 89 p1207 90 ///
    p1208 91 p1209 92 p1210 93 p1211 94 p13 95 p13a 96-97 ///
    p13b 98-99 p13c 100 p13d 101 p13e 102 p14 103 p15 104-105 ///
    p1601 106 p1602 107 p1603 108 p1604 109 p17 110 p18 111 ///
    p18a 112-113 p18b 114-115 p19 116 p20 117 p21 118 p22 119 ///
    p22a01 120-121 p22a02 122-123 p22a03 124-125 p23 126 p23a01 127-128 p23a02 129-130 ///
    p23a03 131-132 p24 133 p24a 134 p24b 135 p2501 136-137 p2502 138-139 ///
    p2601 140 p2602 141 p2603 142 p2702 143 p2701 144 p2703 145 ///
    p2704 146 p28 147 p29 148 p30 149 p31 150-151 p32 152 ///
    p32a 153-154 recuerdo 155-156 p33 157 p34 158-159 p35 160 p36 161 ///
    p37 162 p38 163 p39 164 p4001 165 p4002 166 p4003 167 ///
    p4004 168 p4005 169 p4006 170 p41 171 p41a 172-173 estudios 174 ///
    p42 175 p42a 176 p43 177 p44 178 p44a01 179 p44a02 180 ///
    p44a03 181 p44b 182 p44c 183-184 p45 185-187 ocumar11 188-189 p46 190 ///
    p46a 191 p47 192-194 rama09 195 p48 196 p48a 197 p48b 198-200 ///
    condicion11 201-202 estatus 203-204 p49 205 ///
    using "DA2968.", clear

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

save "spain_2012_gender_master.dta", replace

**# Bookmark 1: situation

* ============================================================
* situation (P201 to P208)
* 1-3 whether women are better, equal or worse off than men in eight domains (pay, promotion, employment, stability, education, business posts, work-life balance, political posts)
* three read categories mejor / igual / peor, igual is a read midpoint and is kept; only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p201 p202 p203 p204 p205 p206 p207 p208

keep id cov_* `survey_cols'

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
export delimited using "spain_2012_gender_situation.csv", replace

**# Bookmark 2: couple

* ============================================================
* couple (P301 to P312)
* 1-4 importance of twelve aspects for a couple relationship to work, muy importante to nada importante
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p301 p302 p303 p304 p305 p306 p307 p308 p309 p310 p311 p312

keep id cov_* `survey_cols'

replace p301 = . if inlist(p301, 8, 9)
replace p302 = . if inlist(p302, 8, 9)
replace p303 = . if inlist(p303, 8, 9)
replace p304 = . if inlist(p304, 8, 9)
replace p305 = . if inlist(p305, 8, 9)
replace p306 = . if inlist(p306, 8, 9)
replace p307 = . if inlist(p307, 8, 9)
replace p308 = . if inlist(p308, 8, 9)
replace p309 = . if inlist(p309, 8, 9)
replace p310 = . if inlist(p310, 8, 9)
replace p311 = . if inlist(p311, 8, 9)
replace p312 = . if inlist(p312, 8, 9)

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
export delimited using "spain_2012_gender_couple.csv", replace

**# Bookmark 3: acceptability

* ============================================================
* acceptability (P501 to P511, P7)
* 1-3 acceptability of eleven behaviours between partners plus domestic violence towards women (P7): inevitable / acceptable in some circumstances / totally unacceptable
* P7 is a singleton on the identical 1-3 scale and the same construct (acceptability of abuse) and is merged into this block
* three read categories, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p501 p502 p503 p504 p505 p506 p507 p508 p509 p510 p511 p7

keep id cov_* `survey_cols'

replace p501 = . if inlist(p501, 8, 9)
replace p502 = . if inlist(p502, 8, 9)
replace p503 = . if inlist(p503, 8, 9)
replace p504 = . if inlist(p504, 8, 9)
replace p505 = . if inlist(p505, 8, 9)
replace p506 = . if inlist(p506, 8, 9)
replace p507 = . if inlist(p507, 8, 9)
replace p508 = . if inlist(p508, 8, 9)
replace p509 = . if inlist(p509, 8, 9)
replace p510 = . if inlist(p510, 8, 9)
replace p511 = . if inlist(p511, 8, 9)
replace p7 = . if inlist(p7, 8, 9)

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
export delimited using "spain_2012_gender_acceptability.csv", replace

**# Bookmark 4: prevalence

* ============================================================
* prevalence (P601 to P604)
* 1-4 how widespread abuse is against men, women, children and the elderly, muy extendidos to nada extendidos
* four read categories, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p601 p602 p603 p604

keep id cov_* `survey_cols'

replace p601 = . if inlist(p601, 8, 9)
replace p602 = . if inlist(p602, 8, 9)
replace p603 = . if inlist(p603, 8, 9)
replace p604 = . if inlist(p604, 8, 9)

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
export delimited using "spain_2012_gender_prevalence.csv", replace

**# Bookmark 5: beliefs

* ============================================================
* beliefs (P901 to P906)
* 1-4 agreement with six statements about abusers and abused women, muy de acuerdo to nada de acuerdo
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p901 p902 p903 p904 p905 p906

keep id cov_* `survey_cols'

replace p901 = . if inlist(p901, 8, 9)
replace p902 = . if inlist(p902, 8, 9)
replace p903 = . if inlist(p903, 8, 9)
replace p904 = . if inlist(p904, 8, 9)
replace p905 = . if inlist(p905, 8, 9)
replace p906 = . if inlist(p906, 8, 9)

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
export delimited using "spain_2012_gender_beliefs.csv", replace

**# Bookmark 6: vulnerability

* ============================================================
* vulnerability (P1001 to P1005)
* yes/no whether five groups of women are more vulnerable to gender violence
* yes/no selected response, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p1001 p1002 p1003 p1004 p1005

keep id cov_* `survey_cols'

replace p1001 = . if inlist(p1001, 8, 9)
replace p1002 = . if inlist(p1002, 8, 9)
replace p1003 = . if inlist(p1003, 8, 9)
replace p1004 = . if inlist(p1004, 8, 9)
replace p1005 = . if inlist(p1005, 8, 9)

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
export delimited using "spain_2012_gender_vulnerability.csv", replace

**# Bookmark 7: punishment

* ============================================================
* punishment (P1101 to P1105)
* 1-3 whether five forms of abuse are acceptable, unacceptable but not always punishable, or unacceptable and always punishable
* three read ordered categories, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p1101 p1102 p1103 p1104 p1105

keep id cov_* `survey_cols'

replace p1101 = . if inlist(p1101, 8, 9)
replace p1102 = . if inlist(p1102, 8, 9)
replace p1103 = . if inlist(p1103, 8, 9)
replace p1104 = . if inlist(p1104, 8, 9)
replace p1105 = . if inlist(p1105, 8, 9)

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
export delimited using "spain_2012_gender_punishment.csv", replace

**# Bookmark 8: causes

* ============================================================
* causes (P1201 to P1211)
* yes/no whether eleven factors are causes of gender violence
* yes/no selected response, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p1201 p1202 p1203 p1204 p1205 p1206 p1207 p1208 p1209 p1210 p1211

keep id cov_* `survey_cols'

replace p1201 = . if inlist(p1201, 8, 9)
replace p1202 = . if inlist(p1202, 8, 9)
replace p1203 = . if inlist(p1203, 8, 9)
replace p1204 = . if inlist(p1204, 8, 9)
replace p1205 = . if inlist(p1205, 8, 9)
replace p1206 = . if inlist(p1206, 8, 9)
replace p1207 = . if inlist(p1207, 8, 9)
replace p1208 = . if inlist(p1208, 8, 9)
replace p1209 = . if inlist(p1209, 8, 9)
replace p1210 = . if inlist(p1210, 8, 9)
replace p1211 = . if inlist(p1211, 8, 9)

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
export delimited using "spain_2012_gender_causes.csv", replace

**# Bookmark 9: coordination

* ============================================================
* coordination (P1601 to P1604)
* 1-4 agreement with statements about coordination and decentralisation of services for victims
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p1601 p1602 p1603 p1604

keep id cov_* `survey_cols'

replace p1601 = . if inlist(p1601, 8, 9)
replace p1602 = . if inlist(p1602, 8, 9)
replace p1603 = . if inlist(p1603, 8, 9)
replace p1604 = . if inlist(p1604, 8, 9)

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
export delimited using "spain_2012_gender_coordination.csv", replace

**# Bookmark 10: campaigns

* ============================================================
* campaigns (P20, P21)
* yes/no whether awareness campaigns help to raise social awareness and help victims to become aware of their situation
* two adjacent yes/no items on the same construct paired into a two-item table; only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p20 p21

keep id cov_* `survey_cols'

replace p20 = . if inlist(p20, 8, 9)
replace p21 = . if inlist(p21, 8, 9)

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
export delimited using "spain_2012_gender_campaigns.csv", replace

**# Bookmark 11: complaints

* ============================================================
* complaints (P2601 to P2603)
* 1-4 agreement with statements about false complaints and withdrawn complaints
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p2601 p2602 p2603

keep id cov_* `survey_cols'

replace p2601 = . if inlist(p2601, 8, 9)
replace p2602 = . if inlist(p2602, 8, 9)
replace p2603 = . if inlist(p2603, 8, 9)

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
export delimited using "spain_2012_gender_complaints.csv", replace

**# Bookmark 12: custody

* ============================================================
* custody (P2701 to P2704)
* 1-4 agreement with statements about custody of children of convicted abusers
* P2702 precedes P2701 in the DATA LIST; items are listed in questionnaire order here
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_gender_master.dta", clear

local survey_cols p2701 p2702 p2703 p2704

keep id cov_* `survey_cols'

replace p2701 = . if inlist(p2701, 8, 9)
replace p2702 = . if inlist(p2702, 8, 9)
replace p2703 = . if inlist(p2703, 8, 9)
replace p2704 = . if inlist(p2704, 8, 9)

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
export delimited using "spain_2012_gender_custody.csv", replace
