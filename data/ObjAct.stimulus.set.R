
library(readxl)
y <- read_excel("QPart1Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df1=df
save(df,file='Part1.Rdata')


y <- read_excel("QPart2Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df2=df
save(df,file='Part2.Rdata')


y <- read_excel("QPart3Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df3=df
save(df,file='Part3.Rdata')


y <- read_excel("QPart4Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df4=df
save(df,file='Part4.Rdata')


y <- read_excel("QPart5Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df5=df
save(df,file='Part5.Rdata')


y <- read_excel("QPart6Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df6=df
save(df,file='Part6.Rdata')


y <- read_excel("QPart7Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df7=df
save(df,file='Part7.Rdata')


y <- read_excel("QPart8Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][1,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df8=df
save(df,file='Part8.Rdata')

