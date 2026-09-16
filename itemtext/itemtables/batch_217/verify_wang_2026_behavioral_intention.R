# verify_wang_2026_behavioral_intention.R -- Step 5b, mapping_basis = paper_explicit
#
# THE CLAIM. The five shipped sentences are tied to the codes BI1..BI5 by the
# study's own S1 Appendix (Questionnaire), which prints each item with its code
# as a literal prefix ("BI1-I will continue to learn about DG technological
# knowledge."). The chain that has to hold is:
#
#   S1 Appendix code prefix  ->  S2 Appendix (data) column header  ->  live item
#
# Link 1 is a string match and is checked here against the freshly fetched .docx.
# Link 2 is checked numerically: the per-item response-level counts in the live
# IRW table must reproduce the counts of the identically-named deposit column,
# and the five count vectors are pairwise distinct, so this pins each live code
# to one deposit column and no other. A swap of any two items' text would break
# link 1; a shifted/permuted column assignment in the processing script would
# break link 2.
#
# WHAT THIS DOES NOT ESTABLISH: (a) that the deposit's own column labelling is
# right -- if the authors mislabelled BI2 as BI3 in their spreadsheet, both links
# still hold; (b) anything about the Chinese wording respondents actually read.
# The administered instrument was a Chinese translation and the appendix is
# English only, so the shipped text is the 2026-09-01 English fallback.

suppressMessages(library(irw))

TABLE <- "wang_2026_behavioral_intention"
DOCX  <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346229.s001"
XLSX  <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346229.s002"
ITEMS <- paste0("BI", 1:5)

# ---- shipped text (this batch's CSV, or hard-coded fallback if run elsewhere)
csv_path <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                      paste0(TABLE, "__items.csv"))
if (!file.exists(csv_path)) csv_path <- paste0("itemtables/batch_217/", TABLE, "__items.csv")
shipped <- read.csv(csv_path, stringsAsFactors = FALSE)
ship_txt <- tapply(shipped$item_text, shipped$item, function(x) unique(x)[1])[ITEMS]

# ---- link 1: S1 Appendix code-prefixed item wording -------------------------
py <- '
import io, re, sys, urllib.request, docx
u = sys.argv[1]
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
b = urllib.request.urlopen(req, timeout=120).read()
d = docx.Document(io.BytesIO(b))
seen = {}
for t in d.tables:
    for r in t.rows:
        for c in r.cells:
            s = " ".join(c.text.split())
            m = re.match(r"^(BI[1-5])[-–—]\\s*(.+)$", s)
            if m and m.group(1) not in seen:
                seen[m.group(1)] = m.group(2)
for k in sorted(seen):
    print(k + "\\t" + seen[k])
'
tf <- tempfile(fileext = ".py"); writeLines(py, tf)
raw <- system2("python3", c(tf, shQuote(DOCX)), stdout = TRUE)
appendix <- setNames(sub("^[^\t]*\t", "", raw), sub("\t.*$", "", raw))[ITEMS]

cat("=== Link 1: S1 Appendix code prefix -> shipped item_text ===\n")
ok1 <- TRUE
for (it in ITEMS) {
    a <- appendix[[it]]; s <- ship_txt[[it]]
    same <- !is.na(a) && identical(a, s)
    ok1 <- ok1 && same
    cat(sprintf("%-4s %s\n     appendix: %s\n     shipped : %s\n",
                it, if (same) "MATCH" else "DIFFER", a, s))
}
cat(sprintf("link 1: %d/%d item codes matched verbatim\n\n", sum(!is.na(appendix) & appendix == ship_txt), length(ITEMS)))

# ---- link 2: deposit column counts == live item counts ----------------------
py2 <- '
import io, sys, urllib.request, pandas as pd
req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "Mozilla/5.0"})
d = pd.read_excel(io.BytesIO(urllib.request.urlopen(req, timeout=180).read()))
for c in ["BI1","BI2","BI3","BI4","BI5"]:
    v = d[c].value_counts().reindex([1,2,3,4,5]).fillna(0).astype(int).tolist()
    print(c + "\\t" + ",".join(map(str, v)))
'
tf2 <- tempfile(fileext = ".py"); writeLines(py2, tf2)
raw2 <- system2("python3", c(tf2, shQuote(XLSX)), stdout = TRUE)
dep <- setNames(sub("^[^\t]*\t", "", raw2), sub("\t.*$", "", raw2))[ITEMS]

d <- irw::irw_fetch(TABLE)
live <- sapply(ITEMS, function(it) {
    v <- table(factor(as.numeric(d$resp[d$item == it]), levels = 1:5))
    paste(as.integer(v), collapse = ",")
})

cat("=== Link 2: S2 Appendix column -> live item, response-level counts ===\n")
cat(sprintf("%-4s %-22s %-22s %s\n", "item", "deposit column", "live IRW table", ""))
ok2 <- TRUE
for (it in ITEMS) {
    same <- identical(dep[[it]], live[[it]])
    ok2 <- ok2 && same
    cat(sprintf("%-4s %-22s %-22s %s\n", it, dep[[it]], live[[it]], if (same) "MATCH" else "DIFFER"))
}
# the count vectors must also be pairwise distinct, or the match is not a pin
ndist <- length(unique(unlist(live)))
cat(sprintf("distinct live count vectors: %d of %d (a repeat would mean the match\n", ndist, length(ITEMS)))
cat("  cannot separate the items that share it)\n")
# cross-item check: does each live vector match ONLY its own deposit column?
cross <- sum(outer(unlist(live), unlist(dep), "=="))
cat(sprintf("total live-vs-deposit vector equalities across all %d pairs: %d (5 expected,\n",
            length(ITEMS)^2, cross))
cat("  i.e. only the diagonal)\n\n")

cat("Note: this pins code -> wording (link 1) and code -> live column (link 2).\n")
cat("It does NOT establish that the authors' own spreadsheet labelling is correct,\n")
cat("nor anything about the Chinese wording actually administered -- the shipped\n")
cat("English is the recoverability fallback.\n")

cat(if (ok1 && ok2 && ndist == length(ITEMS) && cross == length(ITEMS))
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
