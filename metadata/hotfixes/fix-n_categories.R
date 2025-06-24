##fix n_categories [in particular, NA values are currently reporting as 'real' and messing up counts]

##new tables
library(redivis)
v1<- redivis$organization("datapages")$dataset("Item Response Warehouse")
tables<-v1$list_tables()
new.tables<-sapply(tables,function(x) x$name)
length(new.tables)

f<-function(tab) {
  getvars<-function(tab) {
      variables <- tab$list_variables() 
      nms<-sapply(variables,function(x) x$get()$properties$name)
      stats<-lapply(variables,function(x) x$get_statistics() ) 
      ##
      resp.index<-which(nms=="resp")
      variable<-variables[[resp.index]]
      out<-variable$get_statistics()
      out<-out$frequencyDistribution
      z<-lapply(out,function(x) x$value)
      z<-z[!sapply(z,is.null)]
      ncats<-as.numeric(unlist(z))
      n_categories<-length(ncats[!is.na(ncats)])
      ##
      ##
      testvec<-c(n_categories=n_categories
                 )
      testvec
  }
  try.counter<-0
  while (try.counter<4) { #sometimes the download fails, this gives multiple tries to get that
      testvec<-getvars(tab)
      if (length(testvec)==7) try.counter<-100 else try.counter<-try.counter+1
  }
  return(testvec)
}

nc<-numeric()

for (i in 1:length(tables)) {
    print(i)
    nc[i]<-f(tables[[i]])
}


nc<-data.frame(tolower(new.tables),nc)
write.csv(nc,'n_categories.csv',quote=FALSE,row.names=FALSE)
           
