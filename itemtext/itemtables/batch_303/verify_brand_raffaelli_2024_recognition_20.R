# Verification for brand_raffaelli_2024_recognition_20 (#2228, batch_303).
#
# SOURCE. ResearchBox 1892 (CC BY), which ships both memory-task Qualtrics
# files and the auto-generated codebooks for their raw exports. The codebooks
# name every recognition column by serial position, which is the whole content
# of item_text here -- the stimulus itself is condition-dependent and cannot be
# put in a column keyed on `item` alone.
#
# Route 1: the two codebooks' column sets are offset by one and their union is
#   the live item set -- this is why the same code means different positions in
#   the two subsamples, and it is the claim item_text makes.
# Route 2: the Old/New choice labels come from the .qsf, not from guesswork.
# Route 3: the old/new structure is visible in the data -- odd-numbered lists
#   recognise the low half and reject the high half, even lists the reverse --
#   which also fixes resp 1 = Old rather than 1 = New.
# ResearchBox publishes no per-file endpoint, so a cold cache costs the whole
# box (~140 MB) for these three. The zip is not kept; the members are.
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

cbB <- ".cache/batch_303/rbox/Raw_Brand_Memory_Task_Prolific.xlsx___CODEBOOK.csv"
cbL <- ".cache/batch_303/rbox/Raw_Logo_Memory_Task_Prolific.xlsx___CODEBOOK.csv"
qB  <- ".cache/batch_303/rbox/Brand_Memory_Task_Prolific.qsf"
cached_zip_members(
    c(cbB, cbL, qB),
    c("Raw_Brand_Memory_Task_Prolific.xlsx___CODEBOOK.csv",
      "Raw_Logo_Memory_Task_Prolific.xlsx___CODEBOOK.csv",
      "Brand_Memory_Task_Prolific.qsf"),
    "https://s3.wasabisys.com/zipballs.researchbox.org/ResearchBox_1892.zip")

d <- as.data.frame(irw::irw_fetch("brand_raffaelli_2024_recognition_20"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
d$n <- as.integer(sub("_recognition$", "", d$item))
items <- shipped_items("brand_raffaelli_2024_recognition_20", "itemtables/batch_303/brand_raffaelli_2024_recognition_20__items.csv")

nums <- function(p) {
    z <- read.csv(p, header = FALSE, stringsAsFactors = FALSE)
    v <- z[[2]][grepl("_Recognition$", z[[2]])]
    sort(as.integer(sub("_Recognition$", "", v)))
}
nb <- nums(cbB); nl <- nums(cbL)
cat("=== Route 1: the one-position offset between subsamples ===\n")
cat(sprintf("  brand codebook: %d columns, %d..%d\n", length(nb), min(nb), max(nb)))
cat(sprintf("  logo  codebook: %d columns, %d..%d\n", length(nl), min(nl), max(nl)))
liveB <- sort(unique(d$n[d$item_family == "name"]))
liveL <- sort(unique(d$n[d$item_family == "logo"]))
r1 <- identical(nb, liveB) && identical(nl, liveL) &&
      setequal(union(nb, nl), sort(unique(d$n))) && length(unique(d$n)) == 101
cat(sprintf("  live name-family codes match the brand codebook: %s\n", identical(nb, liveB)))
cat(sprintf("  live logo-family codes match the logo  codebook: %s\n", identical(nl, liveL)))
cat(sprintf("  -> union is the 101-item live set: %s\n", r1))

cat("\n=== Route 2: the choice labels ===\n")
q <- readLines(qB, warn = FALSE)
has <- any(grepl('"Old"', q)) && any(grepl('"New"', q))
cat(sprintf("  .qsf declares Choices 1 = Old, 2 = New: %s\n", has))
r2 <- has && setequal(unique(items$option_text[items$resp == 1]), "Old") &&
      setequal(unique(items$option_text[items$resp == 2]), "New")
cat(sprintf("  -> shipped option_text agrees: %s\n", r2))

cat("\n=== Route 3: old/new structure by list, and the direction of resp ===\n")
chk <- function(fam, cut) {
    z <- d[d$item_family == fam, ]
    z$half <- ifelse(z$n <= cut, "low", "high")
    a <- stats::aggregate(resp ~ cov_condition + half, data = z,
                          FUN = function(v) mean(v == 1))
    stats::reshape(a, idvar = "cov_condition", timevar = "half", direction = "wide")
}
for (f in list(c("name", "51"), c("logo", "50"))) {
    t <- chk(f[1], as.integer(f[2]))
    t <- t[order(t$cov_condition), ]
    cat(sprintf("  -- %s (cut at %s) --\n", f[1], f[2]))
    for (i in seq_len(nrow(t)))
        cat(sprintf("     %-8s p(Old) low=%.2f high=%.2f\n",
                    t$cov_condition[i], t$resp.low[i], t$resp.high[i]))
}
tn <- chk("name", 51); tl <- chk("logo", 50)
odd <- function(x) as.integer(sub("List_", "", x)) %% 2 == 1
r3 <- all(tn$resp.low[odd(tn$cov_condition)]  > 0.6) &&
      all(tn$resp.low[!odd(tn$cov_condition)] < 0.4) &&
      all(tl$resp.low[odd(tl$cov_condition)]  > 0.6) &&
      all(tl$resp.low[!odd(tl$cov_condition)] < 0.4)
cat(sprintf("  -> odd lists studied the low half, even lists the high half: %s\n", r3))
cat("  Hit rates near .8 against false-alarm rates near .2 only come out this\n")
cat("  way if resp 1 is 'Old'; the reverse coding would invert every cell.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Which brand or logo sits at a given position for a given respondent.\n")
cat("  That is a three-way key (item x item_family x cov_condition) against the\n")
cat("  .qsf loop tables and cannot be expressed in a table keyed on item alone;\n")
cat("  it is tracked separately as irw#1656. item_text therefore describes the\n")
cat("  position, not the stimulus.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
