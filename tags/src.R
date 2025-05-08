tabs<-irw::irw_list_tables()
tabs<-tolower(tabs$name)

library(gsheet)
work<-gsheet2tbl('https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123')
tabs.done<-tolower(work$Table)[-1]
tabs.done<-tabs.done[!is.na(tabs.done)]

all(tabs.done %in% tabs) ##confirming all is well, should be TRUE

index<-tabs %in% tabs.done ##to remove
tabs.todo<-tabs[!index]
any(tabs.todo %in% tabs.done) ##confirming all is well, should be FALSE

z<-sample(tabs.todo,50)
write.csv(z,'',quote=FALSE,row.names=FALSE)




##
##organizing queue
x<-gsheet::gsheet2tbl('https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=48265913#gid=48265913')
tab<-table(x)
tab[tab>1]
