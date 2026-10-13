##Autonomous-weapons vignette experiment (US, Brazil, Germany, China) from
##Rosendorf, O., Smetana, M., Vranka, M., & Dahlmann, A. (2026). Mind over metal: Public opinion
##on autonomous weapons in the United States, Brazil, Germany, and China.
##International Studies Quarterly, 70(1). https://doi.org/10.1093/isq/sqag001
##(SSRN preprint https://doi.org/10.2139/ssrn.5021966)
##Replication data: Harvard Dataverse doi:10.7910/DVN/DMV0G1, CC0 1.0. File read:
##rsvd_isq_replication_data1.dta; read_me.docx (variable list) and rsvd_isq_replication_code1.do
##read as text, not run.
##Usage: Rscript rosendorf_2026.R <dir holding rsvd_isq_replication_data1.dta> <output dir>
##
##4,053 online-panel respondents (US 1,003, Brazil 1,033, Germany 1,002, China 1,015), ONE
##text vignette each (id = the deposit's id; task = profile = 1, inferred). All four countries are
##one table (cov_country): the authors pool them in every model (country dummies) and the
##instrument is the same translated scenario. The vignette: a military commander choosing
##between a remote-controlled drone and an autonomous drone for a strike, 2 x 2 randomized
##(read_me variables `terrorists`, `unequal`; the four groups of the do-file):
##  attr_target : "soldiers" / "terrorists"  (who the strike targets)
##  attr_risk   : "equal risk for both drones" / "higher risk for the remote-controlled drone"
##                (risk of target misidentification: 5.7% for both, or 5.7% for the autonomous drone
##                and a higher figure for the remote-controlled one)
##The attribute text is the authors' own description of the conditions (read_me.docx, do-file
##group labels), NOT the verbatim vignette, which is not in the deposit. The recall items (`target`,
##`risk`) show the scenario named "a military base of Jengizstan" / "a terrorist base" and, for the
##unequal arm, a remote-controlled figure of 7.1% (most) or 11.5% percent; which was shown to whom
##cannot be recovered. Cells: 1,021 / 1,010 / 997 / 1,025.
##Outcomes (about the same vignette; stored raw):
##  rating = preference_binary, the forced-choice drone preference: 0 = prefer the commander to
##    use a remote-controlled drone, 1 = prefer an autonomous drone (respondents who first chose
##    "neither" were asked again, Q8/Q9). It is a pick between two drone OPTIONS, not between
##    profiles, so it is stored as a 0/1 rating.
##  rating_preference_first = preference_ordinal: 1 remote-controlled drone, 2 autonomous drone,
##    3 prefer neither (first question).
##  rating_ethicality_rc / rating_ethicality_aws: ethicality of using a remote-controlled /
##    autonomous drone, 1 Highly unethical .. 6 Highly ethical (HIGHER = more favourable).
##Covariates: cov_country (ccode: 2 United States, 140 Brazil, 255 Germany, 710 China; do-file
##labels), cov_gender (1 male, 2 female, 98 other, 99 prefer not to answer = NA; read_me),
##cov_age (years, 18-64), cov_age_group (age_cat band text; read_me), cov_education (edu text
##from read_me/do-file: elementary school / high school / university or college (any degree);
##99 = NA), cov_conservative (1 very liberal .. 7 very conservative; NA = prefer not to answer),
##cov_robots_attitude (1 very positive .. 5 very negative, per read_me; the do-file labels run
##the other way: kept as codes), cov_region (region of the country, text),
##cov_attention_pass (ac_pass: correctly recalled the target) and cov_attention_pass_2
##(mc_pass: correctly recalled the risk) -- these are the authors' recall checks of the
##manipulation, not separate attention items --, cov_survey_weight (w).
##Dropped: the authors' derived dummies (female, college, terrorists, unequal, group, *_binary,
##preference_binary_percent), target/risk and *_value (recall answers), free text (open_rc,
##open_aws) and its GPT-4o codes. No personal identifiers in the file.
##N: 4,053 respondents; the paper was not available in full to compare.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "rsvd_isq_replication_data1.dta"))
stopifnot(nrow(k) == 4053, uniqueN(k$id) == 4053)
n <- function(v) as.integer(zap_labels(k[[v]]))
d <- data.table(id = n("id"), task = 1L, profile = 1L, rating = n("preference_binary"),
  rating_preference_first = n("preference_ordinal"), rating_ethicality_rc = n("ethicality_rc"), rating_ethicality_aws = n("ethicality_aws"),
  attr_target = c("soldiers", "terrorists")[n("terrorists") + 1L],
  attr_risk = c("equal risk for both drones", "higher risk for the remote-controlled drone")[n("unequal") + 1L])
d[, cov_country := c("2" = "United States", "140" = "Brazil", "255" = "Germany", "710" = "China")[as.character(n("ccode"))]]
d[, cov_gender := c("1" = "male", "2" = "female")[as.character(n("gender"))]]
d[, cov_age := n("age")]
d[, cov_age_group := c("18-24", "25-34", "35-44", "45-54", "55-64")[n("age_cat")]]
d[, cov_education := c("1" = "elementary school", "2" = "high school", "3" = "university or college (any degree)")[as.character(n("edu"))]]
d[, cov_conservative := n("conservative")]
d[, cov_robots_attitude := n("robots_attitude")]
d[, cov_region := as.character(zap_labels(k$region))]
d[, cov_attention_pass := n("ac_pass")]
d[, cov_attention_pass_2 := n("mc_pass")]
d[, cov_survey_weight := as.numeric(k$w)]
for (cc in c("cov_gender", "cov_education")) d[, (cc) := unname(get(cc))]
stopifnot(!anyNA(d[, .(rating, attr_target, attr_risk, cov_country)]), d[, .N, .(attr_target, attr_risk)][, .N] == 4)
cat("share autonomous (unweighted) by arm:\n"); print(d[, .(.N, mean(rating)), .(attr_target, attr_risk)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rosendorf_2026_autonomous_weapons.csv"))
