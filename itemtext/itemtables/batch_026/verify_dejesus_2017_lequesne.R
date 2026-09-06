# verify_dejesus_2017_lequesne.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# data/dejesus_2017_ozone_knee.py melts ten columns of the PLOS S4 File
# (10.1371/journal.pone.0179185.s004) with NO rename, so each IRW `item` code IS
# the spreadsheet header ("Leq. Night", "Leq. Dist.", "Leq. Life dificulty 1"...).
# The shipped item_text comes from the study's own Portuguese protocol, S2 File
# "Anexo 3 -- Indice Funcional de Lequesne" (English twin: S3 File, Attachment 3),
# which prints all ten items IN THE SAME ORDER AS THE COLUMNS, with each item's
# own permitted score values.
#
# FALSIFIABLE PREDICTIONS
#
# (1) ROUTE 2 -- response-range fingerprint. The Lequesne index does NOT put its
#     items on one common scale. The supplement assigns, per item:
#       nocturnal pain / morning stiffness / pain on walking   -> 0,1,2   (3 levels)
#       standing 30 min / going up a flight                    -> 0,1     (2 levels)
#       maximum distance walked  0..6, +1 or +2 for crutches   -> 0..8    (9 levels)
#       four everyday-life items, "0 a 2" by half points       -> 0..2    (5 levels)
#     Each shipped item_text must therefore sit on the range the supplement gives
#     it. Checked LIVE via irw::irw_table_sets() (server-side aggregate, no export).
#     This is a 4-class partition; it pins Leq. Dist. outright and pins every other
#     item to its class. Within a class the codes are self-describing
#     ("Night"/"Morning"/"Walking"; "Standing"/"Going up") -- SKILL.md's
#     self-describing-code exemption -- EXCEPT the four "Life dificulty N", which
#     the code does not describe at all.
#
# (2) ROUTE 8 -- semantic coherence, for those four everyday-life items only.
#     The supplement lists them: 1 subir um andar (up a flight), 2 descer um andar
#     (down a flight), 3 agachar-se completamente (squat down fully), 4 caminhar
#     num terreno irregular (uneven ground). Two predictions follow from knee OA:
#       (a) full squatting is the hardest of the four, so item 3 has the HIGHEST
#           mean, and it is the one movement that is not gait/stairs, so it has the
#           LOWEST correlations with the rest;
#       (b) items 1 and 2 are the up/down pair of one activity, so they are the
#           most highly correlated PAIR in the block.
#     Computed from the CC BY S4 File itself (same numbers as the live table: the
#     per-item n and level sets below reproduce irw_table_sets() exactly).
#
# WHAT THIS DOES NOT ESTABLISH: nothing here separates "Leq. Life dificulty 1"
# (up a flight) from "Leq. Life dificulty 2" (down a flight) -- both are stair
# items on the same range, their means differ by only 0.08, and only the
# supplement's listing order ties each to its number. Status is PARTIAL.

suppressMessages(library(irw))
TABLE <- "dejesus_2017_lequesne"

# --- (1) live range fingerprint --------------------------------------------
EXPECTED <- list(  # item -> c(min, max, n_levels) per S2/S3 File, Anexo/Attachment 3
  "Leq. Night"            = c(0, 2, 3), "Leq. Morning"          = c(0, 2, 3),
  "Leq. Walking"          = c(0, 2, 3), "Leq. Standing"         = c(0, 1, 2),
  "Leq. Going up"         = c(0, 1, 2), "Leq. Dist."            = c(0, 8, 9),
  "Leq. Life dificulty 1" = c(0, 2, 5), "Leq. Life dificulty 2" = c(0, 2, 5),
  "Leq. Life dificulty 3" = c(0, 2, 5), "Leq. Life dificulty 4" = c(0, 2, 5))

s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
ok1 <- TRUE
cat(sprintf("%-24s %-16s %-16s\n", "item", "expected(min,max,k)", "live(min,max,k)"))
for (nm in names(EXPECTED)) {
  r <- pi[pi$item == nm, ]
  e <- EXPECTED[[nm]]
  o <- c(r$resp_min[1], r$resp_max[1], r$n_resp_levels[1])
  m <- isTRUE(all.equal(as.numeric(e), as.numeric(o)))
  ok1 <- ok1 && m
  cat(sprintf("%-24s %-16s %-16s %s\n", nm,
              paste(e, collapse = ","), paste(o, collapse = ","),
              if (m) "ok" else "MISMATCH"))
}
cat(sprintf("\nrange fingerprint: %s\n", if (ok1) "all 10 items on the range the supplement gives them"
                                         else "FAILED"))
# max attainable total, a second structural check: 2+2+1+2+1+8+2+2+2+2 = 24,
# and the paper states the Lequesne index runs "0 to 24 points".
tot <- sum(vapply(EXPECTED, function(e) e[2], numeric(1)))
cat(sprintf("sum of per-item maxima: %g (paper states the index scores 0-24)\n", tot))
ok1 <- ok1 && tot == 24

# --- (2) everyday-life block, from the CC BY source file --------------------
S4 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0179185.s004"
f  <- file.path(tempdir(), "s004_dejesus.xls")  # served as .xlsx, actually a legacy .xls
ok2 <- NA
try({
  if (!file.exists(f)) download.file(S4, f, quiet = TRUE, mode = "wb")
  d <- readxl::read_excel(f)
  adl <- paste("Leq. Life dificulty", 1:4)
  m <- vapply(adl, function(c) mean(as.numeric(d[[c]]), na.rm = TRUE), numeric(1))
  cat("\nEveryday-life block, item means (S4 File; 1=up stairs 2=down stairs",
      "3=full squat 4=uneven ground):\n")
  for (i in 1:4) cat(sprintf("  %-24s mean = %.3f\n", adl[i], m[i]))
  R <- cor(sapply(adl, function(c) as.numeric(d[[c]])), use = "pairwise.complete.obs")
  cat("\ncorrelations:\n"); print(round(R, 3))
  off <- R; diag(off) <- NA
  hi_mean  <- which.max(m) == 3
  lo_cor   <- which.min(colMeans(off, na.rm = TRUE)) == 3
  top_pair <- identical(as.integer(sort(unname(which(off == max(off, na.rm = TRUE), arr.ind = TRUE)[1, ]))), c(1L, 2L))
  cat(sprintf("\n  (a) squat item has the highest mean (%.3f vs %.3f/%.3f/%.3f): %s\n",
              m[3], m[1], m[2], m[4], hi_mean))
  cat(sprintf("      squat item has the lowest mean off-diagonal r (%.3f vs %.3f/%.3f/%.3f): %s\n",
              mean(off[, 3], na.rm = TRUE), mean(off[, 1], na.rm = TRUE),
              mean(off[, 2], na.rm = TRUE), mean(off[, 4], na.rm = TRUE), lo_cor))
  cat(sprintf("  (b) items 1-2 are the most correlated pair (r = %.3f, max off-diagonal = %.3f): %s\n",
              R[1, 2], max(off, na.rm = TRUE), top_pair))
  ok2 <- hi_mean && lo_cor && top_pair
}, silent = FALSE)
if (is.na(ok2)) cat("\n(route 8 skipped: source file unreachable)\n")

cat("\nNOT ESTABLISHED: 'Leq. Life dificulty 1' (up a flight) vs '... 2' (down a flight)\n",
    "are not distinguished by any of the above -- same range, means 0.755 vs 0.839.\n",
    "Their assignment rests on the supplement's listing order alone. => PARTIAL.\n", sep = "")

cat(if (ok1 && isTRUE(ok2)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
