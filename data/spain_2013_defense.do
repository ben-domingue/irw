*** This Stata Do File processes the spain_2013_defense study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2013_defense"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES2998

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    area 18 distr 19-20 seccion 21-23 entrev 24-27 p0 28 p101 29-30 ///
    p102 31-32 p103 33-34 p104 35-36 p105 37-38 p106 39-40 p107 41-42 ///
    p108 43-44 p109 45-46 p110 47-48 p2 49 p3 50 p4 51 ///
    p5 52 p6 53 p7 54 p7a01 55 p7a02 56 p7a03 57 ///
    p7a04 58 p7a05 59 p7a06 60 p7a07 61 p8 62 p901 63-64 ///
    p902 65-66 p903 67-68 p904 69-70 p905 71-72 p906 73-74 p907 75-76 ///
    p908 77-78 p909 79-80 p910 81-82 p911 83-84 p912 85-86 p1001 87 ///
    p1002 88 p1003 89 p1004 90 p1005 91 p1006 92 p1007 93 ///
    p1008 94 p1101 95-96 p1102 97-98 p1103 99-100 p12 101 p13 102 ///
    p14 103 p15 104 p16 105 p17 106 p18 107 p19 108 ///
    p20 109 p21 110 p22 111 p23 112 p24 113 p25 114 ///
    p26 115 p26a01 116-117 p26a02 118-119 p27 120 p28 121 p29 122 ///
    p3001 123 p3002 124 p3003 125 p3004 126 p3005 127 p3006 128 ///
    p31 129 p31a01 130-131 p31a02 132-133 p31a03 134-135 p32 136 p32a01 137-138 ///
    p32a02 139-140 p33 141 p34 142 p3501 143 p3502 144 p3503 145 ///
    p3504 146 p3505 147 p3506 148 p3507 149 p3508 150 p3601 151 ///
    p3602 152 p3603 153 p3604 154 p3605 155 p3606 156 p3607 157 ///
    p37 158 p37a 159 p37b 160 p37c 161-162 p38 163 p39 164 ///
    p40 165 p41 166 p42 167 p43 168 p43a 169-170 p43b 171-172 ///
    p44 173 p45 174 p45a 175-176 p45b 177-178 p46 179 p47 180-181 ///
    p48 182 p48a 183-184 p49 185 p50 186-187 p51 188 p52 189 ///
    p52a01 190 p52a02 191 p52a03 192 p52a04 193 p52a05 194 p52a06 195 ///
    p52a07 196 p52a08 197 p52a09 198 p53 199 p53a 200-201 p54 202 ///
    p54a 203 p55 204 p56 205 p57 206-208 p58 209 p58a 210 ///
    p59 211-213 p60 214-215 p61 216-217 p62 218 p6301 219 p6302 220 ///
    p6303 221 p6304 222 str3 p6401 223-225 str3 p6402 226-228 str3 p6403 229-231 str3 p6404 232-234 ///
    str3 p6405 235-237 str3 p6501 238-240 str3 p6502 241-243 str3 p6503 244-246 str3 p6504 247-249 str3 p6505 250-252 ///
    p66 253 p67 254 p68 255 p69 256 i1 257-259 i2 260-262 ///
    i3 263-265 i4 266-268 i5 269-271 i6 272-274 i7 275-277 i8 278-280 ///
    i9 281-283 e101 284-285 e102 286-287 e103 288-289 e2 290 e3 291-293 ///
    e4 294 c1 295 c1a 296-297 c2 298 c2a 299 c2b 300-301 ///
    c3 302 c4 303-304 recuer 305-306 estudi 307 ocu11 308-309 condicion 310-311 ///
    estatus 312 ///
    using "DA2998.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p49 cov_sex
rename p50 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2013_defense_master.dta", replace

**# Bookmark 1: professions

* ============================================================
* professions (P101 to P110)
* 0-10 valuation of ten professions including career soldier and professional soldier
* two-digit rating scale, 98 N.S. and 99 N.C. recoded; 0 is a valid scale point
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p101 p102 p103 p104 p105 p106 p107 p108 p109 p110

keep id cov_* `survey_cols'

replace p101 = . if inlist(p101, 98, 99)
replace p102 = . if inlist(p102, 98, 99)
replace p103 = . if inlist(p103, 98, 99)
replace p104 = . if inlist(p104, 98, 99)
replace p105 = . if inlist(p105, 98, 99)
replace p106 = . if inlist(p106, 98, 99)
replace p107 = . if inlist(p107, 98, 99)
replace p108 = . if inlist(p108, 98, 99)
replace p109 = . if inlist(p109, 98, 99)
replace p110 = . if inlist(p110, 98, 99)

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
export delimited using "spain_2013_defense_professions.csv", replace

**# Bookmark 2: emotion

* ============================================================
* emotion (P4, P5, P6)
* 1-4 emotion felt on seeing the Spanish flag, hearing the national anthem and watching a military ceremony, very strong to nothing special
* code 5 (No leer) Depende on P4 and P5 is a non-scale volunteered code and is recoded to missing; P6 has no such code
* 8/9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p4 p5 p6

keep id cov_* `survey_cols'

replace p4 = . if inlist(p4, 5, 8, 9)
replace p5 = . if inlist(p5, 5, 8, 9)
replace p6 = . if inlist(p6, 8, 9)

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
export delimited using "spain_2013_defense_emotion.csv", replace

**# Bookmark 3: sacrifice

* ============================================================
* sacrifice (P7A01 to P7A07)
* yes/no whether the respondent would risk their life for seven causes (country, another person, justice, freedom, peace, religion, political ideas)
* asked only to respondents who would risk their life for something (P7 = 1); 0 No procede is a structural code and is recoded to missing
* yes/no selected response; 0, 8 and 9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p7a01 p7a02 p7a03 p7a04 p7a05 p7a06 p7a07

keep id cov_* `survey_cols'

replace p7a01 = . if inlist(p7a01, 0, 8, 9)
replace p7a02 = . if inlist(p7a02, 0, 8, 9)
replace p7a03 = . if inlist(p7a03, 0, 8, 9)
replace p7a04 = . if inlist(p7a04, 0, 8, 9)
replace p7a05 = . if inlist(p7a05, 0, 8, 9)
replace p7a06 = . if inlist(p7a06, 0, 8, 9)
replace p7a07 = . if inlist(p7a07, 0, 8, 9)

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
export delimited using "spain_2013_defense_sacrifice.csv", replace

**# Bookmark 4: threats

* ============================================================
* threats (P901 to P912)
* 0-10 perceived seriousness of twelve security threats to Spain
* two-digit rating scale, 98 N.S. and 99 N.C. recoded; 0 is a valid scale point
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p901 p902 p903 p904 p905 p906 p907 p908 p909 p910 p911 p912

keep id cov_* `survey_cols'

replace p901 = . if inlist(p901, 98, 99)
replace p902 = . if inlist(p902, 98, 99)
replace p903 = . if inlist(p903, 98, 99)
replace p904 = . if inlist(p904, 98, 99)
replace p905 = . if inlist(p905, 98, 99)
replace p906 = . if inlist(p906, 98, 99)
replace p907 = . if inlist(p907, 98, 99)
replace p908 = . if inlist(p908, 98, 99)
replace p909 = . if inlist(p909, 98, 99)
replace p910 = . if inlist(p910, 98, 99)
replace p911 = . if inlist(p911, 98, 99)
replace p912 = . if inlist(p912, 98, 99)

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
export delimited using "spain_2013_defense_threats.csv", replace

**# Bookmark 5: prestige

* ============================================================
* prestige (P13, P14)
* 1-4 degree to which the armed forces contribute to the international prestige of a country in general and of Spain
* two adjacent items on the identical mucho to nada scale and the same construct paired into a two-item table; only 8/9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p13 p14

keep id cov_* `survey_cols'

replace p13 = . if inlist(p13, 8, 9)
replace p14 = . if inlist(p14, 8, 9)

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
export delimited using "spain_2013_defense_prestige.csv", replace

**# Bookmark 6: capability

* ============================================================
* capability (P18, P20)
* 1-4 how prepared the Spanish armed forces are to defend Spain and how capable Spanish soldiers are of doing their job
* two items on the identical muy / bastante / poco / nada scale and the same construct paired into a two-item table; P19 between them is a comparison item with a NO LEER midpoint and is dropped
* only 8/9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p18 p20

keep id cov_* `survey_cols'

replace p18 = . if inlist(p18, 8, 9)
replace p20 = . if inlist(p20, 8, 9)

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
export delimited using "spain_2013_defense_capability.csv", replace

**# Bookmark 7: resources

* ============================================================
* resources (P21, P22, P23)
* 1-3 whether the number of troops, the technical means and the defence budget are excessive, adequate or insufficient
* three read ordered categories, adecuado is a read midpoint and is kept; only 8/9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p21 p22 p23

keep id cov_* `survey_cols'

replace p21 = . if inlist(p21, 8, 9)
replace p22 = . if inlist(p22, 8, 9)
replace p23 = . if inlist(p23, 8, 9)

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
export delimited using "spain_2013_defense_resources.csv", replace

**# Bookmark 8: missions

* ============================================================
* missions (P3001 to P3006)
* 1-4 degree to which participation in peace missions brings six benefits to Spain, mucho to nada
* four read categories, no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p3001 p3002 p3003 p3004 p3005 p3006

keep id cov_* `survey_cols'

replace p3001 = . if inlist(p3001, 8, 9)
replace p3002 = . if inlist(p3002, 8, 9)
replace p3003 = . if inlist(p3003, 8, 9)
replace p3004 = . if inlist(p3004, 8, 9)
replace p3005 = . if inlist(p3005, 8, 9)
replace p3006 = . if inlist(p3006, 8, 9)

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
export delimited using "spain_2013_defense_missions.csv", replace

**# Bookmark 9: conditions

* ============================================================
* conditions (P3501 to P3508)
* 1-5 importance of eight employment conditions when considering becoming a professional soldier, 1 muy importante to 5 nada importante
* asked only to respondents in the age range for enlistment; 0 No procede is a structural code and is recoded to missing
* five-point numeric scale with labelled endpoints only, no NO LEER code; 0, 8 and 9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p3501 p3502 p3503 p3504 p3505 p3506 p3507 p3508

keep id cov_* `survey_cols'

replace p3501 = . if inlist(p3501, 0, 8, 9)
replace p3502 = . if inlist(p3502, 0, 8, 9)
replace p3503 = . if inlist(p3503, 0, 8, 9)
replace p3504 = . if inlist(p3504, 0, 8, 9)
replace p3505 = . if inlist(p3505, 0, 8, 9)
replace p3506 = . if inlist(p3506, 0, 8, 9)
replace p3507 = . if inlist(p3507, 0, 8, 9)
replace p3508 = . if inlist(p3508, 0, 8, 9)

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
export delimited using "spain_2013_defense_conditions.csv", replace

**# Bookmark 10: attractions

* ============================================================
* attractions (P3601 to P3607)
* 1-5 importance of seven attractions of military life when considering becoming a professional soldier, 1 muy importante to 5 nada importante
* same filter as P35; 0 No procede is a structural code and is recoded to missing
* five-point numeric scale with labelled endpoints only, no NO LEER code; 0, 8 and 9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p3601 p3602 p3603 p3604 p3605 p3606 p3607

keep id cov_* `survey_cols'

replace p3601 = . if inlist(p3601, 0, 8, 9)
replace p3602 = . if inlist(p3602, 0, 8, 9)
replace p3603 = . if inlist(p3603, 0, 8, 9)
replace p3604 = . if inlist(p3604, 0, 8, 9)
replace p3605 = . if inlist(p3605, 0, 8, 9)
replace p3606 = . if inlist(p3606, 0, 8, 9)
replace p3607 = . if inlist(p3607, 0, 8, 9)

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
export delimited using "spain_2013_defense_attractions.csv", replace

**# Bookmark 11: children

* ============================================================
* children (P43, P44, P45, P46)
* 1-2 whether the respondent would encourage or discourage a daughter or a son who wanted to become a professional soldier or a career officer
* asked only to respondents outside the enlistment age range; 0 No procede is a structural code and is recoded to missing
* code 3 (No leer) Ni lo uno ni lo otro is a NO LEER non-scale code and is recoded to missing; 8/9 recoded
* ============================================================

use "spain_2013_defense_master.dta", clear

local survey_cols p43 p44 p45 p46

keep id cov_* `survey_cols'

replace p43 = . if inlist(p43, 0, 3, 8, 9)
replace p44 = . if inlist(p44, 0, 3, 8, 9)
replace p45 = . if inlist(p45, 0, 3, 8, 9)
replace p46 = . if inlist(p46, 0, 3, 8, 9)

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
export delimited using "spain_2013_defense_children.csv", replace
