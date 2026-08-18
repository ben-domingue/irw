# verify_ftna_kasper_2022.R
#
# Claim under test (two parts):
#
#  (A) item -> subject/exam.  data/ftna_kasper_2022.r builds `item` by stripping the
#      exam suffix from the deposited Stata column names of
#      Harvard Dataverse doi:10.7910/DVN/UMNYYR, file `data_ftna_publication.dta`
#      (`math_ftna_num` -> `math_num`).  The codes are therefore self-describing, but
#      the exam each subject belongs to is a falsifiable prediction: the study's own
#      do-files name the PSLE subject set explicitly as
#        {kiswahili, english, math, society, science}   (edcc_code/taba7_taba8.do,
#        "foreach i in kiswahili english math society science")
#      and the FTNA set as the nine O-level Form-2 subjects.  The processing script
#      assigns wave 0 = PSLE, wave 1 = FTNA.  So science_num and society_num must
#      appear ONLY at wave 0; biology/chemistry/civics/geography/history/physics ONLY
#      at wave 1; english/kiswahili/math at both.  Any other pattern falsifies it.
#
#  (B) resp -> grade letter.  The same do-file recodes each subject's `_num` value to
#      NECTA PSLE points:
#        0 -> 5, 1 -> 15.5, 2 -> 25.5, 3 -> 35.5, 4 -> 45.5
#      and then bands the average into letters E(<=10) D(<=20) C(<=30) B(<=40) A(>40),
#      i.e. 0=E, 1=D, 2=C, 3=B, 4=A -- higher resp = better grade.  The independent
#      data-side prediction is the paper's headline result (Brandt 2022,
#      doi:10.1086/718893): private-school students out-perform public-school students
#      on the FTNA.  If the scale ran the other way the private gap would be negative.
#      Semantic coherence is a second check: Mathematics is the worst-performed FTNA
#      subject in Tanzania and Kiswahili (the primary-school medium of instruction) the
#      best, so math_num must have the LOWEST mean and kiswahili_num the highest.
#
# Transport note: this table is 8.86M rows and irw::irw_fetch() exports the whole
# thing, which trips Redivis' 200GB/30-day egress cap in a busy session.  The checks
# below are aggregate queries against the identical live table, so they run regardless.

suppressMessages(library(redivis))

TBL <- "`datapages.item_response_warehouse.ftna_kasper_2022`"
q <- function(sql) as.data.frame(redivis::query(sql)$to_data_frame())

ok <- TRUE

## ---- (A) item x wave availability ------------------------------------------
a <- q(sprintf("select item, wave, count(*) n from %s group by item, wave
                order by wave, item", TBL))
cat("=== (A) item availability by wave (0 = PSLE, 1 = FTNA) ===\n")
print(a)

psle  <- sort(a$item[a$wave == 0])
ftna  <- sort(a$item[a$wave == 1])
EXP_PSLE <- sort(c("kiswahili_num","english_num","math_num","society_num","science_num"))
EXP_FTNA <- sort(c("biology_num","chemistry_num","civics_num","english_num",
                   "geography_num","history_num","kiswahili_num","math_num","physics_num"))

cat("\nPSLE (wave 0) expected:", paste(EXP_PSLE, collapse=", "), "\n")
cat("PSLE (wave 0) observed:", paste(psle,     collapse=", "), "\n")
cat("FTNA (wave 1) expected:", paste(EXP_FTNA, collapse=", "), "\n")
cat("FTNA (wave 1) observed:", paste(ftna,     collapse=", "), "\n")
if (!identical(psle, EXP_PSLE) || !identical(ftna, EXP_FTNA)) ok <- FALSE

## ---- (B1) private-public gap on the FTNA -----------------------------------
b <- q(sprintf("select wave, cov_private, avg(resp) mean_resp, stddev(resp) sd_resp,
                count(*) n from %s group by wave, cov_private
                order by wave, cov_private", TBL))
cat("\n=== (B1) mean resp by wave x cov_private ===\n")
print(b)
gap1 <- b$mean_resp[b$wave==1 & b$cov_private==1] - b$mean_resp[b$wave==1 & b$cov_private==0]
gap0 <- b$mean_resp[b$wave==0 & b$cov_private==1] - b$mean_resp[b$wave==0 & b$cov_private==0]
cat(sprintf("\nprivate - public, FTNA (wave 1): %+.3f grade points\n", gap1))
cat(sprintf("private - public, PSLE (wave 0): %+.3f grade points\n", gap0))
cat("Brandt (2022) reports a POSITIVE private premium; a negative gap here would mean\n",
    "resp 4 is the failing grade, not A.\n", sep="")
if (!(gap1 > 0 && gap0 > 0)) ok <- FALSE

## ---- (B2) semantic ordering of FTNA subject means ---------------------------
m <- q(sprintf("select item, avg(resp) mean_resp from %s where wave = 1
                group by item order by mean_resp", TBL))
cat("\n=== (B2) FTNA subject means, ascending ===\n")
print(m)
worst <- m$item[1]; best <- m$item[nrow(m)]
cat(sprintf("\nlowest mean: %s (%.3f)   highest mean: %s (%.3f)\n",
            worst, m$mean_resp[1], best, m$mean_resp[nrow(m)]))
cat("Expected under 0=E..4=A: Mathematics lowest, Kiswahili highest.\n")
if (!(worst == "math_num" && best == "kiswahili_num")) ok <- FALSE

## ---- what this does NOT establish -------------------------------------------
cat("\nNote: (A) separates the two PSLE-only subjects and the six FTNA-only subjects\n",
    "as blocks and pins the three core subjects that span both exams, but it does not\n",
    "distinguish e.g. biology_num from chemistry_num by content -- nothing statistical\n",
    "does. That tie is a source-column-name identity, not an inference: the IRW code IS\n",
    "the deposited Stata variable name minus its exam suffix.\n", sep="")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
