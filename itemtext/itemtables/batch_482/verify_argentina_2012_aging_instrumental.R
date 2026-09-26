# verify_argentina_2012_aging_instrumental.R -- batch_482, Step 5b (from references/verify_template.R).
#
# Claim: live item codes dep03_01..dep03_07 are the ENCaViAM 2012 user-file column
# names DEP03_01..DEP03_07 lower-cased (data/argentina_2012_aging.do: `rename *, lower`,
# Bookmark 4 uses the column name as item), and INDEC's "Documento para la utilizacion
# de la base de datos usuario" (doc_utilizacion_ENCaViAM 2012.pdf, Diccionario de
# variables pp.38-39) prints each question under that exact variable name, with value
# labels 1 Si / 2 No. The .do reverses (resp = 3 - x), so live resp 2 = Si, resp 1 = No.
#
# Route 9 (response-frequency matching) against the RAW source file
# ENCaViAM2012_Base_usuario.txt (INDEC ftp, sha256 8c1d18a9...29723, 4654 records),
# tabulated per variable x SEXO, values hard-coded below. The .do sets id = _n straight
# after import with no re-sort, so id is the raw record number and the sum of ids
# answering Si per item is a person-level checksum. Pooled Si counts are already
# mutually distinct across the 7 items (563/688/389/306/736/427/644).
# Live counts are a server-side GROUP BY (no table export).

suppressMessages(library(irw))
TABLE <- "argentina_2012_aging_instrumental"

RAW <- data.frame(
  item  = sprintf("dep03_%02d", 1:7),
  si_v  = c(219, 202, 145, 102, 192, 161, 185),
  si_m  = c(344, 486, 244, 204, 544, 266, 459),
  idsum = c(1110437, 1469721, 807989, 686939, 1597384, 923339, 1473011),
  label = c("telefono", "transporte", "medicamentos", "dinero", "compras", "comidas", "tareas hogar"))
N_V <- 1984; N_M <- 2670   # every record answered 1 or 2 on every DEP03 item

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
cat(sprintf("%-9s %-13s %22s %22s %18s  %s\n", "item", "content", "raw Si V/M, No V/M",
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
  cat(sprintf("%-9s %-13s %22s %22s %18s  %s\n", it, RAW$label[i], paste(rawv, collapse = "/"),
              paste(livev, collapse = "/"), paste0(RAW$idsum[i], "/", lid), if (same) "MATCH" else "MISMATCH"))
}
# off-diagonal: does any live item match a DIFFERENT raw column's signature?
off <- 0
for (i in seq_len(nrow(RAW))) for (j in seq_len(nrow(RAW))) if (i != j) {
  it <- RAW$item[i]
  livev <- c(g(it, "V", "2"), g(it, "M", "2"))
  if (all(livev == c(RAW$si_v[j], RAW$si_m[j]))) off <- off + 1
}
extra <- setdiff(unique(live$item), RAW$item)
if (length(extra)) { cat("unexpected live items:", extra, "\n"); ok <- FALSE }
extra_r <- setdiff(unique(live$resp), c("1", "2"))
if (length(extra_r)) { cat("unexpected live resp:", extra_r, "\n"); ok <- FALSE }

distinct <- length(unique(RAW$si_v + RAW$si_m)) == nrow(RAW) && length(unique(RAW$idsum)) == nrow(RAW)
cat(sprintf("\nraw per-item signatures (pooled Si count, id-sum) mutually distinct: %s\n", distinct))
cat(sprintf("off-diagonal matches (live item vs another column's Si by sex): %d of 42\n", off))
cat(sprintf("items matching under a flipped resp direction: %d of 7\n", flip_hits))
ok <- ok && distinct && flip_hits == 0 && off == 0
cat("Establishes: every code carries its own source column's responses, hence the codebook",
    "text printed under that column, and the option direction (resp 2 = Si).",
    "Does not establish: interviewer preamble, which the codebook does not print.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
