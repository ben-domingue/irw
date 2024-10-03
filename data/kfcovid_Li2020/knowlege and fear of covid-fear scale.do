 import excel "/Users/xichen85/Desktop/Ben-test- data_ knowledge and fear of covid/Knowledge and Fear of COVID-19 
> and Perceived Stress.xls", sheet("DataSet") firstrow allstring
(30 vars, 115 obs)

. edit

. drop Age Gender Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10 Q11 Q12

. drop Q1001 Q1002 Q1003 Q1004 AA Survey1Total Survey2Total Survey3Total

. drop in 111/115
(5 observations deleted)

. reshape long Q, i(ID) j (resp)
(j = 101 102 103 104 105 106 107)

rename ID id
rename resp item
rename Q resp

 destring id, replace
id: all characters numeric; replaced as int



. sort id item

. edit
 save "/Users/xichen85/Desktop/knowledge and fear of covid_fear scale.dta"


. export delimited id item resp using "/Users/xichen85/Desktop/knowledge and fear 
> of covid_fear scale.csv"

