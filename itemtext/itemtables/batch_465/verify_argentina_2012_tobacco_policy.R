# verify_argentina_2012_tobacco_policy.R -- batch_465, Step 5b.
#
# Claim: live item codes har04a, har04b, h05, h06 are the EMTA 2012 (GATS Argentina)
# user-file column names lower-cased (data/argentina_2012_tobacco.do, `rename *, lower`),
# and INDEC's "Diseño de registro" (EMTA2012_Argentina_Disenoderegistro.pdf, pp.61-62)
# prints each question under that exact variable name with its sample frequencies.
# The .do (Bookmark 2: policy) drops 7 (No sabe) / 9 (Se niega) and reverses
# 1 A favor / 2 En contra to resp = 3 - x, so live resp 2 = A favor, resp 1 = En contra.
#
# Route 9 / route 1: the codebook's per-item "Muestral Frecuencia" for A favor and
# En contra must equal the live per-item counts of resp 2 and resp 1, cell for cell.
# The four (En contra, A favor) pairs are mutually distinct, so any permutation of
# item text among codes, or a flipped option direction, breaks the match.
#
# Live counts come from a server-side GROUP BY (no table export); falls back to
# irw_fetch() only if the package internals are unavailable (25k rows).

suppressMessages(library(irw))
TABLE <- "argentina_2012_tobacco_policy"

# Codebook frequencies (Muestral Frecuencia): c(En contra = code 2, A favor = code 1)
PUB <- list(
  har04a = c(142, 6390),  # ley que prohíbe fumar en espacios laborales cerrados y lugares públicos
  har04b = c(224, 6110),  # nueva ley: prohíbe fumar en salas de juegos de azar
  h05    = c(894, 5139),  # aumentar los impuestos sobre los productos del tabaco
  h06    = c(542, 5582))  # ley que prohíba todas las publicidades de productos del tabaco

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
cat(sprintf("%-7s %20s %16s  %s\n", "item", "codebook EnContra/AFavor", "live r1/r2", "result"))
for (it in names(PUB)) {
  l <- c(cnt(it, "1"), cnt(it, "2"))
  same <- all(l == PUB[[it]])
  ok <- ok && same
  cat(sprintf("%-7s %20s %16s  %s\n", it, paste(PUB[[it]], collapse = "/"),
              paste(l, collapse = "/"), if (same) "MATCH" else "MISMATCH"))
}
extra <- setdiff(unique(live$item), names(PUB))
if (length(extra)) { cat("unexpected live items:", extra, "\n"); ok <- FALSE }
extra_r <- setdiff(unique(live$resp), c("1", "2"))
if (length(extra_r)) { cat("unexpected live resp:", extra_r, "\n"); ok <- FALSE }

# Would any other assignment also match? Count permutations/flips that reproduce live.
pm <- do.call(rbind, PUB)
distinct <- nrow(unique(pm)) == nrow(pm) && !any(pm[, 1] == pm[, 2])
flip_hits <- sum(sapply(names(PUB), function(it) all(c(cnt(it, "2"), cnt(it, "1")) == PUB[[it]])))
cat(sprintf("\nfour codebook pairs mutually distinct (and asymmetric): %s\n", distinct))
cat(sprintf("items matching under a flipped resp direction: %d of 4\n", flip_hits))
ok <- ok && distinct && flip_hits == 0
cat("Establishes: each code's text (count pair unique per item) and option direction",
    "(resp 2 = A favor). Does not establish: interviewer framing, which the codebook does not print.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
