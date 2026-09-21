# verify_wu2021_empathy.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the IRW item code B{n} carries the wording printed at
# position n of section 二 of the study's administered questionnaire
# (Frontiers Supplementary Data_Sheet_2.PDF, Wu & Qi 2021, Front Psychol
# 12:708342). The processing script data/wu2021_empathy.py melts the deposit's
# bare columns B1..B21 with no rename, and the deposit carries NO variable or
# value labels, so nothing at the source ties code to text: the tie is
# positional and has to be tested against the data.
#
# THE TEST. The deposit ships the study's own precomputed subscale columns
# 职业声望 (prestige+stability), 自我发展 (self-development) and 福利收入
# (welfare+income). Each is an exact raw mean of a subset of B1..B21, and the
# subsets are recovered here by least squares rather than assumed. The
# falsifiable prediction is that the recovered partition agrees, item for item,
# with the content of the wording this table ships at that position: an income
# item must land in 福利收入, a status item in 职业声望, an
# ability/interest/challenge item in 自我发展. A permuted mapping breaks it.
#
# WHAT THIS DOES NOT ESTABLISH: it pins each item to one of three blocks
# (8/8/5), not the order WITHIN a block. Two same-factor items with similar
# wording -- B13 单位知名度高 vs B14 单位规模大, B20 单位级别高 vs B21 单位在大城市 --
# are not separated by it, and their means tie to within 0.03. Status is
# therefore PARTIAL, not VERIFIED. The mean-rank check below adds independent
# separation only for the extremes.

suppressMessages({library(irw); library(jsonlite)})

TABLE <- "wu2021_empathy"
B <- paste0("B", 1:21)

# Content classification of the 21 shipped item_texts, fixed in advance from
# the wording alone (P = 职业声望 prestige/stability, S = 自我发展
# self-development, W = 福利收入 welfare/income).
TEXT <- c("收入高","福利好","职业稳定","能提供受教育的机会","有出国机会",
          "有较高的社会地位","能发挥自己的才能","提供医疗、养老、住房公积金",
          "职业环境优雅","符合兴趣爱好","机会均等，公平竞争","晋升机会多",
          "单位知名度高","单位规模大","能学以致用","交通便利，信息通畅",
          "自主性大，不受拘束","工作有挑战性","容易成名成家","单位级别高",
          "单位在大城市")
EXPECT <- c("W","W","P","W","W","P","S","P","S","S","S","W","P","P","S","S",
            "S","S","P","P","P")
AGG <- c(P = "职业声望", S = "自我发展",
         W = "福利收入")

## --- deposit -------------------------------------------------------------
a <- jsonlite::fromJSON("https://api.figshare.com/v2/articles/16683931")
url <- a$files$download_url[grepl("\\.csv$", tolower(a$files$name))][1]
tmp <- tempfile(fileext = ".csv"); download.file(url, tmp, quiet = TRUE)
d <- read.csv(tmp, fileEncoding = "UTF-8", check.names = FALSE)
for (cn in c(B, AGG)) d[[cn]] <- suppressWarnings(as.numeric(as.character(d[[cn]])))

## --- tie the deposit to the live IRW table (cheap, server-side) ----------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(pi$n, pi$item)[B]
dep_n  <- sapply(d[B], function(x) sum(!is.na(x)))
cat("-- per-item non-missing n, deposit vs live IRW table --\n")
cat(sprintf("%-5s %8s %8s\n", "item", "deposit", "live"))
for (i in seq_along(B)) cat(sprintf("%-5s %8d %8d\n", B[i], dep_n[i], live_n[i]))
tie_ok <- all(dep_n == live_n)
cat(sprintf("all 21 n match: %s\n\n", tie_ok))

## --- recover the subscale subsets ---------------------------------------
cmpl <- d[stats::complete.cases(d[, c(B, AGG)]), c(B, AGG)]
X <- cbind(as.matrix(cmpl[, B]), 1)
got <- character(21); resid <- numeric(3); names(resid) <- names(AGG)
for (k in names(AGG)) {
  y <- cmpl[[AGG[[k]]]]
  co <- qr.solve(crossprod(X), crossprod(X, y))
  resid[k] <- max(abs(X %*% co - y))
  mem <- which(abs(co[1:21]) > 1e-6)
  got[mem] <- k
  cat(sprintf("%s (%s): recovered %d items, weights %.4f, max resid %.2e -> %s\n",
              k, AGG[[k]], length(mem), co[mem[1]], resid[k],
              paste(B[mem], collapse = ",")))
}
cat(sprintf("\ncomplete rows used: %d\n\n", nrow(cmpl)))

cat("-- shipped wording at each position vs recovered subscale --\n")
cat(sprintf("%-5s %-28s %-8s %-8s %s\n", "item", "item_text", "expected", "recovered", "ok"))
for (i in 1:21)
  cat(sprintf("%-5s %-28s %-8s %-8s %s\n", B[i], TEXT[i], EXPECT[i], got[i],
              ifelse(EXPECT[i] == got[i], "y", "NO")))
agree <- sum(EXPECT == got)
cat(sprintf("\nagreement: %d/21\n\n", agree))

## --- independent mean-rank check on the extremes ------------------------
m <- sapply(d[B], mean, na.rm = TRUE)
o <- order(m)
cat("-- item means, ascending --\n")
for (i in o) cat(sprintf("%-5s %-28s %.3f\n", B[i], TEXT[i], m[i]))
rank_ok <- (names(which.min(m)) == "B19") && (names(which.max(m)) == "B11") &&
           (B[o[2]] == "B5")
cat(sprintf("\nlowest = B19 %s (expected: fame is the least valued attribute): %s\n",
            TEXT[19], names(which.min(m)) == "B19"))
cat(sprintf("2nd lowest = B5 %s: %s\n", TEXT[5], B[o[2]] == "B5"))
cat(sprintf("highest = B11 %s (expected: fair competition/stability top out): %s\n",
            TEXT[11], names(which.max(m)) == "B11"))
cat(sprintf("B13 %.3f vs B14 %.3f (diff %.3f) and B20 %.3f vs B21 %.3f (diff %.3f)",
            m["B13"], m["B14"], abs(m["B13"] - m["B14"]),
            m["B20"], m["B21"], abs(m["B20"] - m["B21"])))
cat(" -- these pairs are NOT separated by any route here.\n")

cat("\nNote: this establishes each item's subscale (21/21) and the extreme ranks;\n")
cat("it does NOT establish the order within a subscale.\n")

cat(if (tie_ok && agree == 21 && max(resid) < 1e-6 && rank_ok)
      "VERDICT: PASS\n" else "VERDICT: FAIL\n")
