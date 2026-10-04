# IL-HTE Econ, Create a list of data sets
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# list of the data sets
datasets <- list(
  # 1
  gilbert2023, kim2023, gilbert2024_a, blattman2017, woods2021,
  # 6
  bruhn2016, kim2024_a, kim2024_b, hidrobo2016, kim2021_a,
  # 11
  kim2021_b, kim2021_c, romero2020_a, romero2020_b, romero2020_c,
  # 16
  debarros2023, duflo2024_a, duflo2024_b, duflo2024_c, jiyanthi2021,
  # 21
  davenport2023, berry2018, bang2022, llaurado2024, schrein2020_a,
  # 26
  schrein2020_b, banerji2017_a, banerji2017_b, banerji2017_c, banerji2017_d,
  # 31
  duflo2015, maruyama2022, alady2017, angelucci2024, persson2020_a, 
  # 36
  persson2020_b, carpena2024_a, carpena2024_b, berry2022_a, berry2022_b,
  # 41
  moho2023, hussam2022_a, hussam2022_b, lee2021, bateman2020,
  # 46
  glatz2023_a, glatz2023_b, cardenas2023, daniel2017, luo2024_a,
  # 51
  luo2024_b, abaluck2022, saha2023_a, saha2023_b, wang2023, 
  # 56
  sebele2023, maselko2020_a, maselko2020_b, maselko2020_c, lyall2019_a,
  # 61
  lyall2019_b, wilson2024, hoffmann2018, zhao2023, oconnor2023_a,
  # 66
  oconnor2023_b, oconnor2023_c, banerjee2017_a, banerjee2017_b, banerjee2017_c,
  # 71
  banerjee2017_d, banerjee2017_e, banerjee2017_f, gilbert2024_b, baron2021
  )

save(datasets, file = glue("{clean}/datasets_list.Rdata"))
