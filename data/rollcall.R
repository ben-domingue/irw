##https://voteview.com/data
x<-read.csv("HSall_votes.csv")

## Cast Codes
## cast_code	Description
## 0	Not a member of the chamber when this vote was taken
## 1	Yea
## 2	Paired Yea
## 3	Announced Yea
## 4	Announced Nay
## 5	Paired Nay
## 6	Nay
## 7	Present (some Congresses)
## 8	Present (some Congresses)
## 9	Not Voting (Abstention)

f<-function(x) {
    x$item<-paste(x$congress,x$rollnumber,sep="__")
    x$id<-x$icpsr
    #
    z<-x$cast_code
    z<-ifelse(z %in% c(0,7:9),NA,z)
    z<-ifelse(z %in% c(1,2,3),1,z)
    z<-ifelse(z %in% c(4,5,6),0,z)
    x$resp<-z
    df<-x[,c("item","id","resp")]
    df
}

y<-x[x$chamber=="House",]
df<-f(y)
save(df,file="rollcall_house.Rdata")

y<-x[x$chamber=="Senate",]
df<-f(y)
save(df,file="rollcall_senate.Rdata")
