*** This Stata Do File processes the spain_2011_immigrant study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2011_immigrant"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES2913

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    area 18 distrito 19-20 seccion 21-23 entrev 24-27 muestra 28 dia 29-30 ///
    mes 31-32 year 33-34 hora 35-36 minuto 37-38 p101 39-40 p102 41-44 ///
    p2 45-47 p301 48-49 p302 50-53 p4 54 p501 55-57 p502 58-60 ///
    p503 61-63 p504 64-66 p601 67-69 p602 70-72 p603 73-75 p604 76-78 ///
    p7 79 p7a 80-81 p7b 82-83 p7c 84-85 p8 86-87 p901 88-89 ///
    p902 90-91 p903 92-93 p904 94-95 p905 96-97 p906 98-99 p907 100-101 ///
    p10a 102 p10b 103-106 p10c01 107 p10c02 108 p10c03 109 p10c04 110 ///
    p1101 111 p1102 112 p1103 113 p1104 114 p1105 115 p1106 116 ///
    p1107 117 p1108 118 p1109 119 p12 120 p12a 121-124 p1301 125 ///
    p1302 126 p1303 127 p1304 128 p14 129 p1501 130 p1502 131 ///
    p1503 132 p1504 133 p1505 134 p1506 135 p1507 136 p1508 137 ///
    p1509 138 p1601 139 p1602 140 p1603 141 p1604 142 p17a 143 ///
    p17b 144-147 p1801 148 p1802 149 p1803 150 p1804 151 p1805 152 ///
    p1806 153 p1807 154 p1808 155 p19 156 p2001 157 p2002 158 ///
    p2003 159 p2004 160 p21 161 p2201 162 p2202 163 p2203 164 ///
    p2204 165 p2205 166 p2206 167 p2207 168 p2208 169 p2301 170 ///
    p2302 171 p2303 172 p2304 173 p24 174-175 p25 176 p2601 177-179 ///
    p2602 180-182 p2603 183-185 p2604 186-188 p2701 189-191 p2702 192-194 p2703 195-197 ///
    p2704 198-200 p28a 201 p28b 202 p28c 203-206 p28d 207 p28j 208 ///
    p30a 209 p30b 210 p30c 211-214 p30d 215 p30j 216 p3201 217 ///
    p3202 218 p3203 219 p3204 220 p3205 221 p3206 222 p3207 223 ///
    p3208 224 p3209 225 p3210 226 p3301 227 p3302 228 p3303 229 ///
    p3304 230 p3305 231 p3306 232 p3307 233 p3308 234 p3401 235 ///
    p3402 236 p3403 237 p3404 238 p3405 239 p3501 240 p3502 241 ///
    p3503 242 p3504 243 p3505 244 p3601 245-247 p3602 248-250 p3603 251-253 ///
    p3604 254-256 p3605 257-259 p3606 260-262 p3701 263-265 p3702 266-268 p3703 269-271 ///
    p3704 272-274 p3705 275-277 p3706 278-280 p3801 281 p3802 282 p3803 283 ///
    p3804 284 p3805 285 p3806 286 p3807 287 p3808 288 p3809 289 ///
    p39 290 p4001 291 p4002 292 p4003 293 p4004 294 p4005 295 ///
    p4006 296 p38a01 297 p38a02 298 p38a03 299 p38a04 300 p38a05 301 ///
    p38a06 302 p38a07 303 p38a08 304 p38a09 305 p39a 306 p40a01 307 ///
    p40a02 308 p40a03 309 p40a04 310 p40a05 311 p40a06 312 p41 313-314 ///
    p42 315 p43 316 p44 317 p4501 318 p4502 319 p4503 320 ///
    p4504 321 p4505 322 p4506 323 p4507 324 p4508 325 p4509 326 ///
    p46a 327-328 p46b 329-330 p46c 331-332 p4701 333 p4702 334 p4703 335 ///
    p4704 336 p4705 337 p4706 338 p4707 339 p4708 340 p4709 341 ///
    p4710 342 p4711 343 p4712 344 p48a 345 p4801a 346-347 p48b 348 ///
    p4801b 349-350 p48c 351 p4801c 352-353 p49 354 p50 355 p5201 356 ///
    p5202 357 p5203 358 p5204 359 p5205 360 p5206 361 p5207 362 ///
    p5208 363 p5209 364 p5210 365 p53 366 p54a 367 p54b 368 ///
    p54c 369 p55 370 p56a1 371 p56a101 372 p56a102 373 p56a103 374 ///
    p56a104 375 p56a105 376 p56a106 377 p56a2 378 p56a201 379 p56a202 380 ///
    p56a203 381 p56a204 382 p56a205 383 p56a206 384 p56a3 385 p56b 386 ///
    p5701 387 p5702 388 p5703 389 p5704 390 p5705 391 p5706 392 ///
    p5707 393 p58 394 p5901 395 p5902 396 p5903 397 p5904 398 ///
    p60 399 p61 400 p62 401 s301 402-403 s302 404-405 s303 406-407 ///
    s401 408-409 s402 410-411 s5 412 s6 413 s6a01 414 s6a02 415 ///
    s6a03 416 s6a04 417 s6a05 418 s6a06 419 s7 420 s801 421 ///
    s802 422 s8a 423 s9 424 s10 425 c1 426 c1a 427-428 ///
    c2 429 c2a 430 c2b 431-432 c3 433 c4 434-435 filp10 436 ///
    filp21 437 filp32 438 filp33 439 filp34 440 filp35 441 filp56 442 ///
    barriomu 443-445 peso1 446-453 peso2 454-461 edad 462-463 p56a107 464 p56a207 465 ///
    using "DA2913.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename s5 cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 99

* S5 is coded 1 Mujer 2 Hombre in ES2913; recoded to the pipeline convention 1 Hombre 2 Mujer
recode cov_sex (1 = 2) (2 = 1)

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2011_immigrant_master.dta", replace

**# Bookmark 1: satisfaction

* ============================================================
* satisfaction (P901 to P907)
* 0-10 satisfaction with life in general, education, current job, housing, family life, health and social life
* two-digit rating scale, 98 N.S. and 99 N.C. recoded; P903 carries an undocumented 97 for respondents without a job, treated as not applicable and recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p901 p902 p903 p904 p905 p906 p907

keep id cov_* `survey_cols'

replace p901 = . if inlist(p901, 98, 99)
replace p902 = . if inlist(p902, 98, 99)
replace p903 = . if inlist(p903, 97, 98, 99)
replace p904 = . if inlist(p904, 98, 99)
replace p905 = . if inlist(p905, 98, 99)
replace p906 = . if inlist(p906, 98, 99)
replace p907 = . if inlist(p907, 98, 99)

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
export delimited using "spain_2011_immigrant_satisfaction.csv", replace

**# Bookmark 2: citizenship

* ============================================================
* citizenship (P1301 to P1304)
* 1-3 degree to which having obtained Spanish nationality has made it easier to get or improve a job, improve education, take part in local public affairs and feel settled in Spain
* asked only to naturalised respondents; blanks are structural; 7 No procede on P1301 (no job) is a documented not-applicable code and is recoded
* three read categories mucho mas facil / algo mas facil / nada, no NO LEER code; 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p1301 p1302 p1303 p1304

keep id cov_* `survey_cols'

replace p1301 = . if inlist(p1301, 7, 8, 9)
replace p1302 = . if inlist(p1302, 8, 9)
replace p1303 = . if inlist(p1303, 8, 9)
replace p1304 = . if inlist(p1304, 8, 9)

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
export delimited using "spain_2011_immigrant_citizenship.csv", replace

**# Bookmark 3: naturalisation

* ============================================================
* naturalisation (P1601 to P1604)
* 1-3 degree to which obtaining Spanish nationality would make the same four things easier
* asked only to respondents without Spanish nationality; blanks are structural
* three read categories mucho mas facil / algo mas facil / nada, no NO LEER code; only 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

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
export delimited using "spain_2011_immigrant_naturalisation.csv", replace

**# Bookmark 4: residence

* ============================================================
* residence (P2001 to P2004)
* 1-3 degree to which having obtained permanent residence has made the same four things easier
* asked only to holders of permanent residence; blanks are structural; 7 No procede on P2001 is a documented not-applicable code and is recoded
* three read categories mucho mas facil / algo mas facil / nada, no NO LEER code; 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p2001 p2002 p2003 p2004

keep id cov_* `survey_cols'

replace p2001 = . if inlist(p2001, 7, 8, 9)
replace p2002 = . if inlist(p2002, 8, 9)
replace p2003 = . if inlist(p2003, 8, 9)
replace p2004 = . if inlist(p2004, 8, 9)

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
export delimited using "spain_2011_immigrant_residence.csv", replace

**# Bookmark 5: permit

* ============================================================
* permit (P2301 to P2304)
* 1-3 degree to which obtaining permanent residence would make the same four things easier
* asked only to respondents without permanent residence or nationality; blanks are structural
* three read categories mucho mas facil / algo mas facil / nada, no NO LEER code; only 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

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
export delimited using "spain_2011_immigrant_permit.csv", replace

**# Bookmark 6: family

* ============================================================
* family (P3401 to P3405)
* 1-3 degree to which family reunification has made it easier to get a job, improve education, take part in public affairs, feel settled and have an easier family life
* asked only to respondents who reunified family members; blanks are structural; 7 No procede on P3401 is a documented not-applicable code and is recoded
* three read categories mucho mas facil / algo mas facil / nada, no NO LEER code; 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p3401 p3402 p3403 p3404 p3405

keep id cov_* `survey_cols'

replace p3401 = . if inlist(p3401, 7, 8, 9)
replace p3402 = . if inlist(p3402, 8, 9)
replace p3403 = . if inlist(p3403, 8, 9)
replace p3404 = . if inlist(p3404, 8, 9)
replace p3405 = . if inlist(p3405, 8, 9)

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
export delimited using "spain_2011_immigrant_family.csv", replace

**# Bookmark 7: reunification

* ============================================================
* reunification (P3501 to P3505)
* 1-3 degree to which family reunification would make the same five things easier
* asked only to respondents who have not reunified family; blanks are structural
* three read categories mucho mas facil / algo mas facil / nada, no NO LEER code; only 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p3501 p3502 p3503 p3504 p3505

keep id cov_* `survey_cols'

replace p3501 = . if inlist(p3501, 8, 9)
replace p3502 = . if inlist(p3502, 8, 9)
replace p3503 = . if inlist(p3503, 8, 9)
replace p3504 = . if inlist(p3504, 8, 9)
replace p3505 = . if inlist(p3505, 8, 9)

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
export delimited using "spain_2011_immigrant_reunification.csv", replace

**# Bookmark 8: spanish

* ============================================================
* spanish (P4001 to P4006)
* 1-3 degree to which the Spanish language course helped with six objectives (basic Spanish, all the Spanish wanted, specific vocabulary, a job, and two further objectives), mucho / algo / nada
* asked only to respondents who took a Spanish course (P39 = 1); blanks are structural
* three read categories, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p4001 p4002 p4003 p4004 p4005 p4006

keep id cov_* `survey_cols'

replace p4001 = . if inlist(p4001, 8, 9)
replace p4002 = . if inlist(p4002, 8, 9)
replace p4003 = . if inlist(p4003, 8, 9)
replace p4004 = . if inlist(p4004, 8, 9)
replace p4005 = . if inlist(p4005, 8, 9)
replace p4006 = . if inlist(p4006, 8, 9)

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
export delimited using "spain_2011_immigrant_spanish.csv", replace

**# Bookmark 9: catalan

* ============================================================
* catalan (P40A01 to P40A06)
* 1-3 degree to which the Catalan language course helped with the same six objectives, mucho / algo / nada
* asked only in Barcelona to respondents who took a Catalan course (P39A = 1); blanks are structural
* three read categories, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p40a01 p40a02 p40a03 p40a04 p40a05 p40a06

keep id cov_* `survey_cols'

replace p40a01 = . if inlist(p40a01, 8, 9)
replace p40a02 = . if inlist(p40a02, 8, 9)
replace p40a03 = . if inlist(p40a03, 8, 9)
replace p40a04 = . if inlist(p40a04, 8, 9)
replace p40a05 = . if inlist(p40a05, 8, 9)
replace p40a06 = . if inlist(p40a06, 8, 9)

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
export delimited using "spain_2011_immigrant_catalan.csv", replace

**# Bookmark 10: representation

* ============================================================
* representation (P5901 to P5904)
* agree / disagree with four statements about representatives of immigrant origin in the Spanish Parliament
* asked only to respondents who answered P58 (N.S. skips to P60); blanks are structural
* two-category agreement scale treated as yes/no selected response; only 8/9 recoded
* ============================================================

use "spain_2011_immigrant_master.dta", clear

local survey_cols p5901 p5902 p5903 p5904

keep id cov_* `survey_cols'

replace p5901 = . if inlist(p5901, 8, 9)
replace p5902 = . if inlist(p5902, 8, 9)
replace p5903 = . if inlist(p5903, 8, 9)
replace p5904 = . if inlist(p5904, 8, 9)

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
export delimited using "spain_2011_immigrant_representation.csv", replace