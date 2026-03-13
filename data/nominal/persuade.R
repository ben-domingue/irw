##https://www.kaggle.com/datasets/julesking/tla-lab-persuade-dataset?select=persuade_train_srctexts.csv

## wget -O persuade_train_srctexts.csv "https://storage.googleapis.com/kagglesdsdata/datasets/5585591/10630493/persuade_train_srctexts.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20260312%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20260312T172345Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=46130396c5fcd2e96bc8d6d9ca0f8e18418d9c9d3d76acc1c7dc68e6beb0893b8061ef602ea4da79db0f3b13858bdbc21a3fda028ab72e930ed6721f3746f7ba1c4789b2453ba1f14d2cc61583553bed0c9bed5e8aebc8a9e4f10bc55679ec0924d1a044b73890449c8acb86c00d3ad7d293b02af5ef957fb0e3255d66c7415ffb2c7251f185458b8c24e11f2c0768aa8102c17f9e39e769df4e66259a4438fffef66501856fc4ceb97f6f3377a3fe206096db4da4b6b00846fe8920f10af83f3d14fb1db5015a39bac7ed395df04eda98db43c2338a45761df9bea4d8546e05b7861e6f1d71bfbdb8ec4c17c68e5a63ff86fa9988f10bee7a57a1133fdbd6a8"

x<-read.csv("persuade_train_srctexts.csv")
nms<-names(x)
dump("nms","")

names(x)<-c("essay_id_comp", "discourse_id", "discourse_start", "discourse_end", 
"discourse_type", "predictionstring", "discourse_text", "discourse_effectiveness", 
"discourse_type_num", "hierarchical_id", "hierarchical_text", 
"hierarchical_label", "prompt_name", "assignment", "gender", 
"grade_level", "ell_status", "race_ethnicity", "economically_disadvantaged", 
"student_disability_status", "source_text_1", "source_text_2", 
"source_text_3", "source_text_4", "task")


##id/item/cov_g
'


essays<-gsub("\"","'",essays)
df$text<-essays

write.table(df,file="asap20train.csv",row.names=FALSE,sep="|")
