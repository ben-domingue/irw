## The item text is abbreviated here, see https://sites.sas.upenn.edu/duckworth/pages/research for the full items

## GS1	I have...
## GS2	New ideas...
## GS3	My interests...
## GS4	Setbacks don't...
## GS5	I have been...
## GS6	I am...
## GS7	I often...
## GS8	I have...
## GS9	I finish...
## GS10	I have...
## GS11	I become...
## GS12	I am...

## The following items were presented as a check-list and subjects were instructed "In the grid below, check all the words whose definitions you are sure you know":

## VCL1	boat
## VCL2	incoherent
## VCL3	pallid
## VCL4	robot
## VCL5	audible
## VCL6	cuivocal
## VCL7	paucity
## VCL8	epistemology
## VCL9	florted
## VCL10	decide
## VCL11	pastiche
## VCL12	verdid
## VCL13	abysmal
## VCL14	lucid
## VCL15	betray
## VCL16	funny

## A value of 1 is checked, 0 means unchecked. The words at VCL6, VCL9, and VCL12 are not real words and can be used as a validity check.

x<-read.table("data.csv",sep="\t",header=TRUE)
z<-x[,c("VCL6","VCL9","VCL12"),]
x<-x[rowSums(z)==0,]
x<-x[,paste("GS",1:12,sep='')]

library(psych)
alpha(x)
#rev 7, 2, 11, 3,5,8 
for (i in 1:ncol(x)) x[,i]<-ifelse(x[,i]==0,NA,x[,i])
for (i in c(7,2,11,3,5,8)) x[,i]<-6-x[,i]
alpha(x)

names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="grit.Rdata")
