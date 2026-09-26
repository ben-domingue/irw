# verify_argentina_2013_reproductive_awareness.R -- batch_464, route 9 (response-frequency matching),
# split by questionnaire (cov_sex).
#
# Claim: IRW item its01_NN is INDEC ENSSyR 2013 column MITS01_NN (women's base) / VITS01_NN (men's
# base), i.e. ITS question 1.NN, whose disease is printed in the "Diseño de registro" of
# ENSSyR_doc_utilizacion_bases_usuario.pdf (pp. 38-39 women, 72-73 men) and in both questionnaires
# (Anexo 3, pp. 108 and 118). data/argentina_2013_reproductive.do strips the m/v prefix, sets
# 9 (Ns/Nc) to missing and reverses 1 Sí / 2 No to resp = 3 - x, so resp 2 = Si, resp 1 = No;
# cov_sex 2 = Mujer (women's base), 1 = Varón (men's base).
#
# Prediction: the codebook's unweighted frequencies ("Frecuencia") for 1. Sí and 2. No, per item and
# per questionnaire, equal the live count(item, cov_sex, resp) cell for cell (40 cells), and each
# live item's 4-cell vector matches ONLY its own codebook row, so any permutation of the ten codes
# or a flipped resp direction fails.
#
# Fetches: live counts via a server-side aggregate query (no table export). Codebook counts are
# hard-coded from the PDF (sha256 564919011f52bda193c11a61695ff0289adc746d88bc1be705b2ce08048d9bba).

suppressMessages(library(irw))
TABLE <- "argentina_2013_reproductive_awareness"
items <- sprintf("its01_%02d", 1:10)
dis <- c("Sifilis/chancro","Gonorrea/blenorragia","VIH/Sida","Herpes genital",
         "Condilomas/verrugas","Leucorrea","Clamidia","Tricomoniasis","Candidiasis","Hepatitis B")

# codebook: women Si, women No, men Si, men No
cb <- rbind(
  c(3666, 1414, 3631, 1275),
  c(2334, 2728, 2195, 2691),
  c(5008,   80, 4805,  113),
  c(3072, 2002, 2541, 2353),
  c(2171, 2890, 1370, 3513),
  c( 659, 4384,  475, 4384),
  c( 856, 4188,  497, 4363),
  c( 595, 4445,  371, 4482),
  c( 854, 4189,  402, 4458),
  c(4490,  584, 3994,  899))
dimnames(cb) <- list(items, c("W_si","W_no","M_si","M_no"))

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, CAST(cov_sex AS STRING) AS sex,",
                   "TRIM(CAST(resp AS STRING)) AS resp, COUNT(*) AS n FROM `%s`",
                   "GROUP BY item, sex, resp"), tbl$qualified_reference)
d <- as.data.frame(irw:::.irw_query_tibble(q))
d$sex <- ifelse(d$sex %in% c("2", "Mujer"), "W", ifelse(d$sex %in% c("1", "Varón", "Varon"), "M", d$sex))
get <- function(it, s, r) { v <- d$n[d$item == it & d$sex == s & d$resp == r]; if (length(v)) sum(v) else 0 }
live <- t(sapply(items, function(it) c(get(it,"W","2"), get(it,"W","1"), get(it,"M","2"), get(it,"M","1"))))
dimnames(live) <- dimnames(cb)

cat(sprintf("%-9s %-20s %22s   %22s\n", "item", "disease", "codebook W si/no M si/no", "live W si/no M si/no"))
for (i in seq_along(items))
  cat(sprintf("%-9s %-20s %5d %5d %5d %5d   %5d %5d %5d %5d\n", items[i], dis[i],
              cb[i,1], cb[i,2], cb[i,3], cb[i,4], live[i,1], live[i,2], live[i,3], live[i,4]))

exact <- sum(cb == live)
cat(sprintf("\ncells matching exactly: %d / %d\n", exact, length(cb)))

# uniqueness: each live row matches exactly one codebook row, and it is its own
uniq <- all(sapply(seq_along(items), function(i) {
  hits <- which(apply(cb, 1, function(r) all(r == live[i, ])))
  length(hits) == 1 && hits == i }))
cat("each live item matches only its own codebook row:", uniq, "\n")

# direction: under the reversed coding (resp 2 = No) the counts would not match
flipped <- sum(cb[, c(2,1,4,3)] == live)
cat(sprintf("cells matching if resp direction were flipped: %d / %d\n", flipped, length(cb)))

cat(if (exact == length(cb) && uniq && flipped < length(cb)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
