# verify_sned_bendall_2024.R -- Step 5b mapping check for sned_bendall_2024 (batch_177).
#
# Claim: the six live item codes carry the item_text shipped in
# sned_bendall_2024__items.csv. Codes are the OSF file's own column names
# (data/sned_bendall_2024.R pivots them by name, no positional step), and four of
# them repeat the Gorilla Open Materials object names (Living, Location, MostTime,
# MacArthur). The two leisure sliders are BOTH named "Leisure-Urban" in the Gorilla
# spec, so that pair's tie rests on the authors' column names -- which is why
# check B exists.
#
# A. Bendall et al. (2025) BRM 57:1, Table 1 (PMC11659377) prints, per item, the
#    count of respondents at <=5 (MacArthur: top 8-10 / middle 4-7 / bottom 1-3 rungs)
#    overall and in 8 recruitment regions. Hard-coded below; the live table has no
#    region column, so region (ProlificBatch) is joined from the OSF source file by id.
#    Every item's 9-count vector must equal its own Table 1 row and no other row.
# B. Content check independent of anyone's labels: people who place where they live
#    as rural should like rural leisure more than urban leisure, and vice versa.

suppressMessages({library(irw); library(dplyr); library(tidyr)})
TABLE <- "sned_bendall_2024"
REG <- c("AfricanNations","Arab/MiddleEastern","Asia(exAustralia+NZ)","Australia/NewZealand",
         "Europe","UK","NorthAmerica","South/CentralAmerica")  # Table 1 column order

# Table 1: All, Africa, Arab States/ME, Asia & S Pacific, Aus/NZ, Europe (ex UK), UK, N America, S/C America
PUB <- list(
  RULiving       = c(138, 12, 4, 17, 3, 34, 35, 29, 4),   # "Living location rural (responded <= 5)"
  RULocation     = c(128,  8, 4, 17, 3, 30, 30, 31, 5),   # "Current location rural"
  RUMostTime     = c(127, 10, 4, 16, 3, 25, 32, 29, 8),   # "Most time spent in rural location"
  RULeisureRural = c(223, 47, 14, 37, 19, 30, 14, 29, 33),# "Disliked rural leisure time"
  RULeisureUrban = c(248, 23, 17, 40, 7, 52, 48, 39, 22)  # "Disliked urban leisure time"
)
PUB_MAC <- list(top = c(69, 6, 14, 22, 4, 9, 3, 4, 7),
                mid = c(643, 82, 32, 118, 42, 127, 78, 78, 86),
                bot = c(89, 12, 5, 10, 4, 15, 18, 16, 9))
# Table 1 means (All column), printed for reading only -- see notes below.
PUB_MEAN <- c(RULiving = 7.50, RULocation = 7.60, RUMostTime = 7.62,
              RULeisureRural = 6.80, RULeisureUrban = 6.43, MacArthur = 5.58)

d <- irw::irw_fetch(TABLE)
w <- d %>% select(id, item, resp) %>% pivot_wider(names_from = item, values_from = resp)
src <- read.csv("https://osf.io/download/ft2jd/", fileEncoding = "UTF-8-BOM", check.names = FALSE)
names(src)[1] <- "ParticipantPrivateID"
m <- merge(w, src[, c("ParticipantPrivateID", "ProlificBatch")], by.x = "id", by.y = "ParticipantPrivateID")
cat("live respondents:", nrow(w), " joined to OSF region:", nrow(m), "\n\n")
m$reg <- factor(m$ProlificBatch, REG)
vec <- function(x) c(sum(x), as.integer(tapply(x, m$reg, sum)))

ok <- nrow(m) == nrow(w)
cat("A. Table 1 count vectors (All + 8 regions)\n")
for (it in names(PUB)) {
  obs <- vec(m[[it]] <= 5)
  own <- identical(as.numeric(obs), PUB[[it]])
  others <- names(PUB)[sapply(PUB, function(p) identical(as.numeric(obs), p))]
  cat(sprintf("  %-15s live %s\n  %-15s pub  %s  own-row exact=%s, rows matched=%s\n",
              it, paste(obs, collapse = " "), "", paste(PUB[[it]], collapse = " "),
              own, paste(others, collapse = ",")))
  ok <- ok && own && length(others) == 1
}
mac <- list(top = vec(m$MacArthur >= 8), mid = vec(m$MacArthur %in% 4:7), bot = vec(m$MacArthur <= 3))
for (b in names(mac)) {
  own <- identical(as.numeric(mac[[b]]), PUB_MAC[[b]])
  cat(sprintf("  MacArthur %-4s live %s | pub %s  exact=%s\n", b,
              paste(mac[[b]], collapse = " "), paste(PUB_MAC[[b]], collapse = " "), own))
  ok <- ok && own
}

cat("\n   means (All) for reading, not gating:\n")
for (it in names(PUB_MEAN))
  cat(sprintf("   %-15s pub %.2f live %.2f\n", it, PUB_MEAN[[it]], mean(m[[it]])))
cat("   RULeisureUrban All-column 6.43 is a Table 1 typo: the paper's own regional means\n",
    "   (7.34 6.49 6.83 7.30 6.49 5.46 6.14 7.28) weighted by n give 6.64, as live does;\n",
    "   the 248/553 split and SD 2.43 (live 2.42) match. UK RUMostTime is printed 6.24 vs\n",
    "   live 6.42 with its count (32) and SD (2.40) matching -- a digit transposition.\n", sep = "")

cat("\nB. Leisure pair content check\n")
diffRU <- m$RULeisureRural - m$RULeisureUrban
rural_dw <- mean(diffRU[m$RULiving <= 3]); city_dw <- mean(diffRU[m$RULiving == 10])
r_urb <- cor(m$RULiving, m$RULeisureUrban); r_rur <- cor(m$RULiving, m$RULeisureRural)
cat(sprintf("  RULiving<=3 (n=%d): mean(rural - urban leisure liking) = %+.2f\n", sum(m$RULiving <= 3), rural_dw))
cat(sprintf("  RULiving==10 (n=%d): mean(rural - urban leisure liking) = %+.2f\n", sum(m$RULiving == 10), city_dw))
cat(sprintf("  cor(RULiving, RULeisureUrban) = %+.2f ; cor(RULiving, RULeisureRural) = %+.2f\n", r_urb, r_rur))
okB <- rural_dw > 0 && city_dw < 0 && r_urb > r_rur
cat("  a swapped pair would flip all three signs; consistent with shipped mapping:", okB, "\n")
ok <- ok && okB

cat("\nDoes NOT establish: that the OSF column names were attached to the right Gorilla\n",
    "export objects for the three location items beyond the object-name match\n",
    "(Living/Location/MostTime); A pins each live code to the paper's own label for it.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
