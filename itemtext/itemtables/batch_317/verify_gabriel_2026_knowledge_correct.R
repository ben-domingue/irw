# verify_gabriel_2026_knowledge_correct.R
#
# CLAIMS UNDER TEST
#   (a) item know_N is knowledge statement N of Gabriel & Bitsch (2026) Table 2
#       (source column Q21_SQ00N#0, number-preserving rename in
#       data/gabriel_2026_ag_knowledge.py);
#   (b) resp 1 = "Richtig" (respondent judged the statement TRUE), resp 0 =
#       "Falsch" (judged FALSE) -- i.e. the live table stores the raw judgement,
#       NOT a correct/incorrect score, despite the table name;
#   (c) correct_response (1 for statements 2,4,5,8; 0 for 1,3,6,7,9) is the
#       paper's published key.
#
# ROUTE 1: paper Table 4 publishes each statement's mean correct rate (2 dp).
#   Scoring the live judgements with the key must reproduce all nine to rounding.
#   Rounded to 2 dp the nine published rates also separate every near-tie in
#   order (2 vs 8: .67/.66; 4 vs 5: .76/.77), so a swap of any two items fails.
# ROUTE 9: count of "Richtig" per statement in the S2 Dataset's Data_label sheet
#   must equal the live count of resp=1 per item (9 distinct counts).
# CONTROL: reading resp as already-scored (mean of resp) must NOT reproduce
#   Table 4 for the five false statements -- this is what establishes (b).

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "gabriel_2026_knowledge_correct"
self <- sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])
CACHE <- file.path(dirname(normalizePath(self)), "..", "..", ".cache", TABLE)
XLSX <- file.path(CACHE, "S2.xlsx")
URL <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0341457.s002&type=supplementary"
if (!file.exists(XLSX)) {
  dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
  download.file(URL, XLSX, mode = "wb", quiet = TRUE)
}

PUB <- c(.43, .67, .41, .76, .77, .78, .70, .66, .56)   # Table 4, statements 1..9
KEY <- c(0, 1, 0, 1, 1, 0, 0, 1, 0)                    # Table 2 (yes)/(no)
items <- paste0("know_", 1:9)

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
key_by_item <- setNames(KEY, items)
correct <- tapply(d$resp == key_by_item[d$item], d$item, mean)[items]
rawmean <- tapply(d$resp, d$item, mean)[items]
live1 <- tapply(d$resp == 1, d$item, sum)[items]

lab <- readxl::read_excel(XLSX, sheet = "Data_label")
src1 <- sapply(1:9, function(i) sum(lab[[sprintf("Q21_SQ00%d#0", i)]] == "Richtig", na.rm = TRUE))

cat(sprintf("%-7s %4s %9s %13s %11s %10s %10s\n", "item", "key", "published",
            "live_scored", "live_mean", "src_Richt", "live_r1"))
for (i in 1:9) cat(sprintf("%-7s %4d %9.2f %13.4f %11.4f %10d %10d\n", items[i], KEY[i],
                           PUB[i], correct[i], rawmean[i], src1[i], live1[i]))

ok1 <- all(abs(round(correct, 2) - PUB) < 1e-9)
ok9 <- all(src1 == live1) && length(unique(src1)) == 9
ctrl <- !all(abs(round(rawmean, 2) - PUB) < 1e-9)
# swap test: every pairwise swap of item_text must break route 1
swaps_caught <- 0; npairs <- 0
for (a in 1:8) for (b in (a+1):9) {
  p <- PUB; p[c(a, b)] <- p[c(b, a)]; k <- KEY; k[c(a, b)] <- k[c(b, a)]
  sc <- tapply(d$resp == setNames(k, items)[d$item], d$item, mean)[items]
  npairs <- npairs + 1
  if (!all(abs(round(sc, 2) - p) < 1e-9)) swaps_caught <- swaps_caught + 1
}
cat(sprintf("\nroute 1 (Table 4 reproduced by scoring with key): %s\n", ok1))
cat(sprintf("route 9 (Richtig counts == live resp=1 counts, 9 distinct): %s\n", ok9))
cat(sprintf("control (resp read as already-scored FAILS Table 4): %s\n", ctrl))
cat(sprintf("pairwise item swaps detected by route 1: %d / %d\n", swaps_caught, npairs))
cat(if (ok1 && ok9 && ctrl && swaps_caught == npairs) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
