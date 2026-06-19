*** This Do File creates tables from the Colombia ECP 2023 survey ***

******************************************
***********  Prepare the data ************
******************************************

clear all
set more off

* import each source file to a tempfile

* covariate block 1 - has ALL persons incl. minors; keep adults only
import delimited "Caracteríasticas generales.csv", varnames(1) case(preserve) clear
rename *, lower
destring p5785, replace force
keep if p5785 >= 18 & !missing(p5785)
tempfile cov1
save `cov1', replace

* covariate block 2
import delimited "Caracteríasticas generales 2.csv", varnames(1) case(preserve) clear
rename *, lower
tempfile cov2
save `cov2', replace

* response file: Elecciones y partidos
import delimited "Elecciones y partidos.csv", varnames(1) case(preserve) clear
rename *, lower
tempfile elec
save `elec', replace

* response file: Democracia
import delimited "Democracia.csv", varnames(1) case(preserve) clear
rename *, lower
tempfile demo
save `demo', replace

* response file: Componente capital social
import delimited "Componente capital social.csv", varnames(1) case(preserve) clear
rename *, lower
tempfile capsoc
save `capsoc', replace

* build wide master from Participacion (adult spine), merge everything
import delimited "Participación.csv", varnames(1) case(preserve) clear
rename *, lower
merge 1:1 directorio nro_encuesta hogar_numero persona_numero using `cov1',   keep(match master) nogen
merge 1:1 directorio nro_encuesta hogar_numero persona_numero using `cov2',   keep(match master) nogen
merge 1:1 directorio nro_encuesta hogar_numero persona_numero using `elec',   keep(match master) nogen
merge 1:1 directorio nro_encuesta hogar_numero persona_numero using `demo',   keep(match master) nogen
merge 1:1 directorio nro_encuesta hogar_numero persona_numero using `capsoc', keep(match master) nogen

* rename covariates
rename p5785  cov_age        // anios cumplidos
rename p220   cov_sex        // sexo (1 hombre 2 mujer)
rename p6210  cov_educ       // nivel educativo mas alto
rename p5465  cov_ethnic     // autorreconocimiento etnico
rename p6008  cov_hhsize     // total personas en el hogar
rename p6050  cov_parentesco // parentesco con jefe de hogar
rename p6160  cov_literate   // sabe leer y escribir
rename p606   cov_activity   // actividad principal semana pasada

* clean covariates
replace cov_educ = . if cov_educ == 99
gen long id = _n
order id directorio nro_encuesta hogar_numero persona_numero cov_*, first
compress
save "colombia_2023_master.dta", replace

******************************************
***********  Process the data ************
******************************************

**# Bookmark 1: part_belonging  (P2001, 17 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2001s1 p2001s2 p2001s3 p2001s4 p2001s5 p2001s17 p2001s7 p2001s8 p2001s9 p2001s10 p2001s11 p2001s12 p2001s13 p2001s14 p2001s15 p2001s18 p2001s16
local question_cols p2001s1 p2001s2 p2001s3 p2001s4 p2001s5 p2001s17 p2001s7 p2001s8 p2001s9 p2001s10 p2001s11 p2001s12 p2001s13 p2001s14 p2001s15 p2001s18 p2001s16
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
drop p2001s1 p2001s2 p2001s3 p2001s4 p2001s5 p2001s17 p2001s7 p2001s8 p2001s9 p2001s10 p2001s11 p2001s12 p2001s13 p2001s14 p2001s15 p2001s18 p2001s16
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_belonging.csv", replace

**# Bookmark 2: part_organizations  (P2003, 17 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2003s1 p2003s2 p2003s3 p2003s4 p2003s5 p2003s17 p2003s7 p2003s8 p2003s9 p2003s10 p2003s11 p2003s12 p2003s13 p2003s14 p2003s15 p2003s18 p2003s16
local question_cols p2003s1 p2003s2 p2003s3 p2003s4 p2003s5 p2003s17 p2003s7 p2003s8 p2003s9 p2003s10 p2003s11 p2003s12 p2003s13 p2003s14 p2003s15 p2003s18 p2003s16
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
drop p2003s1 p2003s2 p2003s3 p2003s4 p2003s5 p2003s17 p2003s7 p2003s8 p2003s9 p2003s10 p2003s11 p2003s12 p2003s13 p2003s14 p2003s15 p2003s18 p2003s16
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_organizations.csv", replace

**# Bookmark 3: part_problems  (P5373+P5374, 13 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5373s1 p5373s2 p5373s3 p5373s4 p5373s5 p5373s6 p5373s7 p5373s8 p5373s9 p5373s10 p5373s12 p5373s13 p5374
local question_cols p5373s1 p5373s2 p5373s3 p5373s4 p5373s5 p5373s6 p5373s7 p5373s8 p5373s9 p5373s10 p5373s12 p5373s13 p5374
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
drop p5373s1 p5373s2 p5373s3 p5373s4 p5373s5 p5373s6 p5373s7 p5373s8 p5373s9 p5373s10 p5373s12 p5373s13 p5374
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_problems.csv", replace

**# Bookmark 4: part_mechanisms  (P5376+P5386+P5366, 8 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5376s1 p5376s2 p5376s3 p5376s4 p5376s5 p5376s6 p5386 p5366
local question_cols p5376s1 p5376s2 p5376s3 p5376s4 p5376s5 p5376s6 p5386 p5366
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
drop p5376s1 p5376s2 p5376s3 p5376s4 p5376s5 p5376s6 p5386 p5366
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_mechanisms.csv", replace

**# Bookmark 5: part_spaces  (P5367+P5368, 9 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5367s1 p5367s2 p5367s3 p5367s4 p5367s5 p5367s6 p5367s7 p5367s8 p5368
local question_cols p5367s1 p5367s2 p5367s3 p5367s4 p5367s5 p5367s6 p5367s7 p5367s8 p5368
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
drop p5367s1 p5367s2 p5367s3 p5367s4 p5367s5 p5367s6 p5367s7 p5367s8 p5368
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_spaces.csv", replace

**# Bookmark 6: part_reasons  (P5396+P5400, 15 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5396s1 p5396s2 p5396s3 p5396s4 p5396s5 p5396s6 p5400s1 p5400s2 p5400s3 p5400s4 p5400s5 p5400s6 p5400s7 p5400s9 p5400s8
local question_cols p5396s1 p5396s2 p5396s3 p5396s4 p5396s5 p5396s6 p5400s1 p5400s2 p5400s3 p5400s4 p5400s5 p5400s6 p5400s7 p5400s9 p5400s8
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
drop p5396s1 p5396s2 p5396s3 p5396s4 p5396s5 p5396s6 p5400s1 p5400s2 p5400s3 p5400s4 p5400s5 p5400s6 p5400s7 p5400s9 p5400s8
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_reasons.csv", replace

**# Bookmark 7: elec_registration  (P5369+P5370, 11 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5369 p5370s1 p5370s2 p5370s3 p5370s4 p5370s5 p5370s6 p5370s7 p5370s8 p5370s9 p5370s10
local question_cols p5369 p5370s1 p5370s2 p5370s3 p5370s4 p5370s5 p5370s6 p5370s7 p5370s8 p5370s9 p5370s10
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
drop p5369 p5370s1 p5370s2 p5370s3 p5370s4 p5370s5 p5370s6 p5370s7 p5370s8 p5370s9 p5370s10
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_registration.csv", replace

**# Bookmark 8: elec_voting  (P6933+P5336+P5337, 24 items)
use "colombia_2023_master.dta", clear
keep id cov_* p6933 p5336s1 p5336s6 p5336s7 p5336s8 p5336s10 p5336s11 p5336s13 p5336s14 p5336s15 p5336s17 p5336s19 p5336s20 p5336s22 p5336s23 p5336s12 p5337s1 p5337s2 p5337s3 p5337s4 p5337s5 p5337s6 p5337s8 p5337s7
local question_cols p6933 p5336s1 p5336s6 p5336s7 p5336s8 p5336s10 p5336s11 p5336s13 p5336s14 p5336s15 p5336s17 p5336s19 p5336s20 p5336s22 p5336s23 p5336s12 p5337s1 p5337s2 p5337s3 p5337s4 p5337s5 p5337s6 p5337s8 p5337s7
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
drop p6933 p5336s1 p5336s6 p5336s7 p5336s8 p5336s10 p5336s11 p5336s13 p5336s14 p5336s15 p5336s17 p5336s19 p5336s20 p5336s22 p5336s23 p5336s12 p5337s1 p5337s2 p5337s3 p5337s4 p5337s5 p5337s6 p5337s8 p5337s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_voting.csv", replace

**# Bookmark 9: elec_difficulties  (P5338+P5371+P5372, 12 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5338s1 p5338s2 p5338s3 p5338s4 p5338s5 p5338s7 p5338s8 p5338s10 p5338s11 p5338s6 p5371 p5372
local question_cols p5338s1 p5338s2 p5338s3 p5338s4 p5338s5 p5338s7 p5338s8 p5338s10 p5338s11 p5338s6 p5371 p5372
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
drop p5338s1 p5338s2 p5338s3 p5338s4 p5338s5 p5338s7 p5338s8 p5338s10 p5338s11 p5338s6 p5371 p5372
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_difficulties.csv", replace

**# Bookmark 10: elec_transparency  (P5339, 3 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5339s1 p5339s3 p5339s2
local question_cols p5339s1 p5339s3 p5339s2
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
drop p5339s1 p5339s3 p5339s2
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_transparency.csv", replace

**# Bookmark 11: elec_party  (P5323+P5324+P5325+P5326+P5328, 18 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5323 p5324s2 p5324s3 p5324s4 p5324s6 p5324s7 p5324s8 p5324s5 p5325s1 p5325s2 p5325s3 p5325s4 p5325s5 p5325s7 p5325s8 p5325s6 p5326
local question_cols p5323 p5324s2 p5324s3 p5324s4 p5324s6 p5324s7 p5324s8 p5324s5 p5325s1 p5325s2 p5325s3 p5325s4 p5325s5 p5325s7 p5325s8 p5325s6 p5326
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
drop p5323 p5324s2 p5324s3 p5324s4 p5324s6 p5324s7 p5324s8 p5324s5 p5325s1 p5325s2 p5325s3 p5325s4 p5325s5 p5325s7 p5325s8 p5325s6 p5326
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_party.csv", replace

**# Bookmark 12: elec_candidates  (P2009+P5313, 14 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2009s1 p2009s2 p2009s3 p2009s4 p2009s8 p2009s9 p2009s10 p5313s1 p5313s2 p5313s3 p5313s4 p5313s8 p5313s9 p5313s10
local question_cols p2009s1 p2009s2 p2009s3 p2009s4 p2009s8 p2009s9 p2009s10 p5313s1 p5313s2 p5313s3 p5313s4 p5313s8 p5313s9 p5313s10
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
drop p2009s1 p2009s2 p2009s3 p2009s4 p2009s8 p2009s9 p2009s10 p5313s1 p5313s2 p5313s3 p5313s4 p5313s8 p5313s9 p5313s10
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_candidates.csv", replace

**# Bookmark 13: demo_meaning  (P5314, 6 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5314s2 p5314s3 p5314s4 p5314s5 p5314s6 p5314s7
local question_cols p5314s2 p5314s3 p5314s4 p5314s5 p5314s6 p5314s7
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
drop p5314s2 p5314s3 p5314s4 p5314s5 p5314s6 p5314s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_meaning.csv", replace

**# Bookmark 14: demo_requisites  (P5317+P2011+P5319+P5301+P5302, 15 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5317s1 p5317s2 p5317s3 p5317s4 p5317s5 p5317s6 p5317s7 p5317s8 p5317s9 p5317s10 p5317s11 p2011 p5319 p5301 p5302
local question_cols p5317s1 p5317s2 p5317s3 p5317s4 p5317s5 p5317s6 p5317s7 p5317s8 p5317s9 p5317s10 p5317s11 p2011 p5319 p5301 p5302
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
drop p5317s1 p5317s2 p5317s3 p5317s4 p5317s5 p5317s6 p5317s7 p5317s8 p5317s9 p5317s10 p5317s11 p2011 p5319 p5301 p5302
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_requisites.csv", replace

**# Bookmark 15: demo_rights  (P5304+P3573+P3574, 10 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5304s1 p5304s2 p5304s3 p5304s4 p5304s5 p5304s6 p5304s9 p5304s10 p3573 p3574
local question_cols p5304s1 p5304s2 p5304s3 p5304s4 p5304s5 p5304s6 p5304s9 p5304s10 p3573 p3574
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
drop p5304s1 p5304s2 p5304s3 p5304s4 p5304s5 p5304s6 p5304s9 p5304s10 p3573 p3574
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_rights.csv", replace

**# Bookmark 16: demo_guarantees  (P5306, 7 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5306s1 p5306s2 p5306s3 p5306s4 p5306s5 p5306s6 p5306s7
local question_cols p5306s1 p5306s2 p5306s3 p5306s4 p5306s5 p5306s6 p5306s7
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
drop p5306s1 p5306s2 p5306s3 p5306s4 p5306s5 p5306s6 p5306s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_guarantees.csv", replace

**# Bookmark 17: demo_protection  (P5307+P5308+P5309, 7 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5307s1 p5307s2 p5307s3 p5307s4 p5307s5 p5308 p5309
local question_cols p5307s1 p5307s2 p5307s3 p5307s4 p5307s5 p5308 p5309
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
drop p5307s1 p5307s2 p5307s3 p5307s4 p5307s5 p5308 p5309
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_protection.csv", replace

**# Bookmark 18: demo_attitudes  (P5261, 8 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5261s1 p5261s2 p5261s3 p5261s4 p5261s5 p5261s6 p5261s7 p5261s8
local question_cols p5261s1 p5261s2 p5261s3 p5261s4 p5261s5 p5261s6 p5261s7 p5261s8
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
drop p5261s1 p5261s2 p5261s3 p5261s4 p5261s5 p5261s6 p5261s7 p5261s8
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_attitudes.csv", replace

**# Bookmark 19: demo_prevention  (P6934, 7 items)
use "colombia_2023_master.dta", clear
keep id cov_* p6934s1 p6934s2 p6934s3 p6934s4 p6934s5 p6934s6 p6934s7
local question_cols p6934s1 p6934s2 p6934s3 p6934s4 p6934s5 p6934s6 p6934s7
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
drop p6934s1 p6934s2 p6934s3 p6934s4 p6934s5 p6934s6 p6934s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_prevention.csv", replace

**# Bookmark 20: demo_risks  (P6936, 9 items)
use "colombia_2023_master.dta", clear
keep id cov_* p6936s1 p6936s2 p6936s3 p6936s4 p6936s5 p6936s6 p6936s8 p6936s9 p6936s7
local question_cols p6936s1 p6936s2 p6936s3 p6936s4 p6936s5 p6936s6 p6936s8 p6936s9 p6936s7
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
drop p6936s1 p6936s2 p6936s3 p6936s4 p6936s5 p6936s6 p6936s8 p6936s9 p6936s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_risks.csv", replace

**# Bookmark 21: demo_trust  (P5263, 15 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5263s1 p5263s2 p5263s3 p5263s4 p5263s5 p5263s6 p5263s7 p5263s8 p5263s9 p5263s10 p5263s11 p5263s12 p5263s13 p5263s14 p5263s15
local question_cols p5263s1 p5263s2 p5263s3 p5263s4 p5263s5 p5263s6 p5263s7 p5263s8 p5263s9 p5263s10 p5263s11 p5263s12 p5263s13 p5263s14 p5263s15
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
drop p5263s1 p5263s2 p5263s3 p5263s4 p5263s5 p5263s6 p5263s7 p5263s8 p5263s9 p5263s10 p5263s11 p5263s12 p5263s13 p5263s14 p5263s15
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_trust.csv", replace

**# Bookmark 22: demo_media  (P517+P5264, 9 items)
use "colombia_2023_master.dta", clear
keep id cov_* p517 p5264s1 p5264s2 p5264s3 p5264s4 p5264s5 p5264s6 p5264s7 p5264s8
local question_cols p517 p5264s1 p5264s2 p5264s3 p5264s4 p5264s5 p5264s6 p5264s7 p5264s8
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
drop p517 p5264s1 p5264s2 p5264s3 p5264s4 p5264s5 p5264s6 p5264s7 p5264s8
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_media.csv", replace

**# Bookmark 23: demo_discrimination  (P3328, 14 items)
use "colombia_2023_master.dta", clear
keep id cov_* p3328s1 p3328s2 p3328s3 p3328s4 p3328s5 p3328s6 p3328s7 p3328s8 p3328s9 p3328s10 p3328s11 p3328s12 p3328s13 p3328s15
local question_cols p3328s1 p3328s2 p3328s3 p3328s4 p3328s5 p3328s6 p3328s7 p3328s8 p3328s9 p3328s10 p3328s11 p3328s12 p3328s13 p3328s15
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
drop p3328s1 p3328s2 p3328s3 p3328s4 p3328s5 p3328s6 p3328s7 p3328s8 p3328s9 p3328s10 p3328s11 p3328s12 p3328s13 p3328s15
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_discrimination.csv", replace

**# Bookmark 24: demo_procedures  (P5265+P2013, 9 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5265 p2013s1 p2013s2 p2013s3 p2013s4 p2013s5 p2013s6 p2013s8 p2013s7
local question_cols p5265 p2013s1 p2013s2 p2013s3 p2013s4 p2013s5 p2013s6 p2013s8 p2013s7
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
drop p5265 p2013s1 p2013s2 p2013s3 p2013s4 p2013s5 p2013s6 p2013s8 p2013s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_procedures.csv", replace

**# Bookmark 25: demo_hurdles  (P2014+P2015, 12 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2014 p2015s1 p2015s2 p2015s3 p2015s4 p2015s5 p2015s6 p2015s7 p2015s8 p2015s9 p2015s10
local question_cols p2014 p2015s1 p2015s2 p2015s3 p2015s4 p2015s5 p2015s6 p2015s7 p2015s8 p2015s9 p2015s10
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
drop p2014 p2015s1 p2015s2 p2015s3 p2015s4 p2015s5 p2015s6 p2015s7 p2015s8 p2015s9 p2015s10
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_hurdles.csv", replace

**# Bookmark 26: demo_channels  (P5266+P3329+P5268, 15 items)
use "colombia_2023_master.dta", clear
keep id cov_* p5266s1 p5266s2 p5266s3 p5266s4 p5266s5 p5266s6 p5266s7 p5266s8 p3329s1 p3329s2 p3329s3 p3329s4 p3329s5 p3329s6 p5268
local question_cols p5266s1 p5266s2 p5266s3 p5266s4 p5266s5 p5266s6 p5266s7 p5266s8 p3329s1 p3329s2 p3329s3 p3329s4 p3329s5 p3329s6 p5268
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
drop p5266s1 p5266s2 p5266s3 p5266s4 p5266s5 p5266s6 p5266s7 p5266s8 p3329s1 p3329s2 p3329s3 p3329s4 p3329s5 p3329s6 p5268
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_channels.csv", replace

**# Bookmark 27: demo_corruption  (P2016+P2017+P2019, 17 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2016s1 p2016s2 p2016s3 p2016s4 p2016s5 p2016s6 p2016s7 p2016s8 p2016s9 p2017s1 p2017s2 p2017s3 p2017s4 p2017s5 p2017s6 p2017s7
local question_cols p2016s1 p2016s2 p2016s3 p2016s4 p2016s5 p2016s6 p2016s7 p2016s8 p2016s9 p2017s1 p2017s2 p2017s3 p2017s4 p2017s5 p2017s6 p2017s7
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
drop p2016s1 p2016s2 p2016s3 p2016s4 p2016s5 p2016s6 p2016s7 p2016s8 p2016s9 p2017s1 p2017s2 p2017s3 p2017s4 p2017s5 p2017s6 p2017s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_corruption.csv", replace

**# Bookmark 28: demo_anticorruption  (P2021+P1754+P3330, 3 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2021 p1754 p3330
local question_cols p2021 p1754 p3330
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
drop p2021 p1754 p3330
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_anticorruption.csv", replace

**# Bookmark 29: demo_bribery  (P3331+P3332+P5375+P5376+P5378, 5 items)
use "colombia_2023_master.dta", clear
keep id cov_* p3331 p3332 p5375 p5376
local question_cols p3331 p3332 p5375 p5376
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
drop p3331 p3332 p5375 p5376
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_bribery.csv", replace

**# Bookmark 30: capsoc_importance  (P2023, 6 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2023s1 p2023s2 p2023s3 p2023s4 p2023s5 p2023s6
local question_cols p2023s1 p2023s2 p2023s3 p2023s4 p2023s5 p2023s6
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
drop p2023s1 p2023s2 p2023s3 p2023s4 p2023s5 p2023s6
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_importance.csv", replace

**# Bookmark 31: capsoc_confidence  (P2025, 6 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2025s1 p2025s2 p2025s4 p2025s5 p2025s6 p2025s7
local question_cols p2025s1 p2025s2 p2025s4 p2025s5 p2025s6 p2025s7
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
drop p2025s1 p2025s2 p2025s4 p2025s5 p2025s6 p2025s7
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_confidence.csv", replace

**# Bookmark 32: capsoc_wellbeing  (P2027+P2034+P2039, 9 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2027s1 p2027s2 p2027s3 p2027s4 p2027s5 p2027s9 p2027s10 p2034 p2039
local question_cols p2027s1 p2027s2 p2027s3 p2027s4 p2027s5 p2027s9 p2027s10 p2034 p2039
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
drop p2027s1 p2027s2 p2027s3 p2027s4 p2027s5 p2027s9 p2027s10 p2034 p2039
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_wellbeing.csv", replace

**# Bookmark 33: capsoc_neighbors  (P2041, 13 items)
use "colombia_2023_master.dta", clear
keep id cov_* p2041s1 p2041s2 p2041s3 p2041s4 p2041s5 p2041s6 p2041s7 p2041s8 p2041s9 p2041s10 p2041s11 p2041s12 p2041s13
local question_cols p2041s1 p2041s2 p2041s3 p2041s4 p2041s5 p2041s6 p2041s7 p2041s8 p2041s9 p2041s10 p2041s11 p2041s12 p2041s13
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
drop p2041s1 p2041s2 p2041s3 p2041s4 p2041s5 p2041s6 p2041s7 p2041s8 p2041s9 p2041s10 p2041s11 p2041s12 p2041s13
drop if missing(item) | item == ""
replace resp = . if inlist(resp, 97, 98, 99)
order id item resp cov*, first
sort id item
export delimited using "colombia_2023_politics_neighbors.csv", replace