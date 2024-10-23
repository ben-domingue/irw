import excel "./Assessing psychological flexibility.xlsx", sheet("Sheet 1 - Dataset (2)") firstrow allstring
drop Pohlavi Pohlavi_kod Vek VA1 OE2R BA3R OE4R VA5 OE6R VA7 OE8R BA9R VA10 OE11R BA12R OE13 VA14 OE15R BA16R VA17 OE18R BA19R OE20 VA21 OE22 VA23
drop AAQ1 AAQ2 AAQ3 AAQ4 AAQ5 AAQ6 AAQ7 SWL1 SWL2 SWL3 SWL4 SWL5
rename (S1 A2 D3 A4 D5 S6 A7 S8 A9 D10 S11 S12 D13 S14 A15 D16 D17 S18 A19 A20 D21) (Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10 Q11 Q12 Q13 Q14 Q15 Q16 Q17 Q18 Q19 Q20 Q21)
reshape long Q, i(ID) j(resp)
rename ID id
rename resp item
rename Q resp
destring id, replace
label define D21 1 "S1" 2 "A2" 3 "D3" 4 "A4" 5 "D5" 6 "S6" 7 "A7" 8 "S8" 9 "A9" 10 "D10" 11 "S11" 12 "S12" 13 "D13" 14 "S14" 15 "A15" 16 "D16" 17 "D17" 18 "S18" 19 "A19" 20 "A20" 21 "D21"
label values item D21
sort id
save "/Users/xichen85/Desktop/Ben/DASS_21.dta"
export delimited using "/Users/xichen85/Desktop/CompACT_Ptacek 2024.csv"