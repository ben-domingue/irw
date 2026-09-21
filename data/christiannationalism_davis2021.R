##https://dataverse.harvard.edu/file.xhtml?fileId=5153037&version=3.0&toolType=PREVIEW
##Davis, Nicholas, 2021, "Replication Data for: "The psychometric properties of the Christian nationalism index"", https://doi.org/10.7910/DVN/GUSJEI, Harvard Dataverse, V3; small-relig.tab [fileName], UNF:6:S9zD+VLQ5KTxcmfUA8L/xw== [fileUNF]
##
##ITEM LABELS WERE SHIFTED BY ONE COLUMN. `items` drops column 1 (the id), so
##items[1] already names column 2 -- and it was then indexed with the unshifted
##loop counter `i`. Every one of the six items carried the NEXT column's name,
##and the sixth ran off the end of `items` and became the literal string "NA".
##
##  source column            published as
##  2 xiannation        ->    "xianvalues"
##  3 xianvalues        ->    "pubreligion"
##  4 pubreligion       ->    "godsplan"
##  5 godsplan          ->    "prayer"
##  6 prayer            ->    "churchstate"
##  7 churchstate       ->    "NA"
##
##`xiannation` -- the item the scale is named for -- never appeared at all.
##Confirmed against the deposit by matching each source column's response
##distribution to the published label's, a 1:1 shift with no ambiguity. Found via
##the item-text re-audit checkpoint on #2255; see #2326.
##
##Indexing `items` by position at all was the hazard, so this pairs the name and
##the column in one step and cannot drift again.

x<-read.table("small-relig.tab",sep="\t",header=TRUE)
id<-x[,1]
items<-names(x)[-1]
L<-list()
for (j in seq_along(items)) L[[j]]<-data.frame(id=id,item=items[j],resp=x[,j+1])
df<-data.frame(do.call("rbind",L))
df$resp<-as.integer(df$resp)
df$id<-as.character(df$id)

##Every source item column must appear exactly once, with the id column absent:
##the defect this replaces produced a label that was not a column name at all.
stopifnot(setequal(unique(df$item),items),
          !(names(x)[1] %in% df$item),
          nrow(df)==nrow(x)*length(items))

##The filename was misspelled "christiannatinoalism" (transposed), so it did not
##match the table name it uploads as.
write.csv(df,file="christiannationalism_davis2021.csv",quote=FALSE,row.names=FALSE)
