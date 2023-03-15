##all data sheet from excel spreadsheet

x<-read.csv("all_data.csv",header=TRUE,sep="|")
rater<-x$sub_num
item<-x$condition
id<-x$stimulus
resp<-x$response
rt<-x$rt/1000

df<-data.frame(id=id,rater=rater,item=item,resp=resp,rt=rt)
save(df,file="famous_melodies.Rdata")
