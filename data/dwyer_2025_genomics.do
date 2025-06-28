*** This Do File creates tables from the Psychometric properties of a culturally adapted Spanish version of the Attitudes Toward Genomics and Precision Medicine instrument study ***

* clear
clear

* import main dataset
import excel "dwyer_2025_genomics_originaldata.xls", firstrow
export delimited "dwyer_2025_genomics.csv", replace

* convert variables to lowercase
rename *, lower

* renames covariates
rename languagepref cov_language
rename gender cov_gender
rename age cov_age
rename ethnicity cov_ethnicity
rename race cov_race
rename education cov_education
rename liveinus cov_liveinus
rename income cov_income
rename job cov_job
rename healthstatus cov_healthstatus
rename popdensity cov_popdensity
rename healthlitsubj  cov_healthlitsubj 

* rename certain response variables for consistency
rename agpm_4_pb_r agpm_4_pb
rename agpm_36_ec_r agpm_36_ec
rename agpm_38_ec_r agpm_38_ec
rename agpm_25_gec_r agpm_25_gec
rename agpm_33_ec_r agpm_33_ec
rename agpm_41_ec_r agpm_41_ec
rename agpm_18_pc_r agpm_18_pc
rename agpm_26_gec_r agpm_26_gec

* drop unnecessary variables
drop consent be bf bg bh bi bj bk bl bm bn bo bp bq br bs bt bu bv bw bx by bz ca cb cc cd ce cf cg

* encodes needed variables
destring cov_age, generate(cov_age_int) force
drop cov_age
rename cov_age_int cov_age

* adds id
gen id = _n

* reorder variables
order id cov_language cov_gender cov_age cov_ethnicity cov_race cov_education cov_liveinus cov_income cov_income cov_healthstatus cov_popdensity cov_healthlitsubj cov_job, first

* save cleaned dataset
save "dwyer_2025_genomics.csv", replace

* creates long data from wide data
local question_cols agpm_1_os agpm_2_pb agpm_3_pb agpm_4_pb agpm_12_pb agpm_20_pc agpm_28_gec agpm_36_ec agpm_5_pb agpm_13_pc agpm_21_pc agpm_29_gec agpm_37_os agpm_6_pb agpm_14_sjc agpm_22_pc agpm_30_gec agpm_38_ec agpm_7_sjc agpm_15_pc agpm_23_pc agpm_31_gec agpm_39_pb agpm_8_sjc agpm_16_pc agpm_24_os agpm_32_os agpm_40_ec agpm_9_sjc agpm_17_os agpm_25_gec  agpm_33_ec  agpm_41_ec agpm_10_os agpm_18_pc agpm_26_gec agpm_34_ec agpm_42_ec agpm_11_pb agpm_19_pb agpm_27_gec agpm_35_ec agpm_43_ec

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop agpm_1_os agpm_2_pb agpm_3_pb agpm_4_pb agpm_12_pb agpm_20_pc agpm_28_gec agpm_36_ec agpm_5_pb agpm_13_pc agpm_21_pc agpm_29_gec agpm_37_os agpm_6_pb agpm_14_sjc agpm_22_pc agpm_30_gec agpm_38_ec agpm_7_sjc agpm_15_pc agpm_23_pc agpm_31_gec agpm_39_pb agpm_8_sjc agpm_16_pc agpm_24_os agpm_32_os agpm_40_ec agpm_9_sjc agpm_17_os agpm_25_gec  agpm_33_ec  agpm_41_ec agpm_10_os agpm_18_pc agpm_26_gec agpm_34_ec agpm_42_ec agpm_11_pb agpm_19_pb agpm_27_gec agpm_35_ec agpm_43_ec

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov_language cov_gender cov_age cov_ethnicity cov_race cov_education cov_liveinus cov_income cov_income cov_healthstatus cov_popdensity cov_healthlitsubj cov_job, first

* save cleaned dataset
save "dwyer_2025_genomics.csv", replace

* create subset of tables
local suffixes os pb pc ec gec sjc
foreach suffix of local suffixes {
    preserve
    keep if regexm(item, "_`suffix'$")
    export delimited using "dwyer_2025_genomics_`suffix'.csv", replace
    restore
}