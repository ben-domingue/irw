table<-'gilbert_meta_49'
library(gsheet)
tabs <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1jvwxYJ3gjSpEDtx4km-8czvDXu7iEIHhF5V5Y9VWNG0/edit?gid=0#gid=0')
tabs$table<-tolower(tabs$table)
f<-function(table,tabs) {
    L<-list()
    ii<-grep(table,tabs$table)
    for (i in 1:4) L[[i]]<-gsheet2tbl(tabs[ii,i+2])
    L
}
L<-f(table,tabs) ##note that i changed to lowercase

##lapply(L,names)
items<-L[[1]]
for (i in 2:length(L)) items<-merge(items,L[[i]],all.x=TRUE)

df<-irw::irw_fetch(table) ##see authentication and installation notes here. https://github.com/ben-domingue/irwpkg
unique(df$item)[!(unique(df$item) %in% unique(items$item))]
unique(items$item)[!(unique(items$item) %in% unique(df$item))]

write.csv(items,file=paste(table,"__items.csv",sep=''),row.names=FALSE)
