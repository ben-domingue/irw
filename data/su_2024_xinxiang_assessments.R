library(tidyverse)
library(janitor)
library(readr)

# 数据路径
raw_dir <- "raw"
output_dir <- "output"

# 如果 output 文件夹不存在，则自动创建
dir.create(output_dir, showWarnings = FALSE)
demographic <- read_csv(
  file.path(raw_dir, "demographic.csv"),
  show_col_types = FALSE
) |>
  clean_names()
glimpse(demographic)
names(demographic)
nrow(demographic)
head(demographic)
# 整理人口统计变量
demographic_clean <- demographic |>
  transmute(
    id = as.character(export_id),
    cov_gender = as.character(gender),
    cov_age = as.numeric(age),
    cov_education = as.character(edu),
    cov_smoking = as.character(smoke),
    cov_drinking = as.character(drink)
  )

# 查看整理后的数据
glimpse(demographic_clean)
head(demographic_clean)

# 检查ID数量
nrow(demographic_clean)
n_distinct(demographic_clean$id)

# 检查是否存在重复ID
anyDuplicated(demographic_clean$id)

# 检查缺失值
demographic_clean |>
  summarise(
    missing_id = sum(is.na(id)),
    missing_gender = sum(is.na(cov_gender)),
    missing_age = sum(is.na(cov_age)),
    missing_education = sum(is.na(cov_education)),
    missing_smoking = sum(is.na(cov_smoking)),
    missing_drinking = sum(is.na(cov_drinking))
  ) 
  # 读取 PHQ-9 原始数据
phq9_raw <- read_csv(
  file.path(raw_dir, "phq9.csv"),
  show_col_types = FALSE
) |>
  clean_names()

# 查看 PHQ-9 数据结构
glimpse(phq9_raw)

# 查看全部变量名
names(phq9_raw)

# 查看前6行
head(phq9_raw)
# 检查 PHQ-9 题目列和作答时间列
question_cols <- names(phq9_raw)[
  str_detect(names(phq9_raw), "^question\\d+$")
]

time_cols <- names(phq9_raw)[
  str_detect(names(phq9_raw), "^time\\d+$")
]

question_cols
time_cols

length(question_cols)
length(time_cols)
# 将 PHQ-9 转换为 IRW 长格式
phq9_long <- phq9_raw |>
  select(
    export_id,
    all_of(question_cols),
    all_of(time_cols)
  ) |>
  pivot_longer(
    cols = -export_id,
    names_to = c(".value", "item_number"),
    names_pattern = "(question|time)(\\d+)"
  ) |>
  transmute(
    id = as.character(export_id),
    item_number = as.integer(item_number),
    item = paste0("PHQ_", item_number),
    resp = as.numeric(question),
    rt = as.numeric(time)
  ) |>
  left_join(
    demographic_clean,
    by = "id"
  ) |>
  arrange(id, item_number) |>
  select(
    id,
    item,
    resp,
    rt,
    cov_gender,
    cov_age,
    cov_education,
    cov_smoking,
    cov_drinking
  )
nrow(phq9_long)
n_distinct(phq9_long$id)
n_distinct(phq9_long$item)
range(phq9_long$resp, na.rm = TRUE)
head(phq9_long, 12)
# PHQ-9 质量检查

# 1. 检查每个 id-item 组合是否唯一
phq9_duplicates <- phq9_long |>
  count(id, item) |>
  filter(n != 1)

nrow(phq9_duplicates)

# 2. 检查缺失值
phq9_missing <- phq9_long |>
  summarise(
    missing_id = sum(is.na(id)),
    missing_item = sum(is.na(item)),
    missing_resp = sum(is.na(resp)),
    missing_rt = sum(is.na(rt)),
    missing_gender = sum(is.na(cov_gender)),
    missing_age = sum(is.na(cov_age)),
    missing_education = sum(is.na(cov_education)),
    missing_smoking = sum(is.na(cov_smoking)),
    missing_drinking = sum(is.na(cov_drinking))
  )

phq9_missing

# 3. 检查每道题的反应范围
phq9_response_check <- phq9_long |>
  group_by(item) |>
  summarise(
    n = n(),
    min_resp = min(resp, na.rm = TRUE),
    max_resp = max(resp, na.rm = TRUE),
    missing_resp = sum(is.na(resp)),
    .groups = "drop"
  )

phq9_response_check

# 4. 检查 response time
phq9_rt_check <- phq9_long |>
  summarise(
    min_rt = min(rt, na.rm = TRUE),
    median_rt = median(rt, na.rm = TRUE),
    mean_rt = mean(rt, na.rm = TRUE),
    max_rt = max(rt, na.rm = TRUE),
    zero_rt = sum(rt == 0, na.rm = TRUE),
    negative_rt = sum(rt < 0, na.rm = TRUE),
    missing_rt = sum(is.na(rt))
  )

phq9_rt_check
# 导出 PHQ-9 IRW 文件
write_csv(
  phq9_long,
  file.path(output_dir, "su_2024_phq9.csv"),
  na = ""
)
# =========================================================
# 通用 IRW 转换函数
# =========================================================

convert_scale_to_irw <- function(
    input_file,
    item_map,
    output_file
) {
  
  # 1. 读取原始量表数据
  raw_data <- read_csv(
    file.path(raw_dir, input_file),
    show_col_types = FALSE
  ) |>
    clean_names()
  
  # 2. 检查所需变量是否存在
  required_columns <- c(
    "export_id",
    item_map$resp_col,
    item_map$rt_col
  )
  
  missing_columns <- setdiff(
    required_columns,
    names(raw_data)
  )
  
  if (length(missing_columns) > 0) {
    stop(
      paste(
        "Missing columns:",
        paste(missing_columns, collapse = ", ")
      )
    )
  }
  
  # 3. 按照明确的 item map 转成长格式
  long_data <- pmap_dfr(
    item_map,
    function(item, resp_col, rt_col) {
      
      raw_data |>
        transmute(
          id = as.character(export_id),
          item = item,
          resp = as.numeric(.data[[resp_col]]),
          rt = as.numeric(.data[[rt_col]])
        )
    }
  ) |>
    left_join(
      demographic_clean,
      by = "id"
    ) |>
    arrange(id, item) |>
    select(
      id,
      item,
      resp,
      rt,
      cov_gender,
      cov_age,
      cov_education,
      cov_smoking,
      cov_drinking
    )
  
  # 4. 基本质量检查
  duplicate_rows <- long_data |>
    count(id, item) |>
    filter(n != 1)
  
  if (nrow(duplicate_rows) > 0) {
    stop("Duplicate id-item combinations were found.")
  }
  
  if (any(is.na(long_data$id))) {
    stop("Missing id values were found.")
  }
  
  if (any(is.na(long_data$item))) {
    stop("Missing item values were found.")
  }
  
  if (any(is.na(long_data$resp))) {
    stop("Missing response values were found.")
  }
  
  # 5. 打印检查结果
  cat("\nOutput file:", output_file, "\n")
  cat("Rows:", nrow(long_data), "\n")
  cat("IDs:", n_distinct(long_data$id), "\n")
  cat("Items:", n_distinct(long_data$item), "\n")
  cat(
    "Response range:",
    min(long_data$resp, na.rm = TRUE),
    "to",
    max(long_data$resp, na.rm = TRUE),
    "\n"
  )
  cat(
    "RT range:",
    min(long_data$rt, na.rm = TRUE),
    "to",
    max(long_data$rt, na.rm = TRUE),
    "\n"
  )
  
  # 6. 导出
  write_csv(
    long_data,
    file.path(output_dir, output_file),
    na = ""
  )
  
  return(long_data)
}
