*** This Stata Do File processes the spain_2012_entrepreneurship study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2012_entrepreneurship"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES2938

infix ///
    cues 5-9 str9 a1 1-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    area 18 distr 19-20 seccion 21-23 entrev 24-27 muestra 28 p101 29-30 ///
    p102 31-32 p201 33-34 p202 35-36 p3 37 p4 38 p5 39 ///
    p601 40-41 p602 42-43 p701 44 p702 45 p703 46 p704 47 ///
    p705 48 p706 49 p707 50 p801 51-52 p802 53-54 p803 55-56 ///
    p804 57-58 p805 59-60 p806 61-62 p807 63-64 p808 65-66 p809 67-68 ///
    p810 69-70 p9 71-72 p1001 73-74 p1002 75-76 p11 77-78 p1201 79 ///
    p1202 80 p1203 81 p1204 82 p1205 83 p13 84 p13a01 85-86 ///
    p13a02 87-88 p13a03 89-90 p13b01 91-92 p13b02 93-94 p13b03 95-96 p14 97-98 ///
    p14a01 99 p14a02 100 p14a03 101 p14a04 102 p14a05 103 p14a06 104 ///
    p14a07 105 p14b 106 p15 107 p15a01 108-109 p15a02 110-111 p15a03 112-113 ///
    p1601 114-115 p1602 116-117 p1701 118 p1702 119 p1703 120 p1704 121 ///
    p1801 122 p1802 123 p1803 124 p1804 125 p1805 126 p1806 127 ///
    p19 128-129 p20 130 p2101 131 p2102 132 p2103 133 p2104 134 ///
    p22 135 p2301 136 p2302 137 p2303 138 p2304 139 p24 140-141 ///
    p25 142-143 p26 144-145 p27 146 p27a 147-148 p28 149-150 p29 151-152 ///
    p30 153-154 p31 155 p32 156 p33 157 p34 158 p35 159 ///
    p36 160 p37 161 p38 162 p39 163-164 p40 165-166 p41 167-169 ///
    p42 170 p42a 171 p43 172-173 p44 174-175 p45 176 p46 177 ///
    p47 178 p48 179 p49 180-181 p50 182-184 p51 185 p51a 186 ///
    p52 187-188 p53 189 p54 190 p54a 191 p54b 192-194 p54c 195 ///
    p54d 196 p55 197 p5601 198 p5602 199 p5603 200 p5604 201 ///
    str3 p5701 202-204 str3 p5702 205-207 str3 p5703 208-210 str3 p5704 211-213 str3 p5705 214-216 str3 p5801 217-219 ///
    str3 p5802 220-222 str3 p5803 223-225 str3 p5804 226-228 str3 p5805 229-231 p59 232 p60 233 ///
    p61 234 p62 235 str48 final 236-283 recuerdo 284-285 ocupa 286-287 estudios 288 ///
    ocupapp 289-290 condicpp 291-292 estatpp 293 ///
    using "DA2938.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p31 cov_sex
rename p28 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2012_entrepreneurship_master.dta", replace

**# Bookmark 1: economy

* ============================================================
* economy (P4, P5)
* 1-3 whether the economic situation of the country is better, the same or worse than a year ago, and will be in a year
* two adjacent items on the identical mejor / igual / peor scale paired into a two-item table; igual is a read midpoint and is kept
* only 8/9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p4 p5

keep id cov_* `survey_cols'

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
keep id cov_* item resp
label values resp .
export delimited using "spain_2012_entrepreneurship_economy.csv", replace

**# Bookmark 2: unemployment

* ============================================================
* unemployment (P701 to P707)
* 1-4 importance of seven causes of unemployment in Spain, muy importante to nada importante
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p701 p702 p703 p704 p705 p706 p707

keep id cov_* `survey_cols'

replace p701 = . if inlist(p701, 8, 9)
replace p702 = . if inlist(p702, 8, 9)
replace p703 = . if inlist(p703, 8, 9)
replace p704 = . if inlist(p704, 8, 9)
replace p705 = . if inlist(p705, 8, 9)
replace p706 = . if inlist(p706, 8, 9)
replace p707 = . if inlist(p707, 8, 9)

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
export delimited using "spain_2012_entrepreneurship_unemployment.csv", replace

**# Bookmark 3: values

* ============================================================
* values (P801 to P810)
* 0-10 importance of ten aspects in the respondent's life, 0 muy poco importante to 10 muy importante
* two-digit rating scale, 98 N.S. and 99 N.C. recoded; 0 is a valid scale point
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p801 p802 p803 p804 p805 p806 p807 p808 p809 p810

keep id cov_* `survey_cols'

replace p801 = . if inlist(p801, 98, 99)
replace p802 = . if inlist(p802, 98, 99)
replace p803 = . if inlist(p803, 98, 99)
replace p804 = . if inlist(p804, 98, 99)
replace p805 = . if inlist(p805, 98, 99)
replace p806 = . if inlist(p806, 98, 99)
replace p807 = . if inlist(p807, 98, 99)
replace p808 = . if inlist(p808, 98, 99)
replace p809 = . if inlist(p809, 98, 99)
replace p810 = . if inlist(p810, 98, 99)

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
export delimited using "spain_2012_entrepreneurship_values.csv", replace

**# Bookmark 4: friends

* ============================================================
* friends (P1201 to P1205)
* 1-3 share of the respondent's friends who share their social class, education, origin, ideology and religion: more than half / half / less than half
* three read ordered categories, la mitad is a read midpoint and is kept; only 8/9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p1201 p1202 p1203 p1204 p1205

keep id cov_* `survey_cols'

replace p1201 = . if inlist(p1201, 8, 9)
replace p1202 = . if inlist(p1202, 8, 9)
replace p1203 = . if inlist(p1203, 8, 9)
replace p1204 = . if inlist(p1204, 8, 9)
replace p1205 = . if inlist(p1205, 8, 9)

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
export delimited using "spain_2012_entrepreneurship_friends.csv", replace

**# Bookmark 5: motives

* ============================================================
* motives (P14A01 to P14A07)
* 1-4 importance of seven factors in the decision to start a business, muy importante to nada importante
* asked only to respondents who have or had a business or are taking steps (codes 3 to 8 in P14); 0 is a structural not-asked code and is recoded to missing
* four read categories, no NO LEER code; 0, 8 and 9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p14a01 p14a02 p14a03 p14a04 p14a05 p14a06 p14a07

keep id cov_* `survey_cols'

replace p14a01 = . if inlist(p14a01, 0, 8, 9)
replace p14a02 = . if inlist(p14a02, 0, 8, 9)
replace p14a03 = . if inlist(p14a03, 0, 8, 9)
replace p14a04 = . if inlist(p14a04, 0, 8, 9)
replace p14a05 = . if inlist(p14a05, 0, 8, 9)
replace p14a06 = . if inlist(p14a06, 0, 8, 9)
replace p14a07 = . if inlist(p14a07, 0, 8, 9)

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
export delimited using "spain_2012_entrepreneurship_motives.csv", replace

**# Bookmark 6: barriers

* ============================================================
* barriers (P1701 to P1704)
* 1-4 agreement with statements about difficulties in starting a business (finance, paperwork, information, risk)
* four read categories muy de acuerdo to muy en desacuerdo, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p1701 p1702 p1703 p1704

keep id cov_* `survey_cols'

replace p1701 = . if inlist(p1701, 8, 9)
replace p1702 = . if inlist(p1702, 8, 9)
replace p1703 = . if inlist(p1703, 8, 9)
replace p1704 = . if inlist(p1704, 8, 9)

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
export delimited using "spain_2012_entrepreneurship_barriers.csv", replace

**# Bookmark 7: image

* ============================================================
* image (P1801 to P1806)
* 1-3 positive or negative opinion of six occupational groups (public employees, corporate managers, bank managers, entrepreneurs, politicians, liberal professionals)
* code 2 (Ni positiva ni negativa) is marked (NO LEER) and is recoded to missing per the NO LEER rule; exported values are 1 and 3
* 8/9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p1801 p1802 p1803 p1804 p1805 p1806

keep id cov_* `survey_cols'

replace p1801 = . if inlist(p1801, 2, 8, 9)
replace p1802 = . if inlist(p1802, 2, 8, 9)
replace p1803 = . if inlist(p1803, 2, 8, 9)
replace p1804 = . if inlist(p1804, 2, 8, 9)
replace p1805 = . if inlist(p1805, 2, 8, 9)
replace p1806 = . if inlist(p1806, 2, 8, 9)

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
export delimited using "spain_2012_entrepreneurship_image.csv", replace

**# Bookmark 8: education

* ============================================================
* education (P2101 to P2104)
* 1-4 agreement with statements about how school education fostered initiative, understanding of entrepreneurs, interest in a business and business skills
* four read categories muy de acuerdo to muy en desacuerdo, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

local survey_cols p2101 p2102 p2103 p2104

keep id cov_* `survey_cols'

replace p2101 = . if inlist(p2101, 8, 9)
replace p2102 = . if inlist(p2102, 8, 9)
replace p2103 = . if inlist(p2103, 8, 9)
replace p2104 = . if inlist(p2104, 8, 9)

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
export delimited using "spain_2012_entrepreneurship_education.csv", replace

**# Bookmark 9: entrepreneurs

* ============================================================
* entrepreneurs (P2301 to P2304)
* 1-4 agreement with statements about entrepreneurs (create products, self-interested, create jobs, exploit others)
* four read categories muy de acuerdo to muy en desacuerdo, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_entrepreneurship_master.dta", clear

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
keep id cov_* item resp
label values resp .
export delimited using "spain_2012_entrepreneurship_entrepreneurs.csv", replace
