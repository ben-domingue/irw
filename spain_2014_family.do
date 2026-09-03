*** This Stata Do File processes the spain_2014_family study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2014_family"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES3032

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    area 18 distr 19-20 seccion 21-23 entrev 24-27 p0 28 p101 29 ///
    p102 30 p103 31 p104 32 p105 33 p106 34 p107 35 ///
    p108 36 p109 37 p201 38 p202 39 p203 40 p204 41 ///
    p205 42 p206 43 p207 44 p208 45 p209 46 p210 47 ///
    p3 48-49 p4 50-51 p501 52 p502 53 p503 54 p504 55 ///
    p505 56 p506 57 p507 58 p601 59-60 p602 61-62 p701 63 ///
    p702 64 p703 65 p704 66 p705 67 p706 68 p707 69 ///
    p708 70 p8 71 p8a 72 p8b 73 p8c01 74-75 p8c02 76-77 ///
    p8d01 78 p8d02 79 p8d03 80 p8d04 81 p8d05 82 p8d06 83 ///
    p8e01 84 p8e02 85 p8e03 86 p8e04 87 p8e05 88 p8e06 89 ///
    p8f 90 p8g01 91 p8g02 92 p8g03 93 p8g04 94 p8g05 95 ///
    p8g06 96 p901 97 p902 98 p903 99 p904 100 p905 101 ///
    p906 102 p907 103 p908 104 p909 105 p1001 106 p1002 107 ///
    p1003 108 p1004 109 p1005 110 p1006 111 p1101 112-113 p1102 114-115 ///
    p1103 116-117 p1201 118 p1202 119 p1203 120 p1204 121 p1205 122 ///
    p1206 123 p1207 124 p1208 125 p1209 126 p1210 127 p13 128-129 ///
    p1401 130 p1402 131 p1403 132 p1404 133 p1405 134 p1406 135 ///
    p1407 136 p1408 137 p1409 138 p1410 139 p1411 140 p1412 141 ///
    p15 142 p16 143 p1701 144 p1702 145 p1801 146 p1802 147 ///
    p1803 148 p1804 149 p1805 150 p1901 151-152 p1902 153-154 p1903 155-156 ///
    p1904 157-158 p1905 159-160 p20 161 p20a 162-163 p20b 164 p20c01 165 ///
    p20c02 166 p20c03 167 p20c04 168 p20db01 169-170 p20db02 171-172 p20e01 173 ///
    p20e02 174 p20e03 175 p20e04 176 p20e05 177 p20e06 178 p20e07 179 ///
    p20f01 180 p20f02 181 p20f03 182 p20f04 183 p20f05 184 p20f06 185 ///
    p20f07 186 p20f08 187 p20f09 188 p20f10 189 p21 190 p21a 191-192 ///
    p21b 193 p21c01 194-195 p21c02 196-197 p21c03 198-199 p21d01 200 p21d02 201 ///
    p21d03 202 p21d04 203 p21d05 204 p21d06 205 p21d07 206 p21d08 207 ///
    p21d09 208 p21d10 209 p21d11 210 p21d12 211 p21e 212-213 p21f 214-215 ///
    p21g01 216 p21g02 217 p21g03 218 p21g04 219 p21g05 220 p21g06 221 ///
    p21g07 222 p21g08 223 p22 224 p22a 225 p22b 226 p23 227 ///
    p24 228 p2501 229 p2502 230 p2503 231 p2504 232 p26 233-234 ///
    p27 235 p2801 236 p2802 237 p2803 238 p2804 239 p2805 240 ///
    p2806 241 p2807 242 p2901 243-244 p2902 245-246 p2903 247-248 p30 249-250 ///
    p31 251 p31a 252-253 p32 254 p33 255-256 p34 257 p34a 258-259 ///
    p35 260 p35a 261 p36 262 p37 263 p38 264 p39 265 ///
    p40 266 p40a01 267 p40a02 268 p40a03 269 p40a04 270 p41 271-273 ///
    p42 274 p42a 275 p43 276-278 p44 279-280 p45 281-282 p46 283 ///
    p46a 284 p46b 285 p47 286 p4801 287 p4802 288 p4803 289 ///
    p4804 290 str3 p4901 291-293 str3 p4902 294-296 str3 p4903 297-299 str3 p4904 300-302 str3 p4905 303-305 ///
    str3 p5001 306-308 str3 p5002 309-311 str3 p5003 312-314 str3 p5004 315-317 str3 p5005 318-320 p51 321 ///
    p52 322 p53 323 p54 324 i1 325-327 i2 328-330 i3 331-333 ///
    i4 334-336 i5 337-339 i6 340-342 i7 343-345 i8 346-348 i9 349-351 ///
    e101 352-353 e102 354-355 e103 356-357 e2 358 e3 359-361 e4 362 ///
    c1 363 c1a 364-365 c2 366 c2a 367 c2b 368-369 c3 370 ///
    c4 371-372 p20da01 373-374 p20da02 375-376 recuerdo 377-378 estudios 379 ocumar11 380-381 ///
    rama09 382 condicion11 383-384 estatus 385 ///
    using "DA3032.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p32 cov_sex
rename p33 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2014_family_master.dta", replace

**# Bookmark 1: importance

* ============================================================
* importance (P101 to P109)
* 1-4 importance of life domains, Muy importante to Nada importante
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p101 p102 p103 p104 p105 p106 p107 p108 p109

keep id cov_* `survey_cols'

replace p101 = . if inlist(p101, 8, 9)
replace p102 = . if inlist(p102, 8, 9)
replace p103 = . if inlist(p103, 8, 9)
replace p104 = . if inlist(p104, 8, 9)
replace p105 = . if inlist(p105, 8, 9)
replace p106 = . if inlist(p106, 8, 9)
replace p107 = . if inlist(p107, 8, 9)
replace p108 = . if inlist(p108, 8, 9)
replace p109 = . if inlist(p109, 8, 9)

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
export delimited using "spain_2014_family_importance.csv", replace

**# Bookmark 2: satisfaction

* ============================================================
* satisfaction (P201 to P210)
* 1-4 satisfaction with life domains, Muy satisfecho/a to Nada satisfecho/a
* code 7 (N.P.) is a filter code, recoded to missing; 9 recoded; no NO LEER code
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p201 p202 p203 p204 p205 p206 p207 p208 p209 p210

keep id cov_* `survey_cols'

replace p201 = . if inlist(p201, 7, 9)
replace p202 = . if inlist(p202, 7, 9)
replace p203 = . if inlist(p203, 7, 9)
replace p204 = . if inlist(p204, 7, 9)
replace p205 = . if inlist(p205, 7, 9)
replace p206 = . if inlist(p206, 7, 9)
replace p207 = . if inlist(p207, 7, 9)
replace p208 = . if inlist(p208, 7, 9)
replace p209 = . if inlist(p209, 7, 9)
replace p210 = . if inlist(p210, 7, 9)

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
export delimited using "spain_2014_family_satisfaction.csv", replace

**# Bookmark 3: care

* ============================================================
* care (P501 to P507)
* 1-5 agreement with statements on family versus institutional care and support, Muy de acuerdo to Nada de acuerdo
* code 3 (NO LEER, Ni de acuerdo ni en desacuerdo) is a volunteered midpoint, recoded to missing; 9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p501 p502 p503 p504 p505 p506 p507

keep id cov_* `survey_cols'

replace p501 = . if inlist(p501, 3, 9)
replace p502 = . if inlist(p502, 3, 9)
replace p503 = . if inlist(p503, 3, 9)
replace p504 = . if inlist(p504, 3, 9)
replace p505 = . if inlist(p505, 3, 9)
replace p506 = . if inlist(p506, 3, 9)
replace p507 = . if inlist(p507, 3, 9)

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
export delimited using "spain_2014_family_care.csv", replace

**# Bookmark 4: chores

* ============================================================
* chores (P8D01 to P8D06)
* 1-5 who does household tasks in the couple, Siempre la mujer to Siempre el hombre
* code 6 (a third person) is an off-scale category, recoded to missing; 0 and 7 are N.P. filter codes (no cohabiting partner), recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p8d01 p8d02 p8d03 p8d04 p8d05 p8d06

keep id cov_* `survey_cols'

replace p8d01 = . if inlist(p8d01, 0, 6, 7, 8, 9)
replace p8d02 = . if inlist(p8d02, 0, 6, 7, 8, 9)
replace p8d03 = . if inlist(p8d03, 0, 6, 7, 8, 9)
replace p8d04 = . if inlist(p8d04, 0, 6, 7, 8, 9)
replace p8d05 = . if inlist(p8d05, 0, 6, 7, 8, 9)
replace p8d06 = . if inlist(p8d06, 0, 6, 7, 8, 9)

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
export delimited using "spain_2014_family_chores.csv", replace

**# Bookmark 5: marriage

* ============================================================
* marriage (P901 to P909)
* 1-4 importance of reasons for getting married, Mucho to Nada
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p901 p902 p903 p904 p905 p906 p907 p908 p909

keep id cov_* `survey_cols'

replace p901 = . if inlist(p901, 8, 9)
replace p902 = . if inlist(p902, 8, 9)
replace p903 = . if inlist(p903, 8, 9)
replace p904 = . if inlist(p904, 8, 9)
replace p905 = . if inlist(p905, 8, 9)
replace p906 = . if inlist(p906, 8, 9)
replace p907 = . if inlist(p907, 8, 9)
replace p908 = . if inlist(p908, 8, 9)
replace p909 = . if inlist(p909, 8, 9)

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
export delimited using "spain_2014_family_marriage.csv", replace

**# Bookmark 6: matrimony

* ============================================================
* matrimony (P1001 to P1006)
* 1-5 agreement with statements on what marriage means, Muy de acuerdo to Nada de acuerdo
* code 3 (NO LEER, Ni de acuerdo ni en desacuerdo) is a volunteered midpoint, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p1001 p1002 p1003 p1004 p1005 p1006

keep id cov_* `survey_cols'

replace p1001 = . if inlist(p1001, 3, 8, 9)
replace p1002 = . if inlist(p1002, 3, 8, 9)
replace p1003 = . if inlist(p1003, 3, 8, 9)
replace p1004 = . if inlist(p1004, 3, 8, 9)
replace p1005 = . if inlist(p1005, 3, 8, 9)
replace p1006 = . if inlist(p1006, 3, 8, 9)

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
export delimited using "spain_2014_family_matrimony.csv", replace

**# Bookmark 7: families

* ============================================================
* families (P1201 to P1210)
* 1-5 agreement with statements on family forms, Muy de acuerdo to Nada de acuerdo
* code 3 (NO LEER, Ni de acuerdo ni en desacuerdo) is a volunteered midpoint, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p1201 p1202 p1203 p1204 p1205 p1206 p1207 p1208 p1209 p1210

keep id cov_* `survey_cols'

replace p1201 = . if inlist(p1201, 3, 8, 9)
replace p1202 = . if inlist(p1202, 3, 8, 9)
replace p1203 = . if inlist(p1203, 3, 8, 9)
replace p1204 = . if inlist(p1204, 3, 8, 9)
replace p1205 = . if inlist(p1205, 3, 8, 9)
replace p1206 = . if inlist(p1206, 3, 8, 9)
replace p1207 = . if inlist(p1207, 3, 8, 9)
replace p1208 = . if inlist(p1208, 3, 8, 9)
replace p1209 = . if inlist(p1209, 3, 8, 9)
replace p1210 = . if inlist(p1210, 3, 8, 9)

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
export delimited using "spain_2014_family_families.csv", replace

**# Bookmark 8: adoption

* ============================================================
* adoption (P1701, P1702)
* 1-5 agreement with statements on the purpose of adoption, Muy de acuerdo to Nada de acuerdo
* code 3 (NO LEER, Ni de acuerdo ni en desacuerdo) is a volunteered midpoint, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p1701 p1702

keep id cov_* `survey_cols'

replace p1701 = . if inlist(p1701, 3, 8, 9)
replace p1702 = . if inlist(p1702, 3, 8, 9)

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
export delimited using "spain_2014_family_adoption.csv", replace

**# Bookmark 9: reproduction

* ============================================================
* reproduction (P1801 to P1805)
* 1-2 for or against access to assisted reproduction for five types of person, Mas bien a favor / Mas bien en contra
* code 3 (NO LEER, Depende de los casos) is a volunteered non-scale code, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p1801 p1802 p1803 p1804 p1805

keep id cov_* `survey_cols'

replace p1801 = . if inlist(p1801, 3, 8, 9)
replace p1802 = . if inlist(p1802, 3, 8, 9)
replace p1803 = . if inlist(p1803, 3, 8, 9)
replace p1804 = . if inlist(p1804, 3, 8, 9)
replace p1805 = . if inlist(p1805, 3, 8, 9)

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
export delimited using "spain_2014_family_reproduction.csv", replace

**# Bookmark 10: conflicts

* ============================================================
* conflicts (P21D01 to P21D12)
* 1-3 seriousness of issues with cohabiting children, Un problema grave / Un problema leve / No es un problema
* 0 is N.P. (no cohabiting children), a structural filter code, recoded to missing; 9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p21d01 p21d02 p21d03 p21d04 p21d05 p21d06 p21d07 p21d08 p21d09 p21d10 p21d11 p21d12

keep id cov_* `survey_cols'

replace p21d01 = . if inlist(p21d01, 0, 9)
replace p21d02 = . if inlist(p21d02, 0, 9)
replace p21d03 = . if inlist(p21d03, 0, 9)
replace p21d04 = . if inlist(p21d04, 0, 9)
replace p21d05 = . if inlist(p21d05, 0, 9)
replace p21d06 = . if inlist(p21d06, 0, 9)
replace p21d07 = . if inlist(p21d07, 0, 9)
replace p21d08 = . if inlist(p21d08, 0, 9)
replace p21d09 = . if inlist(p21d09, 0, 9)
replace p21d10 = . if inlist(p21d10, 0, 9)
replace p21d11 = . if inlist(p21d11, 0, 9)
replace p21d12 = . if inlist(p21d12, 0, 9)

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
export delimited using "spain_2014_family_conflicts.csv", replace

**# Bookmark 11: activities

* ============================================================
* activities (P21G01 to P21G08)
* 1-4 frequency of activities with cohabiting children, Todos o casi todos los dias to Casi nunca o nunca
* 0 is N.P. (no cohabiting children) and 7 is N.P. (not applicable), both structural filter codes, recoded to missing; 9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p21g01 p21g02 p21g03 p21g04 p21g05 p21g06 p21g07 p21g08

keep id cov_* `survey_cols'

replace p21g01 = . if inlist(p21g01, 0, 7, 9)
replace p21g02 = . if inlist(p21g02, 0, 7, 9)
replace p21g03 = . if inlist(p21g03, 0, 7, 9)
replace p21g04 = . if inlist(p21g04, 0, 7, 9)
replace p21g05 = . if inlist(p21g05, 0, 7, 9)
replace p21g06 = . if inlist(p21g06, 0, 7, 9)
replace p21g07 = . if inlist(p21g07, 0, 7, 9)
replace p21g08 = . if inlist(p21g08, 0, 7, 9)

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
export delimited using "spain_2014_family_activities.csv", replace

**# Bookmark 12: obstacles

* ============================================================
* obstacles (P2501 to P2504)
* 1-5 agreement that marriage and children are obstacles to men's and women's professional life, Muy de acuerdo to Nada de acuerdo
* code 3 (NO LEER, Ni de acuerdo ni en desacuerdo) is a volunteered midpoint, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p2501 p2502 p2503 p2504

keep id cov_* `survey_cols'

replace p2501 = . if inlist(p2501, 3, 8, 9)
replace p2502 = . if inlist(p2502, 3, 8, 9)
replace p2503 = . if inlist(p2503, 3, 8, 9)
replace p2504 = . if inlist(p2504, 3, 8, 9)

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
export delimited using "spain_2014_family_obstacles.csv", replace

**# Bookmark 13: change

* ============================================================
* change (P2801 to P2807)
* 1-2 whether aspects of family life increase or decrease, Aumenta / Disminuye
* code 3 (NO LEER, Permanece igual) is a volunteered non-scale code, recoded to missing; 8/9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p2801 p2802 p2803 p2804 p2805 p2806 p2807

keep id cov_* `survey_cols'

replace p2801 = . if inlist(p2801, 3, 8, 9)
replace p2802 = . if inlist(p2802, 3, 8, 9)
replace p2803 = . if inlist(p2803, 3, 8, 9)
replace p2804 = . if inlist(p2804, 3, 8, 9)
replace p2805 = . if inlist(p2805, 3, 8, 9)
replace p2806 = . if inlist(p2806, 3, 8, 9)
replace p2807 = . if inlist(p2807, 3, 8, 9)

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
export delimited using "spain_2014_family_change.csv", replace

**# Bookmark 14: housework

* ============================================================
* housework (P40A01 to P40A04)
* 1-3 frequency with which the respondent does domestic tasks, child care, care of dependants and administrative errands, Habitualmente / Ocasionalmente / Nunca
* 0 is N.P. and 4 is No procede (task does not arise), both filter codes, recoded to missing; 9 recoded
* ============================================================

use "spain_2014_family_master.dta", clear

local survey_cols p40a01 p40a02 p40a03 p40a04

keep id cov_* `survey_cols'

replace p40a01 = . if inlist(p40a01, 0, 4, 9)
replace p40a02 = . if inlist(p40a02, 0, 4, 9)
replace p40a03 = . if inlist(p40a03, 0, 4, 9)
replace p40a04 = . if inlist(p40a04, 0, 4, 9)

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
export delimited using "spain_2014_family_housework.csv", replace
