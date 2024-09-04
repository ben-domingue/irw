x<-read.csv("Prelim Data.csv",sep="|")
rater<-x$Subject.Code
id<-x$Sample.Name
intense<-x$How.intense.do.you.find.this.aroma.
pleasant<-x$Pleasantness
familiar<-x$Familiarity
x1<-data.frame(rater=rater,id=id,item='intense',resp=intense)
x2<-data.frame(rater=rater,id=id,item='pleasant',resp=pleasant)
x3<-data.frame(rater=rater,id=id,item='familiar',resp=familiar)
df<-data.frame(do.call("rbind",list(x1,x2,x3)))
save(df,file="wine_luckett2021.Rdata")
