library(gsheet)
tag <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123')
tag<-tag[-1,c(1,6:12)]
n<-apply(tag[,-1],1,function(x) sum(!is.na(x)))
tag[n>0,]

readr::write_csv(tag, "tags.csv")
