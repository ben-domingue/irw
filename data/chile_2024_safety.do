*** This Do File creates tables from the Chile Seguridad ciudadana survey ***

* clear
clear

* import study dataset
import delimited "base-de-datos---enusc-2024-csv.csv", clear varnames(1) case(lower)

* compress
compress

* drop non-Kish respondents
drop if kish == 0

* convert column names to lowercase
rename *, lower

* clean covariates
rename rph_sexo cov_sex
rename rph_edad cov_age
rename rph_nivel cov_education

destring cov_sex cov_age cov_education, replace

foreach var of varlist cov_sex cov_age cov_education {
    replace `var' = . if inlist(`var', 85, 88, 96, 99)
}

* encode cov_sex
label define sex_lbl 1 "Male" 2 "Female"
label values cov_sex sex_lbl

* encode cov_age
label define age_lbl 0 "0-14" 1 "15-19" 2 "20-29" 3 "30-39" 4 "40-49" 5 "50-59" 6 "60-69" 7 "70+"
label values cov_age age_lbl

* encode cov_education
label define edu_lbl 0 "Never attended" 1 "Basic education" 2 "Secondary education" 3 "Higher education"
label values cov_education edu_lbl

* generate new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned household covariate dataset
save "chile_2024_safety.dta", replace

**# Bookmark #1: Perceptions of Safety and Disorder

use "chile_2024_safety.dta", clear

local survey_cols p_inseg_lugares_1 p_inseg_lugares_2 p_inseg_lugares_3 p_inseg_lugares_4 p_inseg_lugares_5 p_inseg_lugares_6 p_inseg_lugares_7 p_inseg_lugares_8 p_inseg_lugares_9 p_inseg_lugares_10 p_inseg_lugares_11 p_inseg_lugares_12 p_inseg_lugares_13 p_inseg_lugares_14 p_inseg_lugares_15 p_inseg_lugares_16 p_inseg_oscuro_1 p_inseg_dia_1 p_inseg_oscuro_2 p_inseg_dia_2

keep id cov_* `survey_cols'

destring `survey_cols', replace

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 85, 86, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

drop p_inseg_lugares_1 p_inseg_lugares_2 p_inseg_lugares_3 p_inseg_lugares_4 p_inseg_lugares_5 p_inseg_lugares_6 p_inseg_lugares_7 p_inseg_lugares_8 p_inseg_lugares_9 p_inseg_lugares_10 p_inseg_lugares_11 p_inseg_lugares_12 p_inseg_lugares_13 p_inseg_lugares_14 p_inseg_lugares_15 p_inseg_lugares_16 p_inseg_oscuro_1 p_inseg_dia_1 p_inseg_oscuro_2 p_inseg_dia_2

keep id cov_* item resp

export delimited using "chile_2024_safety_safety.csv", replace

**# Bookmark #2: Disturbances

use "chile_2024_safety.dta", clear

local survey_cols p_desordenes_1 p_desordenes_2 p_desordenes_3 p_desordenes_4 p_desordenes_5 p_desordenes_6 p_desordenes_7 p_desordenes_8 p_incivilidades_1 p_incivilidades_2 p_incivilidades_3 p_incivilidades_4 p_incivilidades_5 p_incivilidades_6 p_incivilidades_7

keep id cov_* `survey_cols'

destring `survey_cols', replace

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 85, 86, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

drop p_desordenes_1 p_desordenes_2 p_desordenes_3 p_desordenes_4 p_desordenes_5 p_desordenes_6 p_desordenes_7 p_desordenes_8 p_incivilidades_1 p_incivilidades_2 p_incivilidades_3 p_incivilidades_4 p_incivilidades_5 p_incivilidades_6 p_incivilidades_7

keep id cov_* item resp

export delimited using "chile_2024_safety_disturbances.csv", replace

**# Bookmark #3: Fear

use "chile_2024_safety.dta", clear

local survey_cols p_expos_delito p_mod_actividades_1 p_mod_actividades_2 p_mod_actividades_3 p_mod_actividades_4 p_mod_actividades_5 p_mod_actividades_6 p_mod_actividades_7 p_mod_actividades_8 p_mod_actividades_9 p_mod_actividades_10 p_mod_actividades_11 p_mod_actividades_12 p_mod_actividades_13 p_mod_actividades_14

keep id cov_* `survey_cols'

destring `survey_cols', replace

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = . if inlist(resp, 85, 86, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

drop p_expos_delito p_mod_actividades_1 p_mod_actividades_2 p_mod_actividades_3 p_mod_actividades_4 p_mod_actividades_5 p_mod_actividades_6 p_mod_actividades_7 p_mod_actividades_8 p_mod_actividades_9 p_mod_actividades_10 p_mod_actividades_11 p_mod_actividades_12 p_mod_actividades_13 p_mod_actividades_14

keep id cov_* item resp

export delimited using "chile_2024_safety_fear.csv", replace

**# Bookmark #4: Institutional Trust

use "chile_2024_safety.dta", clear

local survey_cols ev_confia_cch ev_confia_pdi ev_confia_fmp

keep id cov_* `survey_cols'

destring `survey_cols', replace

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace
    replace resp = . if inlist(resp, 85, 86, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
sort id item

drop ev_confia_cch ev_confia_pdi ev_confia_fmp

keep id cov_* item resp

export delimited using "chile_2024_safety_trust.csv", replace

**# Bookmark #5: Institutional Knowledge

use "chile_2024_safety.dta", clear

local survey_cols ev_conoce_cch ev_conoce_pdi ev_conoce_fmp

keep id cov_* `survey_cols'

tempfile long_data

save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 86, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_knowledge.csv", replace

**# Bookmark #6: Victimization - Vehicle

use "chile_2024_safety.dta", clear

local survey_cols screen_prop_vehiculo screen_int_rdv screen_rob_rdv rdv_denuncias screen_rob_rddv rddv_denuncias screen_rob_vandvhc vandvhc_denuncias

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 86, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_vehicle.csv", replace

**# Bookmark #7: Victimization - Dwelling

use "chile_2024_safety.dta", clear

local survey_cols screen_int_rfv screen_rob_rfv rfv_denuncias screen_rob_vandviv vandviv_denuncias

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_dwelling.csv", replace

**# Bookmark #8: Victimization - Personal Robbery Violence

use "chile_2024_safety.dta", clear

local survey_cols screen_int_rvi screen_rob_rvi rvi_denuncias rvi_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_violence.csv", replace

**# Bookmark #9: Victimization - Suprise Robbery

use "chile_2024_safety.dta", clear

local survey_cols screen_int_rps screen_rob_rps rps_denuncias rps_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_surprise.csv", replace

**# Bookmark #10: Victimization - Theft

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_hur hur_denuncias hur_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_theft.csv", replace

**# Bookmark #11: Victimization - Banking

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_frb frb_denuncias frb_personal 

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_banking.csv", replace

**# Bookmark #12: Victimization - Scam

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_est est_denuncias est_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_scam.csv", replace

**# Bookmark #13: Victimization - Aggression

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_agr agr_denuncias agr_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_aggression.csv", replace

**# Bookmark #14: Victimization - Threats

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_amen amen_denuncias amen_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_threats.csv", replace

**# Bookmark #15: Victimization - Extortion

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_ext ext_denuncias ext_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_extortion.csv", replace

**# Bookmark #16: Victimization - Bribes

use "chile_2024_safety.dta", clear

local survey_cols filtro_soborno screen_rob_sob sob_denuncias sob_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_bribes.csv", replace

**# Bookmark #17: Victimization - Personal Hacking

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_hack hack_denuncias hack_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_hacking.csv", replace

**# Bookmark #18: Victimization - Malicious

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_virus virus_denuncias virus_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_malicious.csv", replace

**# Bookmark #19: Victimization - Cyberbullying

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_bully bully_denuncias bully_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_cyberbullying.csv", replace

**# Bookmark #20: Victimization - Identity Theft

use "chile_2024_safety.dta", clear

local survey_cols screen_rob_suplant suplant_denuncias suplant_personal

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_identity.csv", replace

**# Bookmark #21: Victimization - Vehicle Theft Characterization

use "chile_2024_safety.dta", clear

local survey_cols rdv_presente rdv_conoce_resp rdv_violencia rdv_uso_arma rdv_lesiones rdv_denuncia rdv_satisf_den rdv_accion_policial rdv_contacto_mp rdv_denuncia_firma rdv_recuperado rdv_pav rdv_pav_contac

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_vehiclecharacterization.csv", replace

**# Bookmark #22: Victimization - Theft from Vehicle Characterization

use "chile_2024_safety.dta", clear

local survey_cols rddv_denuncia rddv_satisf_den rddv_accion_policial rddv_contacto_mp rddv_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_vehicletheft.csv", replace

**# Bookmark #23: Victimization - Vehicle Vandalism Characterization

use "chile_2024_safety.dta", clear

local survey_cols vandvhc_conoce_resp vandvhc_odio vandvhc_denuncia vandvhc_satisf_den vandvhc_accion_policial vandvhc_contacto_mp vandvhc_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_vehiclevandalism.csv", replace

**# Bookmark #24: Victimization - Dwelling Burglary Characterization

use "chile_2024_safety.dta", clear

local survey_cols rfv_presente rfv_conoce_resp rfv_violencia rfv_uso_arma rfv_lesiones rfv_denuncia rfv_satisf_den rfv_accion_policial rfv_contacto_mp rfv_denuncia_firma rfv_pav rfv_pav_contac rfv_ingr_conf

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_dwellingburglary.csv", replace

**# Bookmark #25: Victimization - Dwelling Vandalism Characterization

use "chile_2024_safety.dta", clear

local survey_cols vandviv_conoce_resp vandviv_odio vandviv_denuncia vandviv_satisf_den vandviv_accion_policial vandviv_contacto_mp vandviv_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_dwellingvandalism.csv", replace

**# Bookmark #26: Victimization - Violent Robbery Characterization

use "chile_2024_safety.dta", clear

local survey_cols rvi_acomp rvi_conoce_resp rvi_uso_arma rvi_lesiones rvi_denuncia rvi_satisf_den rvi_accion_policial rvi_contacto_mp rvi_denuncia_firma rvi_pav rvi_pav_contac

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 86, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_violentrobbery.csv", replace

**# Bookmark #27: Victimization - Surprise Robbery Characterization

use "chile_2024_safety.dta", clear

local survey_cols rps_conoce_resp rps_violencia_cons rps_lesiones rps_denuncia rps_satisf_den rps_accion_policial rps_contacto_mp rps_denuncia_firma rps_pav rps_pav_contac

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_surpriserobbery.csv", replace

**# Bookmark #28: Victimization - Theft Characterization

use "chile_2024_safety.dta", clear

local survey_cols hur_denuncia hur_satisf_den hur_accion_policial hur_contacto_mp hur_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_theftcharacterization.csv", replace

**# Bookmark #29: Victimization - Bank Fraud Characterization

use "chile_2024_safety.dta", clear

local survey_cols frb_denuncia frb_satisf_den frb_accion_policial frb_contacto_mp frb_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_bankfraud.csv", replace

**# Bookmark #30: Victimization - Scam Characterization

use "chile_2024_safety.dta", clear

local survey_cols est_denuncia est_satisf_den est_accion_policial est_contacto_mp est_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 86, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_scamcharacterization.csv", replace

**# Bookmark #31: Victimization - Assault Characterization

use "chile_2024_safety.dta", clear

local survey_cols agr_acomp agr_conoce_resp agr_uso_arma agr_odio agr_denuncia agr_satisf_den agr_accion_policial agr_contacto_mp agr_denuncia_firma agr_pav agr_pav_contac

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_assault.csv", replace

**# Bookmark #32: Victimization - Threats Characterization

use "chile_2024_safety.dta", clear

local survey_cols amen_acomp amen_conoce_resp amen_uso_arma amen_odio amen_denuncia amen_satisf_den amen_accion_policial amen_contacto_mp amen_denuncia_firma amen_pav amen_pav_contac

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_threatscharacterization.csv", replace

**# Bookmark #33: Victimization - Extortion Characterization

use "chile_2024_safety.dta", clear

local survey_cols ext_conoce_resp ext_violencia ext_uso_arma ext_lesiones ext_evasion ext_denuncia ext_satisf_den ext_accion_policial ext_contacto_mp ext_denuncia_firma ext_pav ext_pav_contac

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_extortioncharacterization.csv", replace

**# Bookmark #34: Victimization - Hacking Characterization

use "chile_2024_safety.dta", clear

local survey_cols hack_dinero hack_denuncia hack_satisf_den hack_accion_policial hack_contacto_mp hack_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_hackingcharacterization.csv", replace

**# Bookmark #35: Victimization - Malware Characterization

use "chile_2024_safety.dta", clear

local survey_cols virus_dano virus_pago virus_dinero virus_denuncia virus_satisf_den virus_accion_policial virus_contacto_mp virus_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_victimization_malwarecharacterization.csv", replace

**# Bookmark #36: Victimization - Cyberbullying Characterization

use "chile_2024_safety.dta", clear

local survey_cols bully_identidad bully_odio bully_denuncia bully_satisf_den bully_accion_policial bully_contacto_mp bully_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 86, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_cyberbullyingcharacterization.csv", replace

**# Bookmark #37: Victimization - Identity Theft Characterization

use "chile_2024_safety.dta", clear

local survey_cols suplant_dinero suplant_denuncia suplant_satisf_den suplant_accion_policial suplant_contacto_mp suplant_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_identitytheftcharacterization.csv", replace

**# Bookmark #38: Victimization - Sexual Harassment Characterization

use "chile_2024_safety.dta", clear

local survey_cols acoso_conoce_resp acoso_denuncia acoso_satisf_den acoso_denuncia_firma

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_harassmentcharacterization.csv", replace

**# Bookmark #39: Services - Municipal Evaluation

use "chile_2024_safety.dta", clear

local survey_cols eval_acude eval_patrullaje eval_barrios eval_acciones eval_mediacion

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 96, 86, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_municipal.csv", replace

**# Bookmark #40: Services - Carabineros Evaluation

use "chile_2024_safety.dta", clear

local survey_cols eval_carab_comuna_1 eval_carab_comuna_2 eval_carab_comuna_3 eval_carab_comuna_4 eval_carab_comuna_5 eval_carab_comuna_6 presencia_carabineros

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_carabineros.csv", replace

**# Bookmark #41: Services - Knowledge and Use of Programs

use "chile_2024_safety.dta", clear

local survey_cols conoce_ds utilizo_ds conoce_pav_1 usaria_pav_1

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_programs.csv", replace

**# Bookmark #42: Context

use "chile_2024_safety.dta", clear

local survey_cols p_acciones_vecinos_1 p_acciones_vecinos_2 p_acciones_vecinos_3 p_acciones_vecinos_4 p_acciones_vecinos_5

keep id cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_sex cov_age cov_education `var'
    gen item = "`var'"
    rename `var' resp
    replace resp = "" if resp == "NA"
    destring resp, replace force
    replace resp = . if inlist(resp, 85, 88, 86, 96, 99)
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop if missing(item) | item == ""

keep id cov_* item resp

sort id item

export delimited using "chile_2024_safety_context.csv", replace