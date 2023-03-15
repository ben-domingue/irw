#https://link.springer.com/article/10.3758/s13428-021-01573-x#citeas

## Experiment 1 - lexical decision; item recognition/memory

## Note: word frequencies are after Kucera & Francis

## Columns:

## 1.  subject_number - subject number
## 2.  block_number - test block number within subject
## 3.  stimulus_number - stimulus number within test block
## 4.  response_key_ID - response key ID
##     For task number 1: 
##       key ID = 1 for "valid word" response
##       key ID = 2 for "nonword word" response
##     For task number 2: 
##       key ID = 1 for "studied word" response
##       key ID = 2 for "new word" response
##     For both tasks:
##       key ID = 0 for "invalid keypress" response
## 5.  reaction_time - reaction time (RT) in milliseconds
## 6.  task_number
##     Task number = 1 for lexical decision
##     Task number = 2 for item recognition/memory
## 7.  column_7_value 
##     For task number 1: 
##       column_7_value = 1 for "valid word"
##       column_7_value = 2 for "nonword"
##       Note - for task number 1, nonwords are associated with the word
##         pool from which each was derived.
##     For task number 2: 
##       column_7_value = 1 for high frequency pool
##       column_7_value = 2 for low frequency pool
##       column_7_value = 3 for very low frequency pool
##     For both tasks:
##       column_7_value = 9 for practice trials
## 8.  column_8_value
##     For task number 1: 
##       column_8_value = 1 for high frequency pool
##       column_8_value = 2 for low frequency pool
##       column_8_value = 3 for very low frequency pool
##     For task number 2: 
##       column_8_value = 1 for "study word, presented 2 times"
##       column_8_value = 2 for "study word, presented 1 time"
##       column_8_value = 3 for "new word"
## 9.  word_length = number of characters in the stimulus string
## 10. word_id = an index number identifying the word in its word pool
## 11. test_word_string = the character string presented at test


x<-read.csv("Experiment1.data",header=TRUE)
x<-x[x$column_7_value!=9,]
x$response_key_ID<-ifelse(x$response_key_ID==0,NA,x$response_key_ID)

x1<-x[x$task_number==1,]
x1$resp<-ifelse(x1$response_key_ID==x1$column_7_value,1,0)

x2<-x[x$task_number==2,]
z<-ifelse(x2$column_8_value %in% 1:2,1,2)
x2$resp<-ifelse(x2$response_key_ID==z,1,0)

f<-function(x) {
    id<-x$subject_number
    block<-x$block_number
    order<-x$stimulus_number
    rt<-x$reaction_time/1000
    item<-x$test_word_string
    df<-data.frame(id=id,block=block,order=order,rt=rt,resp=x$resp,item=item)
    df
}

df<-f(x1)
table(df$resp)
save(df,file="mturkddm_lexical.Rdata")

df<-f(x2)
table(df$resp)
save(df,file="mturkddm_recognition.Rdata")




## Experiment 2 - dot difference; dot numerosity

## Note: The "area" values below are the sum of the squares of 
## the radii of individual dots. Multiply by pi to get the actual
## total dot area in square pixels.

## Columns:

## 1.  subject_number - subject number
## 2.  block_number - test block number within subject
## 3.  stimulus_number - stimulus number within test block
## 4.  response_key_ID - response key ID
##     For task number 1: 
##       key ID = 1 for "more yellow dots"
##       key ID = 2 for "more blue dots"
##     For task number 2: 
##       key ID = 1 for "number of dots greater than 25"
##       key ID = 2 for "number of dots less than 25"
##     For both tasks:
##       key ID = 0 for "invalid keypress" response
## 5.  reaction_time - reaction time (RT) in milliseconds
## 6.  task_number
##     Task number = 1 for dot difference
##     Task number = 2 for dot numerosity
## 7.  column_7_value
##     For task number 1: 
##       number of yellow dots
##     For task number 2: 
##       number of dots
## 8.  column_8_value
##     For task number 1:
##       Number of blue dots
##     For task number 2:
##       area flag = 1 for total dot area forced to be near mean area of 25 dots
##       area flag = 2 for total dot area allowed to be unrestricted/proportional
## 9.  column_9_value 
##     For task number 1:
##       area flag = 1 for total dot areas allowed to be unrestricted/proportional
##       area flag = 2 for total yellow/blue dot areas forced to be near each other
##     For task number 2:
##       total area of dots
## 10. column_10_value
##     For task number 1:
##       total area of yellow dots
##     For task number 2:
##       mean area of 25 dots
## 11. column_11_value
##     For task number 1:
##       total area of blue dots
##     For task number 2:
##       not used

x<-read.csv("Experiment2.data",header=TRUE)
x$response_key_ID<-ifelse(x$response_key_ID==0,NA,x$response_key_ID)

x1<-x[x$task_number==1,]
more.yellow<-x1$column_7_value>x1$column_8_value
x1$resp<-ifelse((more.yellow & x1$response_key_ID==1) | (!more.yellow & x1$response_key_ID==2) ,1,0)
x1$item<-paste(x1$column_7_value,x1$column_8_value)

x2<-x[x$task_number==2,]
z<-ifelse(x2$column_7_value>25,1,2)
x2$resp<-ifelse(x2$response_key_ID==z,1,0)
x2$item<-paste(x2$column_7_value,x2$column_8_value)

f<-function(x) {
    id<-x$subject_number
    block<-x$block_number
    order<-x$stimulus_number
    rt<-x$reaction_time/1000
    item<-x$test_word_string
    df<-data.frame(id=id,block=block,order=order,rt=rt,resp=x$resp,item=x$item)
    df
}


df<-f(x1)
table(df$resp)
save(df,file="mturkddm_by.Rdata")

df<-f(x2)
table(df$resp)
save(df,file="mturkddm_y25.Rdata")
