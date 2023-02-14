
x<-read.csv("enem_imv.csv")
x$item<-x$itemkey
x$itemkey<-NULL
x$id<-as.character(x$id)
x$item<-paste("item_",x$item,sep='')

df<-x
save(df,file="enem.Rdata")
