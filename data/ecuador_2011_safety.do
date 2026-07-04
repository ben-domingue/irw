*** This Stata Do File processes the ecuador_2011_safety ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\ecuador_2011_safety"

local files hogares personas informantes automotores robo_automotores_total robo_automotores_parcial robo_vivienda delito_personas ultimo_delito robo_objetosydemas

* generate csv versions of each file
foreach f of local files {
    import spss using "victimizacion_`f'.sav", clear
    export delimited using "victimizacion_`f'.csv", replace
}

* import informant-only information
import delimited "victimizacion_informantes.csv", varnames(1) case(preserve) encoding("UTF-8") clear

gen id = _n

* clean covariates

gen cov_sex = .
replace cov_sex = 1 if P22 == "Hombre"
replace cov_sex = 2 if P22 == "Mujer"
label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

rename P23 cov_age

gen cov_education = .
replace cov_education = 0 if P24A == "Ninguno"
replace cov_education = 1 if P24A == "Centro de alfabetización"
replace cov_education = 2 if P24A == "Jardín de infantes"
replace cov_education = 3 if P24A == "Primaria"
replace cov_education = 4 if P24A == "Educación Básica"
replace cov_education = 5 if P24A == "Secundaria"
replace cov_education = 6 if P24A == "Educación Media"
replace cov_education = 7 if P24A == "Post-Bachillerato"
replace cov_education = 8 if P24A == "Superior"
replace cov_education = 9 if P24A == "Postgrado"
label define edu_lbl 0 "Ninguno" 1 "Alfabetizacion" 2 "Jardin" 3 "Primaria" 4 "Basica" 5 "Secundaria" 6 "Media" 7 "Post-bachillerato" 8 "Superior" 9 "Postgrado"
label values cov_education edu_lbl

save "ecuador_2011_master.dta", replace

**# Table 1: safety

* ============================================================
* safety (I51, I52) - 5.1/5.2, 1-5 safe scale
* ============================================================

use "ecuador_2011_master.dta", clear

local survey_cols I51 I52

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Muy inseguro"
    replace `v'_n = 2 if `v' == "Inseguro"
    replace `v'_n = 3 if `v' == "Ni seguro  ni  inseguro"
    replace `v'_n = 4 if `v' == "Seguro"
    replace `v'_n = 5 if `v' == "Muy seguro"
    drop `v'
    rename `v'_n `v'
}

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
drop I51 I52
export delimited using "ecuador_2011_safety_safety.csv", replace

**# Table 2: places

* ============================================================
* places (I5301-I5312) - 5.3, 1-5 feel-safe by location
* ============================================================

use "ecuador_2011_master.dta", clear

local survey_cols I5301 I5302 I5303 I5304 I5305 I5306 I5307 I5308 I5309 I5310 I5311 I5312

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Muy inseguro"
    replace `v'_n = 2 if `v' == "Inseguro"
    replace `v'_n = 3 if `v' == "Ni seguro  ni  inseguro"
    replace `v'_n = 4 if `v' == "Seguro"
    replace `v'_n = 5 if `v' == "Muy seguro"
    drop `v'
    rename `v'_n `v'
}

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
drop I5301 I5302 I5303 I5304 I5305 I5306 I5307 I5308 I5309 I5310 I5311 I5312
export delimited using "ecuador_2011_safety_places.csv", replace

**# Table 3: trend

* ============================================================
* trend (I55, I56) - 5.5/5.6, crime trend 1-3
* ============================================================

use "ecuador_2011_master.dta", clear

local survey_cols I55 I56

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Aumento"
    replace `v'_n = 2 if `v' == "Se mantuvo igual"
    replace `v'_n = 3 if `v' == "Disminuyo"
    drop `v'
    rename `v'_n `v'
}

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
drop I55 I56
export delimited using "ecuador_2011_safety_trend.csv", replace

**# Table 4: impact

* ============================================================
* impact (I512, I514) - 5.12 life affected + 5.14 media time, 1-3
* ============================================================

use "ecuador_2011_master.dta", clear

local survey_cols I512 I514

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Mucho"
    replace `v'_n = 2 if `v' == "Poco"
    replace `v'_n = 3 if `v' == "Nada"
    drop `v'
    rename `v'_n `v'
}

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
drop I512 I514
export delimited using "ecuador_2011_safety_impact.csv", replace


**# Table 5: confidence

* ============================================================
* confidence (I51501-I51514, I51533) - 5.15, 1-10 trust
* ============================================================

use "ecuador_2011_master.dta", clear

local survey_cols I51501 I51502 I51533 I51504 I51505 I51506 I51507 I51508 I51509 I51510 I51511 I51512 I51513 I51514

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Ninguna confianza"
    replace `v'_n = 2 if `v' == "2"
    replace `v'_n = 3 if `v' == "3"
    replace `v'_n = 4 if `v' == "4"
    replace `v'_n = 5 if `v' == "5"
    replace `v'_n = 6 if `v' == "6"
    replace `v'_n = 7 if `v' == "7"
    replace `v'_n = 8 if `v' == "8"
    replace `v'_n = 9 if `v' == "9"
    replace `v'_n = 10 if `v' == "Total confianza"
    drop `v'
    rename `v'_n `v'
}

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
drop I51501 I51502 I51533 I51504 I51505 I51506 I51507 I51508 I51509 I51510 I51511 I51512 I51513 I51514
export delimited using "ecuador_2011_safety_confidence.csv", replace


**# Table 6: avoidance
* ============================================================
* avoidance (I50901-I50914) - 5.9, yes/no behavior change
* ============================================================
use "ecuador_2011_master.dta", clear

local survey_cols I50901 I50902 I50903 I50904 I50905 I50906 I50907 I50908 I50909 I50910 I50911 I50912 I50913 I50914

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Si"
    replace `v'_n = 0 if `v' == "No"
    drop `v'
    rename `v'_n `v'
}

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
drop I50901 I50902 I50903 I50904 I50905 I50906 I50907 I50908 I50909 I50910 I50911 I50912 I50913 I50914
export delimited using "ecuador_2011_safety_avoidance.csv", replace


**# Table 7: homesec
* ============================================================
* homesec (I51001-I51011) - 5.10, yes/no security measures
* ============================================================
use "ecuador_2011_master.dta", clear

local survey_cols I51001 I51002 I51003 I51004 I51005 I51006 I51007 I51008 I51009 I51010 I51011

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Si"
    replace `v'_n = 0 if `v' == "No"
    drop `v'
    rename `v'_n `v'
}

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
drop I51001 I51002 I51003 I51004 I51005 I51006 I51007 I51008 I51009 I51010 I51011
export delimited using "ecuador_2011_safety_homesec.csv", replace


**# Table 8: operatives
* ============================================================
* operatives (I517, I518) - 5.17/5.18, yes/no govt operations
* ============================================================
use "ecuador_2011_master.dta", clear

local survey_cols I517 I518

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Si"
    replace `v'_n = 0 if `v' == "No"
    drop `v'
    rename `v'_n `v'
}

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
drop I517 I518
export delimited using "ecuador_2011_safety_operatives.csv", replace


**# Table 9: surroundings
* ============================================================
* surroundings (I51901-I51906) - 5.19, yes/no presence
* ============================================================
use "ecuador_2011_master.dta", clear

local survey_cols I51901 I51902 I51903 I51904 I51905 I51906

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Si"
    replace `v'_n = 0 if `v' == "No"
    drop `v'
    rename `v'_n `v'
}

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
drop I51901 I51902 I51903 I51904 I51905 I51906
export delimited using "ecuador_2011_safety_surroundings.csv", replace


**# Table 10: victim
* ============================================================
* victim (I71A, I72A) - 7.1/7.2, yes/no victimization
* ============================================================
use "ecuador_2011_master.dta", clear

local survey_cols I71A I72A

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Si"
    replace `v'_n = 0 if `v' == "No"
    drop `v'
    rename `v'_n `v'
}

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
drop I71A I72A
export delimited using "ecuador_2011_safety_victim.csv", replace


**# Table 11: victimtype
* ============================================================
* victimtype (I7401-I7406) - 7.4, yes/no crime type suffered
* ============================================================
use "ecuador_2011_master.dta", clear

local survey_cols I7401 I7402 I7403 I7404 I7405 I7406

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Si"
    replace `v'_n = 0 if `v' == "No"
    drop `v'
    rename `v'_n `v'
}

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
drop I7401 I7402 I7403 I7404 I7405 I7406
export delimited using "ecuador_2011_safety_victimtype.csv", replace


**# Table 12: crimespecific
* ============================================================
* crimespecific (I75, I7601-I7604, I77, I78, I79, I710) - yes/no
* ============================================================
use "ecuador_2011_master.dta", clear

local survey_cols I75 I7601 I7602 I7603 I7604 I77 I78 I79 I710

keep id cov_* `survey_cols'

foreach v of local survey_cols {
    gen `v'_n = .
    replace `v'_n = 1 if `v' == "Si"
    replace `v'_n = 0 if `v' == "No"
    drop `v'
    rename `v'_n `v'
}

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
drop I75 I7601 I7602 I7603 I7604 I77 I78 I79 I710
export delimited using "ecuador_2011_safety_crime.csv", replace