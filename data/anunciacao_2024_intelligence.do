*** This Do File creates tables from the Psychometric properties of a brief non-verbal test of g factor intelligence study ***

******************************************
***********  Prepare the data ************
******************************************

* clear
clear

* import the main dataset
import delimited "R base - IQ test manuscript.csv", clear

* convert column names to lowercase
rename *, lower

* drop irrelevant covariates
drop v1 teste_reteste sexo_n exame_cnh motoristaprofissional categoria_cnh profissao escolarid_n particular sexo_n ano_aplicacao aplicador grupo_clinico medicacao age_interval age

* drop old id and generate new id
drop id_unique id
gen id = _n

* renames covariates
rename nome cov_name
rename idade cov_age
rename sexo cov_sex
rename cidadedenascimento cov_birthcity
rename escolaridade cov_education

* drop irrelevant point variables
drop figuras_pontos fig_1 fig_2 fig_3 fig_4 fig_5 fig_6 fig_7 fig_8 fig_9 fig_10 fig_11 fig_12 fig_13 fig_14 fig_15 fig_16 fig_17 fig_18 fig_19 fig_20 fig_21 fig_22 fig_23 fig_24 fig_25 fig_26 fig_27 fig_28

* drop any additional irrelevant variables
drop qi_teorico gun cnh pm primeira_habilitacao prof_driver

* keep only the newly defined relevant variables - makes part of the previously used drop commands redundant by nature
keep cov* id figuras*

* reorder variables
order id cov*, first

* save cleaned dataset
save "anunciacao_2024_intelligence.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: General Matrix of Intelligence (GMI) responses

* recall dataset
use "anunciacao_2024_intelligence.csv", clear

* set up the code for long-format data from wide data
local question_cols figuras1 figuras2 figuras3 figuras4 figuras5 figuras6 figuras7 figuras8 figuras9 figuras10 figuras11 figuras12 figuras13 figuras14 figuras15 figuras16 figuras17 figuras18 figuras19 figuras20 figuras21 figuras22 figuras23 figuras24 figuras25 figuras26 figuras27 figuras28

tempfile long_data
save `long_data', emptyok replace

* create long-format data from wide data
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

drop figuras1 figuras2 figuras3 figuras4 figuras5 figuras6 figuras7 figuras8 figuras9 figuras10 figuras11 figuras12 figuras13 figuras14 figuras15 figuras16 figuras17 figuras18 figuras19 figuras20 figuras21 figuras22 figuras23 figuras24 figuras25 figuras26 figuras27 figuras28

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "anunciacao_2024_intelligence_gmi.csv", replace