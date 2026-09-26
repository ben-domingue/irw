# verify_ozkurt_2026_continuance_intention.R
#
# Claim under test: INT<k> is the item that S6 File Table 6 numbers <k>
# ("Original item no." 1..6), and INT2/INT3 -- S6's two items "reverse-coded in
# original form" ("I often think about quitting this sport.", "I intend to quit
# this sport.") -- are stored ALREADY REVERSED, so their shipped anchors run
# 1 = Strongly Agree .. 7 = Strongly Disagree.
#
# Links (none is an item count):
#   A (route 9). S1 File .xlsx holds the same 374 respondents under headers
#     "1.Intention".."6.Intention"; rows are permuted relative to the .sav, so
#     columns are tied by 7-level count vectors. Each k.Intention must match
#     INT<k> and no other INT column (unique bijection).
#   B. Live IRW per-item count vectors equal the .sav's (bijection reaches the
#     shipped codes).
#   C (route 3, published totals). Paper Table 1 row "8. Intention" is the
#     4 retained items -- S6 says original items 1,4,5,6. Of all 15 four-item
#     subsets of INT1..INT6, {INT1,INT4,INT5,INT6} must be the one that best
#     reproduces the published alpha .62 and the correlations of the Intention
#     composite with Enjoyment (.30), Motivation (.43), Competence (.32),
#     Autonomy (.28), Relatedness (.22), Task (.18), Ego (.18). This pins the
#     dropped PAIR {INT2,INT3} as S6's items 2-3.
#   D (route 6, polarity). INT2 and INT3 must correlate POSITIVELY with INT1
#     ("I will continue this sport..."), which is only possible for the two
#     quitting items if they are stored reversed; and they must be each other's
#     strongest correlate.
#
# What this does NOT establish: Link C separates {2,3} from {1,4,5,6} but not
# order inside either set; that rests on Link A (the authors' S1 numbering
# agreeing with the .sav column numbering) plus S6's numbering -- all the
# authors' own files. Nothing external separates INT2 from INT3, or orders
# INT1/INT4/INT5/INT6. Hence PARTIAL.

suppressMessages(library(irw))
TABLE <- "ozkurt_2026_continuance_intention"
BASE  <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0353067."
ITEMS <- paste0("INT", 1:6)
ok <- TRUE

tmp_x <- tempfile(fileext = ".xlsx"); tmp_s <- tempfile(fileext = ".sav")
download.file(paste0(BASE, "s001"), tmp_x, quiet = TRUE, mode = "wb")
download.file(paste0(BASE, "s002"), tmp_s, quiet = TRUE, mode = "wb")
x   <- as.data.frame(readxl::read_excel(tmp_x))
sav <- as.data.frame(haven::zap_labels(haven::read_sav(tmp_s)))

cnt <- function(v) as.integer(table(factor(as.integer(v), levels = 1:7)))
sav_cnt <- sapply(ITEMS, function(c) cnt(sav[[c]]))

## Link B
d <- irw::irw_fetch(TABLE)
cat("Link B -- live vs .sav per-item counts (1..7)\n")
for (i in ITEMS) {
  lc <- cnt(d$resp[d$item == i]); m <- identical(lc, sav_cnt[, i]); ok <- ok && m
  cat(sprintf("%-5s live %-28s sav %-28s %s\n", i, paste(lc, collapse=" "),
              paste(sav_cnt[, i], collapse=" "), ifelse(m, "yes", "NO")))
}

## Link A
cat("\nLink A -- S1 header 'k.Intention' vs .sav column, unique match\n")
for (k in 1:6) {
  cc <- cnt(x[[paste0(k, ".Intention")]])
  hits <- ITEMS[apply(sav_cnt, 2, function(z) identical(z, cc))]
  g <- length(hits) == 1 && hits == paste0("INT", k); ok <- ok && g
  cat(sprintf("%d.Intention %-28s -> %s %s\n", k, paste(cc, collapse=" "),
              paste(hits, collapse=","), ifelse(g, "ok", "FAIL")))
}

## Link C
alpha <- function(X) { k <- ncol(X); k/(k-1)*(1 - sum(apply(X,2,var))/var(rowSums(X))) }
m <- function(cols) rowMeans(sav[, cols])
other <- list(Enjoyment = m(paste0("PACES", c(3,4,5,6,8))),
              Motivation = m(paste0("SMS", c(3,5,7,9,10,12,14,15,16))),
              Competence = m(paste0("BPNS", 1:5)), Autonomy = m(paste0("BPNS", 6:9)),
              Relatedness = m(paste0("BPNS", 10:14)),
              Task = m(paste0("EGOQ", c(1,3,4,6,9))), Ego = m(paste0("EGOQ", c(2,5,7,8,10))))
PUB <- c(alpha = .62, Enjoyment = .30, Motivation = .43, Competence = .32,
         Autonomy = .28, Relatedness = .22, Task = .18, Ego = .18)
subs <- combn(ITEMS, 4, simplify = FALSE)
res <- t(sapply(subs, function(s) {
  comp <- m(s); c(alpha = alpha(sav[, s]), sapply(other, function(o) cor(comp, o)))
}))
dist <- apply(res, 1, function(r) sum(abs(r - PUB[colnames(res)])))
o <- order(dist)
cat("\nLink C -- 4-item subsets vs paper Table 1 'Intention' row (published:",
    paste(names(PUB), PUB, sep="=", collapse=" "), ")\n")
for (j in o[1:5]) cat(sprintf("%-24s %s  sum|diff|=%.3f\n", paste(subs[[j]], collapse=","),
                             paste(sprintf("%.2f", res[j, ]), collapse=" "), dist[j]))
best <- paste(subs[[o[1]]], collapse=",")
g <- best == "INT1,INT4,INT5,INT6" && dist[o[2]] > 2 * dist[o[1]]; ok <- ok && g
cat("best subset:", best, "(expected INT1,INT4,INT5,INT6)", ifelse(g, "ok", "FAIL"), "\n")

## Link D
R <- cor(sav[, ITEMS])
cat("\nLink D -- polarity: r(INT2,INT1)=", round(R["INT2","INT1"],2),
    " r(INT3,INT1)=", round(R["INT3","INT1"],2), " r(INT2,INT3)=", round(R["INT2","INT3"],2), "\n", sep="")
g <- R["INT2","INT1"] > 0.2 && R["INT3","INT1"] > 0.2 &&
     which.max(R["INT2", -2]) == which(colnames(R)[-2] == "INT3") &&
     which.max(R["INT3", -3]) == which(colnames(R)[-3] == "INT2")
ok <- ok && g
cat("means INT2/INT3 as stored:", round(mean(sav$INT2),2), round(mean(sav$INT3),2),
    "vs INT1", round(mean(sav$INT1),2), "->", ifelse(g, "stored reversed: ok", "FAIL"), "\n")

cat("\nNOT established: order within {INT1,INT4,INT5,INT6} and INT2 vs INT3 rest on the authors' own numbering only.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
