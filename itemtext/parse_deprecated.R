##getting irw data
df<-irw::irw_fetch("coach_chen_2022_phq9") ##see authentication and installation notes here. https://github.com/ben-domingue/irwpkg

library(gsheet)
tabs <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1jvwxYJ3gjSpEDtx4km-8czvDXu7iEIHhF5V5Y9VWNG0/edit?gid=0#gid=0')

f<-function(table,tabs) {
    L<-list()
    ii<-grep(table,tabs$table)
    for (i in 1:4) L[[i]]<-gsheet2tbl(tabs[ii,i+1])
    L
}
##getting text data for same table
L<-f("coach_chen_2022_phq9",tabs) ##note that i changed to lowercase

##a match of these is critical
unique(df$item)
unique(L[[3]]$item)
## > unique(df$item)
## [1] "pcp_phq9_q1" "pcp_phq9_q2" "pcp_phq9_q3" "pcp_phq9_q4" "pcp_phq9_q5" "pcp_phq9_q6"
## [7] "pcp_phq9_q7" "pcp_phq9_q8" "pcp_phq9_q9"
## > unique(L[[3]]$item)
## [1] "pcp_phq9_q1" "pcp_phq9_q2" "pcp_phq9_q3" "pcp_phq9_q4" "pcp_phq9_q5" "pcp_phq9_q6"
## [7] "pcp_phq9_q7" "pcp_phq9_q8" "pcp_phq9_q9"

z<-L[[3]]
z<-z[,c("item","item_text")]
dim(df)
df<-merge(df,z)
dim(df)

z<-L[[4]]
z<-z[,c("item","resp","option_text")]
dim(df)
df<-merge(df,z)
dim(df)

head(df)
