*** This Do File creates tables from the How efficient is translation in language testing? Deriving valid student vocabulary tests in Spanish (StuVoc1-Esp and StuVoc2-Esp) from established English tests study ***

************************************************************************************
************************************************************************************
************************************* Study 1 **************************************
************************************************************************************
************************************************************************************

* clear
clear

* import the demographics dataset and convert to csv
import excel "Demographics_corrdata161_study1.xlsx", firstrow clear

* keep only the relevant variables for the demographics dataset
drop English French German Mandarin Basque Catalan Galician Other stuvocEng1 stuvocEng2 stuvocEng3 stuvocEsp1 stuvocEsp2 stuvocEsp_com GK RC lextale

* format Country variable
replace Country = "Germany" if Country == "Alemania"
replace Country = "Chile" if lower(Country) == "chile"

* renames covariates
rename Country cov_country
rename Age cov_age
rename Gender cov_gender
rename Occupation cov_occupation
rename Highesteducationlevel cov_educationlevel
rename Motherlanguage cov_motherlanguage
rename Speaksotherlanguage cov_multilingual

* save cleaned demographics data
save "demographics.dta", replace

******************************************
******************************************
**********  Vocabulary Test (1) **********
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "stuvoc1_231.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_1_vocabulary_1.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: Study 1 Vocabulary Test 1

* recall dataset
use "margaretto_2025_translation_study_1_vocabulary_1.csv", clear

* set up the code for long-format data from wide data
local question_cols compost	ahondar	rechupete	panacea	requisito	autentico	ablucion	tumulto	irrisorio	sagaz	amuleto	sopor	jovial	aperitivo	omnipresente	manutencion	tirabuzones	garras	trino	fractura	balandra	pragmatica	rublo	pomez	saliente	azalea	ejemplificar	ungir	impio	refectorio	fulguroso	marsupial	amago	lentejuela	flancos	rendija	atolon	fagot	desistir inefable	galimatias	taxon	yunque	aquelarre	augurio	curruca	sincero	emir

tempfile long_vocab
save `long_vocab', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_vocab'
    save `long_vocab', replace
    restore
}

use `long_vocab', clear

drop compost	ahondar	rechupete	panacea	requisito	autentico	ablucion	tumulto	irrisorio	sagaz	amuleto	sopor	jovial	aperitivo	omnipresente	manutencion	tirabuzones	garras	trino	fractura	balandra	pragmatica	rublo	pomez	saliente	azalea	ejemplificar	ungir	impio	refectorio	fulguroso	marsupial	amago	lentejuela	flancos	rendija	atolon	fagot	desistir inefable	galimatias	taxon	yunque	aquelarre	augurio	curruca	sincero	emir

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
export delimited using "margaretto_2025_translation_study_1_vocabulary_1.csv", replace

******************************************
******************************************
**********  Vocabulary Test (2) **********
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "stuvoc2_231.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_1_vocabulary_2.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #2: Study 1 Vocabulary Test 2

* recall dataset
use "margaretto_2025_translation_study_1_vocabulary_2.csv", clear

* set up the code for long-format data from wide data
local question_cols autonomia	deficit	laberinto	arcada	trueque	chapado	encolerizar	desmoronar	estatura	huerfano	alfanje	improvisar	devoto	reprimir	cartilago	astillero	ostentoso	cian	cerca	fervor	chapitel	porrazo	afincar	arrasar	embriaguez	decrepito	cuatrero	mugre	holgazanear	disidencia	inocuo	sarcofago	engrudo	exultacion	chochin	mirra	eludir	sisar	raido	atalaya	silo	gorgorito	marga	etereo	funesto	yola	atril	maligno	pergamino

tempfile long_vocab
save `long_vocab', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_vocab'
    save `long_vocab', replace
    restore
}

use `long_vocab', clear

drop autonomia	deficit	laberinto	arcada	trueque	chapado	encolerizar	desmoronar	estatura	huerfano	alfanje	improvisar	devoto	reprimir	cartilago	astillero	ostentoso	cian	cerca	fervor	chapitel	porrazo	afincar	arrasar	embriaguez	decrepito	cuatrero	mugre	holgazanear	disidencia	inocuo	sarcofago	engrudo	exultacion	chochin	mirra	eludir	sisar	raido	atalaya	silo	gorgorito	marga	etereo	funesto	yola	atril	maligno	pergamino

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
export delimited using "margaretto_2025_translation_study_1_vocabulary_2.csv", replace

******************************************
******************************************
**********  Vocabulary Test (3) **********
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "stuvoc3_231.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_1_vocabulary_3.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #3: Study 1 Vocabulary Test 3

* recall dataset
use "margaretto_2025_translation_study_1_vocabulary_3.csv", clear

* set up the code for long-format data from wide data
local question_cols rebotar	auge	jaranear	puritano	retro	pavimentar	homogeneo	acaramelar	obstinado	empalar	correa	lugubre	tinglado	sensiblero	resina	paradigma	asignar	compuesto	truco	convencional	cajon	erratico	ambiguedad	contener	conformidad	desplumar	escalofrio	tiento	manta	arrojar	miniatura	intimidacion	oblea	campesinado	retorcido	excretar	alardear	cafeina	optimista	estatuto	bazo	virar	umbral	velocimetro	caldera	sinverguenza

tempfile long_vocab
save `long_vocab', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_vocab'
    save `long_vocab', replace
    restore
}

use `long_vocab', clear

drop rebotar	auge	jaranear	puritano	retro	pavimentar	homogeneo	acaramelar	obstinado	empalar	correa	lugubre	tinglado	sensiblero	resina	paradigma	asignar	compuesto	truco	convencional	cajon	erratico	ambiguedad	contener	conformidad	desplumar	escalofrio	tiento	manta	arrojar	miniatura	intimidacion	oblea	campesinado	retorcido	excretar	alardear	cafeina	optimista	estatuto	bazo	virar	umbral	velocimetro	caldera	sinverguenza

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
export delimited using "margaretto_2025_translation_study_1_vocabulary_3.csv", replace

******************************************
******************************************
*********  General Knowledge Test ********
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "GK_231.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_1_generalknowledge.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #4: Study 1 General Knowledge Test

* recall dataset
use "margaretto_2025_translation_study_1_generalknowledge.csv", clear

* set up the code for long-format data from wide data
local question_cols maravillas	estatua	vangogh	estaciones	astronautas	agua	planetas	eclipse	frecrespirato~a	globulos	abejas	samsung	billgates	incubacion	ikea	vilvaldi	beethoven	te	dente	mazzarella	antibioticos	vino	veganos	basmati	guacamole	continente	diamante	francia	piel	corazon	telefono	otelo	bella	circunferencia	raiz	oscar	brian	naciones	consejo	color	luz	obama	reina	abba	rolling	incineracion	natacion	baloncesto	golf	ay	buffy	america	pulpo	serpiente	hormiga	trufas	romanos	letra	mov	luchadores	sonic	ajedrez	scrabble	candy	presion

tempfile long_GK
save `long_GK', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_GK'
    save `long_GK', replace
    restore
}

use `long_GK', clear

drop maravillas	estatua	vangogh	estaciones	astronautas	agua	planetas	eclipse	frecrespirato~a	globulos	abejas	samsung	billgates	incubacion	ikea	vilvaldi	beethoven	te	dente	mazzarella	antibioticos	vino	veganos	basmati	guacamole	continente	diamante	francia	piel	corazon	telefono	otelo	bella	circunferencia	raiz	oscar	brian	naciones	consejo	color	luz	obama	reina	abba	rolling	incineracion	natacion	baloncesto	golf	ay	buffy	america	pulpo	serpiente	hormiga	trufas	romanos	letra	mov	luchadores	sonic	ajedrez	scrabble	candy	presion

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
export delimited using "margaretto_2025_translation_study_1_generalknowledge.csv", replace

******************************************
******************************************
******* Reading Comprehension Test *******
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "RC_231.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_1_readingcomprehension.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #5: Study 1 Reading Comprehension Test

* recall dataset
use "margaretto_2025_translation_study_1_readingcomprehension.csv", clear

* set up the code for long-format data from wide data
local question_cols t1q1	t1q2	t1q3	t2q1	t2q2	t2q3	t3q1	t3q2	t3q3	t4q1	t4q2	t4q3	t5q1	t5q2	t5q3	t6q1	t6q2	t6q3	t7q1	t7q2	t7q3	t8q1	t8q2	t8q3	t9q1	t9q2	t9q3	t10q1	t10q2	t10q3	t11q1	t11q2	t11q3	t12q1	t12q2	t12q3	t13q1	t13q2	t13q3	t14q1	t14q2	t14q3

tempfile long_RC
save `long_RC', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_RC'
    save `long_RC', replace
    restore
}

use `long_RC', clear

drop t1q1	t1q2	t1q3	t2q1	t2q2	t2q3	t3q1	t3q2	t3q3	t4q1	t4q2	t4q3	t5q1	t5q2	t5q3	t6q1	t6q2	t6q3	t7q1	t7q2	t7q3	t8q1	t8q2	t8q3	t9q1	t9q2	t9q3	t10q1	t10q2	t10q3	t11q1	t11q2	t11q3	t12q1	t12q2	t12q3	t13q1	t13q2	t13q3	t14q1	t14q2	t14q3

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
export delimited using "margaretto_2025_translation_study_1_readingcomprehension.csv", replace

******************************************
******************************************
*********** Lextale-Esp Test *************
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "lextale_231.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_1_lextale.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #6: Study 1 Lextale-Esp Test

* recall dataset
use "margaretto_2025_translation_study_1_lextale.csv", clear

* set up the code for long-format data from wide data
local question_cols pseterzo	psebatillon	palpellizcar	palpulmones	palzapato	paltergiversar	palpesimo	psecadenia	palhacha	pseantar	palcenefa	palasesinato	palhelar	palyunque	palregar	pseabracer	psefloroso	psearsa	psebrecedad	palavido	psecapillo	pallacayo	pselampera	pallatigo	palbisagra	palsecuestro	pseacutacion	palmerodear	psedecar	psealardio	palpandilla	psefatacidad	psepauca	palaviso	pserompido	palloro	palgranuja	palestornudar	paltorpe	palalfombra	palrebuscar	psecadallo	palcanela	palcuchara	paljilguero	palmartillo	psecartinar	palladron	palganar	pseflamida	palcandado	palcamisa	psevegada	palclavel	palfomentar	palnevar	palmusgo	paltacanio	pseplaudir	palbesar	palmatar	palseda	palflaco	pseesposante	palorgulloso	palbizcocho	psehacido	palcabello	palalegre	palengatusar	psetemblo	palpolvoriento	psepemicion	palhervidor	psecintro	palyacer	palatar	paltiburon	palfrondoso	psetropaje	palhormiga	palpozo	pseempirador	palguante	pseescuto	pallaud	palbarato	psegrodo	palacantilado	palprisa

tempfile long_lextale
save `long_lextale', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_lextale'
    save `long_lextale', replace
    restore
}

use `long_lextale', clear

drop pseterzo	psebatillon	palpellizcar	palpulmones	palzapato	paltergiversar	palpesimo	psecadenia	palhacha	pseantar	palcenefa	palasesinato	palhelar	palyunque	palregar	pseabracer	psefloroso	psearsa	psebrecedad	palavido	psecapillo	pallacayo	pselampera	pallatigo	palbisagra	palsecuestro	pseacutacion	palmerodear	psedecar	psealardio	palpandilla	psefatacidad	psepauca	palaviso	pserompido	palloro	palgranuja	palestornudar	paltorpe	palalfombra	palrebuscar	psecadallo	palcanela	palcuchara	paljilguero	palmartillo	psecartinar	palladron	palganar	pseflamida	palcandado	palcamisa	psevegada	palclavel	palfomentar	palnevar	palmusgo	paltacanio	pseplaudir	palbesar	palmatar	palseda	palflaco	pseesposante	palorgulloso	palbizcocho	psehacido	palcabello	palalegre	palengatusar	psetemblo	palpolvoriento	psepemicion	palhervidor	psecintro	palyacer	palatar	paltiburon	palfrondoso	psetropaje	palhormiga	palpozo	pseempirador	palguante	pseescuto	pallaud	palbarato	psegrodo	palacantilado	palprisa

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
export delimited using "margaretto_2025_translation_study_1_lextale.csv", replace

************************************************************************************
************************************************************************************
************************************* Study 2 **************************************
************************************************************************************
************************************************************************************

* clear
clear

* import the demographics dataset and convert to csv
import excel "Demographics_corrdata196_study2.xlsx", firstrow clear

* keep only the relevant variables for the demographics dataset
drop English French German Mandarin Basque Catalan Galician Other lextale RC GK1 GK2 J stuvoc1 stuvoc2 stuvoc_comb Nationality

* renames covariates
rename Country cov_country
rename Age cov_age
rename Gender cov_gender
rename Occupation cov_occupation
rename Highesteducationlevel cov_educationlevel
rename Motherlanguage cov_motherlanguage
rename Speaksotherlanguage cov_multilingual

* save cleaned demographics data
save "demographics.dta", replace

******************************************
******************************************
*******  General Knowledge Test (1) ******
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "GK1_220.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 Participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_2_generalknowledge_1.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #7: Study 2 General Knowledge Test 1

* recall dataset
use "margaretto_2025_translation_study_2_generalknowledge_1.csv", clear

* set up the code for long-format data from wide data
local question_cols maravillas	estatua	vangogh	agua	planetas	eclipse	globulos	samsung	billgates	incubacion	ikea	vilvaldi	beethoven	te	dente	mazzarella	antibioticos	vino	veganos	basmati	guacamole	continente	diamante	francia	corazon	telefono	otelo	bella	circunferencia	raiz	oscar	naciones	consejo	luz	obama	reina	abba	rolling	baloncesto	ao	buffy	america	pulpo	serpiente	hormiga	trufas	romanos	letra	mov	luchadores	sonic	ajedrez	scrabble	candy	presion

tempfile long_GK
save `long_GK', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_GK'
    save `long_GK', replace
    restore
}

use `long_GK', clear

drop maravillas	estatua	vangogh	agua	planetas	eclipse	globulos	samsung	billgates	incubacion	ikea	vilvaldi	beethoven	te	dente	mazzarella	antibioticos	vino	veganos	basmati	guacamole	continente	diamante	francia	corazon	telefono	otelo	bella	circunferencia	raiz	oscar	naciones	consejo	luz	obama	reina	abba	rolling	baloncesto	ao	buffy	america	pulpo	serpiente	hormiga	trufas	romanos	letra	mov	luchadores	sonic	ajedrez	scrabble	candy	presion

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
export delimited using "margaretto_2025_translation_study_2_generalknowledge_1.csv", replace

******************************************
******************************************
*******  General Knowledge Test (2) ******
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "GK2_220.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 Participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_2_generalknowledge_2.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #8: Study 2 General Knowledge Test 2

* recall dataset
use "margaretto_2025_translation_study_2_generalknowledge_2.csv", clear

* set up the code for long-format data from wide data
local question_cols everest	muralla	brocoli	juegos	depresion	feta	perro	agni	romulo	internet	isohelios	aerolinea	seppuku	pixel	frasier	alfabeto	hipocrates	muro	venecia	saopaulo	concorde	etna	guyana	atajo	karenina	tchaikovsky	dividendo	bielorrusia	twain	trenbala	danubio	tap	planetas	leucemia	parasitismo	pseudociencia	lost	bowie	celula	zurich	guepardo	esperanto	unicef	grito	inri	descomposicion	agorafobia	encefalitis	aurora	trauma	supernova	hipoglucemia	ramadan

tempfile long_GK
save `long_GK', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_GK'
    save `long_GK', replace
    restore
}

use `long_GK', clear

drop everest	muralla	brocoli	juegos	depresion	feta	perro	agni	romulo	internet	isohelios	aerolinea	seppuku	pixel	frasier	alfabeto	hipocrates	muro	venecia	saopaulo	concorde	etna	guyana	atajo	karenina	tchaikovsky	dividendo	bielorrusia	twain	trenbala	danubio	tap	planetas	leucemia	parasitismo	pseudociencia	lost	bowie	celula	zurich	guepardo	esperanto	unicef	grito	inri	descomposicion	agorafobia	encefalitis	aurora	trauma	supernova	hipoglucemia	ramadan

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
export delimited using "margaretto_2025_translation_study_2_generalknowledge_2.csv", replace

******************************************
******************************************
************    Lextale-Esp    ***********
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "lextale_220.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 Participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_2_lextale.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #9: Study 2 Lextale-Esp Test

* recall dataset
use "margaretto_2025_translation_study_2_lextale.csv", clear

* set up the code for long-format data from wide data
local question_cols pseterzo	psebatillon	palpellizcar	palpulmones	palzapato	paltergiversar	palpesimo	psecadenia	palhacha	pseantar	palcenefa	palasesinato	palhelar	palyunque	palregar	pseabracer	psefloroso	psearsa	psebrecedad	palavido	psecapillo	pallacayo	pselampera	pallatigo	palbisagra	palsecuestro	pseacutacion	palmerodear	psedecar	psealardio	palpandilla	psefatacidad	psepauca	palaviso	pserompido	palloro	palgranuja	palestornudar	paltorpe	palalfombra	palrebuscar	psecadallo	palcanela	palcuchara	paljilguero	palmartillo	psecartinar	palladron	palganar	pseflamida	palcandado	palcamisa	psevegada	palclavel	palfomentar	palnevar	palmusgo	paltacanio	pseplaudir	palbesar	palmatar	palseda	palflaco	pseesposante	palorgulloso	palbizcocho	psehacido	palcabello	palalegre	palengatusar	psetemblo	palpolvoriento	psepemicion	palhervidor	psecintro	palyacer	palatar	paltiburon	palfrondoso	psetropaje	palhormiga	palpozo	pseempirador	palguante	pseescuto	pallaud	palbarato	psegrodo	palacantilado	palprisa

tempfile long_lextale
save `long_lextale', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_lextale'
    save `long_lextale', replace
    restore
}

use `long_lextale', clear

drop pseterzo	psebatillon	palpellizcar	palpulmones	palzapato	paltergiversar	palpesimo	psecadenia	palhacha	pseantar	palcenefa	palasesinato	palhelar	palyunque	palregar	pseabracer	psefloroso	psearsa	psebrecedad	palavido	psecapillo	pallacayo	pselampera	pallatigo	palbisagra	palsecuestro	pseacutacion	palmerodear	psedecar	psealardio	palpandilla	psefatacidad	psepauca	palaviso	pserompido	palloro	palgranuja	palestornudar	paltorpe	palalfombra	palrebuscar	psecadallo	palcanela	palcuchara	paljilguero	palmartillo	psecartinar	palladron	palganar	pseflamida	palcandado	palcamisa	psevegada	palclavel	palfomentar	palnevar	palmusgo	paltacanio	pseplaudir	palbesar	palmatar	palseda	palflaco	pseesposante	palorgulloso	palbizcocho	psehacido	palcabello	palalegre	palengatusar	psetemblo	palpolvoriento	psepemicion	palhervidor	psecintro	palyacer	palatar	paltiburon	palfrondoso	psetropaje	palhormiga	palpozo	pseempirador	palguante	pseescuto	pallaud	palbarato	psegrodo	palacantilado	palprisa

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
export delimited using "margaretto_2025_translation_study_2_lextale.csv", replace

******************************************
******************************************
********** Reading Comprehension  ********
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "RC_220.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 Participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_2_readingcomprehension.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #10: Study 2 Reading Comprehension Test

* recall dataset
use "margaretto_2025_translation_study_2_readingcomprehension.csv", clear

* set up the code for long-format data from wide data
local question_cols t1q1	t1q2	t1q3	t2q1	t2q2	t2q3	t3q1	t3q2	t3q3	t4q1	t4q2	t4q3	t5q1	t5q2	t5q3	t6q1	t6q2	t6q3	t7q1	t7q2	t7q3	t8q1	t8q2	t8q3	t9q1	t9q2	t9q3	t10q1	t10q2	t10q3	t11q1	t11q2	t11q3	t12q1	t12q2	t12q3	t13q1	t13q2	t13q3	t14q1	t14q2	t14q3

tempfile long_RC
save `long_RC', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_RC'
    save `long_RC', replace
    restore
}

use `long_RC', clear

drop t1q1	t1q2	t1q3	t2q1	t2q2	t2q3	t3q1	t3q2	t3q3	t4q1	t4q2	t4q3	t5q1	t5q2	t5q3	t6q1	t6q2	t6q3	t7q1	t7q2	t7q3	t8q1	t8q2	t8q3	t9q1	t9q2	t9q3	t10q1	t10q2	t10q3	t11q1	t11q2	t11q3	t12q1	t12q2	t12q3	t13q1	t13q2	t13q3	t14q1	t14q2	t14q3

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
export delimited using "margaretto_2025_translation_study_2_readingcomprehension.csv", replace

******************************************
******************************************
*********** Vocabulary Tests *************
******************************************
******************************************

* clear
clear

* import the main dataset and convert to csv
import excel "fullstuvoc_220.xlsx", firstrow clear
save "margaretto_2025_translation_temp.dta", replace

* import the demographics dataset
use "demographics.dta", clear

* merge the demographics data set with the main dataset by using participant
use "demographics.dta", clear
merge 1:1 Participant using "margaretto_2025_translation_temp.dta"

* convert column names to lowercase
rename *, lower

* drop old id
drop participant

* drop additional unnecessary variables
drop _merge

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "margaretto_2025_translation_study_2_vocabulary_full.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #11: Study 2 Vocabulary Tests

* recall dataset
use "margaretto_2025_translation_study_2_vocabulary_full.csv", clear

* set up the code for long-format data from wide data
local question_cols compost	cuatrero	erratico	excretar	umbral	impio	alardear	decrepito	disidencia	rechupete	tumulto	jovial	lugubre	sinverguenza	pragmatica	auge	saliente	arcada	arrasar	cafeina	rublo	ostentoso	homogeneo	lentejuela	rendija	maligno	acaramelar	resina	manta	flancos	desistir	afincar	virar	augurio	devoto	ablucion	atril	paradigma	reprimir	desmoronar	alfanje	jaranear	fervor	obstinado	funesto	oblea	campesinado	marga	asignar	puritano	retro	sarcofago	miniatura	eludir	fulguroso	escalofrio	balandra	omnipresente	taxon	fractura	marsupial	sincero	inefable	yola	empalar	yunque	manutencion	sagaz	pergamino	ahondar	chapado	trueque	tiento	raido

tempfile long_vocab
save `long_vocab', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_vocab'
    save `long_vocab', replace
    restore
}

use `long_vocab', clear

drop compost	cuatrero	erratico	excretar	umbral	impio	alardear	decrepito	disidencia	rechupete	tumulto	jovial	lugubre	sinverguenza	pragmatica	auge	saliente	arcada	arrasar	cafeina	rublo	ostentoso	homogeneo	lentejuela	rendija	maligno	acaramelar	resina	manta	flancos	desistir	afincar	virar	augurio	devoto	ablucion	atril	paradigma	reprimir	desmoronar	alfanje	jaranear	fervor	obstinado	funesto	oblea	campesinado	marga	asignar	puritano	retro	sarcofago	miniatura	eludir	fulguroso	escalofrio	balandra	omnipresente	taxon	fractura	marsupial	sincero	inefable	yola	empalar	yunque	manutencion	sagaz	pergamino	ahondar	chapado	trueque	tiento	raido

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
export delimited using "margaretto_2025_translation_study_2_vocabulary_full.csv", replace