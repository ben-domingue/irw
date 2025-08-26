*** This Do File creates tables from the Chile children and adolescents 2023 survey ***

* clear
clear

* import the main dataset and convert to csv
use "Base de datos EANNA 2023.dta", clear
export delimited "chile_children-adolescents-survey.csv", replace

* drop unnecessary variables
drop folio id_hogar id_persona region area expr varunit estrato check_hogar_casen check_nuevos int_nuevo f1	f10	f10_quien	f2a	f2a_esp	f2b	f2b_esp	f3	f3_esp	f4	f5	f6a_asiste	f6a_no_asiste	f6b_asiste	f6b_no_asiste	f6d_preg	f7	f8	f9	f9_esp	f9_esp_cod	pco1	pco1_a	pco1_b	pco1_nna	pco1_nna	th1	th1_quien	th2_1	th2_1_tiempo	th2_10	th2_10_tiempo	th2_11	th2_11_tiempo	th2_12	th2_12_tiempo	th2_2	th2_2_tiempo	th2_3	th2_3_tiempo	th2_4	th2_4_tiempo	th2_5	th2_5_tiempo	th2_6	th2_6_tiempo	th2_7	th2_7_tiempo	th2_77	th2_77_esp	th2_77_esp_cod	th2_77_tiempo	th2_8	th2_8_tiempo	th2_9	th2_9_tiempo	th3_1	th3_1_tiempo	th3_10	th3_10_tiempo	th3_11	th3_11_tiempo	th3_12	th3_12_tiempo	th3_2	th3_2_tiempo	th3_3	th3_3_tiempo	th3_4	th3_4_tiempo	th3_5	th3_5_tiempo	th3_6	th3_6_tiempo	th3_7	th3_7_tiempo	th3_77	th3_77_esp	th3_77_esp_cod	th3_77_tiempo	th3_8	th3_8_tiempo	th3_9	th3_9_tiempo	th4	th4_esp	th4_esp_cod	th5	th5_esp	th5_esp_cod	th6_1	th6_2	th6_3	th6_4	th6_5	th6_6	th7	th7_tiempo	th8	th8_tiempo	w1	w10_tiempo	w11	w11_esp	w2	w3	w4_1	w4_2	w4_3	w4_4	w4_5	w4_6	w4_7	w4_77	w4_8	w4_esp	w5	w6	w7	w8	w8_esp	w8_esp_cod	w9_tiempo ac7 

* drop casen covariates to reduce processing time
drop e6a_casen	activ_casen	allega_ext_casen	allega_int_casen	dau_casen	depen_casen	disc_wg_casen	e6b_casen	hh_d_acc_casen	hh_d_accesi_casen	hh_d_act_casen	hh_d_appart_casen	hh_d_asis_casen	hh_d_cot_casen	hh_d_entorno_casen	hh_d_equipo_casen	hh_d_esc_casen	hh_d_estado_casen	hh_d_habitab_casen	hh_d_hacina_casen	hh_d_hapoyo_casen	hh_d_jub_casen	hh_d_mal_casen	hh_d_medio_casen	hh_d_part_casen	hh_d_prevs_casen	hh_d_rez_casen	hh_d_seg_casen	hh_d_servbas_casen	hh_d_tiempo_casen	hh_d_tsocial_casen	ind_hacina_casen	indsan_casen	lugar_nac_casen	pobreza_casen	pobreza_multi_4d_casen	pobreza_multi_5d_casen	pueblos_indigenas_casen	qaut_casen	r17a_casen	r17b_casen	r17c_casen	r17d_casen	r17e_casen	r8a_casen	r8b_casen	r8c_casen	r8d_casen	r8e_casen	r8f_casen	r8g_casen	r8h_casen	s13_casen	s6_casen	ten_viv_casen	ten_viv_f_casen	tot_hog_casen	v1_casen	v2_casen	v4_casen	v6_casen	yaimh_casen	yautcorh_casen	yauth_casen	ymonecorh_casen	ypch_casen	ypchautcor_casen	ypchtrabcor_casen	ysubh_casen	ytoth_casen	ytrabajocorh_casen

* renames covariates
rename sexo_eanna cov_gender
rename edad_tramos cov_age_range

* encode any needed covariates
decode cov_age_range, generate(cov_age_range_str)
drop cov_age_range
rename cov_age_range_str cov_age_range

* drop children under the age of 4
drop if cov_age_range == "0 - 4 años"

* implement aggressive recoding to NA for -88, -99, -89, -98, 87, 77 values
mvdecode _all, mv(-88)
mvdecode _all, mv(-99)
mvdecode _all, mv(-89)
mvdecode _all, mv(-98)
mvdecode _all, mv(87)
mvdecode _all, mv(77)

* implement aggressive recoding to NA for -88, -99, -89, -98, 87, and 77 values that are string
ds, has(type string)
foreach var of varlist `r(varlist)' {
    replace `var' = "" if inlist(`var', "-88", "-89", "-99", "-98", "87", "77")
}

* reorder variables
order cov*, first

* save claned dataset for easy recall for each subsection
save "chile_2023_children-adolescents-survey.csv", replace

***************************************
***************************************
******** Cuidador(a) Principal ********
***************************************
***************************************

* recall main dataset
use "chile_2023_children-adolescents-survey.csv", clear

* drop observations not in this questionnaire
keep if rp2 == 1

* keep only the relevant variables of this section
keep cov_gender cov_age_range ac1_1	ac1_2	ac1_3	ac1_4	ac1_5	ac1_6	ac1_7	ac1_8	ac1_8_esp	ac2_1	ac2_2	ac2_3	ac2_4	ac2_5	ac3	ac5_1	ac5_10	ac5_2	ac5_3	ac5_4	ac5_5	ac5_6	ac5_7	ac5_77	ac5_77_esp	ac5_77_esp_cod	ac5_8	ac5_9	ac6_1	ac6_2	ac6_3	ac6_4	ac6_77	ac6_77_esp	ac6_77_esp_cod cp2_1	cp2_10	cp2_2	cp2_3	cp2_4	cp2_5	cp2_6	cp2_7	cp2_77	cp2_8	cp2_9	cp3	cp4	cp5_1	cp5_2	cp5_3	cp5_4	cp5_5	cp5_6	cp5_7	cp6_1	cp6_2	cp6_3	cp6_4	cp6_5	cp6_6	cp6_7	cp6_8	cp7_1	cp7_2	cp7_3	cp7_4	cp8_1	cp8_2	cp8_3	cp8_4	cp8_5	cp8_6	cp9_1	cp9_2	cp9_3	cp9_4 cp1 n14

* drop additional text-based answers
drop ac1_8_esp ac6_77_esp ac6_77_esp_cod ac5_77_esp ac5_77_esp_cod n14

* format time indicators correctly
gen cp7_1_num = real(substr(cp7_1,1,strpos(cp7_1,":")-1)) + real(substr(cp7_1,strpos(cp7_1,":")+1,.))/60

gen cp7_2_num = real(substr(cp7_2,1,strpos(cp7_2,":")-1)) + real(substr(cp7_2,strpos(cp7_2,":")+1,.))/60

gen cp7_3_num = real(substr(cp7_3,1,strpos(cp7_3,":")-1)) + real(substr(cp7_3,strpos(cp7_3,":")+1,.))/60

gen cp7_4_num = real(substr(cp7_4,1,strpos(cp7_4,":")-1)) + real(substr(cp7_4,strpos(cp7_4,":")+1,.))/60

gen cp9_1_num = real(substr(cp9_1,1,strpos(cp9_1,":")-1)) + real(substr(cp9_1,strpos(cp9_1,":")+1,.))/60

gen cp9_2_num = real(substr(cp9_2,1,strpos(cp9_2,":")-1)) + real(substr(cp9_2,strpos(cp9_2,":")+1,.))/60

gen cp9_3_num = real(substr(cp9_3,1,strpos(cp9_3,":")-1)) + real(substr(cp9_3,strpos(cp9_3,":")+1,.))/60

gen cp9_4_num = real(substr(cp9_4,1,strpos(cp9_4,":")-1)) + real(substr(cp9_4,strpos(cp9_4,":")+1,.))/60

* drop original time indicators to avoid duplicates
drop cp7_1 cp7_2 cp7_3 cp7_4 cp9_1 cp9_2 cp9_3 cp9_4

* rename time indicators back to their original names
rename cp7_1_num cp7_1
rename cp7_2_num cp7_2
rename cp7_3_num cp7_3
rename cp7_4_num cp7_4
rename cp9_1_num cp9_1
rename cp9_2_num cp9_2
rename cp9_3_num cp9_3
rename cp9_4_num cp9_4

* adjust the decimal points of selected numeric variables to one decimal
replace cp7_1 = round(cp7_1, 0.1)
replace cp7_2 = round(cp7_2, 0.1)
replace cp7_3 = round(cp7_3, 0.1)
replace cp7_4 = round(cp7_4, 0.1)
replace cp9_1 = round(cp9_1, 0.1)
replace cp9_2 = round(cp9_2, 0.1)
replace cp9_3 = round(cp9_3, 0.1)
replace cp9_4 = round(cp9_4, 0.1)

* adjust to the preferred format
format cp7_1 %9.1f
format cp7_2 %9.1f
format cp7_3 %9.1f
format cp7_4 %9.1f
format cp9_1 %9.1f
format cp9_2 %9.1f
format cp9_3 %9.1f
format cp9_4 %9.1f

foreach var in cp7_1 cp7_2 cp7_3 cp7_4 cp9_1 cp9_2 cp9_3 cp9_4 {
    gen str_`var' = string(round(`var',0.1), "%9.1f")
}

drop cp7_1 cp7_2 cp7_3 cp7_4 cp9_1 cp9_2 cp9_3 cp9_4

rename str_cp7_1 cp7_1
rename str_cp7_2 cp7_2
rename str_cp7_3 cp7_3
rename str_cp7_4 cp7_4
rename str_cp9_1 cp9_1
rename str_cp9_2 cp9_2
rename str_cp9_3 cp9_3
rename str_cp9_4 cp9_4

* rename other germane variables
rename cp1 cov_age_first_job

* adds id
gen id = _n

* reorder variables
order id cov*, first

* create long-format data from wide data
local question_cols	ac1_1	ac1_2	ac1_3	ac1_4	ac1_5	ac1_6	ac1_7	ac1_8	ac2_1	ac2_2	ac2_3	ac2_4	ac2_5	ac3	ac5_1	ac5_10	ac5_2	ac5_3	ac5_4	ac5_5	ac5_6	ac5_7	ac5_77	ac5_8	ac5_9	ac6_1	ac6_2	ac6_3	ac6_4	ac6_77 cp2_1	cp2_10	cp2_2	cp2_3	cp2_4	cp2_5	cp2_6	cp2_7	cp2_77	cp2_8	cp2_9	cp3	cp4	cp5_1	cp5_2	cp5_3	cp5_4	cp5_5	cp5_6	cp5_7	cp6_1	cp6_2	cp6_3	cp6_4	cp6_5	cp6_6	cp6_7	cp6_8	cp7_1	cp7_2	cp7_3	cp7_4	cp8_1	cp8_2	cp8_3	cp8_4	cp8_5	cp8_6	cp9_1	cp9_2	cp9_3	cp9_4

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
	capture confirm string variable resp
    if !_rc {
        destring resp, replace force
    }
    order id item resp cov_*
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop ac1_1	ac1_2	ac1_3	ac1_4	ac1_5	ac1_6	ac1_7	ac1_8	ac2_1	ac2_2	ac2_3	ac2_4	ac2_5	ac3	ac5_1	ac5_10	ac5_2	ac5_3	ac5_4	ac5_5	ac5_6	ac5_7	ac5_77	ac5_8	ac5_9	ac6_1	ac6_2	ac6_3	ac6_4	ac6_77 cp2_1	cp2_10	cp2_2	cp2_3	cp2_4	cp2_5	cp2_6	cp2_7	cp2_77	cp2_8	cp2_9	cp3	cp4	cp5_1	cp5_2	cp5_3	cp5_4	cp5_5	cp5_6	cp5_7	cp6_1	cp6_2	cp6_3	cp6_4	cp6_5	cp6_6	cp6_7	cp6_8	cp7_1	cp7_2	cp7_3	cp7_4	cp8_1	cp8_2	cp8_3	cp8_4	cp8_5	cp8_6	cp9_1	cp9_2	cp9_3	cp9_4

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* creates subset of tables
local base_items a c 
foreach prefix of local base_items {
    preserve
        keep if strpos(item, "`prefix'") == 1
        export delimited using "chile_2023_children-adolescents-survey_cp_`prefix'.csv", replace
    restore
}

***************************************
***************************************
****** Niños y Niñas 5 a 8 años *******
***************************************
***************************************

* recall main dataset
use "chile_2023_children-adolescents-survey.csv", clear

* drop observations not in this questionnaire
drop if nna_selec == 0
drop if rp2 == 1
keep if inlist(cov_age_range, "5 años", "6 años", "7 años", "8 años")

* keep only the relevant variables of this section
keep cov_gender cov_age_range n1	n2	n3a	n3b	n4	n4_esp	n5	n6	n7_1	n7_2	n7_3	n7_4	n7_5	n7_77	n7_78	n7_87	n7_88	n7_99	n8_1	n8_2	n8_3	n8_4	n8_5	n8_77	n8_78	n8_87	n8_88	n8_99	n9	n10	n11_1	n11_1a	n11_1b	n11_2	n11_3	n11_4	n11_5	n11_6	n11_7	n11_8	n11_9	n11_10	n11_11	n11_12	n11_77	n11_77_esp	n11_77_esp_cod	n14	n14_esp	n15	n15_1_1	n15_1_2	n15_1_3	n15_1_4	n15_1_5	n15_1_6	n15_1_77	n15_1_88	n15_1_99	n15_1_esp	n16	n17_1	n17_2	n17_3	n17_3_destino	n17_3_pago	n17_4	n17_5	n17_6	n17_7	n17_7_destino	n17_7_pago	n17_8	n17_8_destino	n17_8_pago	n17_9	n17_9_destino	n17_9_pago	n17_10	n17_10_destino	n17_10_pago	n17_11	n17_11_destino	n17_11_pago	n17_12	n17_12_destino	n17_12_pago	n17_13	n17_77	n17_77_esp	n17_77_esp_cod	n17_77_destino	n17_77_pago	n19	n21	n21_cod	n22_1	n22_1_cod	n22_2_1	n22_2_2	n22_2_3	n22_2_4	n22_2_5	n22_2_6	n22_2_7	n22_2_8	n22_2_77	n24	n24_cod	n25a_1	n25a_2	n25a_3	n25a_4	n25a_5	n25a_6	n25a_7	n25a_8	n25_1a_1	n25_1a_2	n25_1a_3	n26_1	n26_2	n26_3	n26_88	n26_99	n27_1	n27_2	n27_3	n27_4	n27_5	n27_77	n27_78	n27_88	n27_99	n28	n29	n30	n30_esp	n31	n32_1	n32_2	n32_3	n32_4	n32_5	n32_77	n32_78	n32_87	n32_88	n32_99	n35	n35_1_1	n35_1_2	n35_1_3	n35_1_4	n35_1_5	n35_1_6	n35_1_77	n35_1_88	n35_1_99	n35_1_esp	n36_1	n36_2	n36_3	n36_4	n36_5	n36_6	n36_77	n36_78	n36_88	n36_99	n36_esp	n37_1	n37_2	n37_3	n37_4	n37_5	n37_6	n37_77	n37_78	n37_88	n37_99	n37_esp	n38_1	n38_2	n38_3	n38_4	n38_5	n38_77	n38_78	n38_88	n38_99	n38_esp	n38_esp_cod	n39_1	n39_2	n39_3	n39_4	n39_5	n39_6	n39_7	n39_8	n39_9	n39_10	n39_11	n39_12	n39_78	n39_88	n39_99

* drop additional text-based answers or unnecessary variables (such as with very few responses at all)
drop n1 n11_77_esp n11_77_esp_cod n14_esp n15_1_esp n2 n3a n3b n4 n4_esp n17_1	n17_1	n17_2	n17_2	n17_3	n17_3	n17_3_destino	n17_3_destino	n17_3_destino	n17_3_destino	n17_3_pago	n17_3_pago	n17_3_pago	n17_3_pago	n17_4	n17_4	n17_5	n17_5	n17_6	n17_6	n17_7	n17_7	n17_7_destino	n17_7_destino	n17_7_destino	n17_7_destino	n17_7_pago	n17_7_pago	n17_7_pago	n17_7_pago	n17_8	n17_8	n17_8_destino	n17_8_destino	n17_8_destino	n17_8_destino	n17_8_pago	n17_8_pago	n17_8_pago	n17_8_pago	n17_9	n17_9	n17_9_destino	n17_9_destino	n17_9_destino	n17_9_destino	n17_9_pago	n17_9_pago	n17_9_pago	n17_9_pago	n17_10	n17_10	n17_10_destino	n17_10_destino	n17_10_destino	n17_10_destino	n17_10_pago	n17_10_pago	n17_10_pago	n17_10_pago	n17_11	n17_11	n17_11_destino	n17_11_destino	n17_11_destino	n17_11_destino	n17_11_pago	n17_11_pago	n17_11_pago	n17_11_pago	n17_12	n17_12	n17_12_destino	n17_12_destino	n17_12_destino	n17_12_destino	n17_12_pago	n17_12_pago	n17_12_pago	n17_12_pago	n17_13	n17_13	n17_77	n17_77	n17_77_esp	n17_77_esp	n17_77_esp_cod	n17_77_esp_cod	n17_77_esp_cod	n17_77_esp_cod	n17_77_destino	n17_77_destino	n17_77_destino	n17_77_destino	n17_77_pago	n17_77_pago	n17_77_pago	n17_77_pago	n19	n19	n19	n19	n19	n19	n19	n19	n19	n19	n19	n19	n19	n19	n21	n21_cod	n21_cod	n21_cod	n21_cod	n21_cod	n21_cod	n21_cod	n21_cod	n22_1	n22_1_cod	n22_1_cod	n22_1_cod	n22_1_cod	n22_1_cod	n22_1_cod	n22_1_cod	n22_1_cod	n22_2_1	n22_2_1	n22_2_2	n22_2_2	n22_2_3	n22_2_3	n22_2_4	n22_2_4	n22_2_5	n22_2_5	n22_2_6	n22_2_6	n22_2_7	n22_2_7	n22_2_8	n22_2_8	n22_2_77	n22_2_77	n24	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n24_cod	n25a_1	n25a_1	n25a_1	n25a_2	n25a_2	n25a_2	n25a_3	n25a_3	n25a_3	n25a_4	n25a_4	n25a_4	n25a_5	n25a_5	n25a_5	n25a_6	n25a_6	n25a_6	n25a_7	n25a_7	n25a_7	n25a_8	n25a_8	n25a_8	n25_1a_1	n25_1a_1	n25_1a_2	n25_1a_2	n25_1a_3	n25_1a_3	n26_1	n26_1	n26_2	n26_2	n26_3	n26_3	n26_88	n26_88	n26_99	n26_99	n27_1	n27_1	n27_2	n27_2	n27_3	n27_3	n27_4	n27_4	n27_5	n27_5	n27_77	n27_77	n27_78	n27_78	n27_88	n27_88	n27_99	n27_99	n28	n28	n28	n28	n29	n29	n29	n29	n29	n29	n30	n30	n30	n30	n30	n30	n30	n30	n30	n30	n30	n30_esp	n31	n31	n31	n31	n31	n31	n31	n32_1	n32_1	n32_2	n32_2	n32_3	n32_3	n32_4	n32_4	n32_5	n32_5	n32_77	n32_77	n32_78	n32_78	n32_87	n32_87	n32_88	n32_88	n32_99	n32_99	n35	n35	n35	n35	n35_1_1	n35_1_1	n35_1_2	n35_1_2	n35_1_3	n35_1_3	n35_1_4	n35_1_4	n35_1_5	n35_1_5	n35_1_6	n35_1_6	n35_1_77	n35_1_77	n35_1_88	n35_1_88	n35_1_99	n35_1_99	n35_1_esp	n36_1	n36_1	n36_2	n36_2	n36_3	n36_3	n36_4	n36_4	n36_5	n36_5	n36_6	n36_6	n36_77	n36_77	n36_78	n36_78	n36_88	n36_88	n36_99	n36_99	n36_esp	n37_1	n37_1	n37_2	n37_2	n37_3	n37_3	n37_4	n37_4	n37_5	n37_5	n37_6	n37_6	n37_77	n37_77	n37_78	n37_78	n37_88	n37_88	n37_99	n37_99	n37_esp	n38_1	n38_1	n38_2	n38_2	n38_3	n38_3	n38_4	n38_4	n38_5	n38_5	n38_77	n38_77	n38_78	n38_78	n38_88	n38_88	n38_99	n38_99	n38_esp	n38_esp_cod	n38_esp_cod	n39_1	n39_1	n39_2	n39_2	n39_3	n39_3	n39_4	n39_4	n39_5	n39_5	n39_6	n39_6	n39_7	n39_7	n39_8	n39_8	n39_9	n39_9	n39_10	n39_10	n39_11	n39_11	n39_12	n39_12	n39_78	n39_78	n39_88	n39_88	n39_99	n39_99 n14

* drop additional subquestion variables
drop n15_1_1 n15_1_2 n15_1_3 n15_1_4 n15_1_5 n15_1_6 n15_1_77 n15_1_88 n15_1_99

* adds id
gen id = _n

* reorder variables
order id cov*, first

* create long-format data from wide data
local question_cols n5 n6 n7_1 n7_2 n7_3 n7_4 n7_5 n7_77 n7_78 n7_87 n7_88 n7_99 n8_1 n8_2 n8_3 n8_4 n8_5 n8_77 n8_78 n8_87 n8_88 n8_99 n9 n10 n11_1 n11_1a n11_1b n11_2 n11_3 n11_4 n11_5 n11_6 n11_7 n11_8 n11_9 n11_10 n11_11 n11_12 n11_77 n15 n16

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop n5 n6 n7_1 n7_2 n7_3 n7_4 n7_5 n7_77 n7_78 n7_87 n7_88 n7_99 n8_1 n8_2 n8_3 n8_4 n8_5 n8_77 n8_78 n8_87 n8_88 n8_99 n9 n10 n11_1 n11_1a n11_1b n11_2 n11_3 n11_4 n11_5 n11_6 n11_7 n11_8 n11_9 n11_10 n11_11 n11_12 n11_77 n15 n16

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* export file
export delimited using "chile_2023_children-adolescents-survey_n.csv", replace

***************************************
***************************************
***** Niños y Niñas 9 a 17 años *******
***************************************
***************************************

* recall main dataset
use "chile_2023_children-adolescents-survey.csv", clear

* drop observations not in this questionnaire
drop if nna_selec == 0
drop if rp2 == 1
drop if inlist(cov_age_range, "5 años", "6 años", "7 años", "8 años")
drop if inlist(cov_age_range, "18 - 29 años", "30 - 44 años", "45 - 59 años", "60 o más años")

* keep only the relevant variables of this section
keep cov_gender cov_age_range a1a	a1b	a2	a2_esp	a3	a4	a4_esp	a4_esp_cod	a5_1	a5_2	a5_3	a6	a8_1	a8_2	a8_3	a8_4	a8_5	a8_6	a8_77	a8_78	a8_87	a8_88	a8_99	a9_1	a9_2	a9_3	a9_4	a9_5	a9_6	a9_77	a9_78	a9_87	a9_88	a9_99	a10	a11_1	a11_2	a11_3	a11_4	a11_5	a11_6	a11_77	a11_88	a11_99	a11_77_esp	a11_77_esp_cod	a12	a13	a14_1	a14_1_dias	a14_1_tiempo	a14_1_destino	a14_1_pago	a14_1a	a14_1b	a14_2	a14_2_dias	a14_2_tiempo	a14_3	a14_3_dias	a14_3_tiempo	a14_4	a14_4_dias	a14_4_tiempo	a14_5	a14_5_dias	a14_5_tiempo	a14_5_destino	a14_5_pago	a14_6	a14_6_dias	a14_6_tiempo	a14_6_destino	a14_6_pago	a14_7	a14_7_dias	a14_7_tiempo	a14_7_destino	a14_7_pago	a14_8	a14_8_dias	a14_8_tiempo	a14_9	a14_9_dias	a14_9_tiempo	a14_10	a14_10_dias	a14_10_tiempo	a14_11	a14_11_dias	a14_11_tiempo	a14_11_destino	a14_11_pago	a14_12	a14_12_dias	a14_12_tiempo	a14_12_destino	a14_12_pago	a14_77	a14_77_esp	a14_77_esp_cod	a14_77_dias	a14_77_tiempo	a14_77_destino	a14_77_pago	a15_1	a15_2	a15_3	a17	a17_esp	a18	a18_1_1	a18_1_2	a18_1_3	a18_1_4	a18_1_5	a18_1_6	a18_1_7	a18_1_8	a18_1_9	a18_1_10	a18_1_11	a18_1_12	a18_1_13	a18_1_77	a18_1_88	a18_1_99	a18_1_esp	a19	a20	a25_1	a25_2	a26_1	a26_2	a27_1	a27_2	a27_3	a27_3_destino	a27_3_pago	a27_4	a27_5	a27_6	a27_7	a27_7_destino	a27_7_pago	a27_8	a27_8_destino	a27_8_pago	a27_9	a27_9_destino	a27_9_pago	a27_10	a27_10_destino	a27_10_pago	a27_11	a27_11_destino	a27_11_pago	a27_12	a27_12_destino	a27_12_pago	a27_13	a27_77	a27_77_esp	a27_77_esp_cod	a27_77_destino	a27_77_pago	a28	a28_1_1	a28_1_2	a28_1_3	a28_1_4	a28_1_5	a28_1_6	a28_1_7	a28_1_8	a28_1_9	a28_1_10	a28_1_11	a28_1_12	a28_1_13	a28_1_77	a28_1_esp	a28_1_esp_cod	a29a	a29b	a30	a30_cod	a31	a31_cod	a32_1	a32_2	a32_3	a32_4	a32_5	a32_6	a32_7	a32_8	a32_77	a32_esp	a34	a34_cod	a35a_1	a35a_2	a35a_3	a35a_4	a35a_5	a35a_6	a35a_7	a35a_8	a35b_1	a35b_2	a35b_3	a35b_4	a35b_5	a35b_6	a35b_7	a35b_8	a36	a37	a38	a39	a40	a41	a42	a43a_1	a43a_2	a43a_3	a43b_1	a43b_2	a43b_3	a44a_1	a44a_2	a44a_3	a44b_1	a44b_2	a44b_3	a45_1	a45_2	a45_3	a45_88	a45_99	a48	a48_esp	a49_1	a49_2	a49_3	a49_4	a49_5	a49_77	a49_78	a49_88	a49_99	a50	a51	a52	a52_esp	a53_1_1	a53_1_2	a53_1_3	a53_1_4	a53_1_5	a53_1_6	a53_1_77	a53_1_78	a53_1_88	a53_1_99	a53_1_esp	a53_2_1	a53_2_2	a53_2_3	a53_2_4	a53_2_5	a53_2_6	a53_2_77	a53_2_78	a53_2_88	a53_2_99	a53_2_esp	a53_3	a54_1	a54_2	a54_3	a54_4	a54_5	a54_6	a54_77	a54_78	a54_87	a54_88	a54_99	a56	a57	a58	a59	a60_1	a60_2	a60_3	a60_4	a61_1	a61_2	a61_4	a61_5	a62_1	a62_2	a62_3	a62_4	a62_5	a62_7	a62_8	a62_9	a63	a63_1_1	a63_1_2	a63_1_3	a63_1_4	a63_1_5	a63_1_6	a63_1_7	a63_1_8	a63_1_9	a63_1_10	a63_1_11	a63_1_12	a63_1_13	a63_1_77	a63_1_88	a63_1_99	a64	a65	a66	a67_1	a67_2	a68	a70	a70_esp	a71	a72	a80_1	a80_2	a80_3	a80_4	a80_5	a80_77	a80_78	a80_88	a80_99	a80_esp	a80_esp_cod	a81_1	a81_2	a81_3	a81_4	a81_5	a81_6	a81_7	a81_8	a81_9	a81_10	a81_11	a81_12	a81_78	a81_88	a81_99 

* drop additional text-based answers or unnecessary variables (such as with very few responses at all)
drop a1a a1b	a2	a2_esp a4_esp a4_esp_cod a11_77_esp a11_77_esp_cod a14_1	a14_1_dias	a14_1_tiempo	a14_1_destino	a14_1_pago	a14_1a	a14_1b	a14_2	a14_2_dias	a14_2_tiempo	a14_3	a14_3_dias	a14_3_tiempo	a14_4	a14_4_dias	a14_4_tiempo	a14_5	a14_5_dias	a14_5_tiempo	a14_5_destino	a14_5_pago	a14_6	a14_6_dias	a14_6_tiempo	a14_6_destino	a14_6_pago	a14_7	a14_7_dias	a14_7_tiempo	a14_7_destino	a14_7_pago	a14_8	a14_8_dias	a14_8_tiempo	a14_9	a14_9_dias	a14_9_tiempo	a14_10	a14_10_dias	a14_10_tiempo	a14_11	a14_11_dias	a14_11_tiempo	a14_11_destino	a14_11_pago	a14_12	a14_12_dias	a14_12_tiempo	a14_12_destino	a14_12_pago	a14_77	a14_77_esp	a14_77_esp_cod	a14_77_dias	a14_77_tiempo	a14_77_destino	a14_77_pago	a15_1	a15_2	a15_3	a17	a17_esp	a18	a18_1_1	a18_1_2	a18_1_3	a18_1_4	a18_1_5	a18_1_6	a18_1_7	a18_1_8	a18_1_9	a18_1_10	a18_1_11	a18_1_12	a18_1_13	a18_1_77	a18_1_88	a18_1_99	a18_1_esp	a19	a20	a25_1	a25_2	a26_1	a26_2	a27_1	a27_2	a27_3	a27_3_destino	a27_3_pago	a27_4	a27_5	a27_6	a27_7	a27_7_destino	a27_7_pago	a27_8	a27_8_destino	a27_8_pago	a27_9	a27_9_destino	a27_9_pago	a27_10	a27_10_destino	a27_10_pago	a27_11	a27_11_destino	a27_11_pago	a27_12	a27_12_destino	a27_12_pago	a27_13	a27_77	a27_77_esp	a27_77_esp_cod	a27_77_destino	a27_77_pago	a28	a28_1_1	a28_1_2	a28_1_3	a28_1_4	a28_1_5	a28_1_6	a28_1_7	a28_1_8	a28_1_9	a28_1_10	a28_1_11	a28_1_12	a28_1_13	a28_1_77	a28_1_esp	a28_1_esp_cod	a29a	a29b	a30	a30_cod	a31	a31_cod	a32_1	a32_2	a32_3	a32_4	a32_5	a32_6	a32_7	a32_8	a32_77	a32_esp	a34	a34_cod	a35a_1	a35a_2	a35a_3	a35a_4	a35a_5	a35a_6	a35a_7	a35a_8	a35b_1	a35b_2	a35b_3	a35b_4	a35b_5	a35b_6	a35b_7	a35b_8	a36	a37	a38	a39	a40	a41	a42	a43a_1	a43a_2	a43a_3	a43b_1	a43b_2	a43b_3	a44a_1	a44a_2	a44a_3	a44b_1	a44b_2	a44b_3	a45_1	a45_2	a45_3	a45_88	a45_99	a48	a48_esp	a49_1	a49_2	a49_3	a49_4	a49_5	a49_77	a49_78	a49_88	a49_99	a50	a51	a52	a52_esp	a53_1_1	a53_1_2	a53_1_3	a53_1_4	a53_1_5	a53_1_6	a53_1_77	a53_1_78	a53_1_88	a53_1_99	a53_1_esp	a53_2_1	a53_2_2	a53_2_3	a53_2_4	a53_2_5	a53_2_6	a53_2_77	a53_2_78	a53_2_88	a53_2_99	a53_2_esp	a53_3	a54_1	a54_2	a54_3	a54_4	a54_5	a54_6	a54_77	a54_78	a54_87	a54_88	a54_99	a56	a57	a58	a59	a60_1	a60_2	a60_3	a60_4	a61_1	a61_2	a61_4	a61_5	a62_1	a62_2	a62_3	a62_4	a62_5	a62_7	a62_8	a62_9	a63	a63_1_1	a63_1_2	a63_1_3	a63_1_4	a63_1_5	a63_1_6	a63_1_7	a63_1_8	a63_1_9	a63_1_10	a63_1_11	a63_1_12	a63_1_13	a63_1_77	a63_1_88	a63_1_99	a64	a65	a66	a67_1	a67_2	a68	a70	a70_esp	a71	a72	a80_1	a80_2	a80_3	a80_4	a80_5	a80_77	a80_78	a80_88	a80_99	a80_esp	a80_esp_cod	a81_1	a81_2	a81_3	a81_4	a81_5	a81_6	a81_7	a81_8	a81_9	a81_10	a81_11	a81_12	a81_78	a81_88	a81_99 a4 a13

* adds id
gen id = _n

* reorder variables
order id cov*, first

* create long-format data from wide data
local question_cols a3 a5_1 a5_2 a5_3 a6 a8_1 a8_2 a8_3 a8_4 a8_5 a8_6 a8_77 a8_78 a8_87 a8_88 a8_99 a9_1 a9_2 a9_3 a9_4 a9_5 a9_6 a9_77 a9_78 a9_87 a9_88 a9_99 a10 a11_1 a11_2 a11_3 a11_4 a11_5 a11_6 a11_77 a11_88 a11_99 a12

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop a3 a5_1 a5_2 a5_3 a6 a8_1 a8_2 a8_3 a8_4 a8_5 a8_6 a8_77 a8_78 a8_87 a8_88 a8_99 a9_1 a9_2 a9_3 a9_4 a9_5 a9_6 a9_77 a9_78 a9_87 a9_88 a9_99 a10 a11_1 a11_2 a11_3 a11_4 a11_5 a11_6 a11_77 a11_88 a11_99 a12

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* export file
export delimited using "chile_2023_children-adolescents-survey_aa.csv", replace

***************************************
***************************************
**** Niños y Niñas 9 a 17 años Auto ***
***************************************
***************************************

* recall main dataset
use "chile_2023_children-adolescents-survey.csv", clear

* drop observations not in this questionnaire
keep if responde_autoaplicado == 1

* keep only the relevant variables of this section
keep cov_gender cov_age_range k1	k2	k3	k4	k5	k6	k7	k8	k9	k10	k11	k12	k13	k14	k15	k16	k17	k18	k19	k20	k21	k22	k23	k24	k25	k26	k27	k28	g1_1	g1_2	g1_3	g1_4	g1_5	g1_6	g1_7	g1_8

* adds id
gen id = _n

* reorder variables
order id cov*, first

* create long-format data from wide data
local question_cols k1	k2	k3	k4	k5	k6	k7	k8	k9	k10	k11	k12	k13	k14	k15	k16	k17	k18	k19	k20	k21	k22	k23	k24	k25	k26	k27	k28	g1_1	g1_2	g1_3	g1_4	g1_5	g1_6	g1_7	g1_8

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop k1	k2	k3	k4	k5	k6	k7	k8	k9	k10	k11	k12	k13	k14	k15	k16	k17	k18	k19	k20	k21	k22	k23	k24	k25	k26	k27	k28	g1_1	g1_2	g1_3	g1_4	g1_5	g1_6	g1_7	g1_8

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* creates subset of tables
local base_items k g
foreach prefix of local base_items {
    preserve
        keep if strpos(item, "`prefix'") == 1
        export delimited using "chile_2023_children-adolescents-survey_`prefix'.csv", replace
    restore
}