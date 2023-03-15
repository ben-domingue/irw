library(foreign)
x<-read.dta("/home/bd/Dropbox/projects/hrs/web/data/randhrs1992_2018v2.dta",
            convert.factors=FALSE)

## ##iadls, adls, chronic conditions
## RwHIBPE, RwDIABE, RwCANCRE, RwLUNGE, RwHEARTE, RwSTROKE, RwPSYCHE, and RwARTHRE
## R2WALKRA:W2
## R2DRESSA:W2
## R2BATHA:W2
## R2EATA:W2
## R2BEDA:W2
## R2TOILTA:W2
## R2MAPA:W2
## R2PHONEA:W2
## R2MONEYA:W2
## R2MEDSA:W2
## R2SHOPA:W2
## R2MEALSA:W2

L<-list()
for (i in 2:13) {
    tmp.nms<-c("hhidpn","rabyear",
               paste("r",i,"iwendy",sep=""),
               ##
               paste("r",i,"hibpe",sep=""),
               paste("r",i,"diabe",sep=""),
               paste("r",i,"cancre",sep=""),
               paste("r",i,"lunge",sep=""),
               paste("r",i,"hearte",sep=""),
               paste("r",i,"stroke",sep=""),
               paste("r",i,"psyche",sep=""),
               paste("r",i,"arthre",sep=""),
               ##adls
               paste("r",i,"walkra",sep=""),
               paste("r",i,"dressa",sep=""),
               paste("r",i,"batha",sep=""),
               paste("r",i,"eata",sep=""),
               paste("r",i,"beda",sep=""),
               paste("r",i,"toilta",sep=""),
               ##iadls
               paste("r",i,"mapa",sep=""),
               paste("r",i,"phonea",sep=""),
               paste("r",i,"moneya",sep=""),
               paste("r",i,"medsa",sep=""),
               paste("r",i,"shopa",sep=""),
               paste("r",i,"mealsa",sep="")
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
xx<-xx[!is.na(xx$iwendy),]

conditions<-c("hibpe", "diabe", "cancre", "lunge", "hearte", "stroke", "psyche", "arthre")
adls<-c("walkra", "dressa", "batha", "eata", "beda", "toilta")
iadls<-c("mapa", "phonea", "moneya", "medsa", "shopa", "mealsa")
id<-xx$hhidpn
interview.year<-xx$iwendy
birth.year<-xx$rabyear
L<-list()
nms<-c(conditions,adls,iadls)
for (nm in nms) L[[nm]]<-data.frame(id=id,interview.year=interview.year,birth.year=birth.year,item=nm,resp=xx[,nm])
df<-data.frame(do.call("rbind",L))

txt<-ifelse(df$item %in% conditions,paste("conditions",df$item,sep='.'),df$item)
txt<-ifelse(txt %in% adls,paste("adls",txt,sep='.'),txt)
txt<-ifelse(txt %in% iadls,paste("iadls",txt,sep='.'),txt)
df$item<-txt

t<-paste(df$interview.year,"-1-1",sep='')
t<-as.POSIXlt(t)
t<-as.numeric(t)
df$date<-t

save(df,file="/home/bd/Dropbox/projects/irw/priv/hrs_health.Rdata")
