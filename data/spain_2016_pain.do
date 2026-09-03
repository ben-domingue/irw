*** This Stata Do File processes the spain_2016_pain study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2016_pain"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES3137

infix ///
    str5 estudio 1-5 cues 6-9 registro 10-18 str10 fechaini 19-28 str8 horaini 29-36 str10 fechafin 37-46 ///
    str8 horafin 47-54 duracion 55-59 ccaa 60-61 prov 62-63 mun 64-66 tamuni 67 ///
    distr 68-70 seccion 71-73 capital 74 coordinador 75-78 entrev 79-83 p0 84 ///
    p0a 85-87 p1_1 88-89 p1_2 90-91 p1_3 92-93 p1_4 94-95 p1_5 96-97 ///
    p1_6 98-99 p2 100-101 p3 102 p4 103 p5 104 p6a 105-106 ///
    p6b 107-108 p7_1 109 p7_2 110 p7_3 111 p7_4 112 p7_5 113 ///
    p7_6 114 p7_7 115 p7_8 116 p7_9 117 p7_10 118 p7_11 119 ///
    p7_12 120 p7_13 121 p7_14 122 p7_15 123 p7_96 124 p7_97 125 ///
    p7_98 126 p7_99 127 p8 128 p9_1 129 p9_2 130 p9_3 131 ///
    p9_4 132 p9_5 133 p9_6 134 p9_7 135 p9_8 136 p9_9 137 ///
    p9_10 138 p9_11 139 p9_12 140 p9_13 141 p9_14 142 p9_15 143 ///
    p9_96 144 p9_97 145 p9_98 146 p9_99 147 p10 148-149 p10a 150 ///
    p11 151-152 p12a 153-154 p12b 155-156 p12c 157-158 p13a 159-160 p13b 161-162 ///
    p14 163-164 p15 165 p16 166 p17 167 p18 168 p18a 169 ///
    p19_1 170 p19_2 171 p19_3 172 p19_4 173 p19_5 174 p19_6 175 ///
    p19_7 176 p19_8 177 p19_9 178 p19_10 179 p19_11 180 p19_12 181 ///
    p19_13 182 p19_14 183 p19_15 184 p19_16 185 p19_96 186 p19_97 187 ///
    p19_98 188 p19_99 189 p19a 190 p20_1 191 p20_2 192 p20_3 193 ///
    p21_1 194 p21_2 195 p21_3 196 p22_1 197 p22_2 198 p22_3 199 ///
    p22_4 200 p22_5 201 p22_6 202 p22_7 203 p22_8 204 p22_9 205 ///
    p22_10 206 p22_11 207 p22_12 208 p22_13 209 p22_96 210 p22_97 211 ///
    p22_98 212 p22_99 213 p23 214-215 p24_1 216 p24_2 217 p24_3 218 ///
    p24_4 219 p24_5 220 p24_6 221 p24_7 222 p24_8 223 p25_1 224 ///
    p25_2 225 p25_3 226 p25_4 227 p25_5 228 p25_6 229 p25_7 230 ///
    p25_8 231 p26_1 232 p26_2 233 p26_3 234 p26_4 235 p27_1 236 ///
    p27_2 237 p27_3 238 p27_4 239 p27_5 240 p27_6 241 p27_7 242 ///
    p27_8 243 p27_9 244 p27_10 245 p28a 246-247 p28b 248-249 p29 250 ///
    p30 251-253 p31 254 p32 255-257 p33 258-259 p34 260 p35 261 ///
    p36 262 p37 263-264 p38 265-266 p38a 267-268 p39 269 p40 270-271 ///
    p41 272 p42 273 p43 274 p43a 275-276 p44 277 p44a 278 ///
    p45 279 p46 280 p47 281 p48 282-284 p49 285 p49a 286 ///
    p50 287-289 p51 290-291 p52 292-293 p53 294 p54 295 p55_1 296 ///
    p55_2 297 p55_3 298 p55_4 299 p56 300 p57 301 p58 302 ///
    p59 303 p60 304 p12 305-309 p28 310-313 p38ar 314-315 estudios 316-317 ///
    ocumar11 318-319 rama09 320 condicion11 321-322 estatus 323 ///
    using "DA3137.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p39 cov_sex
rename p40 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2016_pain_master.dta", replace

**# Bookmark 1: wellbeing

* ============================================================
* wellbeing (P1_1 to P1_6, P2)
* 0-10 satisfaction with life domains plus 0-10 happiness, 97 is N.P. on P1 items, 98 N.S., 99 N.C.
* no midpoint NO LEER code on this scale, nothing recoded except sentinels
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p1_1 p1_2 p1_3 p1_4 p1_5 p1_6 p2

keep id cov_* `survey_cols'

replace p1_1 = . if inlist(p1_1, 97, 98, 99)
replace p1_2 = . if inlist(p1_2, 97, 98, 99)
replace p1_3 = . if inlist(p1_3, 97, 98, 99)
replace p1_4 = . if inlist(p1_4, 97, 98, 99)
replace p1_5 = . if inlist(p1_5, 97, 98, 99)
replace p1_6 = . if inlist(p1_6, 97, 98, 99)
replace p2 = . if inlist(p2, 98, 99)

* QC: tabulate every item after recodes

tab p1_1, missing
tab p1_2, missing
tab p1_3, missing
tab p1_4, missing
tab p1_5, missing
tab p1_6, missing
tab p2, missing

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
export delimited using "spain_2016_pain_wellbeing.csv", replace

**# Bookmark 2: health

* ============================================================
* health (P3, P4, P5)
* 1-5 self-rated health and health compared with peers and with a year ago
* code 3 (Normal / Igual) is a read option, kept
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p3 p4 p5

keep id cov_* `survey_cols'

replace p3 = . if inlist(p3, 8, 9)
replace p4 = . if inlist(p4, 8, 9)
replace p5 = . if inlist(p5, 8, 9)

* QC: tabulate every item after recodes

tab p3, missing
tab p4, missing
tab p5, missing

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
export delimited using "spain_2016_pain_health.csv", replace

**# Bookmark 3: fitness

* ============================================================
* fitness (P29, P34)
* 1-5 degree of rest after sleep and self-rated physical fitness
* code 3 (Descansado/a, Normal) is a read option, kept
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p29 p34

keep id cov_* `survey_cols'

replace p29 = . if inlist(p29, 8, 9)
replace p34 = . if inlist(p34, 8, 9)

* QC: tabulate every item after recodes

tab p29, missing
tab p34, missing

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
export delimited using "spain_2016_pain_fitness.csv", replace

**# Bookmark 4: frequency

* ============================================================
* frequency (P8, P15)
* 1-4 frequency of pain in general and of the most relevant pain
* 0 is N.P. (not asked, no pain reported), recoded to missing; no NO LEER code
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p8 p15

keep id cov_* `survey_cols'

replace p8 = . if inlist(p8, 0, 8, 9)
replace p15 = . if inlist(p15, 0, 8, 9)

* QC: tabulate every item after recodes

tab p8, missing
tab p15, missing

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
export delimited using "spain_2016_pain_frequency.csv", replace

**# Bookmark 5: difficulty

* ============================================================
* difficulty (P16, P17)
* 1-5 difficulty the most relevant pain causes in daily and social activity
* code 3 (Algo) is a (NO LEER) volunteered midpoint, recoded to missing; 0 is N.P., recoded to missing
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p16 p17

keep id cov_* `survey_cols'

replace p16 = . if inlist(p16, 0, 3, 8, 9)
replace p17 = . if inlist(p17, 0, 3, 8, 9)

* QC: tabulate every item after recodes

tab p16, missing
tab p17, missing

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
export delimited using "spain_2016_pain_difficulty.csv", replace

**# Bookmark 6: effectiveness

* ============================================================
* effectiveness (P18A, P19A)
* 1-5 effectiveness of medication and of alternative treatments for the most relevant pain
* code 6 (NO LEER, some effective and others not) is off-scale, recoded to missing; 0 is N.P., recoded to missing
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p18a p19a

keep id cov_* `survey_cols'

replace p18a = . if inlist(p18a, 0, 6, 8, 9)
replace p19a = . if inlist(p19a, 0, 6, 8, 9)

* QC: tabulate every item after recodes

tab p18a, missing
tab p19a, missing

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
export delimited using "spain_2016_pain_effectiveness.csv", replace

**# Bookmark 7: support

* ============================================================
* support (P20_1 to P20_3)
* 1-4 degree to which others understood, attended to and tried to help
* 0 is N.P. and 7 is N.P. (told nobody), both recoded to missing; no NO LEER code
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p20_1 p20_2 p20_3

keep id cov_* `survey_cols'

replace p20_1 = . if inlist(p20_1, 0, 7, 8, 9)
replace p20_2 = . if inlist(p20_2, 0, 7, 8, 9)
replace p20_3 = . if inlist(p20_3, 0, 7, 8, 9)

* QC: tabulate every item after recodes

tab p20_1, missing
tab p20_2, missing
tab p20_3, missing

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
export delimited using "spain_2016_pain_support.csv", replace

**# Bookmark 8: coping

* ============================================================
* coping (P21_1 to P21_3)
* 1-4 degree of coping behaviours when in pain
* 0 is N.P. and 7 is N.P. (does not seek others), both recoded to missing; no NO LEER code
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p21_1 p21_2 p21_3

keep id cov_* `survey_cols'

replace p21_1 = . if inlist(p21_1, 0, 7, 8, 9)
replace p21_2 = . if inlist(p21_2, 0, 7, 8, 9)
replace p21_3 = . if inlist(p21_3, 0, 7, 8, 9)

* QC: tabulate every item after recodes

tab p21_1, missing
tab p21_2, missing
tab p21_3, missing

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
export delimited using "spain_2016_pain_coping.csv", replace

**# Bookmark 9: beliefs

* ============================================================
* beliefs (P25_1 to P25_8)
* 1-4 agreement with statements about pain
* four-point scale with no midpoint, nothing recoded except sentinels
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p25_1 p25_2 p25_3 p25_4 p25_5 p25_6 p25_7 p25_8

keep id cov_* `survey_cols'

replace p25_1 = . if inlist(p25_1, 8, 9)
replace p25_2 = . if inlist(p25_2, 8, 9)
replace p25_3 = . if inlist(p25_3, 8, 9)
replace p25_4 = . if inlist(p25_4, 8, 9)
replace p25_5 = . if inlist(p25_5, 8, 9)
replace p25_6 = . if inlist(p25_6, 8, 9)
replace p25_7 = . if inlist(p25_7, 8, 9)
replace p25_8 = . if inlist(p25_8, 8, 9)

* QC: tabulate every item after recodes

tab p25_1, missing
tab p25_2, missing
tab p25_3, missing
tab p25_4, missing
tab p25_5, missing
tab p25_6, missing
tab p25_7, missing
tab p25_8, missing

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
export delimited using "spain_2016_pain_beliefs.csv", replace

**# Bookmark 10: social

* ============================================================
* social (P26_1 to P26_4)
* 1-2 social support received (as much as desired / less than desired)
* dichotomous ordered scale, nothing recoded except sentinels
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p26_1 p26_2 p26_3 p26_4

keep id cov_* `survey_cols'

replace p26_1 = . if inlist(p26_1, 8, 9)
replace p26_2 = . if inlist(p26_2, 8, 9)
replace p26_3 = . if inlist(p26_3, 8, 9)
replace p26_4 = . if inlist(p26_4, 8, 9)

* QC: tabulate every item after recodes

tab p26_1, missing
tab p26_2, missing
tab p26_3, missing
tab p26_4, missing

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
export delimited using "spain_2016_pain_social.csv", replace

**# Bookmark 11: personality

* ============================================================
* personality (P27_1 to P27_10)
* 1-5 self-description on personality traits
* code 3 (Ni si, ni no) is a (NO LEER) volunteered midpoint, recoded to missing
* ============================================================

use "spain_2016_pain_master.dta", clear

local survey_cols p27_1 p27_2 p27_3 p27_4 p27_5 p27_6 p27_7 p27_8 p27_9 p27_10

keep id cov_* `survey_cols'

replace p27_1 = . if inlist(p27_1, 3, 8, 9)
replace p27_2 = . if inlist(p27_2, 3, 8, 9)
replace p27_3 = . if inlist(p27_3, 3, 8, 9)
replace p27_4 = . if inlist(p27_4, 3, 8, 9)
replace p27_5 = . if inlist(p27_5, 3, 8, 9)
replace p27_6 = . if inlist(p27_6, 3, 8, 9)
replace p27_7 = . if inlist(p27_7, 3, 8, 9)
replace p27_8 = . if inlist(p27_8, 3, 8, 9)
replace p27_9 = . if inlist(p27_9, 3, 8, 9)
replace p27_10 = . if inlist(p27_10, 3, 8, 9)

* QC: tabulate every item after recodes

tab p27_1, missing
tab p27_2, missing
tab p27_3, missing
tab p27_4, missing
tab p27_5, missing
tab p27_6, missing
tab p27_7, missing
tab p27_8, missing
tab p27_9, missing
tab p27_10, missing

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
export delimited using "spain_2016_pain_personality.csv", replace
