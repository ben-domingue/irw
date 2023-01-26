
mat<-matrix(ncol=2,byrow=TRUE,
       c("t_month2","moca_month2",
         "t_date3",NA,
         "t_rhino","moca_rhino",
         "t_clock","moca_clock",
         "t_trail","moca_trail",
         "t_immed1","immed1",
         "t_immed2","immed2",
         "t_digits5","moca_5numbers",
         "t_digits3","moca_3numbers",
         "t_subtract","moca_subtract",
         "t_cat","moca_sentcat",
         "t_word2","moca_word2",
         "t_ruler","moca_alike2",
         "t_delayed","delayed"
         )
       )


#w2<-read.csv("nshap_w2_moca_times.csv")
w3<-read.csv("nshap_w3_moca_times.csv")
setwd("./ICPSR_36873/DS0001/")
load("36873-0001-Data.rda")
df<-da36873.0001
names(df)<-tolower(names(df))
##ii<-grep("moca",names(df))

tmp<-df[,c("moca_ir1_church","moca_ir1_daisy","moca_ir1_face","moca_ir1_red","moca_ir1_velvet")]
for (i in 1:ncol(tmp)) ifelse(tmp[,i]=="(1) Repeated",1,0)->tmp[,i]
df$immed1<-rowSums(tmp)
##
tmp<-df[,c("moca_ir2_church","moca_ir2_daisy","moca_ir2_face","moca_ir2_red","moca_ir2_velvet")]
for (i in 1:ncol(tmp)) ifelse(tmp[,i]=="(1) Repeated",1,0)->tmp[,i]
df$immed2<-rowSums(tmp)
##
tmp<-df[,c("moca_church","moca_daisy","moca_face","moca_red","moca_velvet")]
for (i in 1:ncol(tmp)) ifelse(tmp[,i]=="(1) Repeated",1,0)->tmp[,i]
df$delayed<-rowSums(tmp)

L<-list()
for (i in 1:nrow(mat)) {
    if (!is.na(mat[i,2])) {
        nm<-mat[i,1]
        nm<-gsub("t_","",nm,fixed=TRUE)
        x1<-w3[,c("id",mat[i,1])]
        x2<-df[,c("id","age",mat[i,2])]
        names(x1)[2]<-'rt'
        names(x2)[3]<-'resp'
        x<-merge(x1,x2)
        x$item<-nm
        L[[nm]]<-x
    }
}

key<-list(month2="(1) Correct",
       rhino="(1) Rhino (or rhinoceros)",
       clock="(1) Completed task",
       trail="(1) Completed task",
       digits5="(1) Correct answer",
       digits3="(1) Correct answer",
       cat="(1) Correct answer",
       word2="(1) Correct",
       ruler=c("(1) Measuring instruments","(2) Used to measure"),
       subtract=3:5,
       immed1=5,
       immed2=5,
       delayed=3:5
       )

for (i in 1:length(L)) {
    x<-L[[i]]
    print(unique(x$item))
    print(table(x$resp))
    k<-key[[names(L)[i] ]]
    x$resp2<-ifelse(x$resp %in% k,1,0)
    print(table(x$resp,x$resp2))
    x$resp2->x$resp
    NULL->x$resp2
    L[[i]]<-x
}
x<-data.frame(do.call("rbind",L))

df<-x

save(df,file='nshap.Rdata')
