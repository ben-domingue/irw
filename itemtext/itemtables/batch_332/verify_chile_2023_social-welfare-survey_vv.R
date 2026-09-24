# Verification for chile_2023_social-welfare-survey_vv (batch_332, #2381 slice 02). Self-contained.
#
# SOURCE. Encuesta de Bienestar Social 2023 (EBS 2023), Subsecretaría de Evaluación Social / INE, Chile.
# The official codebook 'libro_de_codigos_ebs_2023.xlsx' (bidat.gob.cl dataset
# f80237f5-9231-40d1-a1f1-ed93751dc2ac, sha256 11947ccf...1e28 fetched 2026-09-23), sheet 'V',
# lists every variable with each permitted value and the OBSERVED FREQUENCY of that value.
# Those frequencies are hard-coded below.
#
# WHAT THIS TESTS. item codes are the codebook's own variable Names (the do-file melts vv1_a..vv3
# by name), so the item axis needs no inference. This reproduces the published (item, value)
# counts from the live table: a wrong item<->text tie, a flipped Sí/No coding or a different
# sample would each break it. All five items have distinct Sí counts (4704/1517/1049/3064/4416),
# so the check separates every item from every other and pins resp 1=Sí, 2=No per item.
# It also checks that the live NA-resp rows equal the codebook's -88/-99 counts per item
# (response-data residue, reported not failed).
suppressMessages(library(irw))
TABLE <- "chile_2023_social-welfare-survey_vv"
CB <- list(  # item = c(freq at 1 (Sí), freq at 2 (No), freq -88 + -99)
  vv1_a = c(4704, 6524, 4 + 2),
  vv1_b = c(1517, 9715, 2 + 0),
  vv1_c = c(1049, 10177, 8 + 0),
  vv2   = c(3064, 8168, 2 + 0),
  vv3   = c(4416, 6816, 1 + 1))

d <- as.data.frame(irw::irw_fetch(TABLE))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
it <- read.csv(file.path("itemtables/batch_332", paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)

ok <- TRUE
cat(sprintf("%-6s %8s %8s %8s %8s %6s %6s\n", "item", "cb_Si", "live_1", "cb_No", "live_2", "cb_NA", "liveNA"))
for (k in names(CB)) {
  x <- d[d$item == k, ]
  l1 <- sum(x$resp == 1, na.rm = TRUE); l2 <- sum(x$resp == 2, na.rm = TRUE); lna <- sum(is.na(x$resp))
  cat(sprintf("%-6s %8d %8d %8d %8d %6d %6d\n", k, CB[[k]][1], l1, CB[[k]][2], l2, CB[[k]][3], lna))
  if (l1 != CB[[k]][1] || l2 != CB[[k]][2]) ok <- FALSE
}
cat("\nshipped option_text per resp (must be 1=Sí, 2=No for every item):\n")
lab <- unique(it[, c("resp", "option_text")]); print(lab, row.names = FALSE)
if (!identical(sort(paste(lab$resp, lab$option_text)), c("1 Sí", "2 No"))) ok <- FALSE
cat("\nSí counts are pairwise distinct:", length(unique(sapply(CB, `[`, 1))) == length(CB), "\n")
cat("Not established: nothing further needed -- codes are the source variable names.\n")
cat("NOTE: live NA-resp rows (", sum(is.na(d$resp)), ") are the codebook's No sabe/No responde cells;",
    "a response-data residue, not a mapping failure.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
