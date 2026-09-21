# verify_dou2025_ans.R -- Step 5b evidence, re-runnable.
#
# THE CLAIM UNDER TEST. data/dou2025_aesthetics.py assigns the IRW item codes
# POSITIONALLY: `ans_{i+1}` over raw.columns[8:26] of the deposit's S1 Table
# (figshare 30033097, file 57597382, Sheet1). The shipped item_text for ans_k is
# the Chinese question header sitting at raw column 8+k-1. A shifted or permuted
# slice is invisible to validate_items.R, so it is checked here against numbers.
#
# THE FALSIFIABLE PREDICTION. The same workbook's Sheet2 carries the study's own
# SPSS "descriptive statistics" block for the ANS -- 18 rows labelled
# Asa1..Asa6, As1..As7, Asb1..Asb5, with N / min / max / mean / SD. If the
# positional slice is right, the live IRW per-item mean and SD for ans_k must
# equal Sheet2 row k, for every k, in order. If the slice were shifted by one,
# or the block order were not (Asa, As, Asb) = (everyday, art, nature), the
# numbers would not line up.
#
# WHAT THIS ESTABLISHES AND WHAT IT DOES NOT. The 18 published means are
# pairwise distinct (smallest gap 0.0053, between Asa2 and Asb1) and are matched
# to 4 dp, so each live item is pinned to exactly one Sheet2 row and to exactly
# one raw column -- every item is distinguished from every other. What it does
# NOT establish is the anchor wording: the administered 6-point Chinese response
# labels are published nowhere, so option_text ships blank and no resp-axis
# claim is made here. The English item_text_translated is IRW's own rendering of
# the Chinese and is likewise not tested by this script.

suppressMessages(library(irw))

TABLE <- "dou2025_ans"

# Sheet2 of the deposit's S1 Table (SPSS 描述统计 block for the ANS), rows in
# file order. Hard-coded: they come from a published file and will not change.
LABEL <- c("Asa1","Asa2","Asa3","Asa4","Asa5","Asa6",
           "As1","As2","As3","As4","As5","As6","As7",
           "Asb1","Asb2","Asb3","Asb4","Asb5")
PUB_N    <- rep(748, 18)
PUB_MEAN <- c(4.8890, 5.0535, 4.9519, 4.2487, 4.3382, 4.8436,
              4.7219, 4.8556, 5.0334, 4.8489, 4.7981, 4.5307, 4.6484,
              5.0588, 5.2045, 4.9759, 5.1270, 4.9666)
PUB_SD   <- c(1.13233, 0.97070, 0.98603, 1.23088, 1.18300, 1.03532,
              1.00744, 1.00893, 0.97091, 0.99256, 1.00369, 1.06690, 1.03779,
              0.93383, 0.98292, 1.02418, 0.94489, 0.93580)

# First 12 characters of the Chinese header at raw column 8+k-1, i.e. the text
# shipped as item_text for ans_k (leading survey numbering "7、".."24、"
# stripped). Recorded so the positional diff is readable without the workbook.
HEADER <- c("喜欢用美丽的事物包围自己",
            "我会努力使周围的环境保持和谐有序",
            "我十分注重房屋装饰的细节",
            "我十分注意别人穿衣打扮的细节",
            "我十分注重食物的外观呈现及摆盘",
            "我更喜欢有吸引力的生活用品",
            "我积极寻找体验艺术的机会",
            "我享受于欣赏艺术作品",
            "我认为欣赏艺术品或听音乐是十分必要的",
            "我喜欢寻找感兴趣的艺术作品的信息",
            "我对身边环境中的艺术活动感兴趣",
            "我感觉到接触艺术的需求十分强烈",
            "我喜欢参与艺术活动",
            "我经常在大自然中寻找美",
            "在旅行中，我会选择在自然风景优美的地方停留",
            "在寻找住所中，我会考虑窗外是否有美丽的风景",
            "我能够从观察和谐美丽的自然环境中获得乐趣",
            "我会关注公共空间的美感度")

TOL_MEAN <- 0.0005   # Sheet2 prints 4 dp
TOL_SD   <- 0.00001  # Sheet2 prints 5 dp (half-ulp 5e-6)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
codes <- paste0("ans_", 1:18)
obs_n    <- sapply(codes, function(k) sum(d$item == k & !is.na(d$resp)))
obs_mean <- sapply(codes, function(k) mean(d$resp[d$item == k], na.rm = TRUE))
obs_sd   <- sapply(codes, function(k) sd(d$resp[d$item == k], na.rm = TRUE))

cat(sprintf("%-7s %-6s %5s %5s %9s %9s %9s %9s %9s\n",
            "item", "sheet2", "pubN", "obsN",
            "pub_mean", "obs_mean", "d_mean", "pub_sd", "obs_sd"))
for (i in 1:18)
    cat(sprintf("%-7s %-6s %5d %5d %9.4f %9.4f %9.5f %9.5f %9.5f\n",
                codes[i], LABEL[i], PUB_N[i], obs_n[i],
                PUB_MEAN[i], obs_mean[i], obs_mean[i] - PUB_MEAN[i],
                PUB_SD[i], obs_sd[i]))

worst_m <- max(abs(obs_mean - PUB_MEAN))
worst_s <- max(abs(obs_sd   - PUB_SD))
n_ok    <- all(obs_n == PUB_N)
cat(sprintf("\nlargest |d_mean| = %.6f (tol %.4f); largest |d_sd| = %.7f (tol %.6f); n all 748: %s\n",
            worst_m, TOL_MEAN, worst_s, TOL_SD, n_ok))

# Uniqueness: does each live item match exactly ONE published row within tol?
amb <- sapply(1:18, function(i) sum(abs(obs_mean[i] - PUB_MEAN) <= TOL_MEAN))
gap <- min(diff(sort(PUB_MEAN)))
cat(sprintf("published means pairwise distinct: smallest gap %.4f (>> tol); ", gap))
cat(sprintf("each live item matches exactly one published row: %s\n", all(amb == 1)))

cat("\nPositional header diff (raw.columns[8:26] of the deposit workbook):\n")
for (i in 1:18) cat(sprintf("  ans_%-2d <- raw col %2d  %s\n", i, 7 + i, HEADER[i]))

cat("\nNot established by this script: the 6-point response anchors (never published;\n")
cat("option_text ships blank) and the English item_text_translated (IRW's own rendering).\n")

ok <- worst_m <= TOL_MEAN && worst_s <= TOL_SD && n_ok && all(amb == 1)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
