*** This Stata Do File processes the spain_2015_immigration study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2015_immigration"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES3119

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    eiex 18 distr 19-20 seccion 21-23 entrev 24-27 p0 28 p101 29 ///
    p102 30 p103 31 p104 32 p201 33-34 p202 35-36 p301 37-38 ///
    p302 39-40 p4 41 p501 42-43 p502 44-45 p503 46-47 p504 48-49 ///
    p505 50-51 p506 52-53 p507 54-55 p508 56-57 p6 58 p7 59 ///
    p8 60 p901 61-62 p902 63-64 p903 65-66 p904 67-68 p10 69-70 ///
    p11 71-72 p12 73-74 p1301 75 p1302 76 p1303 77 p1304 78 ///
    p1305 79 p1401 80 p1402 81 p1403 82 p1404 83 p1501 84 ///
    p1502 85 p1503 86 p1504 87 p16 88 p17 89-90 p18 91-92 ///
    p19 93 p20 94 p2101 95 p2102 96 p2103 97 p2104 98 ///
    p2105 99 p2201 100 p2202 101 p2203 102 p2204 103 p23 104 ///
    p2401 105 p2402 106 p2403 107 p2404 108 p2405 109 p2406 110 ///
    p2407 111 p2408 112 p2501 113 p2502 114 p2503 115 p2504 116 ///
    p2505 117 p2506 118 p2507 119 p2508 120 p26 121 p26a 122 ///
    p26b 123 p26c 124 p27 125 p27a 126 p27b 127 p27c 128 ///
    p28 129-130 p29 131-132 p29a 133-134 p30 135 p31 136 p32 137 ///
    p33 138 p34 139 p35 140 p35a01 141 p35a02 142 p35a03 143 ///
    p35a04 144 p35a05 145 p35a06 146 p35a07 147 p35a08 148 p35a09 149 ///
    p36 150 p37 151 p38 152-153 p39 154-155 p40 156-157 p41 158 ///
    p41a 159-160 p42 161 p42a 162 p43 163 p44 164 p45 165-166 ///
    p46 167 p46a 168 p46b 169 p46c 170-172 p46d 173-176 p47 177 ///
    p47a 178-179 p48 180 p49 181 p49a 182-183 p50 184 p50a 185-186 ///
    p50b 187 p51 188 p52 189 p53 190 p54 191 p55 192 ///
    p56 193-195 p57 196 p57a 197 p58 198-200 p59 201-202 p60 203-204 ///
    p61 205 p61a 206-208 p61b 209-212 p62 213 p6301 214 p6302 215 ///
    p6303 216 p6304 217 str3 p6401 218-220 str3 p6402 221-223 str3 p6403 224-226 str3 p6404 227-229 ///
    str3 p6405 230-232 str3 p6501 233-235 str3 p6502 236-238 str3 p6503 239-241 str3 p6504 242-244 str3 p6505 245-247 ///
    p66 248 p67 249 p68 250 p69 251 i1 252-254 i2 255-257 ///
    i3 258-260 i4 261-263 i5 264-266 i6 267-269 i7 270-272 i8 273-275 ///
    i9 276-278 e101 279-280 e102 281-282 e103 283-284 e2 285 e3 286-288 ///
    e4 289 c1 290 c1a 291-292 c2 293 c2a 294 c2b 295-296 ///
    c3 297 c4 298-299 p35a10 300 p35a11 301 peso 302-306 pesoca01 307-311 ///
    recuerdo 312-313 estudios 314 ocumar11 315-316 rama09 317 condicion11 318-319 estatus 320 ///
    using "DA3119.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p44 cov_sex
rename p45 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2015_immigration_master.dta", replace

**# Bookmark 1: assistance

* ============================================================
* assistance (P101 to P104)
* 1-4 perceived amount of assistance received by social groups (older people alone, pensioners, unemployed, immigrants), Mucha to Ninguna
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p101 p102 p103 p104

keep id cov_* `survey_cols'

replace p101 = . if inlist(p101, 8, 9)
replace p102 = . if inlist(p102, 8, 9)
replace p103 = . if inlist(p103, 8, 9)
replace p104 = . if inlist(p104, 8, 9)

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
export delimited using "spain_2015_immigration_assistance.csv", replace

**# Bookmark 2: criteria

* ============================================================
* criteria (P501 to P508)
* 0-10 importance of criteria for admitting immigrants (education, family, language, Christian origin, white skin, money, qualification, adopting the way of life)
* no NO LEER code, 98/99 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p501 p502 p503 p504 p505 p506 p507 p508

keep id cov_* `survey_cols'

replace p501 = . if inlist(p501, 98, 99)
replace p502 = . if inlist(p502, 98, 99)
replace p503 = . if inlist(p503, 98, 99)
replace p504 = . if inlist(p504, 98, 99)
replace p505 = . if inlist(p505, 98, 99)
replace p506 = . if inlist(p506, 98, 99)
replace p507 = . if inlist(p507, 98, 99)
replace p508 = . if inlist(p508, 98, 99)

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
export delimited using "spain_2015_immigration_criteria.csv", replace

**# Bookmark 3: diversity

* ============================================================
* diversity (P901 to P904)
* 0-10 valuation of the diversity of countries, cultures, religions and skin colours in Spain, Muy negativo to Muy positivo
* no NO LEER code, 98/99 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p901 p902 p903 p904

keep id cov_* `survey_cols'

replace p901 = . if inlist(p901, 98, 99)
replace p902 = . if inlist(p902, 98, 99)
replace p903 = . if inlist(p903, 98, 99)
replace p904 = . if inlist(p904, 98, 99)

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
export delimited using "spain_2015_immigration_diversity.csv", replace

**# Bookmark 4: rights

* ============================================================
* rights (P1301 to P1305)
* yes/no on rights that settled immigrants should have (family reunification, unemployment benefit, municipal vote, general vote, nationality)
* two-category scale, 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p1301 p1302 p1303 p1304 p1305

keep id cov_* `survey_cols'

replace p1301 = . if inlist(p1301, 8, 9)
replace p1302 = . if inlist(p1302, 8, 9)
replace p1303 = . if inlist(p1303, 8, 9)
replace p1304 = . if inlist(p1304, 8, 9)
replace p1305 = . if inlist(p1305, 8, 9)

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
export delimited using "spain_2015_immigration_rights.csv", replace

**# Bookmark 5: health

* ============================================================
* health (P1401 to P1404)
* 1-4 agreement with statements on immigrants and health care, Muy de acuerdo to Muy en desacuerdo
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p1401 p1402 p1403 p1404

keep id cov_* `survey_cols'

replace p1401 = . if inlist(p1401, 8, 9)
replace p1402 = . if inlist(p1402, 8, 9)
replace p1403 = . if inlist(p1403, 8, 9)
replace p1404 = . if inlist(p1404, 8, 9)

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
export delimited using "spain_2015_immigration_health.csv", replace

**# Bookmark 6: education

* ============================================================
* education (P1501 to P1504)
* 1-4 agreement with statements on immigrant children in schools, Muy de acuerdo to Muy en desacuerdo
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p1501 p1502 p1503 p1504

keep id cov_* `survey_cols'

replace p1501 = . if inlist(p1501, 8, 9)
replace p1502 = . if inlist(p1502, 8, 9)
replace p1503 = . if inlist(p1503, 8, 9)
replace p1504 = . if inlist(p1504, 8, 9)

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
export delimited using "spain_2015_immigration_education.csv", replace

**# Bookmark 7: labour

* ============================================================
* labour (P2101 to P2105)
* 1-4 agreement with statements on immigrants and the labour market, Muy de acuerdo to Muy en desacuerdo
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p2101 p2102 p2103 p2104 p2105

keep id cov_* `survey_cols'

replace p2101 = . if inlist(p2101, 8, 9)
replace p2102 = . if inlist(p2102, 8, 9)
replace p2103 = . if inlist(p2103, 8, 9)
replace p2104 = . if inlist(p2104, 8, 9)
replace p2105 = . if inlist(p2105, 8, 9)

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
export delimited using "spain_2015_immigration_labour.csv", replace

**# Bookmark 8: acceptability

* ============================================================
* acceptability (P2201 to P2204)
* 1-4 acceptability of discriminatory situations, Muy aceptable to Nada aceptable
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p2201 p2202 p2203 p2204

keep id cov_* `survey_cols'

replace p2201 = . if inlist(p2201, 8, 9)
replace p2202 = . if inlist(p2202, 8, 9)
replace p2203 = . if inlist(p2203, 8, 9)
replace p2204 = . if inlist(p2204, 8, 9)

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
export delimited using "spain_2015_immigration_acceptability.csv", replace

**# Bookmark 9: distance

* ============================================================
* distance (P2401 to P2408)
* 1-3 social distance towards immigrants, Acepta / Trataria de evitar / Rechazaria
* code 4 (NO LEER, Depende) is an off-scale volunteered code, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p2401 p2402 p2403 p2404 p2405 p2406 p2407 p2408

keep id cov_* `survey_cols'

replace p2401 = . if inlist(p2401, 4, 8, 9)
replace p2402 = . if inlist(p2402, 4, 8, 9)
replace p2403 = . if inlist(p2403, 4, 8, 9)
replace p2404 = . if inlist(p2404, 4, 8, 9)
replace p2405 = . if inlist(p2405, 4, 8, 9)
replace p2406 = . if inlist(p2406, 4, 8, 9)
replace p2407 = . if inlist(p2407, 4, 8, 9)
replace p2408 = . if inlist(p2408, 4, 8, 9)

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
export delimited using "spain_2015_immigration_distance.csv", replace

**# Bookmark 10: roma

* ============================================================
* roma (P2501 to P2508)
* 1-3 social distance towards Roma people, Acepta / Trataria de evitar / Rechazaria
* code 4 (NO LEER, Depende) is an off-scale volunteered code, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p2501 p2502 p2503 p2504 p2505 p2506 p2507 p2508

keep id cov_* `survey_cols'

replace p2501 = . if inlist(p2501, 4, 8, 9)
replace p2502 = . if inlist(p2502, 4, 8, 9)
replace p2503 = . if inlist(p2503, 4, 8, 9)
replace p2504 = . if inlist(p2504, 4, 8, 9)
replace p2505 = . if inlist(p2505, 4, 8, 9)
replace p2506 = . if inlist(p2506, 4, 8, 9)
replace p2507 = . if inlist(p2507, 4, 8, 9)
replace p2508 = . if inlist(p2508, 4, 8, 9)

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
export delimited using "spain_2015_immigration_roma.csv", replace

**# Bookmark 11: contact

* ============================================================
* contact (P26, P26A, P26B, P26C)
* 1-4 how many immigrants among neighbours, friends, workmates and relatives, Muchos to Ninguno
* code 7 (No procede) is a filter code, recoded to missing; 8/9 recoded; no NO LEER code
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p26 p26a p26b p26c

keep id cov_* `survey_cols'

replace p26 = . if inlist(p26, 7, 8, 9)
replace p26a = . if inlist(p26a, 7, 8, 9)
replace p26b = . if inlist(p26b, 7, 8, 9)
replace p26c = . if inlist(p26c, 7, 8, 9)

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
export delimited using "spain_2015_immigration_contact.csv", replace

**# Bookmark 12: proximity

* ============================================================
* proximity (P27, P27A, P27B, P27C)
* 1-4 how many Roma people among neighbours, friends, workmates and relatives, Muchos to Ninguno
* code 7 (No procede) is a filter code, recoded to missing; 8/9 recoded; no NO LEER code
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p27 p27a p27b p27c

keep id cov_* `survey_cols'

replace p27 = . if inlist(p27, 7, 8, 9)
replace p27a = . if inlist(p27a, 7, 8, 9)
replace p27b = . if inlist(p27b, 7, 8, 9)
replace p27c = . if inlist(p27c, 7, 8, 9)

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
export delimited using "spain_2015_immigration_proximity.csv", replace

**# Bookmark 13: punishment

* ============================================================
* punishment (P32, P33)
* 1-4 how often citizens who utter racist insults or incite hatred should be punished, En todos los casos to En ningun caso
* code 5 (NO LEER, Depende) is an off-scale volunteered code, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2015_immigration_master.dta", clear

local survey_cols p32 p33

keep id cov_* `survey_cols'

replace p32 = . if inlist(p32, 5, 8, 9)
replace p33 = . if inlist(p33, 5, 8, 9)

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
export delimited using "spain_2015_immigration_punishment.csv", replace