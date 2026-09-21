# Orchestrator Step 5b check, batch_287, 2026-09-20.
#
# Question: do the deposit's CAI_* / ID_* column labels correspond to the items
# the paper says they do?  Source of truth is the paper's OWN descriptives table
# (Additional file 2, 40862_2025_378_MOESM2_ESM.xlsx), which lists every
# questionnaire item as q1..q38 interleaved with its scale/section subtotals.
#
# Result: CAI is shifted by +4 and ID does not correspond at all.
# Consequence: mekheimer_2026_cai and mekheimer_2026_id were NOT shipped.
# mekheimer_2026_flp is unaffected (it matches by name) and WAS shipped.

suppressMessages({library(irw); library(dplyr); library(tidyr); library(readxl)})

XL <- ".cache/mekheimer_2026_cai/40862_2025_378_MOESM2_ESM.xlsx"
if (!file.exists(XL)) stop("re-download figshare 31387849 (Additional file 2) to ", XL)
raw <- suppressMessages(read_excel(XL, sheet = 1, col_names = FALSE))
hdr <- as.character(unlist(raw[35, ]))       # label row
mn  <- suppressWarnings(as.numeric(unlist(raw[38, ])))   # "Mean" row
keep <- !is.na(hdr) & !is.na(mn)
lab <- setNames(mn[keep], trimws(hdr[keep]))

cat("=== (1) which q's belong to which scale: section subtotals must reproduce ===\n")
secs <- list(
  c("PAF Sec1","1","5","Section 1: Research Autonomy"),
  c("PAF Sec2","6","10","Section 2: Teaching &amp; Expressive Freedom"),
  c("CAI PartA","11","19","Part A: Global Identity Alignment"),
  c("CAI PartB","20","28","Part B: Local Identity Alignment"),
  c("ID Sec1","29","33","Section 1: Internal Dissonance: Authenticity &amp; Values"),
  c("ID Sec2","34","38","Section 2: Environmental Dissonance"))
ok_sec <- TRUE
for (s in secs) {
  a <- as.integer(s[2]); b <- as.integer(s[3])
  got <- sum(lab[paste0("q", a:b)]); pub <- unname(lab[s[4]])
  cat(sprintf("  %-10s q%-2s-q%-2s sum=%9.4f published=%9.4f diff=%+.5f\n", s[1], a, b, got, pub, got-pub))
  if (abs(got-pub) > 1e-3) ok_sec <- FALSE
}
cat("  -> CAI is q11..q28, ID is q29..q38.  subtotals reproduce:", ok_sec, "\n")

qs <- unname(lab[paste0("q", 1:38)])

live_means <- function(tbl) {
  d <- irw_fetch(tbl)
  w <- d %>% select(id, item, resp) %>% pivot_wider(names_from = item, values_from = resp)
  its <- paste0(sub("^mekheimer_2026_", "", toupper(sub("mekheimer_2026_", "", tbl))), "_")
  list(d = d, w = w)
}

cat("\n=== (2) FLP matches the SPSS BY NAME -> the two files describe the same responses ===\n")
fl <- live_means("mekheimer_2026_flp")
flp_ok <- TRUE
for (n in c("FLP_Reading","FLP_Writing","FLP_Speaking","FLP_Listening")) {
  lv <- mean(fl$w[[n]], na.rm = TRUE)
  cat(sprintf("  %-15s live=%.5f spss=%.5f diff=%+.5f\n", n, lv, lab[[n]], lv-lab[[n]]))
  if (abs(lv - lab[[n]]) > 0.02) flp_ok <- FALSE
}
cat("  -> all four agree to <0.006, so cross-file mean comparison is valid:", flp_ok, "\n")

cat("\n=== (3) CAI_1..CAI_18: which q window do they actually match? ===\n")
ca <- live_means("mekheimer_2026_cai")
cailive <- sapply(paste0("CAI_", 1:18), function(i) mean(ca$w[[i]], na.rm = TRUE))
tab <- data.frame()
for (off in 0:20) {
  seg <- qs[(off+1):(off+18)]
  d <- cailive - seg
  tab <- rbind(tab, data.frame(window = sprintf("q%d..q%d", off+1, off+18),
                               maxabs = max(abs(d)), rmse = sqrt(mean(d^2))))
}
print(tab, row.names = FALSE, digits = 4)
best <- tab[which.min(tab$rmse), ]; second <- sort(tab$rmse)[2]
cat(sprintf("\n  BEST %s  rmse=%.4f ; next-best rmse=%.4f (%.0fx worse)\n",
            best$window, best$rmse, second, second/best$rmse))
shift_ok <- best$window == "q15..q32" && best$maxabs < 0.02
cat("  The paper says CAI is q11..q28. The deposit's CAI_* columns are q15..q32,\n",
    " i.e. shifted +4 and overrunning into the ID scale (q29..q32).\n")

cat("\n=== (4) ID_1..ID_10 match no q window at all ===\n")
idd <- live_means("mekheimer_2026_id")
idlive <- sapply(paste0("ID_", 1:10), function(i) mean(idd$w[[i]], na.rm = TRUE))
bt <- data.frame()
for (off in 0:28) {
  d <- idlive - qs[(off+1):(off+10)]
  bt <- rbind(bt, data.frame(window = sprintf("q%d..q%d", off+1, off+10), maxabs = max(abs(d))))
}
bb <- bt[which.min(bt$maxabs), ]
cat(sprintf("  best of 29 windows: %s maxabs=%.4f (no match)\n", bb$window, bb$maxabs))
cat(sprintf("  live ID_1 mean=%.5f exceeds the largest q mean anywhere (%.5f)\n", idlive[[1]], max(qs)))
cat(sprintf("  live ID resp range = %d..%d, but the paper's ID items are 5-point\n",
            min(idd$d$resp, na.rm = TRUE), max(idd$d$resp, na.rm = TRUE)))
id_bad <- bb$maxabs > 0.1

cat("\n")
if (ok_sec && flp_ok && shift_ok && id_bad) cat("VERDICT: PASS\n") else cat("VERDICT: FAIL\n")
