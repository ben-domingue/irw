# verify_argentina_2012_aging_dependence.R -- batch_481, Step 5b.
#
# Claim: live item codes dep01_01..dep01_08 are the ENCaViAM 2012 user-file column
# names DEP01_01..DEP01_08 lower-cased (data/argentina_2012_aging.do: `rename *, lower`,
# Bookmark 3 uses the column name as item), and INDEC's "Documento para la utilizacion
# de la base de datos usuario" (doc_utilizacion_ENCaViAM 2012.pdf pp.37-38) prints each
# question under that exact variable name, with value labels 1 Si / 2 No. The .do reverses
# (resp = 3 - x), so live resp 2 = Si (needs help), resp 1 = No.
#
# Route 9 (response-frequency matching), re-run against the RAW source file
# ENCaViAM2012_Base_usuario.txt (INDEC ftp, sha256 8c1d18a9...29723, 4654 records),
# tabulated per variable x SEXO. Values hard-coded below. Also, because the .do sets
# id = _n straight after import with no re-sort, id is the raw record number, so the sum
# of ids answering Si per item is a person-level checksum: two different items only
# share it if the same people said Si. DEP01_06 and DEP01_07 tie on pooled counts
# (158/4496 each) but split by sex (46/112 vs 54/104) and by id-sum (359995 vs 334220).
#
# Live counts are a server-side GROUP BY (no table export).

suppressMessages(library(irw))
TABLE <- "argentina_2012_aging_dependence"

# RAW: per source column, Si (code 1) counts for Varon(1)/Mujer(2), and sum of record
# numbers answering Si. No (code 2) counts are 1984-Si_V and 2670-Si_M (all 4654 answered).
RAW <- data.frame(
  item   = sprintf("dep01_%02d", 1:8),
  si_v   = c(45, 76, 79, 35, 44, 46, 54, 134),
  si_m   = c(81, 154, 177, 74, 80, 112, 104, 354),
  idsum  = c(257965, 524443, 569336, 248309, 270800, 359995, 334220, 1073940),
  label  = c("comer", "vestirse", "banarse", "peinarse", "inodoro", "cama", "andar casa", "escaleras"))
N_V <- 1984; N_M <- 2670

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

ok <- TRUE; flip_hits <- 0
cat(sprintf("%-9s %-11s %22s %22s %18s  %s\n", "item", "content", "raw Si V/M, No V/M",
            "live r2 V/M, r1 V/M", "idsum raw/live", "result"))
for (i in seq_len(nrow(RAW))) {
  it <- RAW$item[i]
  rawv  <- c(RAW$si_v[i], RAW$si_m[i], N_V - RAW$si_v[i], N_M - RAW$si_m[i])
  livev <- c(g(it, "V", "2"), g(it, "M", "2"), g(it, "V", "1"), g(it, "M", "1"))
  lid   <- g(it, "V", "2", "idsum") + g(it, "M", "2", "idsum")
  same  <- all(rawv == livev) && lid == RAW$idsum[i]
  flipv <- c(g(it, "V", "1"), g(it, "M", "1"), g(it, "V", "2"), g(it, "M", "2"))
  if (all(rawv == flipv)) flip_hits <- flip_hits + 1
  ok <- ok && same
  cat(sprintf("%-9s %-11s %22s %22s %18s  %s\n", it, RAW$label[i], paste(rawv, collapse = "/"),
              paste(livev, collapse = "/"), paste0(RAW$idsum[i], "/", lid), if (same) "MATCH" else "MISMATCH"))
}
extra <- setdiff(unique(live$item), RAW$item)
if (length(extra)) { cat("unexpected live items:", extra, "\n"); ok <- FALSE }
extra_r <- setdiff(unique(live$resp), c("1", "2"))
if (length(extra_r)) { cat("unexpected live resp:", extra_r, "\n"); ok <- FALSE }

sig <- paste(RAW$si_v, RAW$si_m, RAW$idsum)
distinct <- length(unique(sig)) == nrow(RAW) && length(unique(RAW$idsum)) == nrow(RAW)
cat(sprintf("\nraw per-item signatures (Si by sex + id-sum) mutually distinct: %s\n", distinct))
cat(sprintf("items matching under a flipped resp direction: %d of 8\n", flip_hits))
ok <- ok && distinct && flip_hits == 0
cat("Establishes: every code carries its own source column's responses (signature unique per item),",
    "hence the codebook text printed under that column, and option direction (resp 2 = Si).",
    "Does not establish: interviewer preamble, which the codebook does not print.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
