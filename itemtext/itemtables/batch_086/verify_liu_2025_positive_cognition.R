# verify_liu_2025_positive_cognition.R -- Step 5b re-runnable mapping evidence.
#
# CLAIMS UNDER TEST
#  (A) item_1..item_12 are the S1 workbook's survey questions 32..43 (spreadsheet
#      columns 35..46, 1-based), assigned POSITIONALLY by
#      data/liu_2025_meaning_learning.py, and the Chinese sentence shipped as each
#      code's item_text is that column's header with its "NN、" numbering stripped.
#      The live IRW table carries the source header verbatim in its own item_text
#      column, so the tie is checkable directly against the LIVE table, server-side
#      (a GROUP BY; no export -- the 200GB/30d cap).
#  (B) The 12 columns at those positions are the paper's Positive Cognition scale
#      stored RAW (no reverse-scored item): Cronbach's alpha over them as stored
#      must reproduce the published 0.928.
#
# Source: PLOS ONE 10.1371/journal.pone.0330447 (CC BY 4.0), S1 supporting
# information workbook (.s001, XLSX, 345 x 46).
#
# NOT established by this route: the English in item_text_translated (an
# IRW-produced translation -- no published English for the Chinese revision's
# items was locatable), and the administered Chinese wording of the five response
# anchors (nowhere published; the shipped option_text is the paper's own English,
# section 3.2.2).

suppressMessages({library(readxl); library(jsonlite)})

TABLE <- "liu_2025_positive_cognition"
LIVE  <- "datapages.item_response_warehouse_3:5xaj:v5_0.liu_2025_positive_cognition:nqq3"
URL   <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0330447.s001")

SHIPPED <- c(
  item_1  = "我像其他人一样注意好的事物",
  item_2  = "我特别关注生活带给我的很多细微的快乐",
  item_3  = "我注意那些让我感觉鼓舞的事情",
  item_4  = "在我的生命中有很多我喜欢的事情",
  item_5  = "我特别关注我的家人和朋友表扬我的个性特点",
  item_6  = "我关注我性格中好的部分",
  item_7  = "对我来说，记住他人好的事情是很重要的",
  item_8  = "我希望自己能在很多方面得到改善",
  item_9  = "不管是谁在笑，我注意的是高兴的面孔",
  item_10 = "我注意并关注所有事情都进展顺利的时刻",
  item_11 = "我特别注意我做得成功的那些事情",
  item_12 = "我能容易地看到我参与的所有活动中有趣的一面")

PUB_ALPHA <- 0.928   # paper section 3.2.2

ok <- TRUE

## ---- deposit -------------------------------------------------------------
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
pc_cols <- names(raw)[35:46]                       # survey questions 32..43
hdr <- trimws(sub("^\\s*\\d+、\\s*", "", pc_cols))

cat("-- (A1) deposit header at the mapped position vs shipped item_text --\n")
for (i in seq_along(SHIPPED)) {
  same <- identical(hdr[i], unname(SHIPPED[i]))
  ok <- ok && same
  cat(sprintf("%-8s col%-3d %-5s %s\n", names(SHIPPED)[i], 34 + i,
              if (same) "MATCH" else "DIFF", hdr[i]))
}

## ---- live table, server-side --------------------------------------------
py <- paste(
 "import redivis, json",
 sprintf("q = redivis.query('''SELECT item, ANY_VALUE(item_text) t, COUNT(*) n,"),
 "  AVG(CAST(resp AS FLOAT64)) m",
 sprintf("  FROM `%s`", LIVE),
 "  GROUP BY item ORDER BY item''')",
 "print(json.dumps(q.to_arrow_table().to_pylist(), ensure_ascii=False))", sep = "\n")
out <- suppressWarnings(system2("python3", c("-c", shQuote(py)), stdout = TRUE, stderr = FALSE))
live <- NULL
if (length(out)) {
  j <- out[grepl("^\\[", out)]
  if (length(j)) live <- jsonlite::fromJSON(j[1])
}
if (is.null(live)) {
  cat("\nCOULD NOT READ THE LIVE TABLE (redivis query failed) -- claim (A2) untested.\n")
  ok <- FALSE
} else {
  live <- live[match(names(SHIPPED), live$item), ]
  cat("\n-- (A2) live table's own item_text column vs the shipped item_text --\n")
  for (i in seq_along(SHIPPED)) {
    lt <- trimws(sub("^\\s*\\d+、\\s*", "", live$t[i]))
    same <- identical(lt, unname(SHIPPED[i])) && identical(live$item[i], names(SHIPPED)[i])
    ok <- ok && same
    cat(sprintf("%-8s n=%-4d mean=%.4f %-5s %s\n", live$item[i], live$n[i], live$m[i],
                if (same) "MATCH" else "DIFF", lt))
  }
  dep_means <- sapply(pc_cols, function(c) mean(as.numeric(raw[[c]])))
  d <- max(abs(dep_means - live$m))
  cat(sprintf("largest |deposit column mean - live item mean|: %.2e\n", d))
  ok <- ok && d < 1e-9
  cat(sprintf("distinct shipped Chinese strings: %d of 12 -- every item is separated from every other\n",
              length(unique(unname(SHIPPED)))))
}

## ---- (B) published alpha reproduces from those 12 columns, as stored ------
d12 <- as.data.frame(lapply(raw[pc_cols], as.numeric))
alpha <- function(x) { k <- ncol(x); k/(k-1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x))) }
a <- alpha(d12)
cat("\n-- (B) Cronbach's alpha over the 12 mapped columns, stored as-is --\n")
cat(sprintf("observed %.4f   published %.4f   diff %+.4f\n", a, PUB_ALPHA, a - PUB_ALPHA))
ok <- ok && abs(a - PUB_ALPHA) <= 5e-4
mit <- sapply(seq_len(12), function(j) cor(d12[[j]], rowSums(d12[-j])))
cat(sprintf("item-total r range: %.3f .. %.3f (no negative -- nothing is stored reverse-scored)\n",
            min(mit), max(mit)))
ok <- ok && min(mit) > 0

cat("\nNOT established by this route: the English item_text_translated (produced by IRW;\n",
    "no published English for the Chinese revision's items was locatable) and the\n",
    "administered Chinese anchor wording (unpublished; option_text is the paper's English).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
