load("CredentialForm1.RData")
x<-CredentialForm1
## EID: Examinee ID (character)
## • FormID: Test form name (character)
## • Flagged: 1/0 variable to indicate whether the test vendor suspects the examinee may have
## engaged in inappropriate behavior (numeric)
## • Pretest: Pretest item set assigned to candidate (numeric)
## • Attempt: Count of the attempt number for the candidate. A score of 1 indicates that candidate
## is a new, first-time examinee. Any examinee sitting for the exam for the fourth time or more
## is marked as 4+ (character)
## • Country: Country where candidate was educated (character)
## • StateCode: 2-digit code corresponding to the state in which the Candidate applied for licensure
## (numeric)
## • School_ID: 4-digit code corresponding to the particular institution in which the Candidate
## received his/her educational training (numeric)
## • Cent_id: 4-digit code corresponding to the particular testing center in which the Candidate sat
## for the exam (numeric)
## • Tot_time: The number of seconds testing (numeric)
## • iresp.1-170: item responses (1 to 4 or NA) for scored items 1 – 170 (numeric)
## • iresp.171-180: item responses (1 to 4 or NA) for 10 pilot items for pilot set 6 or 9 (numeric)
## • iresp.181-190: item responses (1 to 4 or NA) for 10 pilot items for pilot set 7 or 10 (numeric)
## • iresp.191-200: item responses (1 to 4 or NA) for 10 pilot items for pilot set 8 or 11 (numeric)
## • iraw.1-170: item correct score (1 or 0) for scored items 1 – 170 (numeric)
person<-x[,c("EID","Flagged","Pretest","Attempt","Country","StateCode","School_ID","Cent_id","Tot_time")]
names(person)[1]<-'id'
rt<-x[,paste("idur",1:200,sep=".")]
x<-x[,paste("iraw",1:200,sep=".")]
L<-list()
id<-person$id
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],rt=rt[,i])
df<-data.frame(do.call("rbind",L))
attr(df,which='id')<-person
save(df,file='credentialform_lnirt.Rdata')


load("AmsterdamChess.RData")
x<-AmsterdamChess
elo<-x$ELO
rt<-x[,paste("RT",1:40,sep="")]
x<-x[,paste("Y",1:40,sep="")]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],rt=rt[,i],elo=elo)
df<-data.frame(do.call("rbind",L))
df$resp<-ifelse(df$resp>1,NA,df$resp)
save(df,file='chess_lnirt.Rdata')
