*** This Stata Do File processes the spain_2014_citizenship study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2014_citizenship"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES3020

infix ///
    estu 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    distr 18-19 seccion 20-22 entrev 23-26 id 27-30 p101 31 p102 32 ///
    p103 33 p104 34 p105 35 p106 36 p107 37 p108 38 ///
    p109 39 p2 40 p3 41 p4 42 p501 43 p502 44 ///
    p503 45 p504 46 p505 47 p506 48 p507 49 p508 50 ///
    p6 51 p7 52 p801 53 p802 54 p803 55 p804 56 ///
    p805 57 p901 58 p902 59 p903 60 p904 61 p905 62 ///
    p906 63 p907 64 p908 65 p909 66 p1001 67 p1002 68 ///
    p1003 69 p1004 70 p11 71 p12 72 p13 73 p14 74-75 ///
    p1501 76 p1502 77 p16 78 p17 79 p18 80 p19 81 ///
    p2001 82 p2002 83 p2003 84 p21 85 p22 86 p23 87 ///
    p24 88 p25 89-90 p26 91-92 p27 93-94 p2801 95 p2802 96 ///
    p2803 97 p2804 98 p29 99 p29a01 100 p29a02 101 p29a03 102 ///
    p29a04 103 p29a05 104 p29a06 105 p29a07 106 p29a08 107 p29a09 108 ///
    p29b 109 p29c01 110 p29c02 111 p29c03 112 p29c04 113 p29c05 114 ///
    p29c06 115 p29c07 116 p29c08 117 p29d01 118 p29d02 119 p29d03 120 ///
    p29d04 121 p29d05 122 p29d06 123 p29d07 124 p29d08 125 p29d09 126 ///
    p29d10 127 p29d11 128 p29d12 129 p29d13 130 p29e01 131 p29e02 132 ///
    p29e03 133 p29e04 134 p29e05 135 p29e06 136 p30 137 p31 138-141 ///
    p32 142 p32a 143-144 p32b 145-146 p33 147-148 p34a01 149 p34b01 150-151 ///
    p34c01 152 p34a02 153 p34b02 154-155 p34c02 156 p34a03 157 p34b03 158-159 ///
    p34c03 160 p34a04 161 p34b04 162-163 p34c04 164 p34a05 165 p34b05 166-167 ///
    p34c05 168 p34a06 169 p34b06 170-171 p34c06 172 p34a07 173 p34b07 174-175 ///
    p34c07 176 p34a08 177 p34b08 178-179 p34c08 180 p34a09 181 p34b09 182-183 ///
    p34c09 184 p34a10 185 p34b10 186-187 p34c10 188 p35 189 p35a 190 ///
    p36 191 p3701 192-194 p3702 195-198 p38 199 p38a 200-202 p38b 203 ///
    p38c 204 p39 205-207 p40 208 p40a 209-210 p41 211-213 p42 214 ///
    p43 215 p44 216 p4501 217-219 p4502 220-223 p46 224 p47 225-227 ///
    p48 228 p49 229-230 p50 231 p51 232 p52 233 p53 234 ///
    p53a01 235 p53a02 236 p54 237 p55 238 p56 239-240 p57 241 ///
    p58 242 p58a 243-244 p59 245 p59a 246-247 p59b 248 p60 249-250 ///
    p61 251-252 p6201 253-254 p6202 255-256 p63 257-259 p64 260-262 p65 263-265 ///
    p65a 266-267 p66 268 p66a 269-271 p67 272 p68 273 p69 274 ///
    p7001 275-276 p7002 277-278 p71 279 p71a01 280-281 p71a02 282-283 p72 284-285 ///
    p73 286 p7401 287 p7402 288 p75 289 p76 290 p77 291 ///
    p78 292 p79 293 e101 294-295 e102 296-297 e103 298-299 e2 300 ///
    e3 301-303 e4 304 c1 305 c1a 306-307 c2 308 c2a 309 ///
    c2b 310-311 c3 312 c4 313-314 edad 315-316 estudios 317 ocumar11 318-319 ///
    rama09 320 ocupar 321-322 ramapar 323 condicion11 324-325 estatus 326 recuerdo 327-328 ///
    str6 peso1 329-334 str6 peso2 335-340 ///
    using "DA3020.", clear

destring _all, replace force

* the raw file carries its own ID field; rename it so the pipeline id can be created

rename id idcis

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p30 cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2014_citizenship_master.dta", replace

**# Bookmark 1: citizenship

* ============================================================
* citizenship (P101 to P109)
* 1-7 importance of behaviours for being a good citizen, Nada importante to Muy importante
* seven-point numeric scale, no NO LEER code, 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

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
export delimited using "spain_2014_citizenship_citizenship.csv", replace

**# Bookmark 2: tolerance

* ============================================================
* tolerance (P2, P3, P4)
* 1-4 willingness to allow public meetings of religious extremists, people wanting to overthrow the government and racists, Si por supuesto to No de ninguna manera
* four-point scale with no midpoint and no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p2 p3 p4

keep id cov_* `survey_cols'

replace p2 = . if inlist(p2, 8, 9)
replace p3 = . if inlist(p3, 8, 9)
replace p4 = . if inlist(p4, 8, 9)

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
export delimited using "spain_2014_citizenship_tolerance.csv", replace

**# Bookmark 3: participation

* ============================================================
* participation (P501 to P508)
* 1-4 political participation, Ha participado en el ultimo ano / Participo en un pasado mas lejano / No participo pero podria / Ni participo ni lo haria nunca
* ordered involvement scale, no NO LEER code, 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p501 p502 p503 p504 p505 p506 p507 p508

keep id cov_* `survey_cols'

replace p501 = . if inlist(p501, 8, 9)
replace p502 = . if inlist(p502, 8, 9)
replace p503 = . if inlist(p503, 8, 9)
replace p504 = . if inlist(p504, 8, 9)
replace p505 = . if inlist(p505, 8, 9)
replace p506 = . if inlist(p506, 8, 9)
replace p507 = . if inlist(p507, 8, 9)
replace p508 = . if inlist(p508, 8, 9)

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
export delimited using "spain_2014_citizenship_participation.csv", replace

**# Bookmark 4: media

* ============================================================
* media (P6, P2801 to P2804)
* 1-7 frequency of following politics through the media in general (P6) and through newspaper, television, radio and Internet (P2801 to P2804), Varias veces al dia to Nunca
* seven-point frequency scale, no NO LEER code, 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p6 p2801 p2802 p2803 p2804

keep id cov_* `survey_cols'

replace p6 = . if inlist(p6, 8, 9)
replace p2801 = . if inlist(p2801, 8, 9)
replace p2802 = . if inlist(p2802, 8, 9)
replace p2803 = . if inlist(p2803, 8, 9)
replace p2804 = . if inlist(p2804, 8, 9)

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
export delimited using "spain_2014_citizenship_media.csv", replace

**# Bookmark 5: membership

* ============================================================
* membership (P801 to P805)
* 1-4 membership in organisations, Pertenece y participa / Pertenece sin participar / Antes pertenecia / Nunca ha pertenecido
* ordered involvement scale, no NO LEER code, 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p801 p802 p803 p804 p805

keep id cov_* `survey_cols'

replace p801 = . if inlist(p801, 8, 9)
replace p802 = . if inlist(p802, 8, 9)
replace p803 = . if inlist(p803, 8, 9)
replace p804 = . if inlist(p804, 8, 9)
replace p805 = . if inlist(p805, 8, 9)

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
export delimited using "spain_2014_citizenship_membership.csv", replace

**# Bookmark 6: rights

* ============================================================
* rights (P901 to P909)
* 1-7 importance of rights and conditions in a democracy, Nada importante to Muy importante
* seven-point numeric scale, no NO LEER code, 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

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
export delimited using "spain_2014_citizenship_rights.csv", replace

**# Bookmark 7: efficacy

* ============================================================
* efficacy (P1001 to P1004)
* 1-5 agreement with political efficacy statements, Muy de acuerdo to Muy en desacuerdo
* code 3 (Ni de acuerdo ni en desacuerdo) is a read option in this study, kept; 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p1001 p1002 p1003 p1004

keep id cov_* `survey_cols'

replace p1001 = . if inlist(p1001, 8, 9)
replace p1002 = . if inlist(p1002, 8, 9)
replace p1003 = . if inlist(p1003, 8, 9)
replace p1004 = . if inlist(p1004, 8, 9)

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
export delimited using "spain_2014_citizenship_efficacy.csv", replace

**# Bookmark 8: trust

* ============================================================
* trust (P1501, P1502)
* 1-5 agreement with statements on trust in politicians, Muy de acuerdo to Muy en desacuerdo
* code 3 (Ni de acuerdo ni en desacuerdo) is a read option in this study, kept; 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p1501 p1502

keep id cov_* `survey_cols'

replace p1501 = . if inlist(p1501, 8, 9)
replace p1502 = . if inlist(p1502, 8, 9)

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
export delimited using "spain_2014_citizenship_trust.csv", replace

**# Bookmark 9: discussion

* ============================================================
* discussion (P18, P19)
* 1-4 frequency of discussing politics and of trying to persuade others, Frecuentemente to Nunca
* four-point frequency scale, no NO LEER code, 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p18 p19

keep id cov_* `survey_cols'

replace p18 = . if inlist(p18, 8, 9)
replace p19 = . if inlist(p19, 8, 9)

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
export delimited using "spain_2014_citizenship_discussion.csv", replace

**# Bookmark 10: parties

* ============================================================
* parties (P2001 to P2003)
* 1-5 agreement with statements on parties and referendums, Muy de acuerdo to Muy en desacuerdo
* code 3 (Ni de acuerdo ni en desacuerdo) is a read option in this study, kept; 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p2001 p2002 p2003

keep id cov_* `survey_cols'

replace p2001 = . if inlist(p2001, 8, 9)
replace p2002 = . if inlist(p2002, 8, 9)
replace p2003 = . if inlist(p2003, 8, 9)

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
export delimited using "spain_2014_citizenship_parties.csv", replace

**# Bookmark 11: integrity

* ============================================================
* integrity (P21, P22, P24)
* 1-5 evaluations of public integrity: cleanliness of the last election, equal opportunities of candidates, corruption in the public administration
* code 3 is a read midpoint on P21 and P22 (Ni limpieza ni fraude; Ni igualdad ni desigualdad) and a read category on P24 (Un numero moderado), kept; 8/9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p21 p22 p24

keep id cov_* `survey_cols'

replace p21 = . if inlist(p21, 8, 9)
replace p22 = . if inlist(p22, 8, 9)
replace p24 = . if inlist(p24, 8, 9)

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
export delimited using "spain_2014_citizenship_integrity.csv", replace

**# Bookmark 12: democracy

* ============================================================
* democracy (P25, P26, P27)
* 0-10 rating of how democracy works today, ten years ago and in ten years, Muy mal to Muy bien
* no NO LEER code, 98/99 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p25 p26 p27

keep id cov_* `survey_cols'

replace p25 = . if inlist(p25, 98, 99)
replace p26 = . if inlist(p26, 98, 99)
replace p27 = . if inlist(p27, 98, 99)

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
export delimited using "spain_2014_citizenship_democracy.csv", replace

**# Bookmark 13: online

* ============================================================
* online (P29E01 to P29E06)
* yes/no online political activities in the last year (contacting a politician, an association, subscribing to a list, commenting, donating, signing a petition)
* 0 is N.P. (no Internet use in the last 12 months), recoded to missing; 9 recoded
* ============================================================

use "spain_2014_citizenship_master.dta", clear

local survey_cols p29e01 p29e02 p29e03 p29e04 p29e05 p29e06

keep id cov_* `survey_cols'

replace p29e01 = . if inlist(p29e01, 0, 9)
replace p29e02 = . if inlist(p29e02, 0, 9)
replace p29e03 = . if inlist(p29e03, 0, 9)
replace p29e04 = . if inlist(p29e04, 0, 9)
replace p29e05 = . if inlist(p29e05, 0, 9)
replace p29e06 = . if inlist(p29e06, 0, 9)

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
export delimited using "spain_2014_citizenship_online.csv", replace