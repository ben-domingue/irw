*** This Do File creates tables from the Cool People study ***

************************************************************************************
************************************************************************************
*********************************** Main dataset ***********************************
************************************************************************************
************************************************************************************

* clear
clear

* import the main dataset and convert to csv
import spss using "Data_main experiment_13 countries_July 2 2024.sav", clear

* convert column names to lowercase
rename *, lower

* extrapolate year value from original variable
gen year = year(dofc(recordeddate))

* round up age
gen age_ceil = ceil(age)
drop age
rename age_ceil age

* change format of country variable
decode country, generate(country_str)
drop country
rename country_str country

* rename covariates
rename country cov_country
rename human_development_index cov_hdi
rename national_individualism cov_individualism
rename national_powerdistance cov_powerdistance
rename year cov_year
rename gender cov_gender
rename age cov_age

* rename extra variables for consistency
rename collectivisim8_jpsp collectivism8_jpsp

* clean the age variable
replace cov_age = . if inlist(cov_age, 1986, 1990, 1996, 2000, 2001, 2002, 2003, 2004)

* delete minor observations
drop if finished == 0 | missing(finished)

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "pezzuti_2025_coolpeople_main.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #1: Trendy scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* q66_19 q66_20 q66_21 q66_22

* keep only country(ies)-specific observations
keep if cov_country == "USA"

* rename questions
rename q66_19 trendy1
rename q66_20 trendy2
rename q66_21 trendy3
rename q66_22 trendy4

* create long-format data from wide data
local question_cols trendy1 trendy2 trendy3 trendy4
tempfile long_trendy
save `long_trendy', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_trendy'
    save `long_trendy', replace
    restore
}

use `long_trendy', clear

drop trendy1 trendy2 trendy3 trendy4

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
export delimited using "pezzuti_2025_coolpeople_main_trendy_USA.csv", replace

**# Bookmark #2: Collectivism scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* collectivism1_jpsp collectivism2_jpsp collectivism3_jpsp collectivism4_jpsp collectivism5_jpsp collectivism6_jpsp collectivism7_jpsp collectivism8_jpsp

* keep only country(ies)-specific observations
keep if cov_country == "USA"

* create long-format data from wide data
local question_cols collectivism1_jpsp collectivism2_jpsp collectivism3_jpsp collectivism4_jpsp collectivism5_jpsp collectivism6_jpsp collectivism7_jpsp collectivism8_jpsp
tempfile long_collectivism
save `long_collectivism', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_collectivism'
    save `long_collectivism', replace
    restore
}

use `long_collectivism', clear

drop collectivism1_jpsp collectivism2_jpsp collectivism3_jpsp collectivism4_jpsp collectivism5_jpsp collectivism6_jpsp collectivism7_jpsp collectivism8_jpsp

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
export delimited using "pezzuti_2025_coolpeople_main_collectivism_USA.csv", replace

**# Bookmark #3: Individualism scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* individualism*

* keep only country(ies)-specific observations
keep if cov_country == "USA"

* create long-format data from wide data
local question_cols individualism1_jpsp individualism2_jpsp individualism3_jpsp individualism4_jpsp individualism5_jpsp individualism6_jpsp individualism7_jpsp individualism8_jpsp
tempfile long_individualism
save `long_individualism', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_individualism'
    save `long_individualism', replace
    restore
}

use `long_individualism', clear

drop individualism1_jpsp individualism2_jpsp individualism3_jpsp individualism4_jpsp individualism5_jpsp individualism6_jpsp individualism7_jpsp individualism8_jpsp

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
export delimited using "pezzuti_2025_coolpeople_main_individualism_USA.csv", replace

**# Bookmark #4: Collectivism scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* collectivism1_jicm collectivism2_jicm collectivism3_jicm collectivism4_jicm collectivism5_jicm collectivism6_jicm

* keep only country(ies)-specific observations
keep if cov_country == "Mexico" | cov_country == "Chile"

* create long-format data from wide data
local question_cols collectivism1_jicm collectivism2_jicm collectivism3_jicm collectivism4_jicm collectivism5_jicm collectivism6_jicm
tempfile long_collectivism
save `long_collectivism', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_collectivism'
    save `long_collectivism', replace
    restore
}

use `long_collectivism', clear

drop collectivism1_jicm collectivism2_jicm collectivism3_jicm collectivism4_jicm collectivism5_jicm collectivism6_jicm

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
export delimited using "pezzuti_2025_coolpeople_main_collectivism_Mexico_Chile.csv", replace

**# Bookmark #5: Power Distance scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* power_distance1 power_distance2 power_distance3 power_distance4 power_distance5

* keep only country(ies)-specific observations
keep if cov_country == "USA" | cov_country == "Chile"

* create long-format data from wide data
local question_cols power_distance1 power_distance2 power_distance3 power_distance4 power_distance5
tempfile long_powerdistance
save `long_powerdistance', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_powerdistance'
    save `long_powerdistance', replace
    restore
}

use `long_powerdistance', clear

drop power_distance1 power_distance2 power_distance3 power_distance4 power_distance5

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
export delimited using "pezzuti_2025_coolpeople_main_powerdistance_USA_Chile.csv", replace

**# Bookmark #6: Uncertainty Avoidance scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* uncertainty_avoidance1 uncertainty_avoidance2 uncertainty_avoidance3 uncertainty_avoidance4 uncertainty_avoidance5

* keep only country(ies)-specific observations
keep if cov_country == "USA" | cov_country == "Chile"

* create long-format data from wide data
local question_cols uncertainty_avoidance1 uncertainty_avoidance2 uncertainty_avoidance3 uncertainty_avoidance4 uncertainty_avoidance5
tempfile long_uncertaintyavoidance
save `long_uncertaintyavoidance', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_uncertaintyavoidance'
    save `long_uncertaintyavoidance', replace
    restore
}

use `long_uncertaintyavoidance', clear

drop uncertainty_avoidance1 uncertainty_avoidance2 uncertainty_avoidance3 uncertainty_avoidance4 uncertainty_avoidance5

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
export delimited using "pezzuti_2025_coolpeople_main_uncertaintyavoidance_USA_Chile.csv", replace

**# Bookmark #7: Masculinity scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* masculinity1 masculinity2 masculinity3 masculinity4

* keep only country(ies)-specific observations
keep if cov_country == "Chile"

* create long-format data from wide data
local question_cols masculinity1 masculinity2 masculinity3 masculinity4
tempfile long_masculinity
save `long_masculinity', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_masculinity'
    save `long_masculinity', replace
    restore
}

use `long_masculinity', clear

drop masculinity1 masculinity2 masculinity3 masculinity4

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
export delimited using "pezzuti_2025_coolpeople_main_masculinity_Chile.csv", replace

**# Bookmark #8: Tightness/looseness scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tight*

* keep only country(ies)-specific observations
keep if cov_country == "USA" | cov_country == "Chile"

* combine two categories
gen tight1_agg = tight1
replace tight1_agg = tight_1 if missing(tight1)

gen tight2_agg = tight2
replace tight2_agg = tight_2 if missing(tight2)

gen tight3_agg = tight3
replace tight3_agg = tight_3 if missing(tight3)

gen tight4_agg = tight4
replace tight4_agg = tight_4 if missing(tight4)

gen tight5_agg = tight5
replace tight5_agg = tight_5 if missing(tight5)

gen tight6_agg = tight6
replace tight6_agg = tight_6 if missing(tight6)

drop tight1 tight_1 tight2 tight_2 tight3 tight_3 tight4 tight_4 tight5 tight_5 tight6 tight_6

rename tight1_agg tight1
rename tight2_agg tight2
rename tight3_agg tight3
rename tight4_agg tight4
rename tight5_agg tight5
rename tight6_agg tight6

* create long-format data from wide data
local question_cols tight1 tight2 tight3 tight4 tight5 tight6
tempfile long_tight
save `long_tight', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_tight'
    save `long_tight', replace
    restore
}

use `long_tight', clear

drop tight1 tight2 tight3 tight4 tight5 tight6

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
export delimited using "pezzuti_2025_coolpeople_main_tight_USA_Chile.csv", replace

**# Bookmark #9: Materialism scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* materialism*

* keep only country(ies)-specific observations
keep if cov_country == "Chile"

* create long-format data from wide data
local question_cols materialism1 materialism2 materialism3 materialism4 materialism5 materialism6 materialism7 materialism8 materialism9 materialism10 materialism11 materialism12 materialism13 materialism14 materialism15 materialism16 materialism17 materialism18

tempfile long_material
save `long_material', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_material'
    save `long_material', replace
    restore
}

use `long_material', clear

drop materialism1 materialism2 materialism3 materialism4 materialism5 materialism6 materialism7 materialism8 materialism9 materialism10 materialism11 materialism12 materialism13 materialism14 materialism15 materialism16 materialism17 materialism18

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
export delimited using "pezzuti_2025_coolpeople_main_materialism_Chile.csv", replace

**# Bookmark #10: Big 5 scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* korean_big5_*

* keep only country(ies)-specific observations
keep if cov_country == "South Korea"

* create long-format data from wide data
local question_cols korean_big5_conservative korean_big5_trustworthy korean_big5_lazy korean_big5_sociable korean_big5_faults korean_big5_nervous korean_big5_imaginative korean_big5_thorough korean_big5_laidback

tempfile long_big5
save `long_big5', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_big5'
    save `long_big5', replace
    restore
}

use `long_big5', clear

drop korean_big5_conservative korean_big5_trustworthy korean_big5_lazy korean_big5_sociable korean_big5_faults korean_big5_nervous korean_big5_imaginative korean_big5_thorough korean_big5_laidback

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
export delimited using "pezzuti_2025_coolpeople_main_big5_SouthKorea.csv", replace

**# Bookmark #11: Warm scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* warm1 warm2 warm3 warm4

* create long-format data from wide data
local question_cols warm1 warm2 warm3 warm4

tempfile long_warm
save `long_warm', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_warm'
    save `long_warm', replace
    restore
}

use `long_warm', clear

drop warm1 warm2 warm3 warm4

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
export delimited using "pezzuti_2025_coolpeople_main_warm.csv", replace

**# Bookmark #12: Autonomous scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* autonomous1 autonomous2 autonomous3 autonomous4

* create long-format data from wide data
local question_cols autonomous1 autonomous2 autonomous3 autonomous4

tempfile long_autonomous
save `long_autonomous', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_autonomous'
    save `long_autonomous', replace
    restore
}

use `long_autonomous', clear

drop autonomous1 autonomous2 autonomous3 autonomous4

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
export delimited using "pezzuti_2025_coolpeople_main_autonomous.csv", replace

**# Bookmark #13: Adventurous scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* adventurous1 adventurous2 adventurous3 adventurous4

* create long-format data from wide data
local question_cols adventurous1 adventurous2 adventurous3 adventurous4

tempfile long_adventurous
save `long_adventurous', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_adventurous'
    save `long_adventurous', replace
    restore
}

use `long_adventurous', clear

drop adventurous1 adventurous2 adventurous3 adventurous4

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
export delimited using "pezzuti_2025_coolpeople_main_adventurous.csv", replace

**# Bookmark #14: Hedonistic scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* hedonistic1 hedonistic2 hedonistic3 hedonistic4

* create long-format data from wide data
local question_cols hedonistic1 hedonistic2 hedonistic3 hedonistic4

tempfile long_hedonistic
save `long_hedonistic', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_hedonistic'
    save `long_hedonistic', replace
    restore
}

use `long_hedonistic', clear

drop hedonistic1 hedonistic2 hedonistic3 hedonistic4

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
export delimited using "pezzuti_2025_coolpeople_main_hedonistic.csv", replace

**# Bookmark #15: Capable scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* capable1 capable2 capable3 capable4

* create long-format data from wide data
local question_cols capable1 capable2 capable3 capable4

tempfile long_capable
save `long_capable', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_capable'
    save `long_capable', replace
    restore
}

use `long_capable', clear

drop capable1 capable2 capable3 capable4

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
export delimited using "pezzuti_2025_coolpeople_main_capable.csv", replace

**# Bookmark #16: Conforming scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* conforming1 conforming2 conforming3 conforming4

* create long-format data from wide data
local question_cols conforming1 conforming2 conforming3 conforming4

tempfile long_conforming
save `long_conforming', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_conforming'
    save `long_conforming', replace
    restore
}

use `long_conforming', clear

drop conforming1 conforming2 conforming3 conforming4

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
export delimited using "pezzuti_2025_coolpeople_main_conforming.csv", replace

**# Bookmark #17: Benevolent scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* benevolent1 benevolent2 benevolent3 benevolent4 benevolent5 benevolent6

* create long-format data from wide data
local question_cols benevolent1 benevolent2 benevolent3 benevolent4 benevolent5 benevolent6

tempfile long_benevolent
save `long_benevolent', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_benevolent'
    save `long_benevolent', replace
    restore
}

use `long_benevolent', clear

drop benevolent1 benevolent2 benevolent3 benevolent4 benevolent5 benevolent6

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
export delimited using "pezzuti_2025_coolpeople_main_benevolent.csv", replace

**# Bookmark #18: Secure scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* secure1 secure2 secure3 secure4

* create long-format data from wide data
local question_cols secure1 secure2 secure3 secure4

tempfile long_secure
save `long_secure', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_secure'
    save `long_secure', replace
    restore
}

use `long_secure', clear

drop secure1 secure2 secure3 secure4

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
export delimited using "pezzuti_2025_coolpeople_main_secure.csv", replace

**# Bookmark #19: Traditional scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* traditional1 traditional2 traditional3 traditional4

* create long-format data from wide data
local question_cols traditional1 traditional2 traditional3 traditional4

tempfile long_traditional
save `long_traditional', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_traditional'
    save `long_traditional', replace
    restore
}

use `long_traditional', clear

drop traditional1 traditional2 traditional3 traditional4

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
export delimited using "pezzuti_2025_coolpeople_main_traditional.csv", replace

**# Bookmark #20: Powerful scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* powerful1 powerful2 powerful3 powerful4

* create long-format data from wide data
local question_cols powerful1 powerful2 powerful3 powerful4

tempfile long_powerful
save `long_powerful', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_powerful'
    save `long_powerful', replace
    restore
}

use `long_powerful', clear

drop powerful1 powerful2 powerful3 powerful4

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
export delimited using "pezzuti_2025_coolpeople_main_powerful.csv", replace

**# Bookmark #21: NFC scale

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* nfc_1 nfc_2 nfc_3 nfc_4 nfc_5

* create long-format data from wide data
local question_cols nfc_1 nfc_2 nfc_3 nfc_4 nfc_5

tempfile long_nfc
save `long_nfc', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_nfc'
    save `long_nfc', replace
    restore
}

use `long_nfc', clear

drop nfc_1 nfc_2 nfc_3 nfc_4 nfc_5

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
export delimited using "pezzuti_2025_coolpeople_main_nfc.csv", replace

**# Bookmark #22: Diverse, single-item scale [This scale groups the remaining single-item attributes to make diverse, cohesive dataset]

* recall dataset
use "pezzuti_2025_coolpeople_main.csv", clear

* adjust respective variable names when needed
drop calm
rename calm_1 calm

* keep only id, covariates, and respective variables
keep id cov_* calm anxious extraverted reserved critical sympathetic dependable disorganized open_new_experiences conventional

* create long-format data from wide data
local question_cols calm anxious extraverted reserved critical sympathetic dependable disorganized open_new_experiences conventional

tempfile long_singleitems
save `long_singleitems', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_singleitems'
    save `long_singleitems', replace
    restore
}

use `long_singleitems', clear

drop calm anxious extraverted reserved critical sympathetic dependable disorganized open_new_experiences conventional

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
export delimited using "pezzuti_2025_coolpeople_main_single-items.csv", replace

************************************************************************************
************************************************************************************
****************************** Supplemental Experiments ****************************
************************************************************************************
************************************************************************************

* clear
clear

* import first dataset
import spss using "Data_Study 1S favorability_July 2 2024.sav", clear
gen study = "1S"

* save the dataset temporarily
save temp1, replace

* import second dataset
import spss using "Data_Study 2S isolated cool_July 2 2024.sav", clear
gen study = "2S"
save temp2, replace

* import third dataset
import spss using "Data_Study 3S less more_Jan 6 2025.sav", clear
gen study = "3S"
save temp3, replace

* append all datasets
use temp1, clear
append using temp2
append using temp3

* save the final combined dataset
export delimited "pezzuti_2025_coolpeople_supplemental.csv", replace

* convert column names to lowercase
rename *, lower

* extrapolate year value from original variable
gen year = year(dofc(recordeddate))

* round up age
gen age_ceil = ceil(age)
drop age
rename age_ceil age

* rename covariates
rename year cov_year
rename gender cov_gender
rename age cov_age
rename study cov_study

* delete minor observations
drop if finished == 0 | missing(finished)

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "pezzuti_2025_coolpeople_supplemental.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #23: Warm scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* warm1 warm2 warm3 warm4

* create long-format data from wide data
local question_cols warm1 warm2 warm3 warm4

tempfile long_warm
save `long_warm', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_warm'
    save `long_warm', replace
    restore
}

use `long_warm', clear

drop warm1 warm2 warm3 warm4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_warm.csv", replace

**# Bookmark #24: Autonomous scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* autonomous1 autonomous2 autonomous3 autonomous4

* create long-format data from wide data
local question_cols autonomous1 autonomous2 autonomous3 autonomous4

tempfile long_autonomous
save `long_autonomous', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_autonomous'
    save `long_autonomous', replace
    restore
}

use `long_autonomous', clear

drop autonomous1 autonomous2 autonomous3 autonomous4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_autonomous.csv", replace

**# Bookmark #25: Adventurous scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* adventurous1 adventurous2 adventurous3 adventurous4

* create long-format data from wide data
local question_cols adventurous1 adventurous2 adventurous3 adventurous4

tempfile long_adventurous
save `long_adventurous', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_adventurous'
    save `long_adventurous', replace
    restore
}

use `long_adventurous', clear

drop adventurous1 adventurous2 adventurous3 adventurous4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_adventurous .csv", replace

**# Bookmark #26: Hedonistic scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* hedonistic1 hedonistic2 hedonistic3 hedonistic4

* create long-format data from wide data
local question_cols hedonistic1 hedonistic2 hedonistic3 hedonistic4

tempfile long_hedonistic
save `long_hedonistic', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_hedonistic'
    save `long_hedonistic', replace
    restore
}

use `long_hedonistic', clear

drop hedonistic1 hedonistic2 hedonistic3 hedonistic4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_hedonistic .csv", replace

**# Bookmark #27: Capable scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* capable1 capable2 capable3 capable4

* create long-format data from wide data
local question_cols capable1 capable2 capable3 capable4

tempfile long_capable
save `long_capable', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_capable'
    save `long_capable', replace
    restore
}

use `long_capable', clear

drop capable1 capable2 capable3 capable4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_capable .csv", replace

**# Bookmark #28: Conforming scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* conforming1 conforming2 conforming3 conforming4

* create long-format data from wide data
local question_cols conforming1 conforming2 conforming3 conforming4

tempfile long_conforming
save `long_conforming', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_conforming'
    save `long_conforming', replace
    restore
}

use `long_conforming', clear

drop conforming1 conforming2 conforming3 conforming4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_conforming.csv", replace

**# Bookmark #29: Benevolent scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* benevolent1 benevolent2 benevolent3 benevolent4 benevolent5 benevolent6

* create long-format data from wide data
local question_cols benevolent1 benevolent2 benevolent3 benevolent4 benevolent5 benevolent6

tempfile long_benevolent
save `long_benevolent', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_benevolent'
    save `long_benevolent', replace
    restore
}

use `long_benevolent', clear

drop benevolent1 benevolent2 benevolent3 benevolent4 benevolent5 benevolent6

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
export delimited using "pezzuti_2025_coolpeople_supplemental_benevolent .csv", replace

**# Bookmark #30: Secure scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* secure1 secure2 secure3 secure4

* create long-format data from wide data
local question_cols secure1 secure2 secure3 secure4

tempfile long_secure
save `long_secure', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_secure'
    save `long_secure', replace
    restore
}

use `long_secure', clear

drop secure1 secure2 secure3 secure4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_secure.csv", replace

**# Bookmark #31: Traditional scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* traditional1 traditional2 traditional3 traditional4

* create long-format data from wide data
local question_cols traditional1 traditional2 traditional3 traditional4

tempfile long_traditional
save `long_traditional', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_traditional'
    save `long_traditional', replace
    restore
}

use `long_traditional', clear

drop traditional1 traditional2 traditional3 traditional4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_traditional.csv", replace

**# Bookmark #32: Powerful scale

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* powerful1 powerful2 powerful3 powerful4

* create long-format data from wide data
local question_cols powerful1 powerful2 powerful3 powerful4

tempfile long_powerful
save `long_powerful', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_powerful'
    save `long_powerful', replace
    restore
}

use `long_powerful', clear

drop powerful1 powerful2 powerful3 powerful4

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
export delimited using "pezzuti_2025_coolpeople_supplemental_powerful.csv", replace

**# Bookmark #33: Diverse, single-item scale [This scale groups the remaining single-item attributes to make diverse, cohesive dataset]

* recall dataset
use "pezzuti_2025_coolpeople_supplemental.csv", clear

* adjust respective variable names when needed
drop calm
rename calm_1 calm

* keep only id, covariates, and respective variables
keep id cov_* calm anxious extraverted reserved critical sympathetic dependable disorganized open_new_experiences conventional

* create long-format data from wide data
local question_cols calm anxious extraverted reserved critical sympathetic dependable disorganized open_new_experiences conventional

tempfile long_singleitems
save `long_singleitems', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_singleitems'
    save `long_singleitems', replace
    restore
}

use `long_singleitems', clear

drop calm anxious extraverted reserved critical sympathetic dependable disorganized open_new_experiences conventional

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
export delimited using "pezzuti_2025_coolpeople_supplemental_single-items.csv", replace