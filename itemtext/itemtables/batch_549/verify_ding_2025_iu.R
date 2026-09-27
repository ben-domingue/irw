# verify_ding_2025_iu.R -- Step 5b mapping check for ding_2025_iu (batch_549).
#
# Claim: live IU1..IU12 (assigned POSITIONALLY by data/ding_2025_iu_ocd.py from
# columns 2..13 of the headerless deposit .tsv) are the paper's own IU1..IU12
# (Ding et al. 2025, PeerJ 13:e19791), whose wording is printed in Table 1.
#
# Route: Supplementary Table S1 (peerj-13-19791-s002.docx) prints the 18 x 12
# matrix of correlations between every OCI-R item and every IU item, IU9
# included. Each IU column's 18-vector of correlations is a fingerprint. We
# compute Spearman correlations from the live ding_2025_iu and ding_2025_ocd
# tables (full N = 1551, which is what S1 was computed on) and check that every
# live IU column matches its own published column far better than any other.
# Secondary: Table 1 per-item means (IU9 not printed there).
#
# Caveat this does NOT cover: the OCD columns are themselves positional from
# the same script; a joint shift of both blocks would be caught (the column
# fingerprints would not reproduce), but the check is of the IU axis only.

suppressMessages(library(irw))

P <- matrix(c(
.524,.525,.516,.301,.501,.544,.501,.372,.499,.496,.177,.363,
.463,.442,.470,.402,.425,.452,.472,.402,.424,.416,.307,.423,
.572,.543,.563,.434,.528,.547,.544,.444,.532,.499,.322,.480,
.403,.452,.447,.230,.441,.446,.417,.255,.456,.476,.134,.368,
.463,.473,.503,.259,.449,.466,.457,.266,.465,.476,.166,.394,
.506,.531,.541,.237,.526,.558,.510,.319,.574,.574,.123,.433,
.393,.429,.431,.206,.401,.406,.370,.274,.435,.444,.106,.348,
.304,.315,.339,.234,.304,.324,.332,.264,.336,.323,.192,.348,
.563,.558,.550,.369,.514,.563,.529,.410,.566,.517,.275,.496,
.325,.360,.377,.157,.362,.377,.319,.195,.391,.427,.090,.350,
.343,.362,.374,.197,.370,.374,.361,.239,.388,.419,.140,.376,
.506,.537,.530,.344,.494,.535,.500,.358,.525,.521,.228,.461,
.366,.368,.363,.376,.325,.343,.396,.369,.338,.315,.333,.349,
.316,.312,.343,.309,.328,.327,.358,.334,.329,.329,.272,.320,
.412,.418,.426,.337,.399,.417,.430,.337,.431,.432,.280,.427,
.368,.384,.383,.190,.394,.415,.379,.273,.391,.421,.134,.358,
.330,.352,.363,.164,.381,.397,.356,.198,.432,.419,.108,.314,
.375,.431,.427,.185,.373,.426,.376,.260,.433,.444,.097,.338),
  nrow = 18, byrow = TRUE)

# Table 1 means, IU9 omitted by the paper (excluded from its network).
T1 <- c(IU1=1.94, IU2=1.79, IU3=1.84, IU4=2.29, IU5=1.82, IU6=1.83, IU7=1.95,
        IU8=2.38, IU10=1.73, IU11=2.42, IU12=1.93)

wide <- function(t) {
  d <- as.data.frame(irw::irw_fetch(t))[, c("id", "item", "resp")]
  w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
  names(w) <- sub("^resp\\.", "", names(w)); w
}
w <- merge(wide("ding_2025_iu"), wide("ding_2025_ocd"), by = "id")
cat("respondents:", nrow(w), "\n")
iv <- paste0("IU", 1:12); ov <- paste0("OCD", 1:18)
L <- cor(w[, ov], w[, iv], method = "spearman", use = "pairwise.complete.obs")

D <- sapply(1:12, function(j) sapply(1:12, function(i) sqrt(mean((L[, i] - P[, j])^2))))
own <- diag(D); other <- sapply(1:12, function(i) min(D[i, -i]))
best <- apply(D, 1, which.min)
cat(sprintf("%-5s %10s %14s %10s %10s\n", "item", "rmse_own", "rmse_next_best", "best_pub", "maxabs_own"))
for (i in 1:12) cat(sprintf("%-5s %10.4f %14.4f %10s %10.4f\n", iv[i], own[i], other[i],
                            iv[best[i]], max(abs(L[, i] - P[, i]))))
cat(sprintf("\nall 216 cells: max |live - published| = %.4f (S1 printed to 3 dp)\n", max(abs(L - P))))

m <- tapply(as.data.frame(irw::irw_fetch("ding_2025_iu"))$resp,
            as.data.frame(irw::irw_fetch("ding_2025_iu"))$item, mean)[names(T1)]
cat("\nTable 1 means vs live:\n")
for (k in names(T1)) cat(sprintf("%-5s %6.2f %8.3f %7.3f\n", k, T1[k], m[k], m[k] - T1[k]))
worst_mean <- max(abs(m - T1)); cat(sprintf("largest mean deviation %.3f\n", worst_mean))

ok <- all(best == 1:12) && max(abs(L - P)) <= 0.0015 && all(other > 10 * own) && worst_mean <= 0.006
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
