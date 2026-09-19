*** This Stata Do File processes the spain_2012_reality study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2012_reality"

* fixed-width ASCII import, column positions taken from the SPSS syntax file ES2973

infix ///
    estudio 1-4 cues 5-9 ccaa 10-11 prov 12-13 mun 14-16 tamuni 17 ///
    area 18 distr 19-20 seccion 21-23 entrev 24-27 tipo 28 p0 29 ///
    p1 30 p1a01 31 p1a02 32 p1a03 33 p1a04 34 p1a05 35 ///
    p1a06 36 p1a07 37 p2 38 p3 39 p3a01 40 p3a02 41 ///
    p3a03 42 p3a04 43 p3a05 44 p3a06 45 p4 46 p5 47 ///
    p5a01 48 p5a02 49 p5a03 50 p5a04 51 p5a05 52 p5a06 53 ///
    p5a07 54 p601 55 p602 56 p603 57 p604 58 p605 59 ///
    p606 60 p607 61 p608 62 p609 63 p610 64 p611 65 ///
    p612 66 p613 67 p614 68-69 p7 70 p7a01 71-72 p7a02 73-76 ///
    p7b01 77 p7b02 78 p801 79 p802 80 p803 81 p804 82 ///
    p9 83 p9b 84 p10 85 p11 86 p12a 87-90 p12b 91 ///
    p13 92 p14 93 p15a 94 p15b 95 p16 96 p1701 97 ///
    p1702 98 p1703 99 p1801 100 p1802 101 p1803 102 p1804 103 ///
    p19 104 p20_01 105-106 p20_02 107-108 p21 109 p21b 110 p22 111 ///
    p23 112 p24a 113-114 p24b 115 p2501 116 p2502 117 p2503 118 ///
    p2504 119 p26 120 p26b 121 p27 122 p28 123-124 p2901 125 ///
    p2902 126 p2903 127 p2904 128 p2905 129 p30 130 p31 131 ///
    p32 132 p33 133 p34 134 p35 135 p3601 136 p3602 137 ///
    p3603 138 p3604 139 p3605 140 p3701 141 p3702 142 p3703 143 ///
    p3704 144 p3705 145 p3706 146 p3707 147 p3708 148 p3709 149 ///
    p3710 150 p38 151-152 p39 153-154 p40 155-156 p41 157 p41a 158-159 ///
    p42 160 p4301 161-162 p4302 163-166 p44 167 p45 168 p46 169 ///
    p46a 170-171 p46b 172-173 p47 174-175 p47a 176-177 p47b 178-179 p47c 180-181 ///
    p48 182-183 p49 184-185 p5001 186-187 p5002 188-189 p50a 190-191 p5101 192-193 ///
    p5102 194-195 p51a 196-197 p52 198 p52a 199 p53 200 p53a 201 ///
    p54 202 p5501 203-205 p5502 206-208 p56 209 p56a 210 p5701 211-212 ///
    p5702 213-215 p58 216 p59 217-218 sexo01 219 edad01 220-221 col01 222 ///
    sexo02 223 edad02 224-225 col02 226 sexo03 227 edad03 228-229 col03 230 ///
    sexo04 231 edad04 232-233 col04 234 sexo05 235 edad05 236-237 col05 238 ///
    sexo06 239 edad06 240-241 col06 242 sexo07 243 edad07 244-245 col07 246 ///
    sexo08 247 edad08 248-249 col08 250 sexo09 251 edad09 252-253 col09 254 ///
    sexo10 255 edad10 256-257 col10 258 p61 259 p62 260 p63 261-262 ///
    p64 263 p65 264 p66 265 p67 266 p6801 267 p6802 268 ///
    p6803 269 str3 p6901 270-272 str3 p6902 273-275 str3 p6903 276-278 str3 p6904 279-281 str3 p6905 282-284 ///
    str3 p7001 285-287 str3 p7002 288-290 str3 p7003 291-293 str3 p7004 294-296 str3 p7005 297-299 p71 300 ///
    p71a01 301 p71a02 302 p71a03 303 p71b 304 p72 305 p73 306 ///
    p74 307 i1 308-310 i2 311-313 i3 314-316 i4 317-319 i5 320-322 ///
    i6 323-325 i7 326-328 i8 329-331 i9 332-334 e101 335-336 e102 337-338 ///
    e103 339-340 e2 341 e3 342-344 e4 345 c1 346 c1a 347-348 ///
    c2 349 c2a 350 c2b 351-352 c3 353 c4 354-355 rela01 356-357 ///
    rela02 358-359 rela03 360-361 rela04 362-363 rela05 364-365 rela06 366-367 rela07 368-369 ///
    rela08 370-371 rela09 372-373 rela10 374-375 peso 376-381 recuerdo 382-383 edad 384-385 ///
    estudios 386 ocumar11 387-388 rama09 389 condicion11 390-391 estatus 392 ///
    using "DA2973.", clear

destring _all, replace force

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename p42 cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2012_reality_master.dta", replace

**# Bookmark 1: media

* ============================================================
* media (P1 to P5)
* 1-5 frequency of watching TV news, TV political programmes, listening to radio, radio political programmes and reading newspapers, every day to never
* five read frequency categories, no NO LEER code, only 8/9 recoded
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p1 p2 p3 p4 p5

keep id cov_* `survey_cols'

replace p1 = . if inlist(p1, 8, 9)
replace p2 = . if inlist(p2, 8, 9)
replace p3 = . if inlist(p3, 8, 9)
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
export delimited using "spain_2012_reality_media.csv", replace

**# Bookmark 2: television

* ============================================================
* television (P1A01 to P1A07)
* 0-7 days per week watching each of seven TV news programmes, 0 ninguno to 7 todos
* asked only to respondents who watch TV news (P1 codes 1 to 4); blanks are structural and stay missing
* only 8/9 recoded; 0 is a valid scale point
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p1a01 p1a02 p1a03 p1a04 p1a05 p1a06 p1a07

keep id cov_* `survey_cols'

replace p1a01 = . if inlist(p1a01, 8, 9)
replace p1a02 = . if inlist(p1a02, 8, 9)
replace p1a03 = . if inlist(p1a03, 8, 9)
replace p1a04 = . if inlist(p1a04, 8, 9)
replace p1a05 = . if inlist(p1a05, 8, 9)
replace p1a06 = . if inlist(p1a06, 8, 9)
replace p1a07 = . if inlist(p1a07, 8, 9)

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
export delimited using "spain_2012_reality_television.csv", replace

**# Bookmark 3: radio

* ============================================================
* radio (P3A01 to P3A06)
* 0-7 days per week listening to each of six radio stations, 0 ninguno to 7 todos
* asked only to respondents who listen to the radio (P3 codes 1 to 4); blanks are structural and stay missing
* only 8/9 recoded; 0 is a valid scale point
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p3a01 p3a02 p3a03 p3a04 p3a05 p3a06

keep id cov_* `survey_cols'

replace p3a01 = . if inlist(p3a01, 8, 9)
replace p3a02 = . if inlist(p3a02, 8, 9)
replace p3a03 = . if inlist(p3a03, 8, 9)
replace p3a04 = . if inlist(p3a04, 8, 9)
replace p3a05 = . if inlist(p3a05, 8, 9)
replace p3a06 = . if inlist(p3a06, 8, 9)

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
export delimited using "spain_2012_reality_radio.csv", replace

**# Bookmark 4: press

* ============================================================
* press (P5A01 to P5A07)
* 0-7 days per week reading each of seven newspaper types, 0 ninguno to 7 todos
* asked only to respondents who read newspapers (P5 codes 1 to 4); blanks are structural and stay missing
* only 8/9 recoded; 0 is a valid scale point
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p5a01 p5a02 p5a03 p5a04 p5a05 p5a06 p5a07

keep id cov_* `survey_cols'

replace p5a01 = . if inlist(p5a01, 8, 9)
replace p5a02 = . if inlist(p5a02, 8, 9)
replace p5a03 = . if inlist(p5a03, 8, 9)
replace p5a04 = . if inlist(p5a04, 8, 9)
replace p5a05 = . if inlist(p5a05, 8, 9)
replace p5a06 = . if inlist(p5a06, 8, 9)
replace p5a07 = . if inlist(p5a07, 8, 9)

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
export delimited using "spain_2012_reality_press.csv", replace

**# Bookmark 5: outlets

* ============================================================
* outlets (P601 to P613)
* 1-5 ideological placement of thirteen TV channels, radio stations and newspapers, muy de izquierdas to muy de derechas
* code 3 (Ni de izquierdas ni de derechas) is a read scale point, not marked NO LEER, and is kept; only 8/9 recoded
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p601 p602 p603 p604 p605 p606 p607 p608 p609 p610 p611 p612 p613

keep id cov_* `survey_cols'

replace p601 = . if inlist(p601, 8, 9)
replace p602 = . if inlist(p602, 8, 9)
replace p603 = . if inlist(p603, 8, 9)
replace p604 = . if inlist(p604, 8, 9)
replace p605 = . if inlist(p605, 8, 9)
replace p606 = . if inlist(p606, 8, 9)
replace p607 = . if inlist(p607, 8, 9)
replace p608 = . if inlist(p608, 8, 9)
replace p609 = . if inlist(p609, 8, 9)
replace p610 = . if inlist(p610, 8, 9)
replace p611 = . if inlist(p611, 8, 9)
replace p612 = . if inlist(p612, 8, 9)
replace p613 = . if inlist(p613, 8, 9)

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
export delimited using "spain_2012_reality_outlets.csv", replace

**# Bookmark 6: logos

* ============================================================
* logos (P1701 to P1703)
* correct / incorrect identification of the PSOE, PP and UGT logos (1 acierta, 2 no acierta)
* scored yes/no knowledge items treated as selected response; only 8/9 recoded
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p1701 p1702 p1703

keep id cov_* `survey_cols'

replace p1701 = . if inlist(p1701, 8, 9)
replace p1702 = . if inlist(p1702, 8, 9)
replace p1703 = . if inlist(p1703, 8, 9)

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
export delimited using "spain_2012_reality_logos.csv", replace

**# Bookmark 7: situation

* ============================================================
* situation (P19, P32)
* 1-5 rating of the general economic situation and of the general political situation of Spain, muy buena to muy mala
* two singletons on the identical scale and the same construct paired into a two-item table; code 3 (Regular) is a read option and is kept
* only 8/9 recoded
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p19 p32

keep id cov_* `survey_cols'

replace p19 = . if inlist(p19, 8, 9)
replace p32 = . if inlist(p32, 8, 9)

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
export delimited using "spain_2012_reality_situation.csv", replace

**# Bookmark 8: conversation

* ============================================================
* conversation (P34, P35)
* 1-4 frequency of talking about politics now and at home during childhood, con mucha frecuencia to practicamente nunca
* two adjacent items on the identical scale and the same construct paired into a two-item table; code 8 is No recuerda, treated as non-response
* 8/9 recoded
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p34 p35

keep id cov_* `survey_cols'

replace p34 = . if inlist(p34, 8, 9)
replace p35 = . if inlist(p35, 8, 9)

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
export delimited using "spain_2012_reality_conversation.csv", replace

**# Bookmark 9: participation

* ============================================================
* participation (P3601 to P3605)
* 1-3 recency of five political actions: done in the last twelve months, done in the more distant past, never done
* three read ordered categories, no NO LEER code; only 9 recoded (no 8 code on these items)
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p3601 p3602 p3603 p3604 p3605

keep id cov_* `survey_cols'

replace p3601 = . if inlist(p3601, 9)
replace p3602 = . if inlist(p3602, 9)
replace p3603 = . if inlist(p3603, 9)
replace p3604 = . if inlist(p3604, 9)
replace p3605 = . if inlist(p3605, 9)

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
export delimited using "spain_2012_reality_participation.csv", replace

**# Bookmark 10: personality

* ============================================================
* personality (P3701 to P3710)
* 1-5 self-description on ten cognitive and personality statements, si completamente to no en absoluto
* code 3 (Ni si ni no) is marked (NO LEER) and is recoded to missing per the NO LEER rule; exported values are 1, 2, 4, 5
* 8/9 recoded
* ============================================================

use "spain_2012_reality_master.dta", clear

local survey_cols p3701 p3702 p3703 p3704 p3705 p3706 p3707 p3708 p3709 p3710

keep id cov_* `survey_cols'

replace p3701 = . if inlist(p3701, 3, 8, 9)
replace p3702 = . if inlist(p3702, 3, 8, 9)
replace p3703 = . if inlist(p3703, 3, 8, 9)
replace p3704 = . if inlist(p3704, 3, 8, 9)
replace p3705 = . if inlist(p3705, 3, 8, 9)
replace p3706 = . if inlist(p3706, 3, 8, 9)
replace p3707 = . if inlist(p3707, 3, 8, 9)
replace p3708 = . if inlist(p3708, 3, 8, 9)
replace p3709 = . if inlist(p3709, 3, 8, 9)
replace p3710 = . if inlist(p3710, 3, 8, 9)

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
export delimited using "spain_2012_reality_personality.csv", replace