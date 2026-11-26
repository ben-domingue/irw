## Rajeb, M., & Lakin, J. M. (2024). Mental Rotation Performance [Data set].
## OSF. https://osf.io/kxb9r
## Data: MRT_Response_data_with_gender.csv (https://osf.io/download/wa53j/);
## item images in "Mental Rotation Items.pdf" (https://osf.io/download/9p8ef/).
## Licence: CC BY 4.0 (granted by Joni Lakin by email 2026-11-25 and set on
## the OSF project the same day; copy in irw/licenseinfo/emails/).
## Mental rotation collection.
##
## Test: 15 mental rotation items with Shepard-Metzler style cube figures,
## four response options each (per the item PDF); the project does not name
## the test or describe the sample. 129 students, responses scored 0/1.
##
## Layout:
##   id = the file's "Students Number" (1..129)
##   item = mr01..mr15 (source MR.1..MR.15)
##   resp = 1 correct, 0 incorrect
##   cov_female = 1 F, 0 M, NA where the file says NA
##
## Usage: Rscript lakin_2024_mrt.R <MRT_Response_data_with_gender.csv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw <- if (length(args) >= 1) args[1] else "MRT_Response_data_with_gender.csv"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

## two header rows: "Students Number, Item Numbers, ..., Gender" then MR.1..MR.15
x <- read.csv(raw, skip = 2, header = FALSE, stringsAsFactors = FALSE,
              na.strings = c("", "NA"))
names(x) <- c("id", sprintf("mr%02d", 1:15), "gender")
stopifnot(nrow(x) == 129, !anyDuplicated(x$id),
          all(unlist(x[, 2:16]) %in% 0:1),
          all(is.na(x$gender) | x$gender %in% c("F", "M")))

d <- data.frame(
  id = rep(as.integer(x$id), each = 15),
  item = rep(sprintf("mr%02d", 1:15), times = nrow(x)),
  resp = as.integer(t(as.matrix(x[, 2:16]))),
  cov_female = rep(ifelse(x$gender == "F", 1L, ifelse(x$gender == "M", 0L, NA)), each = 15),
  stringsAsFactors = FALSE)
table <- "lakin_2024_mrt"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
p <- d[!duplicated(d$id), ]
cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f female=%d male=%d gender_na=%d\n",
            table, nrow(d), length(unique(d$id)), length(unique(d$item)), mean(d$resp),
            sum(p$cov_female == 1, na.rm = TRUE), sum(p$cov_female == 0, na.rm = TRUE),
            sum(is.na(p$cov_female))))
print(round(tapply(d$resp, d$item, mean), 2))
