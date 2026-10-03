# verify_argentina_2012_aging_health.R -- batch_482, Step 5b.
#
# Claim: live item codes au01 / au03 are the ENCaViAM 2012 user-file column names
# AU01 / AU03 lower-cased (data/argentina_2012_aging.do: `rename *, lower`, Bookmark 1
# uses the column name as item). INDEC's "Documento para la utilizacion de la base de
# datos usuario" (doc_utilizacion_ENCaViAM 2012.pdf p.32) prints AU01 = "En general,
# ¿usted diria que su salud es..." and AU03 = "Actualmente, ¿usted diria que su memoria
# es...", both with value labels 1 excelente .. 5 mala. The .do reverses (resp = 6 - x),
# so live resp 5 = excelente, 4 = muy buena, 3 = buena, 2 = regular, 1 = mala.
#
# (A) text -> column, independent of the codebook: INDEC's Principales resultados
#     (encaviam.pdf, sha256 97a4f934...) Cuadro 10 is titled "autopercepcion de la salud"
#     and Cuadro 11 "autopercepcion de la memoria"; each prints weighted % Excelente..Mala
#     for Total/Varones/Mujeres. Recomputing those from the raw user base
#     (ENCaViAM2012_Base_usuario.txt, sha256 8c1d18a9...29723) with POND_CALIBRADA gives
#     the values in RAW_W below (computed 2026-09-25, hard-coded).
# (B) column -> live: raw per-code counts by SEXO and the sum of record numbers per code
#     (the .do sets id = _n straight after import, so id = raw record number), reversed
#     per the .do, compared with a server-side GROUP BY of the live table (no export).

suppressMessages(library(irw))
TABLE <- "argentina_2012_aging_health"

## (A) published (Cuadros 10/11) vs recomputed from raw columns; order Excelente..Mala
PUB <- list(
  salud   = rbind(T = c(5.0, 11.9, 42.5, 34.0, 6.7), V = c(6.5, 12.1, 40.9, 34.6, 6.0), M = c(3.8, 11.8, 43.7, 33.5, 7.2)),
  memoria = rbind(T = c(8.2, 19.1, 46.9, 23.9, 1.9), V = c(9.4, 17.0, 46.8, 25.1, 1.7), M = c(7.2, 20.6, 47.0, 23.0, 2.1)))
RAW_W <- list(
  AU01 = rbind(T = c(5.0, 11.9, 42.5, 34.0, 6.7), V = c(6.5, 12.1, 40.9, 34.6, 6.0), M = c(3.8, 11.8, 43.7, 33.5, 7.2)),
  AU03 = rbind(T = c(8.2, 19.1, 46.9, 23.9, 1.9), V = c(9.4, 17.0, 46.8, 25.1, 1.7), M = c(7.2, 20.6, 47.0, 23.0, 2.1)))
cat("(A) weighted % Excelente..Mala, published cuadro vs raw column\n")
tieA <- matrix(NA, 2, 2, dimnames = list(c("AU01", "AU03"), c("salud", "memoria")))
for (col in rownames(tieA)) for (st in colnames(tieA)) {
  tieA[col, st] <- sum(RAW_W[[col]] == PUB[[st]])
  cat(sprintf("  %s vs Cuadro '%s': %d/15 cells equal\n", col, st, tieA[col, st]))
}
okA <- tieA["AU01", "salud"] == 15 && tieA["AU03", "memoria"] == 15 &&
       tieA["AU01", "memoria"] < 15 && tieA["AU03", "salud"] < 15

## (B) raw counts by code 1..5 (excelente..mala) for Varon / Mujer, and id-sum per code
RAW <- list(
  au01 = list(V = c(78, 213, 803, 753, 137), M = c(72, 248, 1005, 1095, 250),
              idsum = c(386617, 1157124, 4319757, 4075794, 892893)),
  au03 = list(V = c(159, 271, 963, 530, 61), M = c(168, 417, 1218, 763, 104),
              idsum = c(790093, 1756518, 5074290, 2873459, 337825)))

live <- tryCatch({
  tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
  q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, CAST(cov_sex AS STRING) AS sex,",
                     "CAST(resp AS STRING) AS resp, COUNT(*) AS n, SUM(CAST(id AS INT64)) AS idsum",
                     "FROM `%s` GROUP BY item, sex, resp"), tbl$qualified_reference)
  as.data.frame(irw:::.irw_query_tibble(q))
}, error = function(e) {
  message("server-side query unavailable (", conditionMessage(e), "); using irw_fetch()")
  d <- as.data.frame(irw::irw_fetch(TABLE))
  aggregate(list(n = rep(1, nrow(d)), idsum = as.numeric(d$id)),
            list(item = d$item, sex = as.character(d$cov_sex), resp = as.character(d$resp)), sum)
})
live$resp <- as.character(as.numeric(live$resp))
live$sex <- ifelse(grepl("^Mujer", live$sex), "M", ifelse(grepl("^Var", live$sex), "V", live$sex))
g <- function(it, s, r, col = "n") sum(as.numeric(live[[col]][live$item == it & live$sex == s & live$resp == r]))
lv <- function(it) {  # live vectors indexed by RAW code 1..5, i.e. live resp 6 - code
  list(V = sapply(1:5, function(k) g(it, "V", as.character(6 - k))),
       M = sapply(1:5, function(k) g(it, "M", as.character(6 - k))),
       idsum = sapply(1:5, function(k) g(it, "V", as.character(6 - k), "idsum") + g(it, "M", as.character(6 - k), "idsum")))
}
cells <- function(a, b) sum(a$V == b$V) + sum(a$M == b$M) + sum(a$idsum == b$idsum)
rev_ <- function(x) lapply(x, rev)

cat("\n(B) raw column (reversed per .do) vs live item; 15 cells = 5 codes x (Varon n, Mujer n, id-sum)\n")
cat(sprintf("%-6s %-26s %-26s %s\n", "item", "raw V / M (code 1..5)", "live V / M (resp 5..1)", "cells"))
okB <- TRUE
for (it in names(RAW)) {
  L <- lv(it); m <- cells(RAW[[it]], L)
  cat(sprintf("%-6s %-26s %-26s %d/15\n", it,
              paste(paste(RAW[[it]]$V, collapse = ","), paste(RAW[[it]]$M, collapse = ","), sep = " | "),
              paste(paste(L$V, collapse = ","), paste(L$M, collapse = ","), sep = " | "), m))
  okB <- okB && m == 15
}
swap <- c(au01 = cells(RAW$au03, lv("au01")), au03 = cells(RAW$au01, lv("au03")))
flip <- c(au01 = cells(rev_(RAW$au01), lv("au01")), au03 = cells(rev_(RAW$au03), lv("au03")))
cat(sprintf("under a swap of au01/au03 text: %d/15 and %d/15 cells\n", swap[1], swap[2]))
cat(sprintf("under a flipped resp direction:  %d/15 and %d/15 cells\n", flip[1], flip[2]))
extra <- setdiff(unique(live$item), names(RAW)); extra_r <- setdiff(unique(live$resp), as.character(1:5))
if (length(extra) || length(extra_r)) { cat("unexpected live values:", extra, extra_r, "\n"); okB <- FALSE }
okB <- okB && all(swap < 15) && all(flip < 15)

cat("\nEstablishes: the salud statement belongs to column AU01 and memoria to AU03 (published cuadros",
    "labelled by content, 15/15 each, not interchangeable), each live code carries its own column's",
    "responses, and resp direction (5 = excelente, 1 = mala). Does not establish interviewer framing,",
    "which the codebook does not print.\n")
cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
