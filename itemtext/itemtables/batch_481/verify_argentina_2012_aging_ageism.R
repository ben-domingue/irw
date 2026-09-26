# verify_argentina_2012_aging_ageism.R -- batch_481, Step 5b.
#
# Claim: live item codes re01..re05 are the ENCaViAM 2012 user-base column names
# RE01..RE05 lower-cased (data/argentina_2012_aging.do: rename *, lower; item = "`var'"),
# and each carries the statement INDEC prints under that variable name in
# "doc_utilizacion_ENCaViAM 2012.pdf" (Relación con el entorno, pp.39-40).
# The .do (Bookmark 5) drops 9 Ns/Nc and reverses re01/re02/re04/re05 (resp = 3 - x),
# leaving re03 as coded. So live resp 2 = Sí for re01/02/04/05, and resp 1 = Sí for re03.
#
# Two independent checks, both hard-coded from INDEC publications, compared to live data:
#  (A) Route 1/8 (text -> code): INDEC "Principales resultados" (encaviam.pdf) Cuadro 32 prints
#      the WEIGHTED Sí/No/Ns-Nc % for each statement, labelled by its wording, not by code.
#      Recomputing those weighted % from the raw user base (POND_CALIBRADA) per column
#      reproduced all 15 values exactly (done offline at extraction time; raw file sha256
#      8c1d18a9...29723). The same raw columns' Sí/No counts are hard-coded below as RAW.
#      The five published triples are mutually distinct, so that step ties every
#      statement to exactly one column.
#  (B) Route 9 (column -> live code + option direction): live per-item resp counts must
#      equal the raw column's counts under the .do's recode, cell for cell; the five
#      count pairs are mutually distinct and a flipped direction must fail.
# Live counts come from a server-side GROUP BY (no table export).

suppressMessages(library(irw))
TABLE <- "argentina_2012_aging_ageism"

# Cuadro 32 (weighted %, Sí/No/NsNc) by statement, keyed to the column whose weighted
# distribution reproduces it (recomputed from ENCaViAM2012_Base_usuario.txt at extraction).
CUADRO32 <- rbind(
  re01 = c(38.9, 55.3, 5.7),  # banco u oficina pública ... peor trato
  re02 = c(21.5, 73.5, 5.1),  # consultorio médico ... peor trato
  re03 = c(68.8, 26.2, 5.0),  # en la familia ... se las respeta más
  re04 = c(20.3, 74.5, 5.2),  # en la familia ... se las insulta o agrede
  re05 = c(20.1, 72.2, 7.6))  # uso del dinero o cosas de valor sin permiso

# Raw unweighted counts of source codes 1 = Sí, 2 = No, 9 = Ns/Nc per column
RAW <- rbind(re01 = c(1648, 2783, 223), re02 = c(977, 3481, 196), re03 = c(3331, 1163, 160),
             re04 = c(1010, 3425, 219), re05 = c(1031, 3321, 302))
SI_IS_2 <- c(re01 = TRUE, re02 = TRUE, re03 = FALSE, re04 = TRUE, re05 = TRUE)

live <- tryCatch({
  tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
  q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, CAST(resp AS STRING) AS resp,",
                     "COUNT(*) AS n FROM `%s` GROUP BY item, resp"), tbl$qualified_reference)
  as.data.frame(irw:::.irw_query_tibble(q))
}, error = function(e) {
  message("server-side query unavailable (", conditionMessage(e), "); using irw_fetch()")
  d <- as.data.frame(irw::irw_fetch(TABLE))
  aggregate(list(n = rep(1, nrow(d))), list(item = d$item, resp = as.character(d$resp)), sum)
})
live$resp <- as.character(as.numeric(live$resp))
cnt <- function(it, r) sum(live$n[live$item == it & live$resp == r])

ok <- TRUE
cat("(A) Cuadro 32 weighted % triples distinct across statements:",
    d32 <- nrow(unique(CUADRO32)) == 5, "\n")
ok <- ok && d32
# Re-derive the text->column tie from the raw user base when it is available locally
# (INDEC ftp .../menusuperior/encaviam/ENCaViAM2012_Base_usuario.txt, 4.9 MB).
RAWF <- ".cache/argentina_2012_aging_ageism/ENCaViAM2012_Base_usuario.txt"
if (file.exists(RAWF)) {
  rd <- read.delim(RAWF, sep = "|", check.names = FALSE); names(rd) <- tolower(names(rd))
  w <- as.numeric(gsub(",", ".", rd$pond_calibrada))
  for (it in rownames(CUADRO32)) {
    x <- as.numeric(rd[[it]])
    wp <- round(100 * tapply(w, factor(x, levels = c(1, 2, 9)), sum) / sum(w), 1)
    rc <- as.vector(table(factor(x, levels = c(1, 2, 9))))
    m <- all(wp == CUADRO32[it, ]) && all(rc == RAW[it, ])
    # would any other statement's triple also match this column?
    oth <- sum(sapply(setdiff(rownames(CUADRO32), it), function(b) all(wp == CUADRO32[b, ])))
    ok <- ok && m && oth == 0
    cat(sprintf("    raw %s weighted %s vs Cuadro 32 %s; raw counts %s  %s\n", it,
                paste(wp, collapse = "/"), paste(CUADRO32[it, ], collapse = "/"),
                paste(rc, collapse = "/"), if (m && oth == 0) "MATCH" else "MISMATCH"))
  }
} else cat("    raw user base not cached; (A) relies on the recorded extraction-time recomputation\n")
cat(sprintf("\n(B) %-5s %14s %14s %14s  %s\n", "item", "raw Si/No", "live Si/No", "flipped", "result"))
flip_hits <- 0
for (it in rownames(RAW)) {
  si_r <- if (SI_IS_2[[it]]) "2" else "1"; no_r <- if (SI_IS_2[[it]]) "1" else "2"
  l <- c(cnt(it, si_r), cnt(it, no_r)); f <- c(cnt(it, no_r), cnt(it, si_r))
  same <- all(l == RAW[it, 1:2]); fl <- all(f == RAW[it, 1:2])
  flip_hits <- flip_hits + fl; ok <- ok && same
  cat(sprintf("    %-5s %14s %14s %14s  %s\n", it, paste(RAW[it, 1:2], collapse = "/"),
              paste(l, collapse = "/"), paste(f, collapse = "/"), if (same) "MATCH" else "MISMATCH"))
}
# does any OTHER item's raw pair match this item's live pair? (permutation test)
cross <- 0
for (a in rownames(RAW)) for (b in rownames(RAW)) if (a != b) {
  si_r <- if (SI_IS_2[[a]]) "2" else "1"; no_r <- if (SI_IS_2[[a]]) "1" else "2"
  if (all(c(cnt(a, si_r), cnt(a, no_r)) == RAW[b, 1:2])) cross <- cross + 1 }
cat(sprintf("\noff-diagonal matches (item a live vs item b raw): %d of 20\n", cross))
cat(sprintf("items matching under a flipped resp direction: %d of 5\n", flip_hits))
extra <- setdiff(unique(live$item), rownames(RAW)); extra_r <- setdiff(unique(live$resp), c("1", "2"))
if (length(extra) || length(extra_r)) { cat("unexpected live values:", extra, extra_r, "\n"); ok <- FALSE }
ok <- ok && cross == 0 && flip_hits == 0
cat("Establishes: each statement's code (Cuadro 32 triple unique per statement; live counts unique per",
    "item) and the per-item option direction (re03 resp 1 = Sí; others resp 2 = Sí).",
    "Does not establish: interviewer framing, which the codebook does not print.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
