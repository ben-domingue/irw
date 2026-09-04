x<-read.csv("Ratings_RawData.csv")
x<-x[x$Filter==1,]
x<-x[x$Rating %in% 1:5,]
# The rated multiword expression is the item; the Qualtrics respondent is the
# person. These two were the wrong way round, which put anonymous ResponseIDs on
# the item axis and made item text permanently unattachable (issue #1876).
item<-x$Expression
id<-x$Participant
resp<-x$Rating

df<-data.frame(id=id,item=item,resp=resp)
save(df,file="concretewords.Rdata")
