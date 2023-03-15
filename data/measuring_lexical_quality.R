## 1. ID: participant number
## 2. SAMPLE: experiment sample label
## 3. AGE: participant age
## 4. GENDER: participant self-reported gender, F=Female; M=Male; O=Other or not specified
## 5. HAND: participant self-reported handedness, L=Left; R=Right 
## 6. ENGL_SPE: English first spoken language, Y=Yes, N=No
## 7. ENGL_SPE: English first read/write language, Y=Yes, N=No
## 8. ND_VOCAB: Nelson-Denny Vocabulary score (number of correct responses)
## 9. ND_COMPR: Nelson-Denny Comprehension score (number of correct responses x 2)
## 10. ND_SPEED: Nelson-Denny Reading Rate (wpm)
## 11. ND_VERS: Nelson-Denny administration condition, full=Standard time limits; half=Reduced time limits
## 12. NDH_VO_A: Number of questions in the Nelson-Denny Vocabulary section attempted at the half-way point for the Full+Half subsample
## 13. NDH_CO_A: Number of questions in the Nelson-Denny Comprehension section attempted at the half-way point for the Full+Half subsample
## 14. NDH_VO_C: Nelson-Denny Vocabulary score at the half-way point for the Full+Half subsample
## 15. NDH_CO_C: Nelson-Denny Comprehension score at the half-way point for the Full+Half subsample
## 16. SPELL_DI: Spelling Dictation Test score (number of correct responses)
## 17. SPELL_RE: Spelling Recognition Test score (number of correct responses)
## 18. TOWRE: Phonemic Decoding Efficiency score
## 19. ART: Author Recognition Test score
## 20-39. SD01-SD20: Item-level Spelling Dictation data, 1=Correct; 0=Incorrect
## 40-127. SR01-SR88: Item-level Spelling Recognition data, 1=Item endorsed as incorrect spelling; 0=Item not endorsed as incorrect spelling

x<-read.csv("LQData.csv",header=TRUE)
id<-x$ID
i<-grep("^SD",names(x))
z<-x[,i]
L<-list()
for (i in 1:ncol(z)) L[[i]]<-data.frame(id=id,item=names(z)[i],resp=z[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="measuring_lexical_quality.Rdata")


##not clear if recognition items are consistently marked
## x<-read.csv("LQData.csv",header=TRUE)
## id<-x$ID
## i<-grep("^SR",names(x))
## z<-x[,i]
## L<-list()
## for (i in 1:ncol(z)) L[[i]]<-data.frame(id=id,item=names(z)[i],resp=z[,i])
## df2<-data.frame(do.call("rbind",L))
