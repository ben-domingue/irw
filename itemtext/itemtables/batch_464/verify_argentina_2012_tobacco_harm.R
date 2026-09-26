# verify_argentina_2012_tobacco_harm.R -- batch_464, Step 5b.
#
# Claim: live item codes h01, h02a..h02g, h03 are the EMTA 2012 (GATS Argentina) user-file
# column names lower-cased (data/argentina_2012_tobacco.do, `rename *, lower`), and INDEC's
# "Diseño de registro" (EMTA2012_Argentina_Disenoderegistro.pdf, pp.58-60) prints each
# question under that exact variable name together with its sample frequencies.
# The .do drops 7 (No sabe) / 9 (Se niega) and reverses 1 Sí / 2 No to resp = 3 - x, so
# live resp 2 = Sí and resp 1 = No.
#
# Route 9 / route 1: the codebook's per-item "Muestral Frecuencia" for Sí and No must equal
# the live per-item counts of resp 2 and resp 1, cell for cell. The nine (No, Sí) count
# pairs are mutually distinct, so any permutation of item text among codes, or a flipped
# option direction, breaks the match.
#
# Live counts come from a server-side GROUP BY (no table export); falls back to
# irw_fetch() only if the package internals are unavailable (43k rows).

suppressMessages(library(irw))
TABLE <- "argentina_2012_tobacco_harm"

# Codebook frequencies (Muestral Frecuencia): c(No = code 2, Sí = code 1)
PUB <- list(
  h01  = c(96,   6478),  # ¿fumar tabaco causa enfermedades graves?
  h02a = c(316,  5129),  # accidente cerebrovascular
  h02b = c(122,  6056),  # infarto o ataque cardíaco
  h02c = c(50,   6516),  # cáncer de pulmón
  h02d = c(790,  2056),  # cáncer de vejiga
  h02e = c(639,  3147),  # cáncer de estómago
  h02f = c(356,  4670),  # nacimiento prematuro
  h02g = c(787,  2403),  # osteoporosis
  h03  = c(524,  3031))  # ¿usar tabaco sin humo causa enfermedades graves?

live <- tryCatch({
  tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
  q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, CAST(resp AS STRING) AS resp,",
                     "COUNT(*) AS n FROM `%s` GROUP BY item, resp"), tbl$qualified_reference)
  as.data.frame(irw:::.irw_query_tibble(q))
}, error = function(e) {
  message("server-side query unavailable (", conditionMessage(e), "); using irw_fetch()")
  d <- as.data.frame(irw::irw_fetch(TABLE))
  a <- aggregate(list(n = rep(1, nrow(d))), list(item = d$item, resp = as.character(d$resp)), sum)
  a
})
live$resp <- as.character(as.numeric(live$resp))

ok <- TRUE
cat(sprintf("%-5s %18s %18s  %s\n", "item", "codebook No/Si", "live r1/r2", "result"))
for (it in names(PUB)) {
  l <- c(sum(live$n[live$item == it & live$resp == "1"]),
         sum(live$n[live$item == it & live$resp == "2"]))
  same <- all(l == PUB[[it]])
  ok <- ok && same
  cat(sprintf("%-5s %18s %18s  %s\n", it, paste(PUB[[it]], collapse = "/"),
              paste(l, collapse = "/"), if (same) "MATCH" else "MISMATCH"))
}
extra <- setdiff(unique(live$item), names(PUB))
if (length(extra)) { cat("unexpected live items:", extra, "\n"); ok <- FALSE }
pm <- do.call(rbind, PUB)
distinct <- nrow(unique(pm)) == nrow(pm)
cat(sprintf("\nnine codebook (No, Si) pairs mutually distinct: %s\n", distinct))
ok <- ok && distinct
cat("Establishes: each code's text (count pair unique per item) and option direction",
    "(resp 2 = Si). Does not establish: interviewer framing, which the codebook does not print.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
