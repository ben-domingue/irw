##psychtools_ability_nom: nominal companion of core `psychtools_ability`.
##
##Source: psychTools (CRAN; licence as recorded for the core table), data set
##`iqitems`: the raw multiple-choice answers to the 16 ICAR items (Revelle,
##Dworak & Condon 2020) whose scored version is `ability`, which data/psychtools.R
##publishes as psychtools_ability. Same 1,525 people in the same row order, same
##item names.
##
##text = the option chosen: 1-6 for the reasoning/letter/matrix items, 1-8 for
##       the rotation items. 0 in the source means no answer and is dropped (the
##       core table has those as missing).
##resp = 1 if text is the key, using the key from the psychTools help page
##       (`iq.keys`); the script asserts this reproduces `ability` cell for cell
##       and the published core table row for row.
library(psychTools)
data(iqitems)
data(ability)
stopifnot(identical(dim(iqitems), dim(ability)),
          identical(colnames(iqitems), colnames(ability)),
          identical(rownames(iqitems), rownames(ability)))

iq.keys <- c(4,4,4, 6, 6,3,4,4, 5,2,2,4, 3,2,6,7)
x <- as.matrix(iqitems)
answered <- !is.na(x) & x != 0
scored <- ifelse(answered, 1 * sweep(x, 2, iq.keys, "=="), NA)
stopifnot(identical(is.na(scored), is.na(as.matrix(ability))),
          all(scored == as.matrix(ability), na.rm = TRUE))

id <- seq_len(nrow(x))
L <- list()
for (i in seq_len(ncol(x))) {
    keep <- answered[, i]
    L[[i]] <- data.frame(id = id[keep], item = colnames(x)[i],
                         resp = scored[keep, i], text = x[keep, i])
}
df <- do.call(rbind, L)

##must reproduce the published core table
core <- irw::irw_fetch("psychtools_ability")
core <- core[!is.na(core$resp), ]
m <- merge(df, core, by = c("id", "item"), all = TRUE, suffixes = c("", "_core"))
stopifnot(nrow(m) == nrow(df), nrow(m) == nrow(core), all(m$resp == m$resp_core))

write.csv(df, "psychtools_ability_nom.csv", quote = FALSE, row.names = FALSE)
cat(nrow(df), length(unique(df$id)), length(unique(df$item)), "\n")
