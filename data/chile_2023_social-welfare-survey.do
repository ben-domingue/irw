*** This Do File creates tables from the Chile social welfare 2023 survey ***

* clear
clear

* import the main dataset and convert to csv
use "Base de datos EBS 2023.dta", clear
export delimited "chile_social-welfare-survey.csv", replace

* drop covariates to reduce processing time
drop l1 sg01 l3_recat l7 l8 l9 l10 l10_a l11 glosa_region glosa_area os1_recat

* renames covariates
rename tramoebs2 cov_age_range
rename sg02 cov_gender

* configures the response time variable
generate double dt = clock(hora_hr, "YMDhm")
generate double unixtime = (dt - mdyhms(1,1,1970,0,0,0)) / 1000
drop hora_hr
drop dt
rename unixtime date

* drop unnecessary variables
drop l1_a sg03 l4 l5_recat l6 folio_et_enmascarado id_unico_viv_enmascarado id_persona id_hogar cdf_unificado fexp estrato_ebs varunit 

* drop single-item variable families
drop activ_ebs insatisfaccion affective_sw affective_sw_recod phq4 tdomestico tcuidados tnr carga_trab dia_uso_del_tiempo dia_semana_uso_del_tiempo

* drop casen covariates to reduce processing time
drop qaut_casen dau_casen pobreza_casen pobreza_multi_4d_casen pobreza_multi_5d_casen sexo_casen region_casen edad_casen_t ecivil_recat_casen numper_casen men6_casen men18c_casen may60c_casen ind_tip_casen ten_viv_casen ind_hacina_casen hh_d_hacina_casen hh_d_estado_casen hh_d_servbas_casen r17a_casen r17b_casen r17c_casen r17d_casen r17e_casen v34b_casen v36a_casen v36b_casen v36c_casen v36d_casen v36e_casen hh_d_seg_casen r6_casen hh_d_part_casen hh_d_appart_casen educ_recat_casen s13_casen h7a_casen h7b_casen h7c_casen h7d_casen h7e_casen h7f_casen disc_wg_casen s32a_casen hh_d_mal_casen activ_casen cat_ocup_casen contrato_casen o20_casen r1b_recat_casen r3_recat_casen tipohogar_casen

* fix cov_age variable to better match desired format in the output
decode cov_age_range, gen(cov_age_range_str)
drop cov_age_range
rename cov_age_range_str cov_age_range
replace cov_age_range = substr(cov_age_range, 4, .)

* fix cov_gender variable to better match desired format in the output
decode cov_gender, gen(cov_gender_str)
drop cov_gender
rename cov_gender_str cov_gender
replace cov_gender = "6. No Sabe" if cov_gender == "No sabe"
replace cov_gender = "7. Otro (especifique)" if cov_gender == "Otro (especifique)"
replace cov_gender = substr(cov_gender, 4, .)

* adds id
gen id = _n

* reorder variables
order id date cov*, first

* implement aggressive recoding to NA for -88, -99, and -89 values
mvdecode _all, mv(-88)
mvdecode _all, mv(-99)
mvdecode _all, mv(-89)

* save cleaned dataset
save "chile_social-welfare-survey.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #1: Group A

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "a" variables
keep id date cov_* a1 a2_a a2_b a2_c a2_d a3 a4 a5 a6 a7 a8 a9 a10 a11 a12

* create long-format data from wide data
local question_cols a1 a2_a a2_b a2_c a2_d a3 a4 a5 a6 a7 a8 a9 a10 a11 a12
tempfile long_a
save `long_a', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_a'
    save `long_a', replace
    restore
}

use `long_a', clear

drop a1 a2_a a2_b a2_c a2_d a3 a4 a5 a6 a7 a8 a9 a10 a11 a12

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "a"
export delimited using "chile_2023_social-welfare-survey_a.csv", replace

**# Bookmark #2: Group ee

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "ee" variables
keep id date cov_* ee1_a ee1_b ee1_c ee2 ee3 ee4 ee5

* create long-format data from wide data
local question_cols ee1_a ee1_b ee1_c ee2 ee3 ee4 ee5
tempfile long_ee
save `long_ee', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_ee'
    save `long_ee', replace
    restore
}

use `long_ee', clear

drop ee1_a ee1_b ee1_c ee2 ee3 ee4 ee5

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "ee"
export delimited using "chile_2023_social-welfare-survey_ee.csv", replace

**# Bookmark #3: Group oo

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "oo" variables
keep id date cov_* oo1 oo2 oo3_a oo3_b oo4 oo5 oo6 oo7_a1 oo7_a2 oo7_a3 oo7_a4 oo7_a5 oo7_a6 oo7_a7 oo8_a oo8_b oo8_c

* create long-format data from wide data
local question_cols oo1 oo2 oo3_a oo3_b oo4 oo5 oo6 oo7_a1 oo7_a2 oo7_a3 oo7_a4 oo7_a5 oo7_a6 oo7_a7 oo8_a oo8_b oo8_c
tempfile long_oo
save `long_oo', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_oo'
    save `long_oo', replace
    restore
}

use `long_oo', clear

drop oo1 oo2 oo3_a oo3_b oo4 oo5 oo6 oo7_a1 oo7_a2 oo7_a3 oo7_a4 oo7_a5 oo7_a6 oo7_a7 oo8_a oo8_b oo8_c

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "oo"
export delimited using "chile_2023_social-welfare-survey_oo.csv", replace

**# Bookmark #4: Group u

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "u" variables
keep id date cov_* u1 u1_a u2 u2_a u3 u3_a u4 u4_a u5 u5_a u6 u6_a u7 u7_a u8 u8_a u9 u9_a u10 u10_a u11 u11_a u12 u13 u14 u15 u15_a u16 u16_a u17 u17_a u18_a u18_b u18_c u19 u20 u21 u22

* create long-format data from wide data
local question_cols u1 u1_a u2 u2_a u3 u3_a u4 u4_a u5 u5_a u6 u6_a u7 u7_a u8 u8_a u9 u9_a u10 u10_a u11 u11_a u12 u13 u14 u15 u15_a u16 u16_a u17 u17_a u18_a u18_b u18_c u19 u20 u21 u22
tempfile long_u
save `long_u', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_u'
    save `long_u', replace
    restore
}

use `long_u', clear

drop u1 u1_a u2 u2_a u3 u3_a u4 u4_a u5 u5_a u6 u6_a u7 u7_a u8 u8_a u9 u9_a u10 u10_a u11 u11_a u12 u13 u14 u15 u15_a u16 u16_a u17 u17_a u18_a u18_b u18_c u19 u20 u21 u22

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "u"
export delimited using "chile_2023_social-welfare-survey_u.csv", replace

**# Bookmark #5: Group yy

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "yy" variables
keep id date cov_* yy1 yy2 yy3 yy4 yy5 yy5_a

* create long-format data from wide data
local question_cols yy1 yy2 yy3 yy4 yy5 yy5_a
tempfile long_yy
save `long_yy', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_yy'
    save `long_yy', replace
    restore
}

use `long_yy', clear

drop yy1 yy2 yy3 yy4 yy5 yy5_a

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "yy"
export delimited using "chile_2023_social-welfare-survey_yy.csv", replace

**# Bookmark #6: Group ss

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "ss" variables
keep id date cov_* ss1 ss2_a ss2_b ss2_c ss3 ss4 ss5 ss6 ss7_a ss7_b ss7_c ss7_d ss8

* create long-format data from wide data
local question_cols ss1 ss2_a ss2_b ss2_c ss3 ss4 ss5 ss6 ss7_a ss7_b ss7_c ss7_d ss8
tempfile long_ss
save `long_ss', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_ss'
    save `long_ss', replace
    restore
}

use `long_ss', clear

drop ss1 ss2_a ss2_b ss2_c ss3 ss4 ss5 ss6 ss7_a ss7_b ss7_c ss7_d ss8

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "ss"
export delimited using "chile_2023_social-welfare-survey_ss.csv", replace

**# Bookmark #7: Group vv

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "vv" variables
keep id date cov_* vv1_a vv1_b vv1_c vv2 vv3

* create long-format data from wide data
local question_cols vv1_a vv1_b vv1_c vv2 vv3
tempfile long_vv
save `long_vv', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_vv'
    save `long_vv', replace
    restore
}

use `long_vv', clear

drop vv1_a vv1_b vv1_c vv2 vv3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "vv"
export delimited using "chile_2023_social-welfare-survey_vv.csv", replace

**# Bookmark #8: Group g

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "g" variables
keep id date cov_* g1 g2 g3_a g3_b g3_c g3_d g3_e g3_f g4_a g4_b g4_c g4_d g4_e

* create long-format data from wide data
local question_cols g1 g2 g3_a g3_b g3_c g3_d g3_e g3_f g4_a g4_b g4_c g4_d g4_e
tempfile long_g
save `long_g', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_g'
    save `long_g', replace
    restore
}

use `long_g', clear

drop g1 g2 g3_a g3_b g3_c g3_d g3_e g3_f g4_a g4_b g4_c g4_d g4_e

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "g"
export delimited using "chile_2023_social-welfare-survey_g.csv", replace

**# Bookmark #9: Group h

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "h" variables
keep id date cov_* h1 h2_a h2_b h2_c h2_d h3_a h3_b h3_c h3_d h3_e h4_a h4_b h4_c

* create long-format data from wide data
local question_cols h1 h2_a h2_b h2_c h2_d h3_a h3_b h3_c h3_d h3_e h4_a h4_b h4_c
tempfile long_h
save `long_h', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_h'
    save `long_h', replace
    restore
}

use `long_h', clear

drop h1 h2_a h2_b h2_c h2_d h3_a h3_b h3_c h3_d h3_e h4_a h4_b h4_c

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "h"
export delimited using "chile_2023_social-welfare-survey_h.csv", replace

**# Bookmark #10: Group rr

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "rr" variables
keep id date cov_* rr1 rr2_a rr2_b rr2_c rr2_d rr2_e rr3 rr4_a rr4_b rr4_c rr4_d rr5_a rr5_b rr5_c rr5_d rr5_e rr5_f rr5_g rr5_h rr6_a rr6_b rr6_c rr6_d rr6_e rr6_f rr6_g rr6_h rr6_i rr6_j rr6_k rr6_l rr6_m rr6_n

* create long-format data from wide data
local question_cols rr1 rr2_a rr2_b rr2_c rr2_d rr2_e rr3 rr4_a rr4_b rr4_c rr4_d rr5_a rr5_b rr5_c rr5_d rr5_e rr5_f rr5_g rr5_h rr6_a rr6_b rr6_c rr6_d rr6_e rr6_f rr6_g rr6_h rr6_i rr6_j rr6_k rr6_l rr6_m rr6_n
tempfile long_rr
save `long_rr', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_rr'
    save `long_rr', replace
    restore
}

use `long_rr', clear

drop rr1 rr2_a rr2_b rr2_c rr2_d rr2_e rr3 rr4_a rr4_b rr4_c rr4_d rr5_a rr5_b rr5_c rr5_d rr5_e rr5_f rr5_g rr5_h rr6_a rr6_b rr6_c rr6_d rr6_e rr6_f rr6_g rr6_h rr6_i rr6_j rr6_k rr6_l rr6_m rr6_n

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "rr"
export delimited using "chile_2023_social-welfare-survey_rr.csv", replace

**# Bookmark #11: Group f

* recall dataset
use "chile_social-welfare-survey.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, date, covariates, and "f" variables
keep id date cov_* f1 f2_a f2_b f2_c f2_d f2_e f2_f f3_a f3_b f3_c f3_d f3_e f3_f f4 f4_1 f4_2 f4_3 f4_4 f4_88 f4_99 f5_a f5_b f5_c f6

* create long-format data from wide data
local question_cols f1 f2_a f2_b f2_c f2_d f2_e f2_f f3_a f3_b f3_c f3_d f3_e f3_f f4 f4_1 f4_2 f4_3 f4_4 f4_88 f4_99 f5_a f5_b f5_c f6
tempfile long_f
save `long_f', emptyok replace

foreach var of local question_cols {
    preserve
    keep id date cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp date cov_*
    append using `long_f'
    save `long_f', replace
    restore
}

use `long_f', clear

drop f1 f2_a f2_b f2_c f2_d f2_e f2_f f3_a f3_b f3_c f3_d f3_e f3_f f4 f4_1 f4_2 f4_3 f4_4 f4_88 f4_99 f5_a f5_b f5_c f6

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp date cov*, first

* export the long-format table for group "f"
export delimited using "chile_2023_social-welfare-survey_f.csv", replace