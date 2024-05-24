library(readxl)
y <- read_excel("QPart1Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df1=df

y <- read_excel("QPart2Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df2=df

y <- read_excel("QPart3Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df3=df

y <- read_excel("QPart4Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df4=df

y <- read_excel("QPart5Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df5=df

y <- read_excel("QPart6Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df6=df

y <- read_excel("QPart7Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df7=df

y <- read_excel("QPart8Data_objects.xlsx")
x=y[, 19:190 ]
colnames(x)<-x[1,]
x<-x[-1,]
x=x[,-grep("Text", colnames(x)) ]
x=x[, -grep("quality", colnames(x))]
n=dim(x)[2]/8
rater.id= y$IPAddress[-1]
L=list()
for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
df=data.frame()
for (i in 1:n){
  l=L[[i]][,-8]
  id=L[[i]][,8]
  m=list()
  for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
  for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
  d<-data.frame(do.call("rbind",m))
  df=rbind(df, d)
}
df8=df
d=rbind(df1, df2, df3, df4, df5, df6, df7, df8)
save(d, file='Object.stimulus.set.Rdata')
