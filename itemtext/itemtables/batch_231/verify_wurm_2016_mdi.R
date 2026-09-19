# verify_wurm_2016_mdi.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: item code mdiN_neu carries the Nth item of the Major
# Depression Inventory (1 Sadness ... 10 Changed Appetite). The item codes are
# the source .sav's own column names (data/wurm_2016_burnout_battery.py melts
# them by name), but the .sav carries NO variable labels for the mdi block, so
# the code->wording tie rests on the canonical MDI numbering. That is what this
# script falsifies.
#
# EVIDENCE: the paper's S1 Table publishes per-item means (SD) under the ten
# SYMPTOM NAMES for four groups (unaffected / mild BO / moderate BO / severe BO
# / MD). Reconstructing those groups from the deposited .sav and computing the
# mean of each mdiN_neu column gives a falsifiable prediction: if any two item
# texts were swapped, that item's four-group profile would land on the wrong
# published row.
#
# Part 2 closes the chain to the live table: live per-item means must equal the
# .sav column means, which is what makes the .sav-based evidence evidence about
# the LIVE item codes.

suppressMessages(library(irw))
suppressMessages(library(haven))

TABLE <- "wurm_2016_mdi"
IT    <- paste0("mdi", 1:10, "_neu")
NAMES <- c("Sadness","Lack of Interest","Lack of Energy","Lack of Selfconfidence",
           "Bad Conscience","Taedium Vitae","Concentration Deficits",
           "Changed Activity","Sleep Disturbances","Changed Appetite")

# Published means, Wurm et al. 2016 PLOS ONE 11(3):e0149913, S1 Table.
PUB <- cbind(
  UA   = c(0.76,0.65,1.04,0.66,0.61,0.20,0.63,0.98,0.77,0.77),
  mild = c(1.45,1.31,2.08,1.42,1.25,0.66,1.23,1.89,1.46,1.43),
  sev  = c(2.17,2.02,3.04,2.55,2.21,1.75,2.31,2.91,2.36,2.45),
  MD   = c(4.13,4.32,4.09,4.04,3.91,4.07,3.83,4.39,3.76,4.51))
rownames(PUB) <- IT

SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?type=supplementary&id=10.1371/journal.pone.0149913.s001")
cache <- file.path("../../.cache", TABLE, "s001.sav")   # from itemtables/batch_231/
if (!file.exists(cache)) cache <- file.path("itemtext/.cache", TABLE, "s001.sav")
if (!file.exists(cache)) {
  cache <- tempfile(fileext = ".sav")
  download.file(SAV_URL, cache, quiet = TRUE, mode = "wb")
}
s <- haven::read_sav(cache)

grp <- list(
  UA   = s[s$Erkrankung == 0, ],                        # unaffected
  mild = s[s$BO_Phase == 1 & s$MD_DSM == 0, ],          # mild burnout, no MD
  sev  = s[s$BO_Phase == 3 & s$MD_DSM == 0, ],          # severe burnout, no MD
  MD   = s[s$Erkrankung == 1, ])                        # major depression, no BO

OBS <- sapply(grp, function(g) sapply(IT, function(i) mean(as.numeric(g[[i]]), na.rm = TRUE)))

cat("=== Part 1: per-item group means, .sav columns vs paper S1 Table ===\n")
cat(sprintf("%-11s %-24s %13s %13s %13s %13s\n", "item", "published symptom",
            "UA", "mildBO", "sevBO", "MD"))
for (k in seq_along(IT))
  cat(sprintf("%-11s %-24s %6.2f/%-6.2f %6.2f/%-6.2f %6.2f/%-6.2f %6.2f/%-6.2f\n",
              IT[k], NAMES[k],
              OBS[k,1], PUB[k,1], OBS[k,2], PUB[k,2],
              OBS[k,3], PUB[k,3], OBS[k,4], PUB[k,4]))

dev3  <- max(abs(OBS[, 1:3] - PUB[, 1:3]))
devMD <- abs(OBS[, 4] - PUB[, 4])
cat(sprintf("\nmax |obs-pub| over UA/mild/severe (30 cells): %.4f  (tolerance 0.01)\n", dev3))
cat(sprintf("MD column: max deviation %.4f at %s -- the paper does not state its MD-group\n",
            max(devMD), IT[which.max(devMD)]))
cat("filter exactly, so this column is reported, not gated.\n")

# Uniqueness: does the 4-group profile separate EVERY item from EVERY other?
dmat <- as.matrix(dist(PUB))
diag(dmat) <- Inf
cat(sprintf("closest pair of published profiles: %s vs %s, L2 distance %.3f\n",
            IT[which(dmat == min(dmat), arr.ind = TRUE)[1,1]],
            IT[which(dmat == min(dmat), arr.ind = TRUE)[1,2]], min(dmat)))

cat("\n=== Part 2: live IRW table vs .sav columns (closes code identity) ===\n")
d <- irw::irw_fetch(TABLE)
live <- tapply(d$resp, d$item, mean)[IT]
savm <- sapply(IT, function(i) mean(as.numeric(s[[i]]), na.rm = TRUE))
for (k in seq_along(IT))
  cat(sprintf("%-11s live %.6f   sav %.6f   diff %.2e\n", IT[k], live[k], savm[k],
              live[k] - savm[k]))
dev2 <- max(abs(live - savm))
cat(sprintf("max |live-sav|: %.3e (tolerance 1e-5)\n", dev2))

cat("\nWhat this does NOT establish: the WORDING shipped is the canonical English MDI,\n",
    "while the study administered a German version that is in neither the deposit nor\n",
    "the paper's supplements; and items 8 and 10 are each scored as the higher of two\n",
    "sub-items, so their item_text carries both alternatives.\n", sep = "")

cat(if (dev3 <= 0.01 && dev2 <= 1e-5) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
