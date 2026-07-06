*** This Stata Do File processes the spain_2013_services study ***

******************************************
***********  Prepare the data ************
******************************************

clear all
set more off
cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2013_services"

* read fixed-width raw data
infix ///
    ESTUDIO 1-4 CUES 5-9 CCAA 10-11 PROV 12-13 MUN 14-16 TAMUNI 17 AREA 18 ///
    DISTR 19-20 SECCION 21-23 ENTREV 24-27 P1 28 P2 29 P301 30 P302 31 ///
    P303 32 P304 33 P305 34 P306 35 P307 36 P308 37 P309 38 P401 39 P402 40 ///
    P403 41 P404 42 P405 43 P406 44 P407 45 P408 46 P409 47 P410 48 P5 49-50 ///
    P6 51 P6A 52 P701 53-54 P702 55-56 P703 57-58 P704 59-60 P705 61-62 ///
    P706 63-64 P707 65-66 P708 67-68 P709 69-70 P8 71 P9 72 P9A 73 P10 74-75 ///
    P1101 76 P1102 77 P1103 78 P1104 79 P1105 80 P1106 81 P1107 82 P1108 83 ///
    P1109 84 P1110 85 P1111 86 P1114 87 P1115 88 P12 89 P13 90 P1401 91 ///
    P1402 92 P1403 93 P1404 94 P1405 95 P1406 96 P1407 97 P1408 98 P1409 99 ///
    P15 100 P16 101 P16A 102 P17 103 P17A 104 P17B 105 P18 106 P18A 107 ///
    P18B 108 P19 109 P20 110-111 P2101 112 P2102 113 P2103 114 P2104 115 ///
    P2105 116 P2106 117 P2107 118 P2108 119 P2109 120 P2110 121 P2114 122 ///
    P2115 123 P2116 124 P22 125 P22A 126-127 P22B 128 P23 129 P2401 130 ///
    P2402 131 P2403 132 P2404 133 P2405 134 P2406 135 P2501 136 P2502 137 ///
    P2601 138 P2602 139 P27 140 P27A 141 P27B 142-143 P27C 144 P27D 145 ///
    P27E 146 P28 147-148 P29 149 P29A 150-151 P30 152 P31 153-154 P32 155 ///
    P33 156 P34 157 P34A01 158 P34A02 159 P34A03 160 P34A04 161 P34A05 162 ///
    P34A06 163 P34A07 164 P34A08 165 P34A09 166 P34A10 167 P35 168 ///
    P35A 169-170 P36 171 P36A 172 P37 173 P38 174 P39 175-177 P40 178 ///
    P40A 179 P41 180-182 P42 183 P42A 184 P42B 185-187 P43 188 P4401 189 ///
    P4402 190 P4403 191 P4404 192 P4501 193-195 P4502 196-198 P4503 199-201 ///
    P4504 202-204 P4505 205-207 P4601 208-210 P4602 211-213 P4603 214-216 ///
    P4604 217-219 P4605 220-222 P47 223 P48 224 P49 225 P50 226 ///
    RECUERDO 275-276 ESTUDIOS 277 OCUMAR11 278-279 RAMA09 280 ///
    CONDICION11 281-282 ESTATUS 283 P1116 284 P1117 285 P2117 286 ///
    using "DA2986.", clear
rename *, lower

* stable person id
gen long id = _n

* rename covariates to cov_ (kept in every table, never counted as items)
rename p30 cov_sex
rename p31 cov_age

* clean covariate sentinels (per-variable; 1-10 scales use 98/99)
replace cov_age = . if inlist(cov_age, 99)

order id cov_*, first
compress
save "spain_2013_services_master.dta", replace

******************************************
***********  Process the data ************
******************************************

**# Bookmark 1: functioning  (11 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p1 p2 p301 p302 p303 p304 p305 p306 p307 p308 p309

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p1 = . if inlist(p1, 8, 9)
replace p2 = . if inlist(p2, 8, 9)
replace p301 = . if inlist(p301, 8, 9)
replace p302 = . if inlist(p302, 8, 9)
replace p303 = . if inlist(p303, 8, 9)
replace p304 = . if inlist(p304, 8, 9)
replace p305 = . if inlist(p305, 8, 9)
replace p306 = . if inlist(p306, 8, 9)
replace p307 = . if inlist(p307, 8, 9)
replace p308 = . if inlist(p308, 8, 9)
replace p309 = . if inlist(p309, 8, 9)

local question_cols p1 p2 p301 p302 p303 p304 p305 p306 p307 p308 p309
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p1 p2 p301 p302 p303 p304 p305 p306 p307 p308 p309
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_functioning.csv", replace

**# Bookmark 2: services  (10 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p401 p402 p403 p404 p405 p406 p407 p408 p409 p410

replace p401 = . if inlist(p401, 8, 9)
replace p402 = . if inlist(p402, 8, 9)
replace p403 = . if inlist(p403, 8, 9)
replace p404 = . if inlist(p404, 8, 9)
replace p405 = . if inlist(p405, 8, 9)
replace p406 = . if inlist(p406, 8, 9)
replace p407 = . if inlist(p407, 8, 9)
replace p408 = . if inlist(p408, 8, 9)
replace p409 = . if inlist(p409, 8, 9)
replace p410 = . if inlist(p410, 8, 9)

local question_cols p401 p402 p403 p404 p405 p406 p407 p408 p409 p410
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p401 p402 p403 p404 p405 p406 p407 p408 p409 p410
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_services.csv", replace

**# Bookmark 3: importance  (2 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p5 p6a

replace p5 = . if inlist(p5, 98, 99)
replace p6a = . if inlist(p6a, 8, 9)

local question_cols p5 p6a
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p5 p6a
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_importance.csv", replace

**# Bookmark 4: offices  (9 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p701 p702 p703 p704 p705 p706 p707 p708 p709

replace p701 = . if inlist(p701, 98, 99)
replace p702 = . if inlist(p702, 98, 99)
replace p703 = . if inlist(p703, 98, 99)
replace p704 = . if inlist(p704, 98, 99)
replace p705 = . if inlist(p705, 98, 99)
replace p706 = . if inlist(p706, 98, 99)
replace p707 = . if inlist(p707, 98, 99)
replace p708 = . if inlist(p708, 98, 99)
replace p709 = . if inlist(p709, 98, 99)

local question_cols p701 p702 p703 p704 p705 p706 p707 p708 p709
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p701 p702 p703 p704 p705 p706 p707 p708 p709
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_offices.csv", replace

**# Bookmark 5: purpose  (11 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p1101 p1102 p1103 p1104 p1105 p1106 p1107 p1108 p1109 p1110 p1111

* multiple-response items (1 = marcado); no NS/NC sentinel to recode

local question_cols p1101 p1102 p1103 p1104 p1105 p1106 p1107 p1108 p1109 p1110 p1111
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p1101 p1102 p1103 p1104 p1105 p1106 p1107 p1108 p1109 p1110 p1111
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_purpose.csv", replace

**# Bookmark 6: inpersonsat  (12 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p12 p13 p1401 p1402 p1403 p1404 p1405 p1406 p1407 p1408 p1409 p15

replace p12 = . if inlist(p12, 8, 9)
replace p13 = . if inlist(p13, 8, 9)
replace p1401 = . if inlist(p1401, 8, 9)
replace p1402 = . if inlist(p1402, 8, 9)
replace p1403 = . if inlist(p1403, 8, 9)
replace p1404 = . if inlist(p1404, 8, 9)
replace p1405 = . if inlist(p1405, 8, 9)
replace p1406 = . if inlist(p1406, 8, 9)
replace p1407 = . if inlist(p1407, 8, 9)
replace p1408 = . if inlist(p1408, 8, 9)
replace p1409 = . if inlist(p1409, 8, 9)
replace p15 = . if inlist(p15, 8, 9)

local question_cols p12 p13 p1401 p1402 p1403 p1404 p1405 p1406 p1407 p1408 p1409 p15
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p12 p13 p1401 p1402 p1403 p1404 p1405 p1406 p1407 p1408 p1409 p15
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_inpersonsat.csv", replace

**# Bookmark 7: othercontact  (7 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p16 p16a p17 p17a p18 p18a p18b

replace p16 = . if inlist(p16, 8, 9)
replace p16a = . if inlist(p16a, 8, 9)
replace p17 = . if inlist(p17, 8, 9)
replace p17a = . if inlist(p17a, 8, 9)
replace p18 = . if inlist(p18, 9)
replace p18a = . if inlist(p18a, 9)
replace p18b = . if inlist(p18b, 8, 9)

local question_cols p16 p16a p17 p17a p18 p18a p18b
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p16 p16a p17 p17a p18 p18a p18b
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_othercontact.csv", replace

**# Bookmark 8: internet  (11 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p19 p2101 p2102 p2103 p2104 p2105 p2106 p2107 p2108 p2109 p2110

replace p19 = . if inlist(p19, 8, 9)

local question_cols p19 p2101 p2102 p2103 p2104 p2105 p2106 p2107 p2108 p2109 p2110
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p19 p2101 p2102 p2103 p2104 p2105 p2106 p2107 p2108 p2109 p2110
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_internet.csv", replace

**# Bookmark 9: internetout  (9 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p22 p22b p23 p2401 p2402 p2403 p2404 p2405 p2406

replace p22 = . if inlist(p22, 8, 9)
replace p22b = . if inlist(p22b, 8, 9)
replace p23 = . if inlist(p23, 8, 9)
replace p2401 = . if inlist(p2401, 8, 9)
replace p2402 = . if inlist(p2402, 8, 9)
replace p2403 = . if inlist(p2403, 8, 9)
replace p2404 = . if inlist(p2404, 8, 9)
replace p2405 = . if inlist(p2405, 8, 9)
replace p2406 = . if inlist(p2406, 8, 9)

local question_cols p22 p22b p23 p2401 p2402 p2403 p2404 p2405 p2406
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p22 p22b p23 p2401 p2402 p2403 p2404 p2405 p2406
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_internetout.csv", replace

**# Bookmark 10: complaints  (3 items)
use "spain_2013_services_master.dta", clear
keep id cov_* p27 p27c p27d

replace p27 = . if inlist(p27, 9)
replace p27c = . if inlist(p27c, 8, 9)
replace p27d = . if inlist(p27d, 8, 9)

local question_cols p27 p27c p27d
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p27 p27c p27d
drop if missing(item) | item == ""
order id item resp cov_*, first
sort id item
export delimited using "spain_2013_services_complaints.csv", replace