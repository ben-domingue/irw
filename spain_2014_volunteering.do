*** This Stata Do File processes the spain_2014_volunteering study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2014_volunteering"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES3039

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    area 18 distr 19-20 seccion 21-23 entrev 24-27 muestra 28 p101 29-30 ///
    p102 31-32 p201 33-34 p202 35-36 p3 37 p4 38 p501 39 ///
    p502 40 p503 41 p504 42 p505 43 p506 44 p507 45 ///
    p508 46 p509 47 p510 48 p511 49 p6 50-51 p7 52-53 ///
    p8 54 p9 55 p1001 56 p1002 57 p1003 58 p1004 59 ///
    p1005 60 p1006 61 p1007 62 p1008 63 p1009 64 p1010 65 ///
    p1011 66 p1012 67 p1013 68 p1014 69 p1015 70 p1016 71 ///
    p1017 72 p10a01 73 p10a02 74 p10a03 75 p10a04 76 p10a05 77 ///
    p10a06 78 p10a07 79 p10a08 80 p10a09 81 p10a10 82 p10a11 83 ///
    p10a12 84 p10a13 85 p10a14 86 p10a15 87 p10a16 88 p10a17 89 ///
    p11 90 p12 91-92 p13 93-94 p14 95 p14a 96 p14b01 97 ///
    p14b02 98 p14b03 99 p14b04 100 p14b05 101 p14b06 102 p14b07 103 ///
    p14b08 104 p14b09 105 p14b10 106 p14b11 107 p14b12 108 p1501 109 ///
    p1502 110 p1503 111 p1504 112 p16 113 p17 114-115 p18 116 ///
    p19 117 p20 118 p21 119-120 p22 121 p23 122 p2401 123 ///
    p2402 124 p2403 125 p2404 126 p2405 127 p2406 128 p2407 129 ///
    p2408 130 p2409 131 p2410 132 p2411 133 p2412 134 p2413 135 ///
    p2501 136 p2502 137 p2503 138 p2504 139 p2505 140 p2506 141 ///
    p2507 142 p2508 143 p2509 144 p2510 145 p26 146-147 p26a 148-149 ///
    p27 150-151 p28 152-153 p29 154-155 p30 156 p30a 157-158 p31 159-160 ///
    p32 161-162 p33 163-164 p34 165 p35 166 p36 167 p37 168 ///
    p38 169 p39 170 p40 171 p41 172-173 p42 174-176 p43 177 ///
    p43a 178 p44 179-181 p45 182 p45a 183-184 p45b 185 p45c 186-187 ///
    p46 188 p47 189 p48 190 p49 191 p50 192-193 p51 194-196 ///
    p52 197 p52a 198 p53 199-201 p54 202 p55 203 p55a 204 ///
    p55b 205-207 p55c 208 p55d 209 p56 210 p5701 211 p5702 212 ///
    p5703 213 p5704 214 str3 p5801 215-217 str3 p5802 218-220 str3 p5803 221-223 str3 p5804 224-226 ///
    str3 p5805 227-229 str3 p5901 230-232 str3 p5902 233-235 str3 p5903 236-238 str3 p5904 239-241 str3 p5905 242-244 ///
    p60 245 p61 246 p62 247 p63 248 i1 249-251 i2 252-254 ///
    i3 255-257 i4 258-260 i5 261-263 i6 264-266 i7 267-269 i8 270-272 ///
    i9 273-275 e101 276-277 e102 278-279 e103 280-281 e2 282 e3 283-285 ///
    e4 286 c1 287 c1a 288-289 c2 290 c2a 291 c2b 292-293 ///
    c3 294 c4 295-296 recuerdo 297-298 ocumar11 299-300 rama09 301 estudios 302 ///
    ocupapp 303-304 ramapp 305 condicion11pp 306-307 estatuspp 308 ///
    using "DA3039.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p34 cov_sex
rename p31 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2014_volunteering_master.dta", replace

**# Bookmark 1: satisfaction

* ============================================================
* satisfaction (P3, P501 to P511)
* 1-4 satisfaction with life in general (P3) and with eleven life domains (P501 to P511), Muy satisfecho/a to Nada satisfecho/a
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_volunteering_master.dta", clear

local survey_cols p3 p501 p502 p503 p504 p505 p506 p507 p508 p509 p510 p511

keep id cov_* `survey_cols'

replace p3 = . if inlist(p3, 8, 9)
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
export delimited using "spain_2014_volunteering_satisfaction.csv", replace

**# Bookmark 2: membership

* ============================================================
* membership (P1001 to P1016)
* 1-3 membership in sixteen types of association, Si perteneces / Ya no perteneces pero pertenecias / Nunca has pertenecido
* ordered involvement scale, no NO LEER code, only 9 recoded
* ============================================================

use "spain_2014_volunteering_master.dta", clear

local survey_cols p1001 p1002 p1003 p1004 p1005 p1006 p1007 p1008 p1009 p1010 p1011 p1012 p1013 p1014 p1015 p1016

keep id cov_* `survey_cols'

replace p1001 = . if inlist(p1001, 9)
replace p1002 = . if inlist(p1002, 9)
replace p1003 = . if inlist(p1003, 9)
replace p1004 = . if inlist(p1004, 9)
replace p1005 = . if inlist(p1005, 9)
replace p1006 = . if inlist(p1006, 9)
replace p1007 = . if inlist(p1007, 9)
replace p1008 = . if inlist(p1008, 9)
replace p1009 = . if inlist(p1009, 9)
replace p1010 = . if inlist(p1010, 9)
replace p1011 = . if inlist(p1011, 9)
replace p1012 = . if inlist(p1012, 9)
replace p1013 = . if inlist(p1013, 9)
replace p1014 = . if inlist(p1014, 9)
replace p1015 = . if inlist(p1015, 9)
replace p1016 = . if inlist(p1016, 9)

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
export delimited using "spain_2014_volunteering_membership.csv", replace

**# Bookmark 3: activity

* ============================================================
* activity (P10A01 to P10A16)
* yes/no active participation in each association the respondent belongs or belonged to
* 0 is No procede (never a member), a structural filter code, recoded to missing; 9 recoded
* ============================================================

use "spain_2014_volunteering_master.dta", clear

local survey_cols p10a01 p10a02 p10a03 p10a04 p10a05 p10a06 p10a07 p10a08 p10a09 p10a10 p10a11 p10a12 p10a13 p10a14 p10a15 p10a16

keep id cov_* `survey_cols'

replace p10a01 = . if inlist(p10a01, 0, 9)
replace p10a02 = . if inlist(p10a02, 0, 9)
replace p10a03 = . if inlist(p10a03, 0, 9)
replace p10a04 = . if inlist(p10a04, 0, 9)
replace p10a05 = . if inlist(p10a05, 0, 9)
replace p10a06 = . if inlist(p10a06, 0, 9)
replace p10a07 = . if inlist(p10a07, 0, 9)
replace p10a08 = . if inlist(p10a08, 0, 9)
replace p10a09 = . if inlist(p10a09, 0, 9)
replace p10a10 = . if inlist(p10a10, 0, 9)
replace p10a11 = . if inlist(p10a11, 0, 9)
replace p10a12 = . if inlist(p10a12, 0, 9)
replace p10a13 = . if inlist(p10a13, 0, 9)
replace p10a14 = . if inlist(p10a14, 0, 9)
replace p10a15 = . if inlist(p10a15, 0, 9)
replace p10a16 = . if inlist(p10a16, 0, 9)

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
export delimited using "spain_2014_volunteering_activity.csv", replace

**# Bookmark 4: solidarity

* ============================================================
* solidarity (P1501 to P1504)
* 1-4 agreement with statements defining solidarity, Mucho to Nada
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_volunteering_master.dta", clear

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
export delimited using "spain_2014_volunteering_solidarity.csv", replace

**# Bookmark 5: profile

* ============================================================
* profile (P2401 to P2413)
* yes/no whether thirteen descriptions apply to people who do volunteer work
* two-category scale, 8/9 recoded
* ============================================================

use "spain_2014_volunteering_master.dta", clear

local survey_cols p2401 p2402 p2403 p2404 p2405 p2406 p2407 p2408 p2409 p2410 p2411 p2412 p2413

keep id cov_* `survey_cols'

replace p2401 = . if inlist(p2401, 8, 9)
replace p2402 = . if inlist(p2402, 8, 9)
replace p2403 = . if inlist(p2403, 8, 9)
replace p2404 = . if inlist(p2404, 8, 9)
replace p2405 = . if inlist(p2405, 8, 9)
replace p2406 = . if inlist(p2406, 8, 9)
replace p2407 = . if inlist(p2407, 8, 9)
replace p2408 = . if inlist(p2408, 8, 9)
replace p2409 = . if inlist(p2409, 8, 9)
replace p2410 = . if inlist(p2410, 8, 9)
replace p2411 = . if inlist(p2411, 8, 9)
replace p2412 = . if inlist(p2412, 8, 9)
replace p2413 = . if inlist(p2413, 8, 9)

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
export delimited using "spain_2014_volunteering_profile.csv", replace

**# Bookmark 6: motives

* ============================================================
* motives (P2501 to P2510)
* 1-4 importance of ten motives for volunteering, Mucha to Ninguna
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_volunteering_master.dta", clear

local survey_cols p2501 p2502 p2503 p2504 p2505 p2506 p2507 p2508 p2509 p2510

keep id cov_* `survey_cols'

replace p2501 = . if inlist(p2501, 8, 9)
replace p2502 = . if inlist(p2502, 8, 9)
replace p2503 = . if inlist(p2503, 8, 9)
replace p2504 = . if inlist(p2504, 8, 9)
replace p2505 = . if inlist(p2505, 8, 9)
replace p2506 = . if inlist(p2506, 8, 9)
replace p2507 = . if inlist(p2507, 8, 9)
replace p2508 = . if inlist(p2508, 8, 9)
replace p2509 = . if inlist(p2509, 8, 9)
replace p2510 = . if inlist(p2510, 8, 9)

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
export delimited using "spain_2014_volunteering_motives.csv", replace
