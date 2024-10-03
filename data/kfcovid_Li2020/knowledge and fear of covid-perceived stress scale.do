 import excel "/Users/xichen85/Desktop/Ben-test- data_ knowledge and fear of covi
> d/Knowledge and Fear of COVID-19 and Perceived Stress.xls", sheet("DataSet") fir
> strow allstring
(30 vars, 115 obs)

. drop Age Gender

. drop AA Survey1Total Survey2Total Survey3Total

. drop in 111/115




. drop Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10 Q11 Q12 Q101 Q102 Q103 Q104 Q105 Q106 Q107

. reshape long Q, i(ID) j (resp)
(j = 1001 1002 1003 1004)

Data                               Wide   ->   Long
-----------------------------------------------------------------------------
Number of observations              110   ->   440         
Number of variables                   5   ->   3           
j variable (4 values)                     ->   resp
xij variables:
                  Q1001 Q1002 ... Q1004   ->   Q
-----------------------------------------------------------------------------

. rename ID id

. 
. rename resp item

. 
. rename Q resp

. 
. destring id, replace
id: all characters numeric; replaced as int

. 
. sort id item

. 
. 
. save "/Users/xichen85/Desktop/knowledge and fear of covid-perceived stress scale
> .dta"
file /Users/xichen85/Desktop/knowledge and fear of covid-perceived stress
    scale.dta saved

. export delimited id item resp using "/Users/xichen85/Desktop/knowledge and fear 
> of covid-perceived stress scale.csv"
file /Users/xichen85/Desktop/knowledge and fear of covid-perceived stress scale.cs
> v saved

. 
