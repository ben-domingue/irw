library(tidyverse)
library(readxl)
library(janitor)

# WAVE 1
ctp_wave1 <- read_csv('ctp_wave1.csv')

names(ctp_wave1) <- tolower(names(ctp_wave1))

drop_vars <- c()

for (i in 1:ncol(ctp_wave1)) {
  unique_vals <- unique(ctp_wave1[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(ctp_wave1)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(ctp_wave1)[i])
  }
  
  if (class(ctp_wave1[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(ctp_wave1)[i])
  }
}

ctp_wave1 <- ctp_wave1 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -asex1,
         -starts_with('arhyming'),
         -starts_with('aletter'),
         -starts_with('aage'),
         -abrnumer11,
         -adays1,
         -starts_with('aword'),
         -arapid_object_std_ori1,
         -acol1,
         -adiff1,
         -achname1,
         -acoderid1,
         -dibel_gr_1,
         -w1age1,
         -starts_with('sumsas'),
         -starts_with('mdigrw'),
         -starts_with('aw1mon'),
         -starts_with('wid'),
         -starts_with('wjcomp'),
         -family_id,
         -rletrw1,
         -starts_with('robj'),
         -starts_with('widst'),
         -starts_with('or31'),
         -starts_with('avsas'),
         -starts_with('sphnst'),
         -starts_with('sphnst'),
         -starts_with('dphnst'),
         -starts_with('wjcomp'),
         -starts_with('stotst'),
         -starts_with('qntsas'),
         -starts_with('memsum'),
         -dphnsto1,
         -starts_with('vocbs'),
         -starts_with('memsas'),
         -starts_with('qntsa'),
         -starts_with('watt'),
         -starts_with('vrbsa'),
         -starts_with('cmpsas'),
         -nw11_tr_1,
         -starts_with('rcol'),
         -starts_with('dcscl'),
         -starts_with('qntrw'),
         -starts_with('rtot'),
         -starts_with('or12_'),
         -starts_with('dtot'),
         -starts_with('isfk1'),
         -starts_with('dcsst'),
         -starts_with('iintst'),
         -starts_with('ltidst'),
         -starts_with('itotst'),
         -starts_with('rtotst'),
         -starts_with('rprdst'),
         -starts_with('rdisst'),
         -starts_with('rprdst'),
         -starts_with('nwfk'),
         -starts_with('ln11'),
         -starts_with('lnk1'),
         -starts_with('patst'),
         -starts_with('msntst'),
         -starts_with('patsum'),
         -starts_with('qnts'),
         -starts_with('mdigst'),
         -starts_with('ps11'),
         -starts_with('bntrw'),
         -starts_with('rleter'),
         -starts_with('psfk2'),
         -starts_with('ltid'),
         -starts_with('rnum'),
         -starts_with('patrw'),
         -starts_with('msntrw'),
         -starts_with('vocbrw'),
         -starts_with('rletst'),
         -adeletion_cs_51,
         -starts_with('iint'),
         -starts_with('itot'),
         -starts_with('rdis'),
         -starts_with('rpr'),
         -starts_with('rdi'),
         -starts_with('sphn'),
         -starts_with('dphn'),
         -starts_with('dcs'),
         -starts_with('stot')) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 1,
         item = if_else(str_starts(item, 'a'), str_replace(item, 'a', ''), item))


# WAVE 2

ctp_wave2 <- read_csv('ctp_wave2.csv')

names(ctp_wave2) <- tolower(names(ctp_wave2))

drop_vars <- c()

for (i in 1:ncol(ctp_wave2)) {
  unique_vals <- unique(ctp_wave2[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(ctp_wave2)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(ctp_wave2)[i])
  }
  
  if (class(ctp_wave2[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(ctp_wave2)[i])
  }
}

ctp_wave2 <- ctp_wave2 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -bsex1,
         -bent_lev1,
         -brnltsum1,
         -brnleb1,
         -brnltb1,
         -brnlea1,
         -brnlta1,
         -brndtsum1,
         -brndeb1,
         -brndtb1,
         -brndea1,
         -brndta1,
         -bv1271,
         -bctp_tid1,
         -bsbf_tr1,
         -contains('_original'),
         -bsbb_tr1,
         -bwjpc_r_original1,
         -starts_with("bwjcomp"),
         -starts_with("bwatt"),
         -starts_with("bwid"),
         -starts_with("bltid"),
         -starts_with("bcmpsas"),
         -starts_with("bsumsas"),
         -starts_with("bmemsas"),
         -starts_with("bmdig"),
         -starts_with("bmsnt"),
         -starts_with("bavsas"),
         -starts_with("bpat"),
         -starts_with("bqnt"),
         -starts_with("bvrbs"),
         -starts_with("bvocb"),
         -starts_with("bdtot"),
         -starts_with("bdphn"),
         -starts_with("bdcs"),
         -starts_with("boost_"),
         -starts_with("bbnt"),
         -starts_with("bdcstot"),
         -starts_with("bor31"),
         -starts_with("bor21"),
         -starts_with("bor12"),
         -starts_with("bor11"),
         -starts_with("bnw"),
         -starts_with("bps"),
         -starts_with("bln"),
         -starts_with("bis"),
         -starts_with("bdibel"),
         -starts_with("brlet"),
         -starts_with("brnum"),
         -starts_with('bwjpc'),
         -starts_with('bword'),
         -starts_with('bletter'),
         -bnumnonmissingsas1,
         -bmemory_sum1,
         -bdeletion_total_calc_original1,
         -contains('_phon_'),
         -contains('_total_'),
         -bsbds_ts1,
         -bsegtot1,
         -bw1age1)  |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 2,
         item = if_else(str_starts(item, 'b'), str_replace(item, 'b', ''), item))



# WAVE 4
cmq_wave4 <- read_csv('cmq_wave4.csv')

names(cmq_wave4) <- tolower(names(cmq_wave4))

drop_vars <- c()

for (i in 1:ncol(cmq_wave4)) {
  unique_vals <- unique(cmq_wave4[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(cmq_wave4)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(cmq_wave4)[i])
  }
  
  if (class(cmq_wave4[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(cmq_wave4)[i])
  }
}

cmq_wave4 <- cmq_wave4 |>
  select(-`...1`,
         -all_of(drop_vars),
         -mcmphm1,
         -mfnpmg1,
         -ends_with('2'),
         -mhw1fc1,
         -mhw2fc1,
         -mhwatt1,
         -mhwenv1,
         -mhwtim1,
         -mhwenv1,
         -mhwtim1,
         -`_havecmq`,
         -randomtwin) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 4,
         item = if_else(str_starts(item, 'm'), str_replace(item, 'm', ''), item))

# ___________________

ctp_wave4 <- read_csv('ctp_wave4.csv')

names(ctp_wave4) <- tolower(names(ctp_wave4))

drop_vars <- c()

for (i in 1:ncol(ctp_wave4)) {
  unique_vals <- unique(ctp_wave4[[i]])
  unique_len <- length(ctp_wave4)
  
  if (unique_len == 1) {
    if (is.na(unique(ctp_wave4[1]))) {
    drop_vars <- append(drop_vars, names(ctp_wave4)[i])
    }
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(ctp_wave4)[i])
  }
  
  if (class(ctp_wave4[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(ctp_wave4)[i])
  }
}

ctp_wave4 <- ctp_wave4 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -mnsex1,
         -contains('bday'),
         -contains('age'),
         -contains('grade'),
         -contains('tot'),
         -mhvrtwt1,
         -mhvrtsc1,
         -starts_with('mhvt6s1'),
         -starts_with('mhvt6t'),
         -mhvt10tt1,
         -mhvt5ttl1,
         -mhvrlntb1,
         -mhvrlnea1,
         -mhvrlnta1,
         -mhvrndeb1,
         -mhvrndtb1,
         -mhvrndea1,
         -mhvrndta1,
         -mhvt18tl1,
         -mhvpcttl1,
         -mhvsshps1,
         -mhvssips1,
         -mhvsspfs1,
         -mhvssfs1,
         -mhvsshpw1,
         -mhvssipw1,
         -mhvsspfw1,
         -mhvssfw1,
         -mhvssgcc1,
         -mhvsshpc1,
         -mhvssipc1,
         -mhvsspfc1,
         -mhvssfc1,
         -randomtwin,
         -mwjpc_col1,
         -mwjpc_diff1,
         -mwjcomprs1,
         -mwjcompws1,
         -mqcws1,
         -mapws1,
         -mfluws1,
         -mcalcws1,
         -mqcst1,
         -mapst1,
         -mflust1,
         -mcalcst1,
         -mwjcompst1,
         -mwratst1,
         -mrletst1,
         -mrnumst1,
         -mgccs1,
         -mhpcs1,
         -mpcs1,
         -mpfcs1,
         -mfcs1,
         -mwratrw1,
         -mwjcomprw1,
         -mqcrw1,
         -maprw1,
         -mflurw1,
         -mcalcrw1,
         -starts_with('mor31'),
         -starts_with('mor21'),
         -mrletrw1,
         -mrnumrw1,
         -starts_with('m18'),
         -mnw21_tr_1,
         -mhvrlneb1) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 4,
         item = if_else(str_starts(item, 'm'), str_replace(item, 'm', ''), item))

# WAVE 7

cq_wave7 <- read_csv('cq_wave7.csv')

names(cq_wave7) <- tolower(names(cq_wave7))

drop_vars <- c()

for (i in 1:ncol(cq_wave7)) {
  unique_vals <- unique(cq_wave7[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(cq_wave7)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(cq_wave7)[i])
  }
  
  if (class(cq_wave7[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(cq_wave7)[i])
  }
}

cq_wave7 <- cq_wave7 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -randomtwin,
         -fcqfmm1,
         -fcqfms1,
         -fcqartspk1,
         -fcqartppk1,
         -fcqartspkdivbyn1,
         -fcqartppkdivbyn1,
         -fcqarttpe1,
         -fcqsmintrin1,
         -fcqsmintroj1,
         -fcqsmamot1,
         -fcqsmident1,
         -fcqfmscore1,
         -fcqmpstrict1,
         -fcqmpwarmth1,
         -fcqchaos1,
         -fcoderid1) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 7,
         item = if_else(str_starts(item, 'f'), str_replace(item, 'f', ''), item))
# ______________

cqb_wave7 <- read_csv('cqb_wave7.csv')

names(cqb_wave7) <- tolower(names(cqb_wave7))

drop_vars <- c()

for (i in 1:ncol(cqb_wave7)) {
  unique_vals <- unique(cqb_wave7[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(cqb_wave7)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(cqb_wave7)[i])
  }
  
  if (class(cqb_wave7[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(cqb_wave7)[i])
  }
}

cqb_wave7 <- cqb_wave7 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -randomtwin,
         -fcoderid1,
         -frefce1,
         -frefcen1,
         -frefcesum1,
         -frefsl1,
         -frefsln1,
         -frefslsum1,
         -frefrw1,
         -frefav1,
         -frefrc1,
         -frefso1,
         -frefgr1,
         -frefre1,
         -frefco1,
         -frefim1,
         -frefae1,
         -frefcu1,
         -frefch1,
         -frefef1,
         -fcqhoatt1,
         -fcqhotime1,
         -fcqhoenv1,
         -fcqmsneg1,
         -fcqmsactiv1,
         -fcqmsbond1,
         -fcqmsattach1,
         -fcqctsupp1,
         -fcqctcomp1,
         -fcqctcoop1,
         -fcqamtotalscas1,
         -fcqamga1,
         -fcqampif1,
         -fcqamsa1,
         -fcqampif1,
         -fcqamsa1,
         -fcqampa1,
         -fcqamsp1,
         -fcqamocd1,
         -frefcysum1,
         -frefcyn1,
         -frefcy1,
         -frefcnsum1,
         -frefcnn1,
         -frefcn1,
         -frefitsum1,
         -frefitn1,
         -frefit1,
         -frefwasum1,
         -frefwan1,
         -frefwa1,
         -frefeysum1,
         -frefeyn1,
         -frefey1,
         -frefrnsum1,
         -frefrnn1,
         -frefrn1) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 7,
         item = if_else(str_starts(item, 'f'), str_replace(item, 'f', ''), item))

# WAVE 8

ctp_wave8 <- read_csv('ctp_wave8.csv')

names(ctp_wave8) <- tolower(names(ctp_wave8))

drop_vars <- c()

for (i in 1:ncol(ctp_wave8)) {
  unique_vals <- unique(ctp_wave8[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(ctp_wave8)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(ctp_wave8)[i])
  }
  
  if (class(ctp_wave8[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(ctp_wave8)[i])
  }
}

ctp_wave8 <- ctp_wave8 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -randomtwin,
         -starts_with('gasddans'),
         -starts_with('gasstans'),
         -starts_with('gaspstr'),
         -starts_with('gasddstr'),
         -gasstrtm1,
         -gasstcorn1,
         -gasstcorrtm1,
         -gasfrcorrtm1,
         -starts_with('gasstsrt'),
         -starts_with('gasstcrt'),
         -starts_with('gasstccrt'),
         -contains('sum'),
         -contains('suc'),
         -contains('suf'),
         -contains('suv'),
         -contains('sur'),
         -contains('sud'),
         -contains('min'),
         -contains('max'),
         -starts_with('gasddsu'),
         -gasstac1,
         -gasma1,
         -gasmas1,
         -gasmac1,
         -starts_with('gfcrt'),
         -starts_with('gfcin'),
         -starts_with('gfccorrt'),
         -starts_with('gasfrrt'),
         -starts_with('gasstrt'),
         -starts_with('gpetrt'),
         -starts_with('gpetstim'),
         -gfccorpct1,
         -starts_with('gpethard'),
         -contains('correct'),
         -contains('practice'),
         -starts_with('gpet'),
         -starts_with('gfm'),
         -contains('original'),
         -starts_with('gfmef'),
         -starts_with('gneline'),
         -starts_with('gnelen'),
         -starts_with('gdn'),
         -contains('leter'),
         -contains('rapid'),
         -contains('numer'),
         -contains('day'),
         -contains('year'),
         -contains('sex'),
         -gcoderid1,
         -starts_with('gasfrans'),
         -starts_with('gdtnogbest'),
         -starts_with('gdtnogsuper'),
         -starts_with('gdtbest'),
         -starts_with('gdtsuper'),
         -starts_with('gstop_'),
         -contains('age'),
         -gwjt6tl1,
         -gwjt6s1,
         -grndtb1,
         -grndea1,
         -grndta1,
         -starts_with('gneans'),
         -starts_with('gnedif'),
         -gasfrcorn1,
         -starts_with('gassts'),
         -starts_with('gap'),
         -starts_with('gflu'),
         -starts_with('gcalc'),
         -gttwrest1,
         -gtpdest1,
         -gtswest1,
         -gssst1,
         -starts_with('gnenum'),
         -gnwrst1,
         -gmdst1,
         -grletst1,
         -grnumst1,
         -starts_with('gcktc'),
         -starts_with('gckpc'),
         -gcblv1,
         -starts_with('gasbuc'),
         -starts_with('gasbu'),
         -starts_with('gasfrac'),
         -gssrw1,
         -gaprw1,
         -gflurw1,
         -gcalcrw1,
         -gssi1,
         -gssc1,
         -grletrw1,
         -gcktid1,
         -grnumrw1,
         -gnwrrw1,
         -starts_with('gmd'),
         -gcbrw1,
         -gpdetim1,
         -gtpderw1,
         -gswetim1,
         -gsst1,
         -gtswerw1,
         -grnltb1,
         -grnlta1,
         -grndeb1) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 8,
         item = if_else(str_starts(item, 'g'), str_replace(item, 'g', ''), item))


# WAVE 9
cq_wave9 <- read_csv('cq_wave9.csv')

names(cq_wave9) <- tolower(names(cq_wave9))

drop_vars <- c()

for (i in 1:ncol(cq_wave9)) {
  unique_vals <- unique(cq_wave9[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(cq_wave9)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(cq_wave9)[i])
  }
  
  if (class(cq_wave9[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(cq_wave9)[i])
  }
}

cq_wave9 <- cq_wave9 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -hcqfqb1,
         -hcqfqe1,
         -hcqfqg1,
         -hrefrn1,
         -hrefey1,
         -hrefwa1,
         -hrefit1,
         -hrefcn1,
         -hrefcy1,
         -hrefce1,
         -hrefsl1,
         -hrefrw1,
         -hrefav1,
         -hrefrc1,
         -hrefso1,
         -hrefgr1,
         -hrefre1,
         -hrefco1,
         -hrefim1,
         -hrefae1,
         -hrefcu1,
         -hrefch1,
         -hrefef1,
         -hcqamga1,
         -hcqamsa1,
         -hcqampa1,
         -hcqartspk1,
         -hcqartppk1,
         -hcqartspkdivbyn1,
         -hcqartppkdivbyn1,
         -hcqarttpe1,
         -hcqfmscore1,
         -hcqchaos1) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 9,
         item = if_else(str_starts(item, 'h'), str_replace(item, 'h', ''), item))

# --------------

ctp_wave9 <- read_csv('ctp_wave9.csv')

names(ctp_wave9) <- tolower(names(ctp_wave9))

drop_vars <- c()

for (i in 1:ncol(ctp_wave9)) {
  unique_vals <- unique(ctp_wave9[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(ctp_wave9)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(ctp_wave9)[i])
  }
  
  if (class(ctp_wave9[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(ctp_wave9)[i])
  }
}

ctp_wave9 <- ctp_wave9 |>
  select(-`...1`,
         -all_of(drop_vars),
         -ends_with('2'),
         -starts_with('hfcrt'),
         -starts_with('hasddrt'),
         -starts_with('hasstrt'),
         -starts_with('hfccorrt'),
         -starts_with('hfcincrt'),
         -matches("^hfm\\d"),
         -starts_with('hfmrtd'),
         -starts_with('hstop_'),
         -starts_with('hfccor'),
         -starts_with('hfm'),
         -contains('sum'),
         -contains('mean'),
         -starts_with('hlmt12f'),
         -starts_with('hlmt11f'),
         -starts_with('hlmt10f'),
         -starts_with('hlmt9f'),
         -starts_with('hlmt8f'),
         -starts_with('hlmt7f'),
         -starts_with('hlmt6f'),
         -starts_with('hlmt5f'),
         -starts_with('hlmt4f'),
         -starts_with('hlmt3f'),
         -starts_with('hlmt2f'),
         -starts_with('hlmt1f'),
         -contains('original'),
         -starts_with('hasstans'),
         -hasptcraw1,
         -starts_with('hasddstr'),
         -starts_with('haspstr'),
         -starts_with('hwjt6'),
         -starts_with('hneline'),
         -starts_with('hnelen'),
         -starts_with('hcpsct'),
         -starts_with('hcpsbt'),
         -hcpsatr1,
         -hcpsati1,
         -hneline221,
         -starts_with('hrnd'),
         -starts_with('hrnl'),
         -starts_with('htswe'),
         -starts_with('htpd'),
         -hswetim1,
         -hpdetim1,
         -contains('sex'),
         -contains('age'),
         -starts_with('husp'),
         -starts_with('hrnum'),
         -starts_with('hrlet'),
         -hcpsatc1,
         -hgmcrw1,
         -starts_with('hmd'),
         -starts_with('hnwr'),
         -starts_with('hwcs'),
         -hwcrw1,
         -starts_with('hcalc'),
         -starts_with('hflu'),
         -starts_with('hwjcomp'),
         -starts_with('has'),
         -starts_with('hap'),
         -starts_with('hwjpc'),
         -httwrest1,
         -htpdest1,
         -htswest1,
         -starts_with('hnedif'),
         -starts_with('hneans'),
         -starts_with('hnedif'),
         -starts_with('hnenum')) |>
  pivot_longer(cols = -c(sid1, fid),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(wave = 9,
         item = if_else(str_starts(item, 'h'), str_replace(item, 'h', ''), item))
         
# COMBINE WAVES

df <- rbind(ctp_wave1, ctp_wave2, ctp_wave4, cmq_wave4, cq_wave7, 
            cqb_wave7, ctp_wave8, ctp_wave9, cq_wave9)

items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$sid1))
ids <- ids |>
  mutate(id = row_number())

fam_id <- as.data.frame(unique(df$fid))
fam_id <- fam_id |>
  mutate(family_id = row_number())
  

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('sid1' = "unique(df$sid1)")) |>
  left_join(fam_id, by=c('fid' = "unique(df$fid)")) |>
  mutate(person_id = id,
         id = paste0(person_id, '_', wave)) |>
  # drop character item variable
  select(person_id, id, family_id, wave, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(person_id, item, wave)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="western_reserve_project.Rdata")
