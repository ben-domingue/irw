# verify_PROMISPME_Forrest_2021_LS_Proxy.R
#
# This table is BLOCKED ON RIGHTS: no item text was shipped, so there is no
# item -> wording mapping to verify. What IS verifiable, and what the block
# rests on, are two factual claims. This script re-runs both from source.
#
#   A. IDENTITY. Every live item code of this table is a PROMIS Pediatric Life
#      Satisfaction item-bank item (parent-proxy edition; Forrest CB et al.
#      2018, Qual Life Res 27(1):217-234). The deposit's own codebook
#      (Harvard Dataverse doi:10.7910/DVN/QOO7QX, ProxyLifeSat_Codebook.pdf,
#      datafile id 4271431) is titled "PROMIS Proxy Life Satisfaction" and
#      labels each SWB_LS_nnn_PX code with its administered wording. So the
#      register's ^promis match is a true positive, not a name collision.
#
#   B. CLAUSE. The wording's rights holder (PROMIS Health Organization /
#      Northwestern University, via HealthMeasures) still publishes an
#      explicit, quotable permission-required + no-redistribution bar, in the
#      same PDF the 2026-09-05 ruling was made on (md5 fe672ca0...).
#
# Together they make the block determinate under the PROMIS ruling in
# references/itemtext_standard.md and row "PROMIS / HealthMeasures family" of
# itemtext/instrument_rights_register.csv, notwithstanding the deposit's
# CC0 1.0 licence -- the deposit licence is not the instrument licence.
#
# What this does NOT establish: anything about item-text accuracy, since none
# was shipped; and it does not re-open the POLICY question -- only that these
# items are PROMIS content and that the clause is still published.
#
# VERDICT: PASS means "the block reproduces". It does not mean item text is
# correct; there is none.
#
# Item-set retrieval uses irw::irw_table_sets() (server-side aggregate), NOT
# irw_fetch(), because of the 200GB/30-day account-wide Redivis export cap.

suppressMessages(library(irw))

TABLE   <- "PROMISPME_Forrest_2021_LS_Proxy"
CB_ID   <- 4271431                      # ProxyLifeSat_Codebook.pdf
CB_MD5  <- "84b7f963067b6d84598a0fa9fbe08697"
DV      <- "https://dataverse.harvard.edu/api/access/datafile/"
TOU_URL <- paste0("https://healthmeasures.net/wp-content/uploads/2026/06/",
                  "Terms-of-Use_HM_approved_1-12-17-Updated-Copyright-Notices.pdf")
TOU_MD5 <- "fe672ca0c092d6b324a8098ac049c7e3"
CLAUSES <- c(
  "User shall not reproduce HealthMeasures Instruments except as needed to conduct the authorized single use",
  "User shall not distribute, publish, sell, license, or provide HealthMeasures products, by any means whatsoever"
)

ok <- TRUE
fail <- function(msg) { cat("FAIL: ", msg, "\n", sep = ""); ok <<- FALSE }
tmp <- tempdir()

flatten <- function(path) {
  txt <- system2("pdftotext", c("-layout", shQuote(path), "-"), stdout = TRUE, stderr = FALSE)
  gsub("[[:space:]]+", " ", paste(txt, collapse = " "))
}

## ---- A. IDENTITY ------------------------------------------------------
cat("== A. IDENTITY: codebook variable codes vs live item set ==\n")

cb <- file.path(tmp, "ProxyLifeSat_Codebook.pdf")
utils::download.file(paste0(DV, CB_ID), cb, quiet = TRUE, mode = "wb")
cb_md5 <- as.character(tools::md5sum(cb))
cat("codebook md5 fetched : ", cb_md5, "\n", sep = "")
cat("codebook md5 expected: ", CB_MD5, "\n", sep = "")
if (!identical(cb_md5, CB_MD5))
  cat("NOTE: codebook bytes differ from the recorded copy; codes are re-read below anyway.\n")

flat <- flatten(cb)
cb_codes <- sort(unique(regmatches(flat, gregexpr("SWB_LS_[0-9]{3}_PX", flat))[[1]]))
cat("codebook is titled   : ",
    if (grepl("PROMIS Proxy Life Satisfaction", flat, fixed = TRUE))
      "PROMIS Proxy Life Satisfaction (found)" else "TITLE NOT FOUND", "\n", sep = "")

s <- irw::irw_table_sets(TABLE, source = "core")
live <- sort(unique(as.character(s$items)))

cat(sprintf("codebook codes: %d | live items: %d | shared: %d | codebook-only: %d | live-only: %d\n",
            length(cb_codes), length(live), length(intersect(cb_codes, live)),
            length(setdiff(cb_codes, live)), length(setdiff(live, cb_codes))))
cat("live resp set: ", paste(sort(unique(s$resp)), collapse = ", "), "\n", sep = "")

if (!setequal(cb_codes, live))
  fail("codebook code set and live item set differ -- identity claim does not reproduce")
if (length(live) != 56)
  fail(sprintf("expected 56 live items, got %d", length(live)))
if (!grepl("PROMIS Proxy Life Satisfaction", flat, fixed = TRUE))
  fail("codebook no longer identifies itself as PROMIS Proxy Life Satisfaction")

## ---- B. CLAUSE --------------------------------------------------------
cat("\n== B. CLAUSE: HealthMeasures Terms of Use still published ==\n")
tou <- file.path(tmp, "hm_tou.pdf")
utils::download.file(TOU_URL, tou, quiet = TRUE, mode = "wb")
tou_md5 <- as.character(tools::md5sum(tou))
cat("ToU md5 fetched : ", tou_md5, "\n", sep = "")
cat("ToU md5 expected: ", TOU_MD5, "\n", sep = "")
if (!identical(tou_md5, TOU_MD5))
  cat("NOTE: ToU bytes differ from the 2026-09-05 copy; clause text is re-checked below.\n")

tflat <- flatten(tou)
for (cl in CLAUSES) {
  hit <- grepl(cl, tflat, fixed = TRUE)
  cat(sprintf("clause present [%s]: %s\n", ifelse(hit, "yes", "NO"), substr(cl, 1, 60)))
  if (!hit) fail(paste0("clause no longer found in the Terms of Use: ", substr(cl, 1, 60)))
}

cat("\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
