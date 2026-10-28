## pks_probability: problems in elementary probability theory, before and after a
## learning object, with the package's own Q-matrix (#3229).
##
## Source: the pks R package (Heller, Wickelmaier et al.; CRAN, GPL (>= 2)), object
## `probability`. https://cran.r-project.org/web/packages/pks/index.html
##
## 504 participants answered twelve problems (b101..b112), then received instructions
## on four concepts, then answered twelve parallel problems (b201..b212). The two sets
## are matched item by item -- p101 and p201 are the same marble problem with different
## numbers, p102/p202 the same coin problem, and so on. 159 participants did not
## complete the second set, so their b2.. cells are missing and those 1,908 rows carry
## no response. The rows stay (Ben, 2026-09-09: leave missing rows missing); what
## changes here is that the cell is now EMPTY rather than the literal string "NA",
## which had typed the whole `resp` column `string` on Redivis (#2029). This table was
## above that campaign's 5% threshold and so was never in its worklist; red_up's
## resp_numeric gate, which postdates the original upload, refuses the token outright,
## so the rebuild clears it -- which is what #2029 left standing for any rebuild.
##
##   id    participant, 1..504 in the source's row order
##   item  b101..b112 (before) and b201..b212 (after)
##   resp  correct (1) or error (0)
##   wave  0 before the learning object, 1 after
##   qmatrix1..qmatrix4  the four concepts the instructions taught:
##         qmatrix1 = cp, the probability of the complement of an event
##         qmatrix2 = id, the probability of two independent events
##         qmatrix3 = pb, the classic probability of an event
##         qmatrix4 = un, the probability of the union of two disjoint events
##
## The Q-matrix is `sf1` from the package's own `probability` examples, the
## "conjunctive skill function, one-to-one problem function". Two things follow from
## reading it there rather than retyping it from the paper. The package applies the
## same sf1 to BOTH parts (`N.R1` from b1.., `N.R2` from b2..), which is why the
## attributes attach to all 24 items here: they are properties of the problem, and the
## problems are matched across the two sets. And sf1 is a choice -- the same examples
## give an extended skill function sf2, which adds a second skill assignment for items
## 2, 3, 6, 7 and 12. What this table publishes is sf1.
##
## This replaces `heller2013_probability` in irw_simsyn, which was the b2.. half of
## these same responses (345 x 12) carrying this same Q-matrix under non-conforming
## column names, in a family defined as responses not produced by real people (#3229).

library(pks)
data(probability)
x <- probability
id <- 1:nrow(x)
items1 <- paste("b", 100 + 1:12, sep = "")
items2 <- paste("b", 200 + 1:12, sep = "")
items <- c(items1, items2)

## sf1, verbatim from the pks `probability` examples. Its leading column is the
## problem number within a set, 1..12, so one row serves b10k and b20k alike.
sf1 <- read.table(header = TRUE, text = "
item cp id pb un
1  0  0  1  0
2  1  0  0  0
3  0  0  0  1
4  0  1  0  0
5  1  0  1  0
6  1  0  1  0
7  0  0  1  1
8  0  0  1  1
9  0  1  1  0
10 1  1  0  0
11 1  1  1  0
12 0  1  1  1
")

L <- list()
for (item in items) {
    after.intervention <- ifelse(item %in% items2, 1, 0)
    ## the problem number within its set: b107 and b207 are both problem 7
    k <- as.integer(substr(item, 3, 4))
    q <- sf1[sf1$item == k, c("cp", "id", "pb", "un")]
    L[[item]] <- data.frame(id = id, item = item, resp = x[, item],
                            wave = after.intervention,
                            qmatrix1 = q$cp, qmatrix2 = q$id,
                            qmatrix3 = q$pb, qmatrix4 = q$un)
}
df <- data.frame(do.call("rbind", L))
stopifnot(nrow(df) == 504L * 24L, !anyNA(df$qmatrix1))
write.csv(df, file = "pks_probability.csv", row.names = FALSE, quote = FALSE, na = "")
