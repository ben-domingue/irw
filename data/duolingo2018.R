##only 4 users???? the person id seems wrong...


##http://sharedtask.duolingo.com/2018.html#task-definition-data
##Settles, Burr, 2018, "Data for the 2018 Duolingo Shared Task on Second Language Acquisition Modeling (SLAM)", https://doi.org/10.7910/DVN/8SWHNO, Harvard Dataverse, V4, https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/8SWHNO

con<-file("en_es.slam.20190204.train")
x<-readLines(con)
close(con)


index<-grep("# prompt",x)
index<-c(index,length(x))
L<-list()
for (i in 1:(length(index)-1)) L[[i]]<-x[index[i]:(index[i+1]-1)]

f<-function(x) {
    item<-gsub("# prompt:","",x[1])
    users<-grep("user:",x)
    ##
    out<-list()
    for (j in 1:length(users)) {
        z<-strsplit(x[users[j]]," ")[[1]][-1]
        z<-z[z!=""]
        z<-strsplit(z,":")
        nms<-sapply(z,"[",1,drop=FALSE)
        dat<-sapply(z,"[",2,drop=FALSE)
        ##response
        mm<-ifelse(j==length(users),length(x),users[j+1]-1)
        z<-strsplit(x[(users[j]+1):mm]," ")
        z<-lapply(z,function(z) z[z!=""])
        z<-data.frame(do.call("rbind",z))
        ## A Unique 12-digit ID for each token instance: the first 8 digits are a B64-encoded ID representing the session, the next 2 digits denote the index of this exercise within the session, and the last 2 digits denote the index of the token (word) in this exercise
        ## The token (word)
        ## Part of speech in Universal Dependencies (UD) format
        ## Morphological features in UD format
        ## Dependency edge label in UD format
        ## Dependency edge head in UD format (this corresponds to the last 1-2 digits of the ID in the first column)
        ##     The label to be predicted (0 or 1)
        names(z)<-c("resp.id","token","part.speech","morphology","dependency.label","dependency.head","resp")
        ##
        z$item<-item
        for (i in 1:length(nms)) z[nms[i]]<-dat[i]
        z$resp<-as.numeric(z$resp)
        out[[as.character(j)]]<-z
    }
    data.frame(do.call("rbind",out))
}
options(warn=2)
#for (i in 1:length(L)) L[[i]]<-f(L[[i]])
library(parallel)
L<-mclapply(L,f,mc.cores=3)

types<-c("reverse_translate","reverse_tap","listen")
L2<-list()
for (type in types) L2[[type]]<-list()
for (i in 1:length(L)) {
    x<-L[[i]]
    ##just us
    #x<-x[x$countries=="US",]
    ##
    levs<-unique(x$format)
    for (lev in levs) {
        L2[[lev]][[as.character(i)]]<-x[x$format==lev,]
    }
    print(i/length(L))
}

for (i in 1:length(L2)) {
    print(i)
    L<-L2[[i]]
    df<-data.frame(do.call("rbind",L))
    ##
    df$id<-df$user
    df$user<-NULL
    df$stem<-df$item
    df$item<-paste(df$item,df$token,sep="__")
    df$token<-NULL
    ##
    print(length(unique(df$id)))
    print(length(unique(df$item)))
    ##
    fn<-paste('duolingo__',names(L2)[i],'.Rdata',sep='')
    save(df,file=fn)
}
