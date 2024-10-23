import excel "./Assessing psychological flexibility.xlsx", sheet("Sheet 1 - Dataset (2)") firstrow allstring
(60 vars, 299 obs)

. drop Pohlavi Pohlavi_kod Vek

. drop OE4R VA5 OE6R

. drop OE13

. drop OE18R

. drop OE20

. drop S1 A2 D3 A4 D5 S6 A7 S8 A9 D10 S11 S12 D13 S14 A15 D16 D17 S18 A19 A20 D
> 21 AAQ1 AAQ2 AAQ3 AAQ4 AAQ5 AAQ6 AAQ7 SWL1 SWL2 SWL3 SWL4 SWL5

. reshape long Q, i(ID) j (resp)
(j = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17)

. destring ID, replace 
ID: all characters numeric; replaced as int


. rename ID id
rename Q item
destring item, replace
label define VA23 1 "VA1" 2 "OE2R" 3 "BA3R" 4 "VA7" 5 "OE8R" 6 "BA9R" 7 "VA10" 8 "OE11R" 9 "BA12R" 10 "VA14" 11 "OE15R" 12 "BA16R" 13 "VA17" 14 "BA19R" 15 "VA21" 16 "OE22" 17 "VA23"
label values item VA23

save "./CompACT_Ptacek 2024.dta", replace
export delimited using "./CompACT_Ptacek 2024.csv"

