# verify_kern_2021_life_satisfaction.R
#
# CLAIM UNDER TEST: item_text for SWLS1..SWLS4 is tied to those exact codes by the
# study's own Supplementary Material 1 (Frontiers, CC BY; Gan et al. 2022,
# 10.3389/fpsyg.2022.827517), which prints a two-column table of Labels x Measurement
# items using the very codes the live IRW data uses. The processing script
# (data/kern_2021_positive_edu.py) melts the figshare workbook by column NAME
# (var_name="item"), so item == source column name, and the supplement labels that name.
#
# PRIMARY CHECK (the mapping): re-download the supplement, parse the SWLS rows, and
# require that the text shipped for each code equals the text the supplement prints
# against that same code. This is what would break if SWLS1 and SWLS2 were swapped.
#
# CORROBORATION (numbers): the paper's Table 2 prints PLS outer loadings per SWLS item.
# A one-factor solution on the live data should reproduce their shape.

suppressMessages(library(irw))

TABLE <- "kern_2021_life_satisfaction"
ITEMS <- c("SWLS1", "SWLS2", "SWLS3", "SWLS4")

## ---- 1. shipped text -------------------------------------------------------
csv_path <- file.path(dirname(sub("^--file=", "",
    commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
    paste0(TABLE, "__items.csv"))
ship <- read.csv(csv_path, stringsAsFactors = FALSE)
shipped <- tapply(ship$item_text, ship$item, function(x) unique(x)[1])[ITEMS]

## ---- 2. the source supplement ---------------------------------------------
# Europe PMC ships the article's supplementary files as one zip; Table_2.DOCX is
# "Supplementary Material 1. The measurement scales assessing each of the five constructs".
norm <- function(s) {
    s <- gsub("[‘’“”]", "'", s)
    trimws(gsub("\\s+", " ", s))
}
get_supp_text <- function() {
    cached <- file.path("..", "..", ".cache", TABLE, "supp", "Table_2.DOCX")
    f <- if (file.exists(cached)) cached else {
        tmpzip <- tempfile(fileext = ".zip"); dd <- tempdir()
        ok <- tryCatch({
            download.file("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8931502/supplementaryFiles",
                          tmpzip, quiet = TRUE); TRUE }, error = function(e) FALSE)
        if (!ok) return(NULL)
        unzip(tmpzip, files = "Table_2.DOCX", exdir = dd, overwrite = TRUE)
        file.path(dd, "Table_2.DOCX")
    }
    if (!file.exists(f)) return(NULL)
    xml <- tryCatch(paste(readLines(unz(f, "word/document.xml"), warn = FALSE), collapse = ""),
                    error = function(e) NULL)
    if (is.null(xml)) return(NULL)
    xml <- gsub("</w:p>", " ", xml)           # paragraph break inside a cell
    xml <- gsub("</w:tc>", "\t", xml)         # end of table cell -> tab
    xml <- gsub("</w:tr>", "\n", xml)         # end of table row -> newline
    txt <- gsub("<[^>]+>", "", xml)
    unlist(strsplit(txt, "\n"))
}

lines <- get_supp_text()
ok_labels <- FALSE
if (is.null(lines)) {
    cat("!! could not retrieve Supplementary Material 1 -- primary check could not run\n")
} else {
    cat(sprintf("%-7s %-58s %-58s %s\n", "code", "supplement text", "shipped text", "match"))
    hits <- logical(length(ITEMS))
    for (k in seq_along(ITEMS)) {
        code <- ITEMS[k]
        # the row begins with the label, then a tab, then the item wording
        row <- lines[grepl(paste0("^\\s*", code, "\\s*\t"), lines)]
        supp <- if (length(row)) norm(sub("\t.*$", "", sub(paste0("^\\s*", code, "\\s*\t"), "", row[1]))) else "<not found>"
        got  <- norm(shipped[[code]])
        hits[k] <- identical(supp, got)
        cat(sprintf("%-7s %-58s %-58s %s\n", code, substr(supp, 1, 58), substr(got, 1, 58),
                    if (hits[k]) "OK" else "MISMATCH"))
    }
    ok_labels <- all(hits)
    cat(sprintf("label-to-text match: %d/%d\n", sum(hits), length(ITEMS)))
}

## ---- 3. corroboration: published outer loadings ----------------------------
# Gan et al. (2022) Table 2, "Life satisfaction" block.
PUB <- c(SWLS1 = 0.860, SWLS2 = 0.831, SWLS3 = 0.884, SWLS4 = 0.763)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
m <- as.matrix(w[, ITEMS])
fa <- factanal(na.omit(m), factors = 1)
obs <- round(fa$loadings[, 1], 3)[ITEMS]

cat("\npublished vs live one-factor loadings\n")
cat(sprintf("%-7s %10s %10s\n", "item", "paper", "live"))
for (i in ITEMS) cat(sprintf("%-7s %10.3f %10.3f\n", i, PUB[[i]], obs[[i]]))
extremes_ok <- names(which.max(obs)) == "SWLS3" && names(which.min(obs)) == "SWLS4"
cat(sprintf("highest loading: paper %s / live %s ; lowest: paper %s / live %s\n",
            names(which.max(PUB)), names(which.max(obs)),
            names(which.min(PUB)), names(which.min(obs))))

cat("\nNote: the loading comparison alone does NOT separate SWLS1 from SWLS2 -- the paper\n",
    "puts them at 0.860/0.831 and the live data at ", sprintf("%.3f/%.3f", obs[["SWLS1"]], obs[["SWLS2"]]),
    ", i.e. reversed within a\n0.03 gap. It pins only the extremes (SWLS3 highest, SWLS4 lowest).\n",
    "All four items are separated by the label match in section 2, not by this.\n", sep = "")

cat(if (ok_labels && extremes_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
