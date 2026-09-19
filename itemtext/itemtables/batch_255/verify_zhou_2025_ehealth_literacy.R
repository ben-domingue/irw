# verify_zhou_2025_ehealth_literacy.R -- Step 5b mapping check (batch_255).
# Copied from references/verify_template.R.
#
# Claim: live item ehK carries the wording of S1 Data column K of the eHealth
# literacy battery, i.e. the header "@32、2-K <wording>".
# data/zhou_2025_ehealth_literacy.py assigns codes POSITIONALLY:
#   rename({c: f"eh{i+1}" for i, c in enumerate(EH_COLS)})
# over an explicit list of the eight full header strings, so the code keeps no
# trace of the header. This script is the header diff SKILL.md asks for, done
# at the id level: for each live ehK it finds which S1 column reproduces it
# respondent-for-respondent, and checks that column's header carries the
# wording shipped for ehK (and the source's own "2-K" sub-number).
# NOT established: that the English header wording is what respondents read
# (administered to Chinese students, presumably in Chinese; no Chinese text is
# in the deposit).

suppressMessages({ library(irw) })
TABLE <- "zhou_2025_ehealth_literacy"
S1_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0330637.s001"
pass <- TRUE

# Shipped item_text, read from the batch CSV beside this script.
here <- tryCatch(dirname(sys.frame(1)$ofile), error = function(e) NULL)
if (is.null(here)) {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grep("^--file=", a)])
  here <- if (length(f)) dirname(f) else "."
}
it <- read.csv(file.path(here, "zhou_2025_ehealth_literacy__items.csv"), stringsAsFactors = FALSE)
shipped <- tapply(it$item_text, it$item, function(x) x[1])

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

tf <- tempfile(fileext = ".xlsx")
download.file(S1_URL, tf, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "Mozilla/5.0"))
s1 <- as.data.frame(readxl::read_excel(tf, sheet = "Data", .name_repair = "minimal"))
s1 <- s1[rowSums(!is.na(s1)) > 0, ]
s1$id <- paste0(s1$Questionnaire, "_", s1$Number)
hdr <- grep("^@32", names(s1), value = TRUE)
cat(sprintf("S1 rows %d, eHealth columns %d; live ids %d\n", nrow(s1), length(hdr), nrow(w)))
if (length(hdr) != 8) pass <- FALSE

m <- merge(w, s1[, c("id", hdr)], by = "id")
cat(sprintf("matched ids %d\n\n", nrow(m)))
if (nrow(m) != nrow(w)) pass <- FALSE

codes <- paste0("eh", 1:8)
cat(sprintf("%-4s %-9s %-7s %-7s %s\n", "item", "agree", "bestoth", "subno", "header wording == shipped item_text"))
for (k in codes) {
  ag <- sapply(hdr, function(h) sum(m[[k]] == m[[h]], na.rm = TRUE))
  j <- which.max(ag); oth <- max(ag[-j])
  h <- hdr[j]
  subno <- sub("^@32、2-([0-9]+) .*$", "\\1", h)
  wording <- sub("^@32、2-[0-9]+ ", "", h)
  same <- identical(wording, unname(shipped[k]))
  cat(sprintf("%-4s %5d/%-5d %-7d 2-%-5s %s  [%s]\n", k, ag[j], nrow(m), oth, subno,
              if (same) "YES" else "NO", wording))
  if (ag[j] != nrow(m) || oth == nrow(m) || !same || subno != sub("eh", "", k)) pass <- FALSE
}
cat("\nNot established: that the English header wording is the administered (Chinese) wording.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
