##https://www.kaggle.com/datasets/datasnaek/chess

x<-read.csv('games.csv')
x<-x[,c("winner","white_id","white_rating","black_id","black_rating","last_move_at")]

##this data is compromised as dates aren't recoverable
