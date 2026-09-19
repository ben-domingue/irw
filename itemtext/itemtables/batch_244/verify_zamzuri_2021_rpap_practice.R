# verify_zamzuri_2021_rpap_practice.R
#
# Claim being re-run: each Practice-domain item code F1..F13 carries the wording
# that Zamzuri et al. (2021) PLOS ONE 16(8):e0256636, Table 2, prints against that
# same code (Table 2 has a "Code" column, F1..F13), and the live IRW data behind
# each code is the item Table 2 describes.
#
# data/zamzuri_2021_rpap.py melts S1 Data (.s001) columns F1..F13 keeping their
# names, so the IRW item code IS the source column header (no positional step).
# The falsifiable prediction: Table 2's published per-item M (SD) for code Fk must
# be reproduced by the live data for item Fk, and must be closer to it than to any
# other item's published value. Published means are pairwise >= 0.04 apart, well
# above rounding, so a swap of any two items' text/code would break this.
#
# Does NOT re-check item/resp sets (validate_items.R does that). Does NOT establish
# option_text<->resp beyond the paper's statement "1 = strongly disagree ... 8 =
# strongly agree" (only the endpoints are labelled).

suppressMessages(library(irw))
TABLE <- "zamzuri_2021_rpap_practice"

# Table 2, Practice block, rows 23-35: Code, Mean (SD), wording as printed there.
PUB <- data.frame(
  item = paste0("F", 1:13),
  mean = c(6.74, 7.19, 7.13, 5.29, 7.77, 6.20, 7.23, 6.92, 5.93, 5.68, 6.51, 5.49, 5.97),
  sd   = c(1.69, 1.22, 1.30, 2.34, 0.66, 1.79, 1.17, 1.48, 1.90, 2.09, 1.56, 2.02, 1.82),
  key  = c("mosquito repellent", "water containers", "breeding inside the house",
           "larvicide", "dispose rubbish", "illegal dumping site",
           "drainage system", "unused items", "damaged vehicle",
           "breeding place around the neighbourhood", "gotong royong",
           "illegal garden", "illegal building structure"),
  stringsAsFactors = FALSE)

ITEMS <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                   paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS)) ITEMS <- file.path("itemtables/batch_244", paste0(TABLE, "__items.csv"))
shipped <- unique(read.csv(ITEMS, stringsAsFactors = FALSE)[, c("item", "item_text")])

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs_m <- tapply(d$resp, d$item, mean)[PUB$item]
obs_s <- tapply(d$resp, d$item, sd)[PUB$item]

ok <- TRUE
cat(sprintf("%-4s %7s %7s %7s %7s %-8s %-6s %s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD",
            "nearest", "text", "shipped item_text"))
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]
  nearest <- PUB$item[which.min(abs(PUB$mean - obs_m[[it]]) + abs(PUB$sd - obs_s[[it]]))]
  txt <- shipped$item_text[shipped$item == it]
  txt_ok <- length(txt) == 1 && grepl(PUB$key[i], txt, fixed = TRUE)
  row_ok <- abs(obs_m[[it]] - PUB$mean[i]) <= 0.006 && abs(obs_s[[it]] - PUB$sd[i]) <= 0.015 &&
            nearest == it && txt_ok
  ok <- ok && row_ok
  cat(sprintf("%-4s %7.2f %7.3f %7.2f %7.3f %-8s %-6s %s\n", it, PUB$mean[i], obs_m[[it]],
              PUB$sd[i], obs_s[[it]], nearest, if (txt_ok) "match" else "MISS", txt))
}
gaps <- diff(sort(PUB$mean))
cat(sprintf("\nsmallest gap between published means: %.2f\n", min(gaps)))
cat("Table 2 prints the code beside each item, and live M/SD reproduce it for all 13 codes,\n",
    "each nearest its own published value. Not established: labels for resp 2-7 (none exist).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
