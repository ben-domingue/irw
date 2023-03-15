library(foreign)
x<-read.dta("/home/bd/Dropbox/projects/hrs/web/data/randhrs1992_2018v2.dta",
            convert.factors=FALSE)


L<-list()
for (i in 2:13) {
    tmp.nms<-c("hhidpn","rabyear",
               paste("r",i,"iwendy",sep=""),
               paste("r",i,"depres",sep=""),
               paste("r",i,"effort",sep=""),
               paste("r",i,"sleepr",sep=""),
               paste("r",i,"flone",sep=""),
               paste("r",i,"fsad",sep=""),
               paste("r",i,"going",sep=""),
               paste("r",i,"whappy",sep=""),
               paste("r",i,"enlife",sep=""),
               paste("r",i,"cesd",sep="")
               )
    tmp.index<-    tmp.nms %in% names(x)
    tmp<-x[,tmp.nms[tmp.index]]
    ##in case any variables aren't available
    bad.nms<-tmp.nms[!tmp.index]
    if (length(bad.nms)>0) {
        for (nm in bad.nms) tmp[[nm]]<-NA
        tmp<-tmp[,tmp.nms]
    }
    txt<-paste("r",i,sep="")
    names(tmp)<-gsub(txt,'',names(tmp))
    L[[as.character(i)]]<-tmp
}

xx<-do.call("rbind",L)
xx<-xx[!is.na(xx$cesd),]


## depres effort sleepr flone fsad going whappy enlife
## RwCESD is the sum of RwDEPRES, RwEFFORT, RwSLEEPR, (1-RwWHAPPY), RwFLONE, RwFSAD, RwGOING, and
## (1-RwENLIFE).    
xx$whappy.rev<- 1-xx$whappy
xx$enlife.rev<- 1-xx$enlife
nms<-c("depres","effort","sleepr","flone","fsad","going","whappy.rev","enlife.rev")
plot(xx$cesd,rowSums(xx[,nms]))
xx$whappy<-xx$enlife<-xx$cesd<-NULL

id<-xx$hhidpn
interview.year<-xx$iwendy
birth.year<-xx$rabyear
L<-list()
for (nm in nms) L[[nm]]<-data.frame(id=id,interview.year=interview.year,birth.year=birth.year,item=nm,resp=xx[,nm])
df<-data.frame(do.call("rbind",L))


t<-paste(df$interview.year,"-1-1",sep='')
t<-as.POSIXlt(t)
t<-as.numeric(t)
df$date<-t

save(df,file="/home/bd/Dropbox/projects/irw/priv/hrs_cesd.Rdata")

