# verify_liu_2025_mlq.R -- Step 5b re-runnable mapping evidence.
#
# CLAIMS UNDER TEST
#  (A) item_1..item_9 are the SI workbook's questions 7..15, assigned POSITIONALLY by
#      data/liu_2025_meaning_learning.py, and the Chinese sentence shipped as each code's
#      item_text is that column's header. The live table carries the source header in its
#      own item_text column, so the tie is checkable directly, server-side.
#  (B) The English in item_text_translated is Steger's MLQ wording for the corresponding
#      canonical item; the content mapping implies subscale membership
#      Search = {1,3,5,6}, Presence = {2,4,7,8,9}, which the paper's own published
#      composites must reproduce if it is right.
#  (C) item_2 ("My life has no clear purpose") is stored ALREADY REVERSE-SCORED, which is
#      why its option anchors ship flipped relative to the other eight items.
#
# Source: PLOS ONE 10.1371/journal.pone.0330447, S1 supporting-information workbook.
# The live table is read with a server-side GROUP BY (no export; the 200GB/30d cap).

suppressMessages({library(readxl)})

TABLE <- "liu_2025_mlq"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0330447.s001")

SHIPPED <- c(
  item_1 = "我正在寻觅我人生的一个目的或使命。",
  item_2 = "我的生活没有明确的目的。",
  item_3 = "我正在寻找自己的生活的意义。",
  item_4 = "我明白自己的生活的意义。",
  item_5 = "我正在寻觅让我感觉自己生活饶有意义的东西。",
  item_6 = "我总在尝试找寻自己生活的目的。",
  item_7 = "我的生活有一个清晰的方向。",
  item_8 = "我知道什么东西能使自己的生活有意义。",
  item_9 = "我已经发现一个让自己满意的生活目的。")

# Published composites, paper Table 2 and section 3.2.1 (N = 345).
PUB <- list(seek_m = 5.4087, seek_sd = 1.20832, poss_m = 5.2383, poss_sd = 1.24617,
            alpha_all = 0.855, alpha_poss = 0.892, alpha_seek = 0.849)

ok <- TRUE

## ---- deposit ------------------------------------------------------------
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
mlq_cols <- names(raw)[10:18]                    # questions 7..15, 1-based
hdr <- trimws(sub("^\\s*\\d+、\\s*", "", mlq_cols))

cat("-- (A1) deposit header at the mapped position vs shipped item_text --\n")
for (i in seq_along(SHIPPED)) {
  same <- identical(hdr[i], unname(SHIPPED[i]))
  ok <- ok && same
  cat(sprintf("%-8s col%-3d %-5s %s\n", names(SHIPPED)[i], 9 + i,
              if (same) "MATCH" else "DIFF", hdr[i]))
}

## ---- live table, server-side --------------------------------------------
py <- paste(
 "import redivis, json",
 "q = redivis.query('''SELECT item, ANY_VALUE(item_text) t, COUNT(*) n,",
 "  AVG(CAST(resp AS FLOAT64)) m, STDDEV(CAST(resp AS FLOAT64)) s",
 "  FROM `datapages.item_response_warehouse_3:5xaj:v5_0.liu_2025_mlq:fm9p`",
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
  live <- live[order(live$item), ]
  cat("\n-- (A2) live table's own item_text column vs the deposit header --\n")
  for (i in seq_along(SHIPPED)) {
    lt <- trimws(sub("^\\s*\\d+、\\s*", "", live$t[i]))
    same <- identical(lt, unname(SHIPPED[i])) && identical(live$item[i], names(SHIPPED)[i])
    ok <- ok && same
    cat(sprintf("%-8s n=%-4d mean=%.4f %-5s %s\n", live$item[i], live$n[i], live$m[i],
                if (same) "MATCH" else "DIFF", lt))
  }
  dep_means <- sapply(mlq_cols, function(c) mean(as.numeric(raw[[c]])))
  d <- max(abs(dep_means - live$m))
  cat(sprintf("largest |deposit column mean - live item mean|: %.2e\n", d))
  ok <- ok && d < 1e-9
  cat(sprintf("distinct shipped Chinese strings: %d of 9 -- every item is separated from every other\n",
              length(unique(unname(SHIPPED)))))
}

## ---- (B) published composites reproduce the content-implied subscales ----
d <- as.data.frame(lapply(raw[mlq_cols], as.numeric))
names(d) <- names(SHIPPED)
S <- c("item_1","item_3","item_5","item_6"); P <- c("item_2","item_4","item_7","item_8","item_9")
alpha <- function(x) { k <- ncol(x); k/(k-1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x))) }
sm <- rowMeans(d[S]); pm <- rowMeans(d[P])
cat("\n-- (B) paper's published composites vs the content-implied subscales --\n")
cmp <- function(lab, obs, pub, tol) {
  cat(sprintf("%-28s observed %8.5f  published %8.5f  diff %8.5f\n", lab, obs, pub, obs - pub))
  abs(obs - pub) <= tol
}
ok <- cmp("Seeking Meaning M {1,3,5,6}",  mean(sm), PUB$seek_m,  5e-5) && ok
ok <- cmp("Seeking Meaning SD",           sd(sm),   PUB$seek_sd, 5e-5) && ok
ok <- cmp("Possessing Meaning M {2,4,7,8,9}", mean(pm), PUB$poss_m,  5e-5) && ok
ok <- cmp("Possessing Meaning SD",        sd(pm),   PUB$poss_sd, 5e-5) && ok
ok <- cmp("alpha, all 9",                 alpha(d),    PUB$alpha_all,  5e-4) && ok
ok <- cmp("alpha, Possessing",            alpha(d[P]), PUB$alpha_poss, 5e-4) && ok
ok <- cmp("alpha, Seeking",               alpha(d[S]), PUB$alpha_seek, 5e-4) && ok

## ---- (C) item_2 is stored already reversed ------------------------------
d2 <- d; d2$item_2 <- 8 - d2$item_2
cat("\n-- (C) polarity of item_2 (the reverse-worded item) --\n")
cat(sprintf("r(item_2, mean of the other four Presence items) = %+.3f\n",
            cor(d$item_2, rowMeans(d[setdiff(P, "item_2")]))))
cat(sprintf("r(item_2, mean of the four Seeking items)        = %+.3f\n",
            cor(d$item_2, sm)))
cat(sprintf("alpha over all 9 as stored %.3f  vs  %.3f if item_2 were flipped (8 - x)\n",
            alpha(d), alpha(d2)))
cat(sprintf("Possessing M if item_2 were flipped: %.4f (published %.4f)\n",
            mean(rowMeans(d2[P])), PUB$poss_m))
ok <- ok && cor(d$item_2, rowMeans(d[setdiff(P, "item_2")])) > 0.4

cat("\nNOT established by this route: the ADMINISTERED wording of the response anchors\n",
    "(no Chinese anchor text is published anywhere in the article or its supplement;\n",
    "the shipped option_text is the paper's own English, section 3.2.1), and the paper's\n",
    "prose numbering of the two subscales, which contradicts its own data and composites.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
