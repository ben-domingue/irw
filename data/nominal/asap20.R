##https://github.com/scrosseye/ASAP_2.0/blob/main/ASAP_2_Final_github_train.zip
x<-read.csv("ASAP_2_Final_github_train.csv")
x$full_text->essays
id<-x$essay_id
resp<-x$score
item<-x$prompt_name

df<-data.frame(id=id,resp=resp,item=item)

nm <-
c("economically_disadvantaged", "student_disability_status", "ell_status", 
"race_ethnicity", "gender", "grade_level")
z<-x[,nm]
names(z)<-paste("cov_",nm,sep='')
for (nm in names(z)) df[[nm]]<-z[[nm]]
df$item<-gsub("\"","",df$item)

essays<-gsub("\n","[newline]",essays)
essays<-gsub("¨","\"",essays)
df$text<-essays

write.table(df,file="asap20train.csv",quote=FALSE,row.names=FALSE,sep="|")
