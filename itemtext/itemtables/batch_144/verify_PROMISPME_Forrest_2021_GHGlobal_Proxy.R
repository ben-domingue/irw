# verify_PROMISPME_Forrest_2021_GHGlobal_Proxy.R
#
# This table was BLOCKED ON RIGHTS; no __items.csv was written, so there is no
# shipped item->text mapping to verify and no statistical route applies
# (verification status NO_ROUTE). What this script makes re-runnable is the
# evidence the BLOCK rests on:
#
#   (1) IDENTITY -- the live item codes are PROMIS Pediatric Global Health item
#       bank codes, and the deposit's own codebook is titled "PROMIS Pediatric
#       Global Health-7" and prints canonical PROMIS Global Health wording.
#       (If the wording were the investigators' own, HealthMeasures' terms would
#       not be engaged -- cf. evpromisi_stone_2021_cdiag.)
#   (2) CLAUSE -- the HealthMeasures Terms of Use currently served by the rights
#       holder still contain the redistribution bar, byte-identically to the copy
#       the instrument_rights_register.csv verdict was made from
#       (md5 fe672ca0c092d6b324a8098ac049c7e3).
#
# It does NOT establish anything about item-text accuracy (none shipped), and it
# does not re-decide the policy question -- only that the clause exists and that
# this table's content is PROMIS content.

suppressMessages(library(irw))

TABLE  <- "PROMISPME_Forrest_2021_GHGlobal_Proxy"
TOU    <- "https://www.healthmeasures.net/wp-content/uploads/2026/06/Terms-of-Use_HM_approved_1-12-17-Updated-Copyright-Notices.pdf"
TOU_MD5 <- "fe672ca0c092d6b324a8098ac049c7e3"
CB_URL <- "https://dataverse.harvard.edu/api/access/datafile/4271465"  # GlobHeal_Codebook.pdf
DDI    <- "https://dataverse.harvard.edu/api/access/datafile/4271461/metadata/ddi"  # GH_..._PROXY.tab

ok <- TRUE
tmp <- tempdir()

## ---- (1a) live item codes -------------------------------------------------
ts <- irw::irw_table_sets(TABLE, per_item = TRUE)
items <- sort(unique(unlist(lapply(ts, function(x) if (is.data.frame(x)) x$item else NULL))))
if (length(items) == 0) items <- sort(unique(ts$item))
cat("live item codes (", length(items), "):\n", sep = "")
print(items)
n_promis <- sum(grepl("^(Global|PedGlobal)[0-9]+_Proxy", items))
cat(sprintf("codes matching PROMIS Global/PedGlobal bank pattern: %d/%d\n",
            n_promis, length(items)))
ok <- ok && n_promis == length(items) && length(items) == 21

## ---- (1b) the deposit's own codebook names the instrument ------------------
cb <- file.path(tmp, "GlobHeal_Codebook.pdf")
download.file(CB_URL, cb, quiet = TRUE, mode = "wb")
txt <- suppressWarnings(system2("pdftotext", c("-layout", cb, "-"), stdout = TRUE))
title_hits <- sum(grepl("PROMIS Pediatric Global Health-7", txt, fixed = TRUE))
gl01 <- any(grepl("In general, would you say your health is:", txt, fixed = TRUE))
cat(sprintf("\ndeposit codebook GlobHeal_Codebook.pdf: '%s' appears %d time(s); ",
            "PROMIS Pediatric Global Health-7", title_hits))
cat(sprintf("canonical Global01 stem present: %s\n", gl01))
ok <- ok && title_hits > 0 && gl01

## ---- (1c) the proxy data file carries NO variable labels -------------------
ddi <- file.path(tmp, "ddi.xml")
download.file(DDI, ddi, quiet = TRUE)
x <- paste(readLines(ddi, warn = FALSE), collapse = "")
vars <- regmatches(x, gregexpr('name="[^"]+"', x))[[1]]
vars <- unique(sub('name="', "", sub('"$', "", vars)))
gvars <- grep("^(Global|PedGlobal)", vars, value = TRUE)
labl <- regmatches(x, gregexpr("<labl[^>]*>[^<]*</labl>", x))[[1]]
labl <- gsub("<[^>]*>", "", labl)
self <- sum(labl %in% gvars)
cat(sprintf("proxy .tab DDI: %d Global*/PedGlobal* variables; %d of their labels are just the variable name (no item wording in the data file)\n",
            length(gvars), self))

## ---- (2) the clause is still live and unchanged ----------------------------
p <- file.path(tmp, "hm_tou.pdf")
download.file(TOU, p, quiet = TRUE, mode = "wb")
md5 <- unname(tools::md5sum(p))
cat(sprintf("\nHealthMeasures ToU md5: %s (expected %s) -> %s\n",
            md5, TOU_MD5, if (identical(md5, TOU_MD5)) "MATCH" else "CHANGED"))
ptxt <- suppressWarnings(system2("pdftotext", c(p, "-"), stdout = TRUE))
flat <- gsub("[[:space:]]+", " ", paste(ptxt, collapse = " "))
c1 <- lengths(gregexpr("User shall not distribute, publish, sell, license, or provide HealthMeasures products",
                       flat, fixed = TRUE))
c2 <- lengths(gregexpr("Commercial Users must seek permission to use, reproduce, or distribute",
                       flat, fixed = TRUE))
c1 <- if (regexpr("User shall not distribute, publish, sell, license, or provide HealthMeasures products", flat, fixed = TRUE) > 0) c1 else 0
c2 <- if (regexpr("Commercial Users must seek permission to use, reproduce, or distribute", flat, fixed = TRUE) > 0) c2 else 0
cat(sprintf("redistribution bar occurrences: %d; non-commercial clause occurrences: %d\n", c1, c2))
ok <- ok && identical(md5, TOU_MD5) && c1 >= 1 && c2 >= 1

cat("\nWhat this does NOT establish: nothing about item-text fidelity or the\n",
    "item->text mapping, because no item text was shipped; and it does not\n",
    "re-decide the policy -- only that the clause exists and the content is PROMIS.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
