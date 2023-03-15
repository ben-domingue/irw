x <- read.csv("dat_2MFC.csv")
items <- read.csv("items_2MFC.csv")
x$resp<-x$key_press-1
df<-data.frame(id=x$userid,item=x$itemid,resp=x$resp,rt=x$rt/1000)

#https://link.springer.com/article/10.3758/s13428-019-01302-5/tables/3
#Notes: Statements with an asterisk (*) are negative statements; Emo = Emotional Stability (trait number: 1); Ext = Extraversion (2); Agr = Agreeableness (3); Con = Conscientiousness (4); Int = Intellect/Imagination (5); Japanese versions of the statements are available at https://ipip.ori.org/JapaneseBig-FiveFactorMarkers.htm
vals<-c('emotional stability','extraversion','agreeableness','conscientousness','imagination')
val0<-vals[items$M1]
val1<-vals[items$M2]
negative0<-items$R1
negative1<-items$R2
items<-data.frame(item=1:nrow(items),val0=val0,val1=val1,negative0=negative0,negative1=negative1)
attr(df,which='item')<-items

save(df,file="thurstonian_ddiffusion.Rdata")
