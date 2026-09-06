# Step 5b verification for geacaballero_2019_pes_nwi_short.
#
# THE CLAIM. Each live item code (e.g. Xgoodcoordinator) carries the wording of a
# specific numbered item of the 31-item Spanish PES-NWI printed in the article's
# Appendix 1, and resp=1 is "Yes, it is essential" while resp=0 is "No".
#
# The chain being tested:
#   live item code  ==  .sav column name          (identity; data/geacaballero_2019_pes_nwi.py melts the X* columns)
#   .sav column     ->  "item N"                  (the .sav's own variable labels)
#   N               ->  Spanish wording           (Appendix 1, peerj-07-7369-s001.docx)
#
# WHAT WOULD BREAK IT. Figure 1 of the paper publishes the % of nurses who selected
# each element, keyed by item number in the original scale. If any two items' texts
# were swapped, the live per-item selection % would land on the wrong number.
# Route 9 (per-item YES/NO cell counts, .sav vs live) fixes the resp direction.

suppressMessages({library(irw); library(haven); library(xml2); library(curl)})

TABLE <- "geacaballero_2019_pes_nwi_short"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- paste0("itemtables/batch_036/", TABLE, "__items.csv")

# --- Figure 1, peerj-07-7369-g001.jpg: "% of choices of each item, by professionals",
#     y axis "Item number in original scale (PES-NWI)". Read off the printed data labels.
FIG1 <- c(`20`=60.5, `14`=58.9, `31`=56.3, `11`=51.7, `2`=50.6, `26`=47.1, `15`=46.0,
          `18`=44.5, `19`=44.5, `25`=41.1, `1`=34.2, `6`=33.8, `4`=32.3, `3`=31.9,
          `29`=31.9, `10`=29.7, `16`=28.1, `7`=26.2, `28`=25.5, `21`=23.6, `13`=22.4,
          `24`=22.4, `8`=22.1, `30`=20.5, `22`=20.2, `5`=18.3, `12`=16.3, `23`=15.6,
          `17`=14.1, `27`=12.2, `9`=12.2)
TOL <- 0.06   # figure labels are printed to 0.1pp; live pct computed from n=263

# ---------------------------------------------------------------- source files
# Europe PMC's supplementaryFiles endpoint is the only unblocked route to these two
# files (peerj.com and its CDN both 403), and it intermittently answers 404/503/504.
# Retry with backoff; SUPPL_ZIP can point at an already-downloaded copy.
zipf <- Sys.getenv("SUPPL_ZIP", "")
if (!nzchar(zipf) || !file.exists(zipf)) {
  zipf <- tempfile(fileext = ".zip")
  h <- curl::new_handle(useragent = "IRW-Finder/1.0 (ben.domingue@gmail.com)")
  ok <- FALSE
  for (i in 1:10) {
    try(curl::curl_download(
          "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6660900/supplementaryFiles",
          zipf, handle = h, quiet = TRUE), silent = TRUE)
    if (file.exists(zipf) && file.size(zipf) > 1e5) { ok <- TRUE; break }
    Sys.sleep(15)
  }
  if (!ok) stop("could not fetch the Europe PMC supplementary bundle (endpoint flaky); ",
                "rerun, or set SUPPL_ZIP to a downloaded copy of ",
                "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6660900/supplementaryFiles")
}
ex <- tempfile(); dir.create(ex)
unzip(zipf, exdir = ex)

sav <- haven::read_sav(file.path(ex, "peerj-07-7369-s002.sav"))
labs <- vapply(sav, function(x) { a <- attr(x, "label"); if (is.null(a)) NA_character_ else a }, "")
xcols <- grep("^X", names(sav), value = TRUE)
num <- as.integer(sub("^item ", "", labs[xcols]))            # .sav variable labels: "item 1".."item 31"
names(num) <- xcols
stopifnot(!any(is.na(num)), setequal(num, 1:31))

# Appendix 1 wording, by item number, straight out of the .docx table cells.
doc <- xml2::read_xml(unz(file.path(ex, "peerj-07-7369-s001.docx"), "word/document.xml"))
ns <- xml2::xml_ns(doc)
cells <- xml2::xml_find_all(doc, "//w:tbl[1]//w:tr", ns)
appx <- setNames(rep(NA_character_, 31), 1:31)
for (tr in cells) {
  tc <- xml2::xml_find_all(tr, "./w:tc", ns)
  txt <- vapply(tc, function(x) paste(xml2::xml_text(xml2::xml_find_all(x, ".//w:t", ns)), collapse = ""), "")
  # R's xml2 collapses the .docx's merged cells, so locate the row's item number
  # and its wording by shape rather than by a fixed column index.
  txt <- trimws(txt)
  nums <- txt[grepl("^[0-9]+$", txt)]
  body <- txt[nchar(txt) > 20]
  # each item row reads: <dimension> <item number> <wording> 1 2 3 4
  if (length(nums) >= 2 && length(body)) {
    n <- as.integer(nums[2]); if (n %in% 1:31) appx[[as.character(n)]] <- body[1]
  }
}
stopifnot(!any(is.na(appx)))

# ------------------------------------------------------- live per-item x resp counts
# Server-side GROUP BY: no table export, no Redivis quota spend.
tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, TRIM(CAST(resp AS STRING)) AS resp,",
                   "COUNT(*) AS n FROM `%s` GROUP BY item, resp"), tbl$qualified_reference)
live <- as.data.frame(irw:::.irw_query_tibble(q))
yes <- setNames(live$n[live$resp == "1"], live$item[live$resp == "1"])
no  <- setNames(live$n[live$resp == "0"], live$item[live$resp == "0"])

items <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE, encoding = "UTF-8")
shipped <- unique(items[, c("item", "item_text")])
rownames(shipped) <- shipped$item

# ------------------------------------------------------------------------ report
cat(sprintf("%-21s %4s %14s %8s %8s %7s   %s\n",
            "item", "N#", "sav YES/NO", "liveYES", "fig1%", "live%", "text tie"))
bad_pct <- bad_cell <- bad_text <- 0
for (cc in names(sort(num))) {
  n  <- num[[cc]]
  sv <- as.character(haven::as_factor(sav[[cc]]))
  sy <- sum(sv == "YES", na.rm = TRUE); sn <- sum(sv == "NO", na.rm = TRUE)
  ly <- yes[[cc]]; ln <- no[[cc]]
  pct <- 100 * ly / (ly + ln)
  cell_ok <- (sy == ly && sn == ln)
  pct_ok  <- abs(pct - FIG1[[as.character(n)]]) <= TOL
  txt_ok  <- identical(trimws(shipped[cc, "item_text"]), trimws(appx[[as.character(n)]]))
  if (!cell_ok) bad_cell <- bad_cell + 1
  if (!pct_ok)  bad_pct  <- bad_pct + 1
  if (!txt_ok)  bad_text <- bad_text + 1
  cat(sprintf("%-21s %4d %7d/%-6d %8d %8.1f %7.1f   %s%s%s\n", cc, n, sy, sn, ly,
              FIG1[[as.character(n)]], pct,
              ifelse(cell_ok, "cell.ok ", "CELL.BAD "),
              ifelse(pct_ok, "pct.ok ", "PCT.BAD "),
              ifelse(txt_ok, "text.ok", "TEXT.BAD")))
}

cat(sprintf("\nroute 9  (.sav YES/NO counts vs live 1/0 counts, 31 items x 2 levels): %d mismatched cells\n",
            bad_cell))
cat(sprintf("route 1  (Figure 1 selection %% vs live %% of resp==1, keyed by .sav 'item N' label): %d mismatches (tol %.2f pp)\n",
            bad_pct, TOL))
cat(sprintf("text tie (shipped item_text vs Appendix 1 row at that item number): %d mismatches\n", bad_text))

ties <- names(which(table(FIG1) > 1))
cat("\nWhat this does NOT establish: four published percentages are tied\n",
    "(", paste(ties, collapse = ", "), " -- items 18/19, 3/29, 13/24, 27/9), so Figure 1 alone\n",
    "cannot separate those four pairs. They are separated by the .sav variable label\n",
    "and by the column mnemonic matching the Appendix wording (Xeducation = 'formacion\n",
    "continuada', Xnursingcompetence = 'competencia clinica', etc.), which the text tie above\n",
    "re-checks mechanically. The remaining 23 items are pinned uniquely by percentage.\n", sep = "")

cat(if (bad_cell + bad_pct + bad_text == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
