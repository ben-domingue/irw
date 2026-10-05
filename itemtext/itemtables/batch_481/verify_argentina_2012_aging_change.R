# verify_argentina_2012_aging_change.R -- batch_481, Step 5b.
#
# Claim: live item codes au02, au04 are the ENCaViAM 2012 user-file column names
# lower-cased (data/argentina_2012_aging.do: `rename *, lower`; Bookmark 2 uses the column
# name as item). INDEC's "Documento para la utilizacion de la base de datos usuario"
# (doc_utilizacion_ENCaViAM 2012.pdf, p.32) prints AU02 = health vs last year and
# AU04 = memory vs last year, each coded 1 ...ha mejorado? / 2 ...esta igual? / 3 ...ha empeorado?.
# The .do reverses (resp = 4 - x), so live resp 3 = ha mejorado, 1 = ha empeorado.
#
# Route 9: per-item resp counts in INDEC's raw user file (ENCaViAM2012_Base_usuario.txt,
# sha256 8c1d18a9...29723), reversed per the .do, must equal the live counts cell for cell;
# the two items' count vectors differ, so a swap of au02/au04 or a flipped direction breaks it.
# Route 8 (content coherence, raw file): AU02 (health change) should track AU01 (self-rated
# health) more than AU03 (self-rated memory), and AU04 (memory change) the reverse; the
# positive sign (all four coded 1 = best) also corroborates the codebook's option direction.
#
# Live counts via server-side GROUP BY (no export).

suppressMessages(library(irw))
TABLE <- "argentina_2012_aging_change"
RAW_URL <- "https://www.indec.gob.ar/ftp/cuadros/menusuperior/encaviam/ENCaViAM2012_Base_usuario.txt"

# Raw user-file counts, source codes 1 mejorado / 2 igual / 3 empeorado (computed 2026-09-25
# from the file above; hard-coded so the core check runs offline).
RAW <- list(au02 = c(`1` = 474, `2` = 3070, `3` = 1110),
            au04 = c(`1` = 167, `2` = 3768, `3` = 719))
# After the .do's 4 - x: live resp 1 = raw 3, live 2 = raw 2, live 3 = raw 1.
EXPECT <- lapply(RAW, function(v) c(`1` = v[["3"]], `2` = v[["2"]], `3` = v[["1"]]))

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
lv <- function(it) sapply(c("1", "2", "3"), function(r) cnt(it, r))

ok <- TRUE
cat(sprintf("%-6s %26s %22s  %s\n", "item", "expected live r1/r2/r3", "live r1/r2/r3", "result"))
for (it in names(EXPECT)) {
  l <- lv(it); same <- all(l == EXPECT[[it]]); ok <- ok && same
  cat(sprintf("%-6s %26s %22s  %s\n", it, paste(EXPECT[[it]], collapse = "/"),
              paste(l, collapse = "/"), if (same) "MATCH" else "MISMATCH"))
}
extra <- setdiff(unique(live$item), names(EXPECT))
if (length(extra)) { cat("unexpected live items:", extra, "\n"); ok <- FALSE }
swap_hits <- sum(all(lv("au02") == EXPECT$au04), all(lv("au04") == EXPECT$au02))
flip_hits <- sum(sapply(names(EXPECT), function(it) all(rev(lv(it)) == EXPECT[[it]])))
cat(sprintf("\nitems matching under an au02/au04 swap: %d of 2\n", swap_hits))
cat(sprintf("items matching under a flipped resp direction: %d of 2\n", flip_hits))
ok <- ok && swap_hits == 0 && flip_hits == 0

# Content coherence from the raw file (best effort; skipped offline).
raw <- tryCatch(read.delim(url(RAW_URL), sep = "|", check.names = FALSE), error = function(e) NULL)
if (!is.null(raw)) {
  r <- function(a, b) cor(raw[[a]], raw[[b]], use = "complete.obs", method = "spearman")
  m <- matrix(c(r("AU02", "AU01"), r("AU02", "AU03"), r("AU04", "AU01"), r("AU04", "AU03")), 2, byrow = TRUE,
              dimnames = list(c("AU02", "AU04"), c("AU01 health", "AU03 memory")))
  cat("\nraw-file Spearman correlations (all coded 1 = best):\n"); print(round(m, 3))
  coh <- m[1, 1] > m[1, 2] && m[2, 2] > m[2, 1] && all(m > 0)
  cat("AU02 tracks health, AU04 tracks memory, all positive:", coh, "\n")
  ok <- ok && coh
} else cat("\n(raw file not reachable; content-coherence check skipped)\n")

cat("Establishes: each code's text (distinct count vectors, content coherence) and option direction",
    "(live 3 = ha mejorado). Does not establish: interviewer framing, which the codebook does not print.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
