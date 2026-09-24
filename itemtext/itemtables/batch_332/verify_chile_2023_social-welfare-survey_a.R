# Verification for chile_2023_social-welfare-survey_a (batch_332). Self-contained.
# SOURCE: libro_de_codigos_ebs_2023.xlsx (bidat.gob.cl, EBS 2023 codebook), sheet 'A'. For every
# variable it lists each value, its label and the observed FREQUENCY. Those frequencies are hard-coded
# below (values 1..5; the -88/-99 missing codes are dropped by data/chile_2023_social-welfare-survey.do).
# If item codes, value coding and sample all carried across, each (item, value) count in the live table
# must equal the codebook's. A swap of any two items, or a reversed/shifted scale, breaks it: no two
# items share an identical 5-cell frequency vector (checked below).
suppressMessages(library(irw))
TB <- "chile_2023_social-welfare-survey_a"
CB <- list(
  a1   = c(154, 1077, 1095, 6409, 2485),
  a2_a = c(512, 1073, 2313, 4380, 2946),
  a2_b = c(471, 1042, 2036, 4432, 3244),
  a2_c = c(7498, 1899, 1068, 475, 288),
  a2_d = c(7073, 1669, 1288, 749, 448),
  a3   = c(529, 2989, 1216, 4682, 1802),
  a4   = c(123, 687, 653, 3483, 1386),
  a5   = c(155, 1261, 860, 3208, 853),
  a6   = c(382, 2364, 1355, 5672, 1453),
  a7   = c(1309, 3936, 1527, 3688, 656),
  a8   = c(561, 2628, 1207, 5307, 1524),
  a9   = c(295, 1549, 803, 6175, 2400),
  a10  = c(679, 3032, 1683, 4941, 879),
  a11  = c(1403, 3862, 1360, 3952, 651),
  a12  = c(59, 426, 794, 6927, 3026))

d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
tb <- table(factor(d$item, levels = names(CB)), factor(d$resp, levels = 1:5))

ok <- 0; tot <- 0
cat(sprintf("%-5s %-32s %-32s\n", "item", "codebook 1..5", "live 1..5"))
for (i in names(CB)) {
  live <- as.integer(tb[i, ]); tot <- tot + 5; ok <- ok + sum(live == CB[[i]])
  cat(sprintf("%-5s %-32s %-32s %s\n", i, paste(CB[[i]], collapse = "/"), paste(live, collapse = "/"),
              if (all(live == CB[[i]])) "" else "MISMATCH"))
}
cat(sprintf("\n%d of %d (item, value) frequencies match exactly\n", ok, tot))
distinct <- length(unique(vapply(CB, paste, "", collapse = "/"))) == length(CB)
cat("all 15 codebook frequency vectors distinct (so the test separates every item):", distinct, "\n")
extra <- setdiff(unique(d$item), names(CB))
cat("live items not in codebook:", if (length(extra)) paste(extra, collapse = ", ") else "(none)", "\n")
cat(if (ok == tot && distinct && !length(extra)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
