tabs<-irwpkg::irw_list_datasets()
tabs<-tolower(tabs$name)

library(gsheet)
work<-gsheet2tbl('https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123')
tabs.done<-work$Table

all(tabs.done %in% tabs) ##confirming all is well

index<-tabs %in% tabs.done ##to remove
tabs.todo<-tabs[!index]
any(tabs.todo %in% tabs.done) ##confirming all is well

z<-sample(tabs.todo,30)
write.csv(z,'',quote=FALSE,row.names=FALSE)
