# verify_roar_gijbels2024.R
#
# THIS TABLE IS BLOCKED ON WORDING RIGHTS AND SHIPPED NO ITEM TEXT.
# There is therefore no item_text<->item mapping in existence to verify, and this
# script does not claim to verify one (verification_roar_gijbels2024.csv records
# status=NO_ROUTE for exactly that reason). What it DOES make re-runnable is the
# two findings the block rests on, both of which are falsifiable:
#
#   (A) THE RIGHTS CLAUSE. The ROAR-PA stimuli are distributed only inside
#       github.com/yeatmanlab/roar-pa-manuscript, whose LICENSE.txt is Stanford's
#       ROAR academic-software licence. Its clauses 2/5/8/11 reserve rights named by
#       the irw#1945 test (non-commercial, no-redistribution, permission-required).
#       Re-fetched and hashed here.
#
#   (B) WHAT THE BLOCK WITHHOLDS. "Task materials/Stimuli.xlsx" keys every stimulus
#       triple to a row label spelled exactly as the live IRW item code. This is the
#       mapping-relevant number: 57/57 live codes present in the source key column.
#       It establishes that an unblocked extraction would be data_labels; it
#       establishes NOTHING about any shipped mapping, because none was shipped.
#
# VERDICT: PASS means "the block reproduces" -- the reserved-right clauses are still
# on the originator's page AND the withheld wording is still keyed 57/57 to the live
# codes. It does NOT mean an item mapping was verified.
#
# Costs no export quota: irw_table_sets() runs server-side aggregates, no irw_fetch().

suppressMessages(library(irw))

TABLE <- "roar_gijbels2024"
LIC_URL  <- "https://raw.githubusercontent.com/yeatmanlab/roar-pa-manuscript/main/LICENSE.txt"
XLSX_URL <- "https://raw.githubusercontent.com/yeatmanlab/roar-pa-manuscript/main/Task%20materials/Stimuli.xlsx"
LIC_SHA  <- "18c777856ff1f7321bdb46d4dd6ef3d9fdf5d5a8fa8205d8125ac61c94dd077f"
XLSX_SHA <- "e94a863cc0574620c79dee0fb14cf10347f7aa5634dc3ac072d36e8d3a8c293c"

# The four clause fragments the block is built on (irw#1945 "reserves a right" test).
CLAUSES <- c(
  "including any accompanying information, materials or manuals",
  "solely for internal academic, non-commercial purposes",
  "without express written permission of STANFORD",
  "Title and copyright to the Software")

tmp <- file.path(tempdir(), c("roarpa_LICENSE.txt", "roarpa_Stimuli.xlsx"))
curl::curl_download(LIC_URL,  tmp[1], quiet = TRUE)
curl::curl_download(XLSX_URL, tmp[2], quiet = TRUE)

lic <- paste(readLines(tmp[1], warn = FALSE), collapse = "\n")
lic_sha  <- digest::digest(file = tmp[1], algo = "sha256")
xlsx_sha <- digest::digest(file = tmp[2], algo = "sha256")

cat("== (A) rights clause ==\n")
cat(sprintf("LICENSE.txt  sha256 recorded %s\n             sha256 fetched  %s  %s\n",
            LIC_SHA, lic_sha, if (identical(lic_sha, LIC_SHA)) "MATCH" else "CHANGED"))
found <- vapply(CLAUSES, function(p) grepl(p, lic, fixed = TRUE), logical(1))
for (i in seq_along(CLAUSES))
  cat(sprintf("  clause fragment %d present: %-5s  \"%s\"\n", i, found[i], CLAUSES[i]))
cat(sprintf("  reserved-right fragments found: %d of %d\n", sum(found), length(CLAUSES)))

cat("\n== (B) what the block withholds ==\n")
cat(sprintf("Stimuli.xlsx sha256 recorded %s\n             sha256 fetched  %s  %s\n",
            XLSX_SHA, xlsx_sha, if (identical(xlsx_sha, XLSX_SHA)) "MATCH" else "CHANGED"))

src <- unlist(lapply(c("FSM", "LSM", "Deletion"), function(sh) {
  d <- suppressMessages(readxl::read_excel(tmp[2], sheet = sh, col_names = FALSE))
  k <- as.character(d[[1]])
  k[!is.na(k) & grepl("^(FSM|LSM|DEL)_[0-9]+$", k)]
}))
s <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
live <- sort(s$items)

cat(sprintf("source stimulus keys in Stimuli.xlsx col A: %d (FSM %d, LSM %d, DEL %d)\n",
            length(src), sum(grepl("^FSM", src)), sum(grepl("^LSM", src)), sum(grepl("^DEL", src))))
cat(sprintf("live IRW item codes:                        %d (FSM %d, LSM %d, DEL %d)\n",
            length(live), sum(grepl("^FSM", live)), sum(grepl("^LSM", live)), sum(grepl("^DEL", live))))
missing <- setdiff(live, src)
cat(sprintf("live codes present verbatim in the source key column: %d of %d\n",
            length(live) - length(missing), length(live)))
if (length(missing)) cat("  NOT FOUND: ", paste(missing, collapse = ", "), "\n", sep = "")
cat(sprintf("source keys dropped from the live table (paper's Rasch item removal): %d\n",
            length(setdiff(src, live))))
cat(sprintf("live resp set: {%s}\n", paste(sort(s$resp), collapse = ",")))

cat("\nWhat this does NOT establish: no item_text was ever assigned to any of these\n",
    "codes, so nothing here verifies a mapping. It shows the wording is recoverable\n",
    "and code-keyed, and that the licence still bars redistributing it.\n", sep = "")

ok <- all(found) && length(missing) == 0L
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
