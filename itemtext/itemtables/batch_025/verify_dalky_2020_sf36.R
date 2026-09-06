# verify_dalky_2020_sf36.R
#
# mapping_basis is data_labels: every one of the 35 columns of the source
# .sav carries an SPSS variable label naming its item and a value-label set
# naming its options, and data/dalky_2020_sf36.py melts those columns BY NAME,
# so the IRW item code IS the source column name. item <-> item_text therefore
# needs no statistical route and this script does not attempt one.
#
# What it DOES check is the one inference the extraction made: which of the two
# identically-labelled yes/no blocks is role-PHYSICAL and which is role-EMOTIONAL.
# L8_1/L9_1 and L8_2/L9_2 carry byte-identical variable labels ("Minimizing the
# time you spend doing the work or any other activity"), so only the block stem
# shipped in section_prompt distinguishes them, and that stem was taken from the
# canonical RAND-36 rather than from the file. The falsifiable prediction: the
# L8 block should track physical functioning more closely than the L9 block does,
# and the L9 block should track mental health more closely than the L8 block does.
#
# Runs off the source .sav (Europe PMC, 190KB) -- no Redivis export.

suppressMessages(library(haven))

URL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7519719/supplementaryFiles"
MEMBER <- "peerj-08-9990-s001.sav"

zp <- tempfile(fileext = ".zip")
download.file(URL, zp, quiet = TRUE, mode = "wb")
td <- tempfile(); dir.create(td)
unzip(zp, files = MEMBER, exdir = td)
d <- haven::read_sav(file.path(td, MEMBER))

num <- function(cols) sapply(d[cols], function(x) as.numeric(x))

PF <- c("physical1", "physcial2", paste0("physical", 3:9))
MH <- c("L13_2_L13", "L13_3_L13", "L13_4_L13", "L13_6_L13", "L13_8_L13")
L8 <- paste0("L8_", 1:4, "_L8")
L9 <- paste0("L9_", 1:3, "_L9")

pf <- rowMeans(num(PF), na.rm = TRUE)
mh <- rowMeans(num(MH), na.rm = TRUE)
b8 <- rowMeans(num(L8), na.rm = TRUE)
b9 <- rowMeans(num(L9), na.rm = TRUE)

r <- function(a, b) cor(a, b, use = "complete.obs")
r8pf <- r(b8, pf); r8mh <- r(b8, mh); r9pf <- r(b9, pf); r9mh <- r(b9, mh)

cat(sprintf("n = %d\n\n", nrow(d)))
cat(sprintf("%-22s %10s %10s\n", "block (n items)", "r with PF", "r with MH"))
cat(sprintf("%-22s %10.3f %10.3f\n", sprintf("L8 (%d) -> physical", length(L8)), r8pf, r8mh))
cat(sprintf("%-22s %10.3f %10.3f\n", sprintf("L9 (%d) -> emotional", length(L9)), r9pf, r9mh))

ok_pf <- r8pf > r9pf   # L8 is the more physical block
ok_mh <- r9mh > r8mh   # L9 is the more emotional block
cat(sprintf("\nL8 more physical than L9 (%.3f > %.3f): %s\n", r8pf, r9pf, ok_pf))
cat(sprintf("L9 more emotional than L8 (%.3f > %.3f): %s\n", r9mh, r8mh, ok_mh))
cat(sprintf("item counts 4/3 as SF-36 specifies for RP/RE: %s\n",
            length(L8) == 4 && length(L9) == 3))

cat("Note: this establishes the BLOCK-LEVEL section_prompt assignment only. It does\n",
    "not distinguish items within either block -- the .sav's variable labels do that,\n",
    "which is why mapping_basis is data_labels and this check is supporting, not primary.\n", sep = "")

cat(if (ok_pf && ok_mh) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
