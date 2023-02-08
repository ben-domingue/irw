list.files(pattern="*_2007_.+responses.txt")->lf
for (i in 1:length(lf)) {
    lf[i]->fn
    read.table(fn,header=TRUE)->x
    names(x)<-tolower(names(x))
    L<-list()
    for (j in 1:ncol(x)) L[[j]]<-data.frame(item=names(x)[j],id=1:nrow(x),resp=as.numeric(x[,j]))
    df<-data.frame(do.call("rbind",L))
    save(df,file=paste('state_',gsub(".txt",".Rdata",fn),sep=""))
}

c("state_c1_2007_10_responses.Rdata", "state_c1_2007_3_responses.Rdata", 
"state_c1_2007_4_responses.Rdata", "state_c1_2007_5_responses.Rdata", 
"state_c1_2007_6_responses.Rdata", "state_c1_2007_7_responses.Rdata", 
"state_c1_2007_8_responses.Rdata", "state_c1_2007_9_responses.Rdata", 
"state_c3_2007_5_responses.Rdata", "state_c3_2007_6_responses.Rdata", 
"state_c3_2007_7_responses.Rdata", "state_c3_2007_8_responses.Rdata", 
"state_c3_2007_9_responses.Rdata")
