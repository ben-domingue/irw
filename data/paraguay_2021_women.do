*** This Stata Do File processes the paraguay_2021_women study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\paraguay_2021_women"

* guard: the CSVs carry a UTF-8 byte order mark that can corrupt the first variable name (UPM)

capture program drop fixkey
program define fixkey
    capture confirm variable UPM
    if _rc {
        quietly ds
        local first : word 1 of `r(varlist)'
        rename `first' UPM
    }
end

* import REG02 (household roster) to recover sex and age of each household member

import delimited "REG02_poblacion.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA L02 P104 P105

rename L02 SELEC_AUX

tempfile roster
save `roster'

* import REG08A (family of origin)

import delimited "REG08A_Familia de Origen.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA P801 P802 P803 P804

tempfile origin
save `origin'

* import REG11A (impact), keeping only the permission battery

import delimited "REG11A_Impacto_Fisico_y_emocional_de_las_situaciones_vividas.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA P1120A P1120B P1120C P1120D P1120E P1120F

tempfile impact
save `impact'

* import REG12A (decisions, roles)

import delimited "REG12A_Decisiones_roles_y_aportes.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA P1202A P1202B P1202C P1202D P1202E P1202F P1203A P1203B P1203C P1203D P1205A P1205B P1205C

tempfile decisions
save `decisions'

* import REG05 (selected woman) as the base: SELEC_AUX is the roster line of the final selected woman

import delimited "REG05_seleccion_mujer.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA SELEC_AUX

merge 1:1 UPM NVIVI NHOGA SELEC_AUX using `roster', keep(match) nogenerate

merge 1:1 UPM NVIVI NHOGA using `origin', keep(match) nogenerate

merge 1:1 UPM NVIVI NHOGA using `impact', keep(match) nogenerate

merge 1:1 UPM NVIVI NHOGA using `decisions', keep(match) nogenerate

assert _N == 3276

* rename covariates

rename P104 cov_sex
rename P105 cov_age

* clean covariates
* every selected respondent is a woman (source code 6 = Mujer); recode to the pipeline coding
* cov_age has no sentinel code in this source (observed range 18 to 98)

assert cov_sex == 6

assert inrange(cov_age, 18, 98)

replace cov_sex = 2 if cov_sex == 6

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

sort UPM NVIVI NHOGA

gen long id = _n

order id cov_*, first

compress

save "paraguay_2021_women_master.dta", replace

**# Bookmark 1: roles

* ============================================================
* roles (P1202A to P1202F)
* scale: 1 Muy de acuerdo, 2 De acuerdo, 3 Desacuerdo
* ============================================================

use "paraguay_2021_women_master.dta", clear

local survey_cols P1202A P1202B P1202C P1202D P1202E P1202F

keep id cov_* `survey_cols'

replace P1202A = . if P1202A == 9
replace P1202B = . if P1202B == 9
replace P1202C = . if P1202C == 9
replace P1202D = . if P1202D == 9
replace P1202E = . if P1202E == 9
replace P1202F = . if P1202F == 9

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

assert _N == 19631

assert inlist(resp, 1, 2, 3)

label values resp .

export delimited using "paraguay_2021_women_roles.csv", replace

**# Bookmark 2: justification

* ============================================================
* justification (P1203A to P1203D)
* source codes: 1 Si, 6 No, 9 NR; recoded to 1 No, 2 Si
* ============================================================

use "paraguay_2021_women_master.dta", clear

local survey_cols P1203A P1203B P1203C P1203D

keep id cov_* `survey_cols'

replace P1203A = . if P1203A == 9
replace P1203B = . if P1203B == 9
replace P1203C = . if P1203C == 9
replace P1203D = . if P1203D == 9

recode P1203A (6=1) (1=2)
recode P1203B (6=1) (1=2)
recode P1203C (6=1) (1=2)
recode P1203D (6=1) (1=2)

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

assert _N == 13076

assert inlist(resp, 1, 2)

label values resp .

export delimited using "paraguay_2021_women_justification.csv", replace

**# Bookmark 3: laws

* ============================================================
* laws (P1205A to P1205C), asked only if P1204 == 1
* source codes: 1 Si, 6 No, 9 NR; recoded to 1 No, 2 Si
* ============================================================

use "paraguay_2021_women_master.dta", clear

local survey_cols P1205A P1205B P1205C

keep id cov_* `survey_cols'

replace P1205A = . if P1205A == 9
replace P1205B = . if P1205B == 9
replace P1205C = . if P1205C == 9

recode P1205A (6=1) (1=2)
recode P1205B (6=1) (1=2)
recode P1205C (6=1) (1=2)

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

assert _N == 7971

assert inlist(resp, 1, 2)

label values resp .

export delimited using "paraguay_2021_women_laws.csv", replace

**# Bookmark 4: permission

* ============================================================
* permission (P1120A to P1120F), asked only of women reporting partner conflict
* scale: 1 Siempre, 2 A veces, 3 Nunca
* ============================================================

use "paraguay_2021_women_master.dta", clear

local survey_cols P1120A P1120B P1120C P1120D P1120E P1120F

keep id cov_* `survey_cols'

replace P1120A = . if P1120A == 9
replace P1120B = . if P1120B == 9
replace P1120C = . if P1120C == 9
replace P1120D = . if P1120D == 9
replace P1120E = . if P1120E == 9
replace P1120F = . if P1120F == 9

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

assert _N == 5818

assert inlist(resp, 1, 2, 3)

label values resp .

export delimited using "paraguay_2021_women_permission.csv", replace

**# Bookmark 5: childhood

* ============================================================
* childhood (P801 to P804)
* source codes: 1 De vez en cuando, 2 Con mucha frecuencia, 3 Nunca, 8 No sabe, 9 NR
* recoded to:   1 Nunca, 2 De vez en cuando, 3 Con mucha frecuencia
* ============================================================

use "paraguay_2021_women_master.dta", clear

local survey_cols P801 P802 P803 P804

keep id cov_* `survey_cols'

replace P801 = . if inlist(P801, 8, 9)
replace P802 = . if inlist(P802, 8, 9)
replace P803 = . if inlist(P803, 8, 9)
replace P804 = . if inlist(P804, 8, 9)

recode P801 (3=1) (1=2) (2=3)
recode P802 (3=1) (1=2) (2=3)
recode P803 (3=1) (1=2) (2=3)
recode P804 (3=1) (1=2) (2=3)

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

assert _N == 12996

assert inlist(resp, 1, 2, 3)

label values resp .

export delimited using "paraguay_2021_women_childhood.csv", replace

**# Bookmark 6: public

* ============================================================
* public (P601A, lines 1 and 3 to 22), source register already long, no reshape
* source codes: 1 Si, 6 No, 9 NR; recoded to 1 No, 2 Si
* ============================================================

import delimited "REG06A_Ambito Publico Familiar.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA LS06A P601A

assert _N == 68796

replace P601A = . if P601A == 9

recode P601A (6=1) (1=2)

gen item = "P601A_" + string(LS06A)

rename P601A resp

merge m:1 UPM NVIVI NHOGA using "paraguay_2021_women_master.dta", keepusing(id cov_sex cov_age) keep(match) nogenerate

drop if missing(resp)

keep id item resp cov_sex cov_age

order id item resp cov_*

sort id item

assert _N == 68783

assert inlist(resp, 1, 2)

label values resp .

export delimited using "paraguay_2021_women_public.csv", replace

**# Bookmark 7: family

* ============================================================
* family (P701C, lines 1 to 20), source register already long, no reshape
* source codes: 1 Si, 6 No, 9 NR; recoded to 1 No, 2 Si
* ============================================================

import delimited "REG07A_Ambito Privado Familiar.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA L07A P701C

assert _N == 65520

replace P701C = . if P701C == 9

recode P701C (6=1) (1=2)

gen item = "P701C_" + string(L07A)

rename P701C resp

merge m:1 UPM NVIVI NHOGA using "paraguay_2021_women_master.dta", keepusing(id cov_sex cov_age) keep(match) nogenerate

drop if missing(resp)

keep id item resp cov_sex cov_age

order id item resp cov_*

sort id item

assert _N == 65505

assert inlist(resp, 1, 2)

label values resp .

export delimited using "paraguay_2021_women_family.csv", replace

**# Bookmark 8: control

* ============================================================
* control (P1002 current partner, stacked with P1005 ex partner, lines 1 to 6)
* source registers already long, no reshape
* source codes: 1 Si, 6 No, 9 NR; recoded to 1 No, 2 Si
* ============================================================

* ex-partner version (past tense), women with no current partner

import delimited "REG10B_Relacion_actual_o_ultima_relacion.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA L1005 P1005

replace P1005 = . if P1005 == 9

recode P1005 (6=1) (1=2)

rename L1005 line
rename P1005 resp

gen source = 2

tempfile expartner
save `expartner'

* current-partner version (present tense)

import delimited "REG10A_Relacion_actual_o_ultima_relacion.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA L1002 P1002

replace P1002 = . if P1002 == 9

recode P1002 (6=1) (1=2)

rename L1002 line
rename P1002 resp

gen source = 1

append using `expartner'

* one woman answered both versions; keep her current-partner answers

egen has_current = max(source == 1), by(UPM NVIVI NHOGA)

drop if source == 2 & has_current == 1

gen item = "P1002_" + string(line)

merge m:1 UPM NVIVI NHOGA using "paraguay_2021_women_master.dta", keepusing(id cov_sex cov_age) keep(match) nogenerate

drop if missing(resp)

keep id item resp cov_sex cov_age

order id item resp cov_*

sort id item

assert _N == 19345

assert inlist(resp, 1, 2)

label values resp .

export delimited using "paraguay_2021_women_control.csv", replace

**# Bookmark 9: partner

* ============================================================
* partner (P1007 current partner, stacked with P1011 ex partner, lines 1 to 9 and 11 to 24)
* source registers already long, no reshape
* source codes: 1 Si, 6 No, 9 NR; recoded to 1 No, 2 Si
* ============================================================

* ex-partner version (past tense); line 10 exists only in this file and is dropped

import delimited "REG10D_Relacion_actual_o_ultima_relacion.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA L1011 P1011

drop if L1011 == 10

replace P1011 = . if P1011 == 9

recode P1011 (6=1) (1=2)

rename L1011 line
rename P1011 resp

gen source = 2

tempfile expartner
save `expartner'

* current-partner version (present tense)

import delimited "REG10C_Relacion_actual_o_ultima_relacion.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

fixkey

destring _all, replace force

keep UPM NVIVI NHOGA L1007 P1007

replace P1007 = . if P1007 == 9

recode P1007 (6=1) (1=2)

rename L1007 line
rename P1007 resp

gen source = 1

append using `expartner'

* one woman answered both versions; keep her current-partner answers

egen has_current = max(source == 1), by(UPM NVIVI NHOGA)

drop if source == 2 & has_current == 1

gen item = "P1007_" + string(line)

merge m:1 UPM NVIVI NHOGA using "paraguay_2021_women_master.dta", keepusing(id cov_sex cov_age) keep(match) nogenerate

drop if missing(resp)

keep id item resp cov_sex cov_age

order id item resp cov_*

sort id item

assert _N == 74134

assert inlist(resp, 1, 2)

label values resp .

export delimited using "paraguay_2021_women_partner.csv", replace