library(foreign)
x<-read.spss("Race IAT.public.2021.sav",to.data.frame=TRUE)

x<-x[x$num_002==0,]
x$id<-1:nrow(x)
x$race<-x$raceomb_002

## ##
## nms<-c("anes1", "anes2", "anes3", "anes4", "anes5", "anes6" 
## #"atb1", "atb2", "atb3", "atb4", "atb5", "atb6", "atb7", "atb8", 
## #"atb9", "atb10", "atb11", "atb12", "atb13", "atb14", "atb15", 
## #"atb16", "atb17", "atb18", "atb19", "atb20", "atw1", "atw2", 
## #"atw3", "atw4", "atw5", "atw6", "atw7", "atw8", "atw9", "atw10", 
## #"atw11", "atw12", "atw13", "atw14", "atw15", "atw16", "atw17", 
##        #"atw18", "atw19", "atw20"
##        )

## z<-x[,nms]
## L<-list()
## for (i in 1:ncol(z)) {
##     xx<-data.frame(id=x$id,race=x$race,item=names(z)[i],resp=z[,i])
##     L[[i]]<-xx[!is.na(xx$resp),]
## }
## df<-data.frame(do.call("rbind",L))

    

nms<-c("efp1", "efp2", 
"efp3", "efp4", "efp5", "efp6", "efp7", "efp8", "efp9", "efp10", 
"efp11", "efp12")
z<-x[,nms]
L<-list()
for (i in 1:ncol(z)) {
    xx<-data.frame(id=x$id,race=x$race,item=names(z)[i],resp=z[,i])
    L[[i]]<-xx[!is.na(xx$resp),]
}
df<-data.frame(do.call("rbind",L))
levs<-c("Not at All Important","Slightly Important","Moderately Imporant","Very Important","Extremely Important")
ii<-match(df$resp,levs)
df$resp<-ii
save(df,file="iat_poverty.Rdata")

nms<-c("uo1", "uo2", "uo3", "uo4", "uo5", 
"uo6", "uo7", "uo8", "uo9", "uo10", "uo11", "uo12", "uo13", "uo14", 
"uo15", "uo16", "uo17", "uo18", "uo19", "uo20")
z<-x[,nms]
L<-list()
for (i in 1:ncol(z)) {
    xx<-data.frame(id=x$id,race=x$race,item=names(z)[i],resp=z[,i])
    L[[i]]<-xx[!is.na(xx$resp),]
}
df<-data.frame(do.call("rbind",L))
levs<-c("Strongly Disagree", "Moderately Disagree", "Slightly Disagree", 
"Neither Agree Nor Disagree", "Slightly Agree", "Moderately Agree", 
"Strongly Agree")
ii<-match(df$resp,levs)
df$resp<-ii
save(df,file="iat_difference.Rdata")
