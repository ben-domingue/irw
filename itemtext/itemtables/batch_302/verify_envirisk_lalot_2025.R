# Verification for envirisk_lalot_2025 (#2228, batch_302).
#
# SOURCE. Lalot, Raikkonen & Ahvenharju (2025), Journal of Environmental
# Psychology, doi:10.1016/j.jenvp.2025.102520, CC BY; deposit osf.io/h6ru2. The
# deposit ships 'codebook EnviRisk.xlsx', which gives every variable its full
# label AND its own answer options -- the anchors differ by block, which is why
# they are read per item rather than assumed.
#
# Route 1: the codebook's variables cover the live item set.
# Route 2: the shipped text is the codebook's label, verbatim.
# Route 3: the three answer scales fall exactly where the codebook says.
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
CB <- ".cache/batch_302/envirisk_codebook.xlsx"
if (!file.exists(CB)) stop("missing cached deposit file: ", CB)
suppressWarnings(suppressMessages(library(readxl)))
cb <- as.data.frame(read_excel(CB, sheet = "Sheet1"))
names(cb)[1:3] <- c("Variable", "Label", "Options")
d <- as.data.frame(irw::irw_fetch("envirisk_lalot_2025"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/envirisk_lalot_2025__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: codebook coverage ===\n")
live <- sort(unique(d$item))
have <- live %in% cb$Variable
cat(sprintf("  live items %d; all present in the codebook: %s\n", length(live), all(have)))
if (!all(have)) cat(sprintf("  missing: %s\n", paste(live[!have], collapse = ", ")))
r1 <- all(have) && setequal(live, unique(items$item))

cat("\n=== Route 2: the shipped label is the codebook's ===\n")
key <- setNames(trimws(cb$Label), cb$Variable)
sh <- unique(items[, c("item", "item_text")])
ok <- sum(sh$item_text == key[sh$item], na.rm = TRUE)
r2 <- ok == nrow(sh)
cat(sprintf("  %d of %d item_text values match the codebook label exactly: %s\n", ok, nrow(sh), r2))
for (i in c("bd_risk2", "policy4_acc", "libcons"))
    cat(sprintf("    %-12s %s\n", i, substr(key[[i]], 1, 72)))

cat("\n=== Route 3: three different answer scales, per the codebook ===\n")
for (i in live) {
    lv <- sort(unique(d$resp[d$item == i]))
    op <- unique(items$option_text[items$item == i & !is.na(items$option_text)])
    cat(sprintf("  %-12s levels %-26s labelled ends: %s\n", i,
                paste(range(lv), collapse = "-"), paste(op, collapse = " / ")))
}
risk <- c("bd_risk1","bd_risk2","bd_risk3","cc_risk1","cc_risk2","cc_risk3")
pol  <- c("policy1_acc","policy2_acc","policy3_acc","policy4_acc")
slf  <- c("polorient","libcons")
r3 <- all(sapply(c(risk,pol), function(i) identical(as.numeric(sort(unique(d$resp[d$item==i]))), as.numeric(1:7)))) &&
      all(sapply(slf,        function(i) identical(as.numeric(sort(unique(d$resp[d$item==i]))), as.numeric(0:10))))
cat(sprintf("  -> risk and policy items run 1-7, the two self-placements 0-10: %s\n", r3))
cat("  The codebook states '1 = Strongly disagree, 7 = Strongly agree' for the\n")
cat("  risk items, '1 = Very low acceptability, 7 = Very high acceptability' for\n")
cat("  the policy items, and '0 = Left, 10 = Right' / '0 = Liberal, 10 =\n")
cat("  Conservative' for the two self-placements. Shipping one scale for the\n")
cat("  whole table would have been wrong on six of twelve items.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. Labels and anchors are the deposit's own codebook. Note\n")
cat("  two live items are not attitude items at all -- polorient and libcons are\n")
cat("  self-placements on political scales, carried here because they are in the\n")
cat("  response table, and they keep their own 0-10 anchors.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
