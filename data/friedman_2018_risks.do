*** note: we only took the 3 selected response tables, see https://github.com/ben-domingue/irw/issues/1177#issuecomment-3709007325

*** This Do File creates tables from the Replication Data for: Priorities for Preventive Action: Explaining Americans' Divergent Reactions to 100 Public Risks study ***

******************************************
***********  Prepare the data ************
******************************************

* clear
clear

* import the main dataset
use "Risk_Data_Base.dta", clear

* compress file so the following codes run faster
compress
save, replace

* convert column names to lowercase
rename *, lower

* renames covariates
rename age cov_age
rename gender cov_gender
rename durationinseconds cov_sduration
rename education cov_education
rename enddate cov_enddate
rename hispanic cov_hispanic
rename income cov_income
rename democrat cov_democrat
rename independent cov_independent
rename party cov_party
rename race cov_race
rename republican cov_republican
rename startdate cov_startdate
rename state cov_state
rename zip cov_zip

* convert start dates of survey response to standard format, which is the time of the data point in UNIX format
generate double cov_startdate_stata = clock(cov_startdate, "MDYhm")
format cov_startdate_stata %tc
generate double cov_startdate_unix = (cov_startdate_stata - tC(01jan1970 00:00:00)) / 1000

* convert end dates of survey response to standard format, which is the time of the data point in UNIX format
generate double cov_enddate_stata = clock(cov_enddate, "MDYhm")
format cov_enddate_stata %tc
generate double cov_enddate_unix = (cov_enddate_stata - tC(01jan1970 00:00:00)) / 1000

* drop irrelevant time covariates
drop cov_enddate_stata cov_startdate_stata cov_enddate cov_startdate

* rename time covariates
rename cov_enddate_unix cov_enddate
rename cov_startdate_unix cov_startdate

* order seconds, start date, and enddate sequentially
order cov_sduration cov_startdate cov_enddate, first

* drop old id
drop responseid

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "friedman_2018_risks.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: likert-scale responses to the role of the government on people's lives and restrictions

* recall dataset
use "friedman_2018_risks.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* charm climchoi cprotect iinterests iprivacy iprotect

* set up the code for long-format data from wide data
local question_cols charm climchoi cprotect iinterests iprivacy iprotect

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

drop charm climchoi cprotect iinterests iprivacy iprotect

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
export delimited using "friedman_2018_risks_government.csv", replace

**# Bookmark #2: likert-scale responses to the presence of discrimination, inequality, and justice in society currently

* recall dataset
use "friedman_2018_risks.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* ediscrim eradeq ewealth hequal hfeminin hrevdis2

* set up the code for long-format data from wide data
local question_cols ediscrim eradeq ewealth hequal hfeminin hrevdis2

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

drop ediscrim eradeq ewealth hequal hfeminin hrevdis2

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
export delimited using "friedman_2018_risks_discrimination.csv", replace

**# Bookmark #3: yes/no responses to general science-related questions such as whether antibiotics kill viruses or whether electrons are smaller than atoms

* recall dataset
use "friedman_2018_risks.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* osc_anti osc_atoms osc_copern osc_gas osc_lasers osc_radio osc_year

* set up the code for long-format data from wide data
local question_cols osc_anti osc_atoms osc_copern osc_gas osc_lasers osc_radio osc_year

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

drop osc_anti osc_atoms osc_copern osc_gas osc_lasers osc_radio osc_year

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
export delimited using "friedman_2018_risks_science.csv", replace

**# Bookmark #4: a1 through aaaa15/n, wherein the risk respondent selected as more of the government's responsibility to prevent. The number of a's (for "appropriateness") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* a1	a1n	a2	a2n	a3	a3n	a4	a4n	a5	a5n	a6	a6n	a7	a7n	a8	a8n	a9	a9n	a10	a10n	a11	a11n	a12	a12n	a13	a13n	a14	a14n	a15	a15n	aa1	aa1n	aa2	aa2n	aa3	aa3n	aa4	aa4n	aa5	aa5n	aa6	aa6n	aa7	aa7n	aa8	aa8n	aa9	aa9n	aa10	aa10n	aa11	aa11n	aa12	aa12n	aa13	aa13n	aa14	aa14n	aa15	aa15n	aaa1	aaa1n	aaa2	aaa2n	aaa3	aaa3n	aaa4	aaa4n	aaa5	aaa5n	aaa6	aaa6n	aaa7	aaa7n	aaa8	aaa8n	aaa9	aaa9n	aaa10	aaa10n	aaa11	aaa11n	aaa12	aaa12n	aaa13	aaa13n	aaa14	aaa14n	aaa15	aaa15n	aaaa1	aaaa1n	aaaa2	aaaa2n	aaaa3	aaaa3n	aaaa4	aaaa4n	aaaa5	aaaa5n	aaaa6	aaaa6n	aaaa7	aaaa7n	aaaa8	aaaa8n	aaaa9	aaaa9n	aaaa10	aaaa10n	aaaa11	aaaa11n	aaaa12	aaaa12n	aaaa13	aaaa13n	aaaa14	aaaa14n	aaaa15	aaaa15n

* set up the code for long-format data from wide data
local question_cols a1	a1n	a2	a2n	a3	a3n	a4	a4n	a5	a5n	a6	a6n	a7	a7n	a8	a8n	a9	a9n	a10	a10n	a11	a11n	a12	a12n	a13	a13n	a14	a14n	a15	a15n	aa1	aa1n	aa2	aa2n	aa3	aa3n	aa4	aa4n	aa5	aa5n	aa6	aa6n	aa7	aa7n	aa8	aa8n	aa9	aa9n	aa10	aa10n	aa11	aa11n	aa12	aa12n	aa13	aa13n	aa14	aa14n	aa15	aa15n	aaa1	aaa1n	aaa2	aaa2n	aaa3	aaa3n	aaa4	aaa4n	aaa5	aaa5n	aaa6	aaa6n	aaa7	aaa7n	aaa8	aaa8n	aaa9	aaa9n	aaa10	aaa10n	aaa11	aaa11n	aaa12	aaa12n	aaa13	aaa13n	aaa14	aaa14n	aaa15	aaa15n	aaaa1	aaaa1n	aaaa2	aaaa2n	aaaa3	aaaa3n	aaaa4	aaaa4n	aaaa5	aaaa5n	aaaa6	aaaa6n	aaaa7	aaaa7n	aaaa8	aaaa8n	aaaa9	aaaa9n	aaaa10	aaaa10n	aaaa11	aaaa11n	aaaa12	aaaa12n	aaaa13	aaaa13n	aaaa14	aaaa14n	aaaa15	aaaa15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* a1 a1n a2 a2n a3 a3n a4 a4n a5 a5n a6 a6n a7 a7n a8 a8n a9 a9n a10 a10n a11 a11n a12 a12n a13 a13n a14 a14n a15 a15n aa1 aa1n aa2 aa2n aa3 aa3n aa4 aa4n aa5 aa5n aa6 aa6n aa7 aa7n aa8 aa8n aa9 aa9n aa10 aa10n aa11 aa11n aa12 aa12n aa13 aa13n aa14 aa14n aa15 aa15n aaa1 aaa1n aaa2 aaa2n aaa3 aaa3n aaa4 aaa4n aaa5 aaa5n aaa6 aaa6n aaa7 aaa7n aaa8 aaa8n aaa9 aaa9n aaa10 aaa10n aaa11 aaa11n aaa12 aaa12n aaa13 aaa13n aaa14 aaa14n aaa15 aaa15n aaaa1 aaaa1n aaaa2 aaaa2n aaaa3 aaaa3n aaaa4 aaaa4n aaaa5 aaaa5n aaaa6 aaaa6n aaaa7 aaaa7n aaaa8 aaaa8n aaaa9 aaaa9n aaaa10 aaaa10n aaaa11 aaaa11n aaaa12 aaaa12n aaaa13 aaaa13n aaaa14 aaaa14n aaaa15 aaaa15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_appropriateness.csv", replace

**# Bookmark #5: d1 through dddd15/n, wherein the risk respondent selected as having more disaster potential. The number of d's (for "disaster") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper.

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* d1	d1n	d2	d2n	d3	d3n	d4	d4n	d5	d5n	d6	d6n	d7	d7n	d8	d8n	d9	d9n	d10	d10n	d11	d11n	d12	d12n	d13	d13n	d14	d14n	d15	d15n	dd1	dd1n	dd2	dd2n	dd3	dd3n	dd4	dd4n	dd5	dd5n	dd6	dd6n	dd7	dd7n	dd8	dd8n	dd9	dd9n	dd10	dd10n	dd11	dd11n	dd12	dd12n	dd13	dd13n	dd14	dd14n	dd15	dd15n	ddd1	ddd1n	ddd2	ddd2n	ddd3	ddd3n	ddd4	ddd4n	ddd5	ddd5n	ddd6	ddd6n	ddd7	ddd7n	ddd8	ddd8n	ddd9	ddd9n	ddd10	ddd10n	ddd11	ddd11n	ddd12	ddd12n	ddd13	ddd13n	ddd14	ddd14n	ddd15	ddd15n	dddd1	dddd1n	dddd2	dddd2n	dddd3	dddd3n	dddd4	dddd4n	dddd5	dddd5n	dddd6	dddd6n	dddd7	dddd7n	dddd8	dddd8n	dddd9	dddd9n	dddd10	dddd10n	dddd11	dddd11n	dddd12	dddd12n	dddd13	dddd13n	dddd14	dddd14n	dddd15	dddd15n

* set up the code for long-format data from wide data
local question_cols d1	d1n	d2	d2n	d3	d3n	d4	d4n	d5	d5n	d6	d6n	d7	d7n	d8	d8n	d9	d9n	d10	d10n	d11	d11n	d12	d12n	d13	d13n	d14	d14n	d15	d15n	dd1	dd1n	dd2	dd2n	dd3	dd3n	dd4	dd4n	dd5	dd5n	dd6	dd6n	dd7	dd7n	dd8	dd8n	dd9	dd9n	dd10	dd10n	dd11	dd11n	dd12	dd12n	dd13	dd13n	dd14	dd14n	dd15	dd15n	ddd1	ddd1n	ddd2	ddd2n	ddd3	ddd3n	ddd4	ddd4n	ddd5	ddd5n	ddd6	ddd6n	ddd7	ddd7n	ddd8	ddd8n	ddd9	ddd9n	ddd10	ddd10n	ddd11	ddd11n	ddd12	ddd12n	ddd13	ddd13n	ddd14	ddd14n	ddd15	ddd15n	dddd1	dddd1n	dddd2	dddd2n	dddd3	dddd3n	dddd4	dddd4n	dddd5	dddd5n	dddd6	dddd6n	dddd7	dddd7n	dddd8	dddd8n	dddd9	dddd9n	dddd10	dddd10n	dddd11	dddd11n	dddd12	dddd12n	dddd13	dddd13n	dddd14	dddd14n	dddd15	dddd15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* d1	d1n	d2	d2n	d3	d3n	d4	d4n	d5	d5n	d6	d6n	d7	d7n	d8	d8n	d9	d9n	d10	d10n	d11	d11n	d12	d12n	d13	d13n	d14	d14n	d15	d15n	dd1	dd1n	dd2	dd2n	dd3	dd3n	dd4	dd4n	dd5	dd5n	dd6	dd6n	dd7	dd7n	dd8	dd8n	dd9	dd9n	dd10	dd10n	dd11	dd11n	dd12	dd12n	dd13	dd13n	dd14	dd14n	dd15	dd15n	ddd1	ddd1n	ddd2	ddd2n	ddd3	ddd3n	ddd4	ddd4n	ddd5	ddd5n	ddd6	ddd6n	ddd7	ddd7n	ddd8	ddd8n	ddd9	ddd9n	ddd10	ddd10n	ddd11	ddd11n	ddd12	ddd12n	ddd13	ddd13n	ddd14	ddd14n	ddd15	ddd15n	dddd1	dddd1n	dddd2	dddd2n	dddd3	dddd3n	dddd4	dddd4n	dddd5	dddd5n	dddd6	dddd6n	dddd7	dddd7n	dddd8	dddd8n	dddd9	dddd9n	dddd10	dddd10n	dddd11	dddd11n	dddd12	dddd12n	dddd13	dddd13n	dddd14	dddd14n	dddd15	dddd15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_disaster.csv", replace

**# Bookmark #6: f1 through ffff15/n, wherein the risk respondent selected as being more unfair to its victims. The number of f's (for "fairness") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper.

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* f1	f1n	f2	f2n	f3	f3n	f4	f4n	f5	f5n	f6	f6n	f7	f7n	f8	f8n	f9	f9n	f10	f10n	f11	f11n	f12	f12n	f13	f13n	f14	f14n	f15	f15n	ff1	ff1n	ff2	ff2n	ff3	ff3n	ff4	ff4n	ff5	ff5n	ff6	ff6n	ff7	ff7n	ff8	ff8n	ff9	ff9n	ff10	ff10n	ff11	ff11n	ff12	ff12n	ff13	ff13n	ff14	ff14n	ff15	ff15n	fff1	fff1n	fff2	fff2n	fff3	fff3n	fff4	fff4n	fff5	fff5n	fff6	fff6n	fff7	fff7n	fff8	fff8n	fff9	fff9n	fff10	fff10n	fff11	fff11n	fff12	fff12n	fff13	fff13n	fff14	fff14n	fff15	fff15n	ffff1	ffff1n	ffff2	ffff2n	ffff3	ffff3n	ffff4	ffff4n	ffff5	ffff5n	ffff6	ffff6n	ffff7	ffff7n	ffff8	ffff8n	ffff9	ffff9n	ffff10	ffff10n	ffff11	ffff11n	ffff12	ffff12n	ffff13	ffff13n	ffff14	ffff14n	ffff15	ffff15n

* set up the code for long-format data from wide data
local question_cols f1	f1n	f2	f2n	f3	f3n	f4	f4n	f5	f5n	f6	f6n	f7	f7n	f8	f8n	f9	f9n	f10	f10n	f11	f11n	f12	f12n	f13	f13n	f14	f14n	f15	f15n	ff1	ff1n	ff2	ff2n	ff3	ff3n	ff4	ff4n	ff5	ff5n	ff6	ff6n	ff7	ff7n	ff8	ff8n	ff9	ff9n	ff10	ff10n	ff11	ff11n	ff12	ff12n	ff13	ff13n	ff14	ff14n	ff15	ff15n	fff1	fff1n	fff2	fff2n	fff3	fff3n	fff4	fff4n	fff5	fff5n	fff6	fff6n	fff7	fff7n	fff8	fff8n	fff9	fff9n	fff10	fff10n	fff11	fff11n	fff12	fff12n	fff13	fff13n	fff14	fff14n	fff15	fff15n	ffff1	ffff1n	ffff2	ffff2n	ffff3	ffff3n	ffff4	ffff4n	ffff5	ffff5n	ffff6	ffff6n	ffff7	ffff7n	ffff8	ffff8n	ffff9	ffff9n	ffff10	ffff10n	ffff11	ffff11n	ffff12	ffff12n	ffff13	ffff13n	ffff14	ffff14n	ffff15	ffff15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* f1	f1n	f2	f2n	f3	f3n	f4	f4n	f5	f5n	f6	f6n	f7	f7n	f8	f8n	f9	f9n	f10	f10n	f11	f11n	f12	f12n	f13	f13n	f14	f14n	f15	f15n	ff1	ff1n	ff2	ff2n	ff3	ff3n	ff4	ff4n	ff5	ff5n	ff6	ff6n	ff7	ff7n	ff8	ff8n	ff9	ff9n	ff10	ff10n	ff11	ff11n	ff12	ff12n	ff13	ff13n	ff14	ff14n	ff15	ff15n	fff1	fff1n	fff2	fff2n	fff3	fff3n	fff4	fff4n	fff5	fff5n	fff6	fff6n	fff7	fff7n	fff8	fff8n	fff9	fff9n	fff10	fff10n	fff11	fff11n	fff12	fff12n	fff13	fff13n	fff14	fff14n	fff15	fff15n	ffff1	ffff1n	ffff2	ffff2n	ffff3	ffff3n	ffff4	ffff4n	ffff5	ffff5n	ffff6	ffff6n	ffff7	ffff7n	ffff8	ffff8n	ffff9	ffff9n	ffff10	ffff10n	ffff11	ffff11n	ffff12	ffff12n	ffff13	ffff13n	ffff14	ffff14n	ffff15	ffff15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_fairness.csv", replace

**# Bookmark #7: h1 through hhhh15/n, wherein the risk respondent selected as causing more harm last year. The number of h's (for "harm") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper.

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* h1	h1n	h2	h2n	h3	h3n	h4	h4n	h5	h5n	h6	h6n	h7	h7n	h8	h8n	h9	h9n	h10	h10n	h11	h11n	h12	h12n	h13	h13n	h14	h14n	h15	h15n	hh1	hh1n	hh2	hh2n	hh3	hh3n	hh4	hh4n	hh5	hh5n	hh6	hh6n	hh7	hh7n	hh8	hh8n	hh9	hh9n	hh10	hh10n	hh11	hh11n	hh12	hh12n	hh13	hh13n	hh14	hh14n	hh15	hh15n	hhh1	hhh1n	hhh2	hhh2n	hhh3	hhh3n	hhh4	hhh4n	hhh5	hhh5n	hhh6	hhh6n	hhh7	hhh7n	hhh8	hhh8n	hhh9	hhh9n	hhh10	hhh10n	hhh11	hhh11n	hhh12	hhh12n	hhh13	hhh13n	hhh14	hhh14n	hhh15	hhh15n	hhhh1	hhhh1n	hhhh2	hhhh2n	hhhh3	hhhh3n	hhhh4	hhhh4n	hhhh5	hhhh5n	hhhh6	hhhh6n	hhhh7	hhhh7n	hhhh8	hhhh8n	hhhh9	hhhh9n	hhhh10	hhhh10n	hhhh11	hhhh11n	hhhh12	hhhh12n	hhhh13	hhhh13n	hhhh14	hhhh14n	hhhh15	hhhh15n

* set up the code for long-format data from wide data
local question_cols h1	h1n	h2	h2n	h3	h3n	h4	h4n	h5	h5n	h6	h6n	h7	h7n	h8	h8n	h9	h9n	h10	h10n	h11	h11n	h12	h12n	h13	h13n	h14	h14n	h15	h15n	hh1	hh1n	hh2	hh2n	hh3	hh3n	hh4	hh4n	hh5	hh5n	hh6	hh6n	hh7	hh7n	hh8	hh8n	hh9	hh9n	hh10	hh10n	hh11	hh11n	hh12	hh12n	hh13	hh13n	hh14	hh14n	hh15	hh15n	hhh1	hhh1n	hhh2	hhh2n	hhh3	hhh3n	hhh4	hhh4n	hhh5	hhh5n	hhh6	hhh6n	hhh7	hhh7n	hhh8	hhh8n	hhh9	hhh9n	hhh10	hhh10n	hhh11	hhh11n	hhh12	hhh12n	hhh13	hhh13n	hhh14	hhh14n	hhh15	hhh15n	hhhh1	hhhh1n	hhhh2	hhhh2n	hhhh3	hhhh3n	hhhh4	hhhh4n	hhhh5	hhhh5n	hhhh6	hhhh6n	hhhh7	hhhh7n	hhhh8	hhhh8n	hhhh9	hhhh9n	hhhh10	hhhh10n	hhhh11	hhhh11n	hhhh12	hhhh12n	hhhh13	hhhh13n	hhhh14	hhhh14n	hhhh15	hhhh15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* h1	h1n	h2	h2n	h3	h3n	h4	h4n	h5	h5n	h6	h6n	h7	h7n	h8	h8n	h9	h9n	h10	h10n	h11	h11n	h12	h12n	h13	h13n	h14	h14n	h15	h15n	hh1	hh1n	hh2	hh2n	hh3	hh3n	hh4	hh4n	hh5	hh5n	hh6	hh6n	hh7	hh7n	hh8	hh8n	hh9	hh9n	hh10	hh10n	hh11	hh11n	hh12	hh12n	hh13	hh13n	hh14	hh14n	hh15	hh15n	hhh1	hhh1n	hhh2	hhh2n	hhh3	hhh3n	hhh4	hhh4n	hhh5	hhh5n	hhh6	hhh6n	hhh7	hhh7n	hhh8	hhh8n	hhh9	hhh9n	hhh10	hhh10n	hhh11	hhh11n	hhh12	hhh12n	hhh13	hhh13n	hhh14	hhh14n	hhh15	hhh15n	hhhh1	hhhh1n	hhhh2	hhhh2n	hhhh3	hhhh3n	hhhh4	hhhh4n	hhhh5	hhhh5n	hhhh6	hhhh6n	hhhh7	hhhh7n	hhhh8	hhhh8n	hhhh9	hhhh9n	hhhh10	hhhh10n	hhhh11	hhhh11n	hhhh12	hhhh12n	hhhh13	hhhh13n	hhhh14	hhhh14n	hhhh15	hhhh15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_harm.csv", replace

**# Bookmark #8: i1 through iiii15/n, wherein the risk respondent selected as killing more people in the last year. The number of i's (for "incidence") indicates the module number; the numeral indicates the order in which this pair appeared within that module.

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* i1	i1n	i2	i2n	i3	i3n	i4	i4n	i5	i5n	i6	i6n	i7	i7n	i8	i8n	i9	i9n	i10	i10n	i11	i11n	i12	i12n	i13	i13n	i14	i14n	i15	i15n	ii1	ii1n	ii2	ii2n	ii3	ii3n	ii4	ii4n	ii5	ii5n	ii6	ii6n	ii7	ii7n	ii8	ii8n	ii9	ii9n	ii10	ii10n	ii11	ii11n	ii12	ii12n	ii13	ii13n	ii14	ii14n	ii15	ii15n	iii1	iii1n	iii2	iii2n	iii3	iii3n	iii4	iii4n	iii5	iii5n	iii6	iii6n	iii7	iii7n	iii8	iii8n	iii9	iii9n	iii10	iii10n	iii11	iii11n	iii12	iii12n	iii13	iii13n	iii14	iii14n	iii15	iii15n	iiii1	iiii1n	iiii2	iiii2n	iiii3	iiii3n	iiii4	iiii4n	iiii5	iiii5n	iiii6	iiii6n	iiii7	iiii7n	iiii8	iiii8n	iiii9	iiii9n	iiii10	iiii10n	iiii11	iiii11n	iiii12	iiii12n	iiii13	iiii13n	iiii14	iiii14n	iiii15	iiii15n

* set up the code for long-format data from wide data
local question_cols i1	i1n	i2	i2n	i3	i3n	i4	i4n	i5	i5n	i6	i6n	i7	i7n	i8	i8n	i9	i9n	i10	i10n	i11	i11n	i12	i12n	i13	i13n	i14	i14n	i15	i15n	ii1	ii1n	ii2	ii2n	ii3	ii3n	ii4	ii4n	ii5	ii5n	ii6	ii6n	ii7	ii7n	ii8	ii8n	ii9	ii9n	ii10	ii10n	ii11	ii11n	ii12	ii12n	ii13	ii13n	ii14	ii14n	ii15	ii15n	iii1	iii1n	iii2	iii2n	iii3	iii3n	iii4	iii4n	iii5	iii5n	iii6	iii6n	iii7	iii7n	iii8	iii8n	iii9	iii9n	iii10	iii10n	iii11	iii11n	iii12	iii12n	iii13	iii13n	iii14	iii14n	iii15	iii15n	iiii1	iiii1n	iiii2	iiii2n	iiii3	iiii3n	iiii4	iiii4n	iiii5	iiii5n	iiii6	iiii6n	iiii7	iiii7n	iiii8	iiii8n	iiii9	iiii9n	iiii10	iiii10n	iiii11	iiii11n	iiii12	iiii12n	iiii13	iiii13n	iiii14	iiii14n	iiii15	iiii15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* i1	i1n	i2	i2n	i3	i3n	i4	i4n	i5	i5n	i6	i6n	i7	i7n	i8	i8n	i9	i9n	i10	i10n	i11	i11n	i12	i12n	i13	i13n	i14	i14n	i15	i15n	ii1	ii1n	ii2	ii2n	ii3	ii3n	ii4	ii4n	ii5	ii5n	ii6	ii6n	ii7	ii7n	ii8	ii8n	ii9	ii9n	ii10	ii10n	ii11	ii11n	ii12	ii12n	ii13	ii13n	ii14	ii14n	ii15	ii15n	iii1	iii1n	iii2	iii2n	iii3	iii3n	iii4	iii4n	iii5	iii5n	iii6	iii6n	iii7	iii7n	iii8	iii8n	iii9	iii9n	iii10	iii10n	iii11	iii11n	iii12	iii12n	iii13	iii13n	iii14	iii14n	iii15	iii15n	iiii1	iiii1n	iiii2	iiii2n	iiii3	iiii3n	iiii4	iiii4n	iiii5	iiii5n	iiii6	iiii6n	iiii7	iiii7n	iiii8	iiii8n	iiii9	iiii9n	iiii10	iiii10n	iiii11	iiii11n	iiii12	iiii12n	iiii13	iiii13n	iiii14	iiii14n	iiii15	iiii15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_incidence.csv", replace

**# Bookmark #9: l1 through llll15/n, wherein the risk respondent selected as more likely to grow in the longterm. The number of l's (for "long-term") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper.

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* l1	l1n	l2	l2n	l3	l3n	l4	l4n	l5	l5n	l6	l6n	l7	l7n	l8	l8n	l9	l9n	l10	l10n	l11	l11n	l12	l12n	l13	l13n	l14	l14n	l15	l15n	ll1	ll1n	ll2	ll2n	ll3	ll3n	ll4	ll4n	ll5	ll5n	ll6	ll6n	ll7	ll7n	ll8	ll8n	ll9	ll9n	ll10	ll10n	ll11	ll11n	ll12	ll12n	ll13	ll13n	ll14	ll14n	ll15	ll15n	lll1	lll1n	lll2	lll2n	lll3	lll3n	lll4	lll4n	lll5	lll5n	lll6	lll6n	lll7	lll7n	lll8	lll8n	lll9	lll9n	lll10	lll10n	lll11	lll11n	lll12	lll12n	lll13	lll13n	lll14	lll14n	lll15	lll15n	llll1	llll1n	llll2	llll2n	llll3	llll3n	llll4	llll4n	llll5	llll5n	llll6	llll6n	llll7	llll7n	llll8	llll8n	llll9	llll9n	llll10	llll10n	llll11	llll11n	llll12	llll12n	llll13	llll13n	llll14	llll14n	llll15	llll15n

* set up the code for long-format data from wide data
local question_cols l1	l1n	l2	l2n	l3	l3n	l4	l4n	l5	l5n	l6	l6n	l7	l7n	l8	l8n	l9	l9n	l10	l10n	l11	l11n	l12	l12n	l13	l13n	l14	l14n	l15	l15n	ll1	ll1n	ll2	ll2n	ll3	ll3n	ll4	ll4n	ll5	ll5n	ll6	ll6n	ll7	ll7n	ll8	ll8n	ll9	ll9n	ll10	ll10n	ll11	ll11n	ll12	ll12n	ll13	ll13n	ll14	ll14n	ll15	ll15n	lll1	lll1n	lll2	lll2n	lll3	lll3n	lll4	lll4n	lll5	lll5n	lll6	lll6n	lll7	lll7n	lll8	lll8n	lll9	lll9n	lll10	lll10n	lll11	lll11n	lll12	lll12n	lll13	lll13n	lll14	lll14n	lll15	lll15n	llll1	llll1n	llll2	llll2n	llll3	llll3n	llll4	llll4n	llll5	llll5n	llll6	llll6n	llll7	llll7n	llll8	llll8n	llll9	llll9n	llll10	llll10n	llll11	llll11n	llll12	llll12n	llll13	llll13n	llll14	llll14n	llll15	llll15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* l1	l1n	l2	l2n	l3	l3n	l4	l4n	l5	l5n	l6	l6n	l7	l7n	l8	l8n	l9	l9n	l10	l10n	l11	l11n	l12	l12n	l13	l13n	l14	l14n	l15	l15n	ll1	ll1n	ll2	ll2n	ll3	ll3n	ll4	ll4n	ll5	ll5n	ll6	ll6n	ll7	ll7n	ll8	ll8n	ll9	ll9n	ll10	ll10n	ll11	ll11n	ll12	ll12n	ll13	ll13n	ll14	ll14n	ll15	ll15n	lll1	lll1n	lll2	lll2n	lll3	lll3n	lll4	lll4n	lll5	lll5n	lll6	lll6n	lll7	lll7n	lll8	lll8n	lll9	lll9n	lll10	lll10n	lll11	lll11n	lll12	lll12n	lll13	lll13n	lll14	lll14n	lll15	lll15n	llll1	llll1n	llll2	llll2n	llll3	llll3n	llll4	llll4n	llll5	llll5n	llll6	llll6n	llll7	llll7n	llll8	llll8n	llll9	llll9n	llll10	llll10n	llll11	llll11n	llll12	llll12n	llll13	llll13n	llll14	llll14n	llll15	llll15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_longterm.csv", replace

**# Bookmark #10: p1 through pppp15/n, wherein the risk respondent selected as deserving higher priority for marginal spending. The number of p's (for "priority") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper.

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* p1	p1n	p2	p2n	p3	p3n	p4	p4n	p5	p5n	p6	p6n	p7	p7n	p8	p8n	p9	p9n	p10	p10n	p11	p11n	p12	p12n	p13	p13n	p14	p14n	p15	p15n	pp1	pp1n	pp2	pp2n	pp3	pp3n	pp4	pp4n	pp5	pp5n	pp6	pp6n	pp7	pp7n	pp8	pp8n	pp9	pp9n	pp10	pp10n	pp11	pp11n	pp12	pp12n	pp13	pp13n	pp14	pp14n	pp15	pp15n	ppp1	ppp1n	ppp2	ppp2n	ppp3	ppp3n	ppp4	ppp4n	ppp5	ppp5n	ppp6	ppp6n	ppp7	ppp7n	ppp8	ppp8n	ppp9	ppp9n	ppp10	ppp10n	ppp11	ppp11n	ppp12	ppp12n	ppp13	ppp13n	ppp14	ppp14n	ppp15	ppp15n	pppp1	pppp1n	pppp2	pppp2n	pppp3	pppp3n	pppp4	pppp4n	pppp5	pppp5n	pppp6	pppp6n	pppp7	pppp7n	pppp8	pppp8n	pppp9	pppp9n	pppp10	pppp10n	pppp11	pppp11n	pppp12	pppp12n	pppp13	pppp13n	pppp14	pppp14n	pppp15	pppp15n

* set up the code for long-format data from wide data
local question_cols p1	p1n	p2	p2n	p3	p3n	p4	p4n	p5	p5n	p6	p6n	p7	p7n	p8	p8n	p9	p9n	p10	p10n	p11	p11n	p12	p12n	p13	p13n	p14	p14n	p15	p15n	pp1	pp1n	pp2	pp2n	pp3	pp3n	pp4	pp4n	pp5	pp5n	pp6	pp6n	pp7	pp7n	pp8	pp8n	pp9	pp9n	pp10	pp10n	pp11	pp11n	pp12	pp12n	pp13	pp13n	pp14	pp14n	pp15	pp15n	ppp1	ppp1n	ppp2	ppp2n	ppp3	ppp3n	ppp4	ppp4n	ppp5	ppp5n	ppp6	ppp6n	ppp7	ppp7n	ppp8	ppp8n	ppp9	ppp9n	ppp10	ppp10n	ppp11	ppp11n	ppp12	ppp12n	ppp13	ppp13n	ppp14	ppp14n	ppp15	ppp15n	pppp1	pppp1n	pppp2	pppp2n	pppp3	pppp3n	pppp4	pppp4n	pppp5	pppp5n	pppp6	pppp6n	pppp7	pppp7n	pppp8	pppp8n	pppp9	pppp9n	pppp10	pppp10n	pppp11	pppp11n	pppp12	pppp12n	pppp13	pppp13n	pppp14	pppp14n	pppp15	pppp15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* p1	p1n	p2	p2n	p3	p3n	p4	p4n	p5	p5n	p6	p6n	p7	p7n	p8	p8n	p9	p9n	p10	p10n	p11	p11n	p12	p12n	p13	p13n	p14	p14n	p15	p15n	pp1	pp1n	pp2	pp2n	pp3	pp3n	pp4	pp4n	pp5	pp5n	pp6	pp6n	pp7	pp7n	pp8	pp8n	pp9	pp9n	pp10	pp10n	pp11	pp11n	pp12	pp12n	pp13	pp13n	pp14	pp14n	pp15	pp15n	ppp1	ppp1n	ppp2	ppp2n	ppp3	ppp3n	ppp4	ppp4n	ppp5	ppp5n	ppp6	ppp6n	ppp7	ppp7n	ppp8	ppp8n	ppp9	ppp9n	ppp10	ppp10n	ppp11	ppp11n	ppp12	ppp12n	ppp13	ppp13n	ppp14	ppp14n	ppp15	ppp15n	pppp1	pppp1n	pppp2	pppp2n	pppp3	pppp3n	pppp4	pppp4n	pppp5	pppp5n	pppp6	pppp6n	pppp7	pppp7n	pppp8	pppp8n	pppp9	pppp9n	pppp10	pppp10n	pppp11	pppp11n	pppp12	pppp12n	pppp13	pppp13n	pppp14	pppp14n	pppp15	pppp15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_priority_marginalspending.csv", replace

**# Bookmark #11: pt1 through ppppt15/n, wherein the risk respondent selected as deserving higher priority for total spending. The number of p's (for "priority") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* ppppt1	ppppt1n	ppppt2	ppppt2n	ppppt3	ppppt3n	ppppt4	ppppt4n	ppppt5	ppppt5n	ppppt6	ppppt6n	ppppt7	ppppt7n	ppppt8	ppppt8n	ppppt9	ppppt9n	ppppt10	ppppt10n	ppppt11	ppppt11n	ppppt12	ppppt12n	ppppt13	ppppt13n	ppppt14	ppppt14n	ppppt15	ppppt15n	pppt1	pppt1n	pppt2	pppt2n	pppt3	pppt3n	pppt4	pppt4n	pppt5	pppt5n	pppt6	pppt6n	pppt7	pppt7n	pppt8	pppt8n	pppt9	pppt9n	pppt10	pppt10n	pppt11	pppt11n	pppt12	pppt12n	pppt13	pppt13n	pppt14	pppt14n	pppt15	pppt15n	ppt1	ppt1n	ppt2	ppt2n	ppt3	ppt3n	ppt4	ppt4n	ppt5	ppt5n	ppt6	ppt6n	ppt7	ppt7n	ppt8	ppt8n	ppt9	ppt9n	ppt10	ppt10n	ppt11	ppt11n	ppt12	ppt12n	ppt13	ppt13n	ppt14	ppt14n	ppt15	ppt15n	pt1	pt1n	pt2	pt2n	pt3	pt3n	pt4	pt4n	pt5	pt5n	pt6	pt6n	pt7	pt7n	pt8	pt8n	pt9	pt9n	pt10	pt10n	pt11	pt11n	pt12	pt12n	pt13	pt13n	pt14	pt14n	pt15	pt15n

* set up the code for long-format data from wide data
local question_cols ppppt1	ppppt1n	ppppt2	ppppt2n	ppppt3	ppppt3n	ppppt4	ppppt4n	ppppt5	ppppt5n	ppppt6	ppppt6n	ppppt7	ppppt7n	ppppt8	ppppt8n	ppppt9	ppppt9n	ppppt10	ppppt10n	ppppt11	ppppt11n	ppppt12	ppppt12n	ppppt13	ppppt13n	ppppt14	ppppt14n	ppppt15	ppppt15n	pppt1	pppt1n	pppt2	pppt2n	pppt3	pppt3n	pppt4	pppt4n	pppt5	pppt5n	pppt6	pppt6n	pppt7	pppt7n	pppt8	pppt8n	pppt9	pppt9n	pppt10	pppt10n	pppt11	pppt11n	pppt12	pppt12n	pppt13	pppt13n	pppt14	pppt14n	pppt15	pppt15n	ppt1	ppt1n	ppt2	ppt2n	ppt3	ppt3n	ppt4	ppt4n	ppt5	ppt5n	ppt6	ppt6n	ppt7	ppt7n	ppt8	ppt8n	ppt9	ppt9n	ppt10	ppt10n	ppt11	ppt11n	ppt12	ppt12n	ppt13	ppt13n	ppt14	ppt14n	ppt15	ppt15n	pt1	pt1n	pt2	pt2n	pt3	pt3n	pt4	pt4n	pt5	pt5n	pt6	pt6n	pt7	pt7n	pt8	pt8n	pt9	pt9n	pt10	pt10n	pt11	pt11n	pt12	pt12n	pt13	pt13n	pt14	pt14n	pt15	pt15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* ppppt1	ppppt1n	ppppt2	ppppt2n	ppppt3	ppppt3n	ppppt4	ppppt4n	ppppt5	ppppt5n	ppppt6	ppppt6n	ppppt7	ppppt7n	ppppt8	ppppt8n	ppppt9	ppppt9n	ppppt10	ppppt10n	ppppt11	ppppt11n	ppppt12	ppppt12n	ppppt13	ppppt13n	ppppt14	ppppt14n	ppppt15	ppppt15n	pppt1	pppt1n	pppt2	pppt2n	pppt3	pppt3n	pppt4	pppt4n	pppt5	pppt5n	pppt6	pppt6n	pppt7	pppt7n	pppt8	pppt8n	pppt9	pppt9n	pppt10	pppt10n	pppt11	pppt11n	pppt12	pppt12n	pppt13	pppt13n	pppt14	pppt14n	pppt15	pppt15n	ppt1	ppt1n	ppt2	ppt2n	ppt3	ppt3n	ppt4	ppt4n	ppt5	ppt5n	ppt6	ppt6n	ppt7	ppt7n	ppt8	ppt8n	ppt9	ppt9n	ppt10	ppt10n	ppt11	ppt11n	ppt12	ppt12n	ppt13	ppt13n	ppt14	ppt14n	ppt15	ppt15n	pt1	pt1n	pt2	pt2n	pt3	pt3n	pt4	pt4n	pt5	pt5n	pt6	pt6n	pt7	pt7n	pt8	pt8n	pt9	pt9n	pt10	pt10n	pt11	pt11n	pt12	pt12n	pt13	pt13n	pt14	pt14n	pt15	pt15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group
export delimited using "friedman_2018_risks_priority_totalspending.csv", replace

**# Bookmark #12: w1 through wwww15/n, wherein the risk respondent selected as worrying them more. The number of w's (for "worry") indicates the module number; the numeral indicates the order in which this pair appeared within that module. These notations make it possible to examine order effects within the paper.

* recall dataset
use "friedman_2018_risks.csv", clear

* compress the dataset to optimize memory usage
compress

* keep only id, covariates, and respective variables
keep id cov_* w1	w1n	w2	w2n	w3	w3n	w4	w4n	w5	w5n	w6	w6n	w7	w7n	w8	w8n	w9	w9n	w10	w10n	w11	w11n	w12	w12n	w13	w13n	w14	w14n	w15	w15n	ww1	ww1n	ww2	ww2n	ww3	ww3n	ww4	ww4n	ww5	ww5n	ww6	ww6n	ww7	ww7n	ww8	ww8n	ww9	ww9n	ww10	ww10n	ww11	ww11n	ww12	ww12n	ww13	ww13n	ww14	ww14n	ww15	ww15n	www1	www1n	www2	www2n	www3	www3n	www4	www4n	www5	www5n	www6	www6n	www7	www7n	www8	www8n	www9	www9n	www10	www10n	www11	www11n	www12	www12n	www13	www13n	www14	www14n	www15	www15n	wwww1	wwww1n	wwww2	wwww2n	wwww3	wwww3n	wwww4	wwww4n	wwww5	wwww5n	wwww6	wwww6n	wwww7	wwww7n	wwww8	wwww8n	wwww9	wwww9n	wwww10	wwww10n	wwww11	wwww11n	wwww12	wwww12n	wwww13	wwww13n	wwww14	wwww14n	wwww15	wwww15n

* set up the code for long-format data from wide data
local question_cols w1	w1n	w2	w2n	w3	w3n	w4	w4n	w5	w5n	w6	w6n	w7	w7n	w8	w8n	w9	w9n	w10	w10n	w11	w11n	w12	w12n	w13	w13n	w14	w14n	w15	w15n	ww1	ww1n	ww2	ww2n	ww3	ww3n	ww4	ww4n	ww5	ww5n	ww6	ww6n	ww7	ww7n	ww8	ww8n	ww9	ww9n	ww10	ww10n	ww11	ww11n	ww12	ww12n	ww13	ww13n	ww14	ww14n	ww15	ww15n	www1	www1n	www2	www2n	www3	www3n	www4	www4n	www5	www5n	www6	www6n	www7	www7n	www8	www8n	www9	www9n	www10	www10n	www11	www11n	www12	www12n	www13	www13n	www14	www14n	www15	www15n	wwww1	wwww1n	wwww2	wwww2n	wwww3	wwww3n	wwww4	wwww4n	wwww5	wwww5n	wwww6	wwww6n	wwww7	wwww7n	wwww8	wwww8n	wwww9	wwww9n	wwww10	wwww10n	wwww11	wwww11n	wwww12	wwww12n	wwww13	wwww13n	wwww14	wwww14n	wwww15	wwww15n

* create an empty long-format file once
tempfile long_data
clear
save `long_data', emptyok replace

* reload the working data once
use "friedman_2018_risks.csv", clear
compress
keep id cov_* w1	w1n	w2	w2n	w3	w3n	w4	w4n	w5	w5n	w6	w6n	w7	w7n	w8	w8n	w9	w9n	w10	w10n	w11	w11n	w12	w12n	w13	w13n	w14	w14n	w15	w15n	ww1	ww1n	ww2	ww2n	ww3	ww3n	ww4	ww4n	ww5	ww5n	ww6	ww6n	ww7	ww7n	ww8	ww8n	ww9	ww9n	ww10	ww10n	ww11	ww11n	ww12	ww12n	ww13	ww13n	ww14	ww14n	ww15	ww15n	www1	www1n	www2	www2n	www3	www3n	www4	www4n	www5	www5n	www6	www6n	www7	www7n	www8	www8n	www9	www9n	www10	www10n	www11	www11n	www12	www12n	www13	www13n	www14	www14n	www15	www15n	wwww1	wwww1n	wwww2	wwww2n	wwww3	wwww3n	wwww4	wwww4n	wwww5	wwww5n	wwww6	wwww6n	wwww7	wwww7n	wwww8	wwww8n	wwww9	wwww9n	wwww10	wwww10n	wwww11	wwww11n	wwww12	wwww12n	wwww13	wwww13n	wwww14	wwww14n	wwww15	wwww15n

* create long-format data from wide data (no renaming of your variables)
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

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for the group

export delimited using "friedman_2018_risks_worry.csv", replace
