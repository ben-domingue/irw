# verify_neurodegenerative_huizinga_2019_vfq.R
#
# Claim under test: IRW item code VFQ.n is question n of the NEI Visual
# Functioning Questionnaire-25 (version 2000) as printed by RAND, and IRW `resp`
# is the RAND-converted 0-100 item score rescaled to 0-4 (0-5 for VFQ.2), so that
# HIGHER resp = BETTER vision-related functioning.  Both halves of that claim are
# what the shipped item_text / option_text rest on.
#
# The processing script (data/neurodegenerative_huizinga_2019.R) carries the
# deposit's own column names VFQ.1..VFQ.25 / VFQ.15a-c / VFQ.16a through
# unchanged and recodes 0/25/50/75/100 -> 0/1/2/3/4 (VFQ.2: 0/20/40/60/80/100 ->
# 0..5), leaving the unscored skip items VFQ.15/.15a/.15b at their raw codes.
#
# Three checks:
#   A. Live-vs-deposit reconstruction, cell for cell. Every item's live resp
#      frequency table must equal the deposit column's recoded frequency table.
#      This licenses using the deposit for check B and pins the resp recode.
#   B. Subscale arithmetic. The deposit ships the 12 NEI-VFQ scored subscale
#      columns. Each must reproduce exactly as the unweighted mean of the
#      canonical NEI-VFQ item set for that subscale (core items + the optional
#      appendix items VFQ.A*, which this study also administered). This is the
#      item-identity route: it pins each core item to its published subscale, and
#      uniquely identifies VFQ.1, VFQ.2, VFQ.10 (peripheral) and VFQ.12 (colour).
#   C. Scale direction. (i) every pairwise correlation among the 25 scored items
#      is positive, so all items share one direction; (ii) the direction is
#      anchored by VFQ.24 ("I need a lot of help from others because of my
#      eyesight"), whose extreme level holds ~94% of this community sample -- that
#      level must be "Definitely False", not "Definitely True"; (iii) daytime
#      driving in familiar places (VFQ.15c) must be easier than driving at night
#      (VFQ.16).
#
# NOT established here: the order of items WITHIN a subscale (5/6/7, 8/9/14,
# 11/13, 3/21/22/25, 17/18, 20/23/24, 15c/16/16a, 4/19). That rests on the item
# codes being the deposit's own column names, which reproduce the questionnaire's
# printed numbering including the irregular 15/15a/15b/15c/16a sequence.

suppressMessages(library(irw))
TABLE <- "neurodegenerative_huizinga_2019_vfq"

CORE <- c(paste0("VFQ.", 1:14), "VFQ.15", "VFQ.15a", "VFQ.15b", "VFQ.15c",
          "VFQ.16", "VFQ.16a", paste0("VFQ.", 17:25))

## ---- raw deposit (DataverseNL doi:10.34894/CMJXAK, Data_total.csv) ----------
raw_url <- "https://dataverse.nl/api/access/datafile/19456"
f <- file.path(tempdir(), "huizinga_Data_total.csv")
if (!file.exists(f)) download.file(raw_url, f, quiet = TRUE)
raw <- read.csv(f, sep = ";", stringsAsFactors = FALSE, fileEncoding = "latin1")
num <- function(x) suppressWarnings(as.numeric(ifelse(trimws(x) %in% c("", "#NULL!"), NA, trimws(x))))

recode <- function(v, item) {
  if (item == "VFQ.2") {
    m <- c("0" = 0, "20" = 1, "40" = 2, "60" = 3, "80" = 4, "100" = 5)
  } else {
    m <- c("0" = 0, "25" = 1, "50" = 2, "75" = 3, "100" = 4)
  }
  out <- unname(m[as.character(v)])
  ifelse(is.na(out), v, out)   # unscored skip items keep their raw code
}

## ---- A. live vs deposit, cell for cell --------------------------------------
cat("=== A. live resp frequencies vs deposit column, per item ===\n")
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
okA <- TRUE
cat(sprintf("%-9s %-34s %-34s\n", "item", "live counts (resp:n)", "deposit recoded (resp:n)"))
for (it in CORE) {
  lv <- table(d$resp[d$item == it])
  rv <- table(recode(num(raw[[it]]), it))
  s <- function(t) paste(sprintf("%s:%d", names(t), as.integer(t)), collapse = " ")
  same <- identical(s(lv), s(rv))
  okA <- okA && same
  cat(sprintf("%-9s %-34s %-34s %s\n", it, s(lv), s(rv), if (same) "" else "<< MISMATCH"))
}
cat("A:", if (okA) "all 29 items reconstruct cell for cell -- MATCH\n" else "MISMATCH\n")

## ---- B. subscale arithmetic --------------------------------------------------
cat("\n=== B. deposit subscale scores vs canonical NEI-VFQ item sets ===\n")
COMP <- list(
  VFQ_health     = c("VFQ.1", "VFQ.A1"),
  VFQ_vision     = c("VFQ.2", "VFQ.A2"),
  VFQ_ocularpain = c("VFQ.4", "VFQ.19"),
  VFQ_near       = c("VFQ.5", "VFQ.6", "VFQ.7", "VFQ.A3", "VFQ.A4", "VFQ.A5"),
  VFQ_distance   = c("VFQ.8", "VFQ.9", "VFQ.14", "VFQ.A6", "VFQ.A7", "VFQ.A8"),
  VFQ_social     = c("VFQ.11", "VFQ.13", "VFQ.A9"),
  VFQ_mental     = c("VFQ.3", "VFQ.21", "VFQ.22", "VFQ.25", "VFQ.A12"),
  VFQ_role       = c("VFQ.17", "VFQ.18", "VFQ.A11a", "VFQ.A11b"),
  VFQ_dependency = c("VFQ.20", "VFQ.23", "VFQ.24", "VFQ.A13"),
  VFQ_driving    = c("VFQ.15c", "VFQ.16", "VFQ.16a"),
  VFQ_color      = c("VFQ.12"),
  VFQ_peripheral = c("VFQ.10"))
okB <- TRUE; tot <- 0; totok <- 0
for (sc in names(COMP)) {
  its <- COMP[[sc]]
  M <- sapply(its, function(i) num(raw[[i]]))
  pred <- rowMeans(M, na.rm = TRUE)
  obs  <- num(raw[[sc]])
  keep <- !is.na(obs) & !is.nan(pred)
  # deposit stores subscale scores rounded to 2 dp
  agree <- abs(round(pred[keep], 2) - round(obs[keep], 2)) < 1e-9
  tot <- tot + sum(keep); totok <- totok + sum(agree)
  okB <- okB && all(agree)
  cat(sprintf("  %-15s k=%d  n=%4d  exact=%4d  mismatch=%d\n",
              sc, length(its), sum(keep), sum(agree), sum(!agree)))
}
cat(sprintf("B: %d / %d respondent x subscale cells reproduce exactly -- %s\n",
            totok, tot, if (okB) "MATCH" else "MISMATCH"))

## ---- C. direction ------------------------------------------------------------
cat("\n=== C. scale direction ===\n")
SCORED <- setdiff(CORE, c("VFQ.15", "VFQ.15a", "VFQ.15b"))
W <- sapply(SCORED, function(i) num(raw[[i]]))
R <- cor(W, use = "pairwise.complete.obs")
minr <- min(R[upper.tri(R)], na.rm = TRUE)
cat(sprintf("  C1 min pairwise correlation among the %d scored items: %+0.3f\n", length(SCORED), minr))

i24 <- d$resp[d$item == "VFQ.24"]
p24 <- mean(i24 == max(i24, na.rm = TRUE), na.rm = TRUE)
cat(sprintf("  C2 VFQ.24 ('I need a lot of help from others because of my eyesight'): %.1f%% (%d of %d) sit at resp=%d, the level shipped as 'Definitely False'\n",
            100 * p24, sum(i24 == 4, na.rm = TRUE), sum(!is.na(i24)), 4L))

m15c <- mean(d$resp[d$item == "VFQ.15c"], na.rm = TRUE)
m16  <- mean(d$resp[d$item == "VFQ.16"],  na.rm = TRUE)
cat(sprintf("  C3 mean resp: VFQ.15c (daytime, familiar places) = %.2f vs VFQ.16 (at night) = %.2f\n", m15c, m16))
okC <- (minr > 0) && (p24 > 0.80) && (m15c > m16)
cat("C:", if (okC) "one common direction, anchored higher = better functioning -- MATCH\n" else "MISMATCH\n")

cat("\nNote: B pins each item to its published subscale and uniquely identifies VFQ.1,\n",
    "VFQ.2, VFQ.10 and VFQ.12; it does NOT separate items within a subscale.\n", sep = "")
cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
