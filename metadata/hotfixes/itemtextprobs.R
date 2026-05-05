x<-read.csv("itemtext_metadata.csv")
x[x$mean_word>5 & x$mean_character<20,]
