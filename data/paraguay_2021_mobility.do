*** This Stata Do File processes the paraguay_2021_mobility study ***

* Source: Encuesta de Movilidad del Area Metropolitana de Asuncion (AMA) 2021, INE Paraguay
* Habito.csv holds Section VII (habits and opinion): one selected person aged 15 and older per household, N = 2,061
* Persona.csv is the household roster; Habito links to it through IdPersona (verified 2,061 of 2,061)
* The rating battery (P708) is asked only of the 912 respondents who used a bus in the last 30 days
*
* Logged decisions:
* - INE Paraguay codes sex as 1 Hombre, 6 Mujer. Recoded to 1 Hombre, 2 Mujer.
* - cov_age has no sentinel. Ages 99 and 100 are real (confirmed against year of birth).
* - rating scale: 1 Muy malo, 2 Malo, 3 Bueno, 4 Muy bueno. 5 No sabe is recoded to missing.
* - four items carry one undocumented value of 99 each, recoded to missing as NR.
* - the 13 ratings are kept as one table (single question, single scale), not split by theme.
* - excluded: P707, P709, P710, P711, P713 (ranked or multiple-response picks), P703 (nominal),
*   P705, P712, P406 (lone ordered singletons on different scales), household asset items.

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\paraguay_2021_mobility"

* import Persona (household roster) to recover sex and age

import delimited "Persona.csv", delimiter(";") varnames(1) case(preserve) encoding("ISO-8859-1") clear

destring _all, replace force

keep Id IdSexo Edad

rename Id IdPersona

tempfile roster
save `roster'

* import Habito (selected person, habits and opinion)

import delimited "Hábito.csv", delimiter(";") varnames(1) case(preserve) encoding("ISO-8859-1") clear

destring _all, replace force

keep IdPersona IdCalifFrecuencia IdCalifPuntualidad IdCalifTiempoViaje IdCalifPrecio IdCalifPrecioCalidad IdCalifAtencionChofer IdCalifLimpieza IdCalifModoConduccion IdCalifComodidad IdCalifFacilidadSubidaBajada IdCalifDistanciaParada IdCalifInformacionDisp IdCalifParadasBuses

merge 1:1 IdPersona using `roster', keep(match) nogenerate

assert _N == 2061

* rename covariates

rename IdSexo cov_sex
rename Edad cov_age

* clean covariates

assert inlist(cov_sex, 1, 6)

assert inrange(cov_age, 15, 100)

replace cov_sex = 2 if cov_sex == 6

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

sort IdPersona

gen long id = _n

order id cov_*, first

compress

save "paraguay_2021_mobility_master.dta", replace

**# Bookmark 1: mobility

* ============================================================
* mobility (P708, 13 rating items), asked only if the respondent used a bus in the last 30 days
* scale: 1 Muy malo, 2 Malo, 3 Bueno, 4 Muy bueno; 5 No sabe and 99 NR recoded to missing
* ============================================================

use "paraguay_2021_mobility_master.dta", clear

local survey_cols IdCalifFrecuencia IdCalifPuntualidad IdCalifTiempoViaje IdCalifPrecio IdCalifPrecioCalidad IdCalifAtencionChofer IdCalifLimpieza IdCalifModoConduccion IdCalifComodidad IdCalifFacilidadSubidaBajada IdCalifDistanciaParada IdCalifInformacionDisp IdCalifParadasBuses

keep id cov_* `survey_cols'

replace IdCalifFrecuencia = . if inlist(IdCalifFrecuencia, 5, 99)
replace IdCalifPuntualidad = . if inlist(IdCalifPuntualidad, 5, 99)
replace IdCalifTiempoViaje = . if inlist(IdCalifTiempoViaje, 5, 99)
replace IdCalifPrecio = . if inlist(IdCalifPrecio, 5, 99)
replace IdCalifPrecioCalidad = . if inlist(IdCalifPrecioCalidad, 5, 99)
replace IdCalifAtencionChofer = . if inlist(IdCalifAtencionChofer, 5, 99)
replace IdCalifLimpieza = . if inlist(IdCalifLimpieza, 5, 99)
replace IdCalifModoConduccion = . if inlist(IdCalifModoConduccion, 5, 99)
replace IdCalifComodidad = . if inlist(IdCalifComodidad, 5, 99)
replace IdCalifFacilidadSubidaBajada = . if inlist(IdCalifFacilidadSubidaBajada, 5, 99)
replace IdCalifDistanciaParada = . if inlist(IdCalifDistanciaParada, 5, 99)
replace IdCalifInformacionDisp = . if inlist(IdCalifInformacionDisp, 5, 99)
replace IdCalifParadasBuses = . if inlist(IdCalifParadasBuses, 5, 99)

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

keep id item resp cov_*

assert _N == 11669

assert inlist(resp, 1, 2, 3, 4)

label values resp .

export delimited using "paraguay_2021_mobility_mobility.csv", replace