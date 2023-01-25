#(2016). Adaptive geography practice data set. Journal of Learning Analytics, 3(2), 317–321. http://dx.doi.org/10.18608/jla.2016.32.17

#https://www.fi.muni.cz/adaptivelearning/data/slepemapy/

## |        Column       | Description                                                                                          |
## |:-------------------:|:----------------------------------------------------------------------------------------------------:|
## |          id         | answer identifier                                                                                    |
## |         user        | user's identifier                                                                                    |
## |     place_asked     | identifier of the asked place                                                                        |
## |    place_answered   | identifier of the answered place, empty if the user answered "I don't know"                          |
## |         type        | type of the answer: (1) find the given place on the map; (2) pick the name for the highlighted place |
## |        options      | list of identifiers of options (the asked place included)                                            |
## |       inserted      | datetime (yyyy-mm-dd HH:mm:ss) when the answer was inserted to the system                            |
## |     response_time   | how much time the answer took (measured in milliseconds)                                             |
## |       place_map     | identifier of the place representing a map for which the question was asked                          |
## |      ip_country     | country retrieved from the user’s IP address                                                         |
## |        ip_id        | meaningless identifier of the user’s IP address                                                      |

x<-read.csv("answer.csv",sep=";")

df<-x[,c("user","response_time")]
names(df)[1]<-'id'
df$date<-x$inserted
df$resp<-ifelse(x$place_asked==x$place_answered,1,0)

z<-x$options
z<-gsub("[","",z,fixed=TRUE)
z<-gsub("]","",z,fixed=TRUE)
z<-strsplit(z,",")
f<-function(a,b) {
    b<-as.numeric(b)
    ii<-which(b==a)
    ab<-paste(a,paste(b[-ii],collapse='.'),sep='__')
    ab
}
f<-Vectorize(f)
df$item<-f(x$place_asked,z)
df$item<-paste(df$item,x$type,sep="__")

df$item_key<-x$place_asked

save(df,file='geography.Rdata')
