# IRW metadata pipeline run -- 2026-08-31

## Workflow 1: generate + diff (run_pipeline.sh)
```
== Snapshotting current CSVs before running anything ==

== Stage 01: Rscript 01_metadata.R ==
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_meta:bdxt"
[1] 3650    9
[1] 3650
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "item_response_warehouse:as2e"
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "item_response_warehouse_2:epbx"
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "item_response_warehouse_3:5xaj"
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "item_response_warehouse_4:980f"
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "item_response_warehouse_5:3ykx"
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "item_response_warehouse_6:fpe6"
[1] "add"
  [1] "xie_2026_student_questionnaire"                  
  [2] "goldberg_2018_prs_music_preferences"             
  [3] "alan_2018_teacher_extrinsic_motivation"          
  [4] "apaza_2026_sdo"                                  
  [5] "goldberg_2018_prs_tv_preferences"                
  [6] "goldberg_2018_spa_skills"                        
  [7] "kotsou_2016_bdi"                                 
  [8] "goldberg_2018_spa_talents"                       
  [9] "risticdedic_2025_dhq_currentstate"               
 [10] "gan_2024_alexithymia"                            
 [11] "risticdedic_2025_dhq_importance"                 
 [12] "eldor_2022_anomie"                               
 [13] "dalichaouche_2026_covid_attitudes"               
 [14] "tu_2022_achievement_motivation"                  
 [15] "balparda_2021_korq_symptoms"                     
 [16] "rosyid_2025_prosocial_motivation"                
 [17] "gan_2024_depression"                             
 [18] "daderman_2023_naq_r"                             
 [19] "sumner_2022_ipip_neo"                            
 [20] "dss_mouta_2021"                                  
 [21] "sirventruiz_2025_pdat"                           
 [22] "matosaslopez_2024_teacher_assessment"            
 [23] "koksal_2023_psycap"                              
 [24] "manolika_2021_mini_ipip"                         
 [25] "sumner_2022_ftdss"                               
 [26] "balparda_2021_kepaq_emotional"                   
 [27] "xu_2023_mi"                                      
 [28] "daderman_2023_wis"                               
 [29] "daderman_2023_naqr"                              
 [30] "goldberg_2018_sbo"                               
 [31] "demirbag_2025_epistemological_beliefs"           
 [32] "wang_2025_automatic_thoughts"                    
 [33] "personalitychange_kramer_2025_si"                
 [34] "baquerotomas_2026_emas"                          
 [35] "manolika_2021_reading_preferences"               
 [36] "li_2026_coach_leadership"                        
 [37] "rogers_2021_financial_knowledge"                 
 [38] "goldberg_2018_bri_bri"                           
 [39] "arabaci_2025_turnover_intention"                 
 [40] "choi_2026_cmsce_2021_2"                          
 [41] "goldberg_2018_ipip"                              
 [42] "antunez_2013_tmms24"                             
 [43] "goldberg_2018_prs_movie_preferences"             
 [44] "antunez_2013_rmeq"                               
 [45] "goldberg_2018_pas_adjectives"                    
 [46] "arabaci_2025_burnout"                            
 [47] "kermen_2022_self_regulation"                     
 [48] "eldor_2022_violent_extremism"                    
 [49] "szabo_2025_work_addiction"                       
 [50] "sokolovskii_2021_tfeq"                           
 [51] "turpochaparro_2026_social_network_addiction"     
 [52] "tang_2024_self_construal"                        
 [53] "chatzoudes_2021_trust"                           
 [54] "tang_2024_caregiver_child_regulation"            
 [55] "goldberg_2018_jpir"                              
 [56] "tang_2024_panas_negative"                        
 [57] "kotsou_2016_panas"                               
 [58] "chen_2026_social_anxiety"                        
 [59] "goldberg_2018_hpq_h"                             
 [60] "eldor_2022_symbolic_threat"                      
 [61] "apaza_2026_meim_r"                               
 [62] "turpochaparro_2026_self_esteem"                  
 [63] "cavojova_2017_cfc"                               
 [64] "sekowski_2025_mast"                              
 [65] "peng_2024_language_boredom"                      
 [66] "choi_2026_cmsce_2020_2"                          
 [67] "nguyen_2026_isi"                                 
 [68] "szabo_2025_family_conflict"                      
 [69] "kermen_2022_attention"                           
 [70] "choi_2026_cmsce_2021_1"                          
 [71] "chatzoudes_2021_job_satisfaction"                
 [72] "personalitychange_kramer_2025_rses"              
 [73] "alan_2018_teacher_growth_mindset"                
 [74] "balparda_2021_kepaq_functional"                  
 [75] "dalichaouche_2026_covid_practices"               
 [76] "emiral_2025_aips"                                
 [77] "goldberg_2018_ppq_music"                         
 [78] "goldberg_2018_spa_ipip"                          
 [79] "eldor_2022_relative_deprivation"                 
 [80] "demirbag_2025_goal_orientations"                 
 [81] "tang_2024_academic_satisfaction"                 
 [82] "nguyen_2026_pic"                                 
 [83] "cosenza_2015_cfc"                                
 [84] "eldor_2022_collective_anger"                     
 [85] "goldberg_2018_prs_reading_preferences"           
 [86] "huang_2023_medseq"                               
 [87] "nguyen_2026_gad7"                                
 [88] "eyrenci_2025_mental_health_literacy"             
 [89] "kotsou_2016_scs"                                 
 [90] "doherty_2023_burnout"                            
 [91] "li_2026_team_cohesion"                           
 [92] "goldberg_2018_prs_peo"                           
 [93] "goldberg_2018_sdv_ipip_temperament"              
 [94] "goldberg_2018_eps_adjectives"                    
 [95] "chen_2026_self_control"                          
 [96] "kermen_2022_anxiety"                             
 [97] "goldberg_2018_sdv_adjectives"                    
 [98] "teacherjudgements_lohmann_2026_conscientiousness"
 [99] "turpochaparro_2026_family_communication"         
[100] "itemrandom_buchanan_2018_PIL"                    
[101] "cao_2026_cdss_intention_to_use"                  
[102] "matosaslopez_2022_bars_teaching"                 
[103] "goldberg_2018_sdv_desirability"                  
[104] "chatzoudes_2021_ethical_leadership"              
[105] "goldberg_2018_spa_cultural_familiarity"          
[106] "personalitychange_kramer_2025_mls"               
[107] "tang_2024_outcome_expectations"                  
[108] "personalitychange_kramer_2025_swls"              
[109] "onah_2021_covid_knowledge"                       
[110] "kumlander_2018_scs"                              
[111] "sumner_2022_spq"                                 
[112] "alqerem_2024_diabetic_health_literacy"           
[113] "milson_2026_social_media_use"                    
[114] "goldberg_2018_eps_spirituality"                  
[115] "baquerotomas_2026_neoffi"                        
[116] "eldor_2022_school_resilience"                    
[117] "sumner_2022_asi"                                 
[118] "choi_2026_cmsce_2020_1"                          
[119] "goldberg_2018_prs_bas_bis"                       
[120] "teacherjudgements_lohmann_2026_motivation"       
[121] "tang_2024_environmental_support"                 
[122] "floreskanter_2021_cerq"                          
[123] "goldberg_2018_spa_medical_history"               
[124] "goldberg_2018_bri_food"                          
[125] "zhang_2026_ecosystem_services"                   
[126] "xu_2023_pca"                                     
[127] "szabo_2025_pss4"                                 
[128] "choi_2026_cmsce_2019_1"                          
[129] "atik_2026_psych_resilience"                      
[130] "goldberg_2018_prs_pey"                           
[131] "mboya_2020_gds15"                                
[132] "wu_2024_achievement_emotions"                    
[133] "goldberg_2018_sdv_schwartz_values"               
[134] "tang_2024_caregiver_child_communication"         
[135] "wicherts_2023_5pft"                              
[136] "wang_2025_cognitive_fusion"                      
[137] "trang_2023_vocabulary_strategies"                
[138] "goldberg_2018_bri_feel"                          
[139] "goldberg_2018_sdv_influ"                         
[140] "goldberg_2018_ppq_beliefs"                       
[141] "lee_2020_alcohol_use"                            
[142] "milson_2026_body_satisfaction"                   
[143] "woodall_2020_bfi44"                              
[144] "altman_2020_capq"                                
[145] "goldberg_2018_eps_s11"                           
[146] "kalczajanosi_2021_covid_risk"                    
[147] "baquerotomas_2026_pil"                           
[148] "alan_2018_teacher_warmth"                        
[149] "nguyen_2026_barthel"                             
[150] "alexandrowicz_2018_cesd"                         
 [ reached 'max' / getOption("max.print") -- omitted 338 entries ]
[1] "remove"
[1] "APFCompact_Ptacek_2024_DASS-21"     "eammi_grahe_2018_marriage_timing"  
[3] "alomari_2025_student_questionnaire" "altahla_2024_whoqol_bref"          
[1] 3650    9
[1] 3646    9
[1] "1/488 xie_2026_student_questionnaire"
[1] "2/488 goldberg_2018_prs_music_preferences"
[1] "3/488 alan_2018_teacher_extrinsic_motivation"
[1] "4/488 apaza_2026_sdo"
[1] "5/488 goldberg_2018_prs_tv_preferences"
[1] "6/488 goldberg_2018_spa_skills"
[1] "7/488 kotsou_2016_bdi"
[1] "8/488 goldberg_2018_spa_talents"
[1] "9/488 risticdedic_2025_dhq_currentstate"
[1] "10/488 gan_2024_alexithymia"
[1] "11/488 risticdedic_2025_dhq_importance"
[1] "12/488 eldor_2022_anomie"
[1] "13/488 dalichaouche_2026_covid_attitudes"
[1] "14/488 tu_2022_achievement_motivation"
[1] "15/488 balparda_2021_korq_symptoms"
[1] "16/488 rosyid_2025_prosocial_motivation"
[1] "17/488 gan_2024_depression"
[1] "18/488 daderman_2023_naq_r"
[1] "19/488 sumner_2022_ipip_neo"
[1] "20/488 dss_mouta_2021"
[1] "21/488 sirventruiz_2025_pdat"
[1] "22/488 matosaslopez_2024_teacher_assessment"
[1] "23/488 koksal_2023_psycap"
[1] "24/488 manolika_2021_mini_ipip"
[1] "25/488 sumner_2022_ftdss"
[1] "26/488 balparda_2021_kepaq_emotional"
[1] "27/488 xu_2023_mi"
[1] "28/488 daderman_2023_wis"
[1] "29/488 daderman_2023_naqr"
[1] "30/488 goldberg_2018_sbo"
[1] "31/488 demirbag_2025_epistemological_beliefs"
[1] "32/488 wang_2025_automatic_thoughts"
[1] "33/488 personalitychange_kramer_2025_si"
[1] "34/488 baquerotomas_2026_emas"
[1] "35/488 manolika_2021_reading_preferences"
[1] "36/488 li_2026_coach_leadership"
[1] "37/488 rogers_2021_financial_knowledge"
[1] "38/488 goldberg_2018_bri_bri"
[1] "39/488 arabaci_2025_turnover_intention"
[1] "40/488 choi_2026_cmsce_2021_2"
[1] "41/488 goldberg_2018_ipip"
[1] "42/488 antunez_2013_tmms24"
[1] "43/488 goldberg_2018_prs_movie_preferences"
[1] "44/488 antunez_2013_rmeq"
[1] "45/488 goldberg_2018_pas_adjectives"
[1] "46/488 arabaci_2025_burnout"
[1] "47/488 kermen_2022_self_regulation"
[1] "48/488 eldor_2022_violent_extremism"
[1] "49/488 szabo_2025_work_addiction"
[1] "50/488 sokolovskii_2021_tfeq"
[1] "51/488 turpochaparro_2026_social_network_addiction"
[1] "52/488 tang_2024_self_construal"
[1] "53/488 chatzoudes_2021_trust"
[1] "54/488 tang_2024_caregiver_child_regulation"
[1] "55/488 goldberg_2018_jpir"
[1] "56/488 tang_2024_panas_negative"
[1] "57/488 kotsou_2016_panas"
[1] "58/488 chen_2026_social_anxiety"
[1] "59/488 goldberg_2018_hpq_h"
[1] "60/488 eldor_2022_symbolic_threat"
[1] "61/488 apaza_2026_meim_r"
[1] "62/488 turpochaparro_2026_self_esteem"
[1] "63/488 cavojova_2017_cfc"
[1] "64/488 sekowski_2025_mast"
[1] "65/488 peng_2024_language_boredom"
[1] "66/488 choi_2026_cmsce_2020_2"
[1] "67/488 nguyen_2026_isi"
[1] "68/488 szabo_2025_family_conflict"
[1] "69/488 kermen_2022_attention"
[1] "70/488 choi_2026_cmsce_2021_1"
[1] "71/488 chatzoudes_2021_job_satisfaction"
[1] "72/488 personalitychange_kramer_2025_rses"
[1] "73/488 alan_2018_teacher_growth_mindset"
[1] "74/488 balparda_2021_kepaq_functional"
[1] "75/488 dalichaouche_2026_covid_practices"
[1] "76/488 emiral_2025_aips"
[1] "77/488 goldberg_2018_ppq_music"
[1] "78/488 goldberg_2018_spa_ipip"
[1] "79/488 eldor_2022_relative_deprivation"
[1] "80/488 demirbag_2025_goal_orientations"
[1] "81/488 tang_2024_academic_satisfaction"
[1] "82/488 nguyen_2026_pic"
[1] "83/488 cosenza_2015_cfc"
[1] "84/488 eldor_2022_collective_anger"
[1] "85/488 goldberg_2018_prs_reading_preferences"
[1] "86/488 huang_2023_medseq"
[1] "87/488 nguyen_2026_gad7"
[1] "88/488 eyrenci_2025_mental_health_literacy"
[1] "89/488 kotsou_2016_scs"
[1] "90/488 doherty_2023_burnout"
[1] "91/488 li_2026_team_cohesion"
[1] "92/488 goldberg_2018_prs_peo"
[1] "93/488 goldberg_2018_sdv_ipip_temperament"
[1] "94/488 goldberg_2018_eps_adjectives"
[1] "95/488 chen_2026_self_control"
[1] "96/488 kermen_2022_anxiety"
[1] "97/488 goldberg_2018_sdv_adjectives"
[1] "98/488 teacherjudgements_lohmann_2026_conscientiousness"
[1] "99/488 turpochaparro_2026_family_communication"
[1] "100/488 itemrandom_buchanan_2018_PIL"
[1] "101/488 cao_2026_cdss_intention_to_use"
[1] "102/488 matosaslopez_2022_bars_teaching"
[1] "103/488 goldberg_2018_sdv_desirability"
[1] "104/488 chatzoudes_2021_ethical_leadership"
[1] "105/488 goldberg_2018_spa_cultural_familiarity"
[1] "106/488 personalitychange_kramer_2025_mls"
[1] "107/488 tang_2024_outcome_expectations"
[1] "108/488 personalitychange_kramer_2025_swls"
[1] "109/488 onah_2021_covid_knowledge"
[1] "110/488 kumlander_2018_scs"
[1] "111/488 sumner_2022_spq"
[1] "112/488 alqerem_2024_diabetic_health_literacy"
[1] "113/488 milson_2026_social_media_use"
[1] "114/488 goldberg_2018_eps_spirituality"
[1] "115/488 baquerotomas_2026_neoffi"
[1] "116/488 eldor_2022_school_resilience"
[1] "117/488 sumner_2022_asi"
[1] "118/488 choi_2026_cmsce_2020_1"
[1] "119/488 goldberg_2018_prs_bas_bis"
[1] "120/488 teacherjudgements_lohmann_2026_motivation"
[1] "121/488 tang_2024_environmental_support"
[1] "122/488 floreskanter_2021_cerq"
[1] "123/488 goldberg_2018_spa_medical_history"
[1] "124/488 goldberg_2018_bri_food"
[1] "125/488 zhang_2026_ecosystem_services"
[1] "126/488 xu_2023_pca"
[1] "127/488 szabo_2025_pss4"
[1] "128/488 choi_2026_cmsce_2019_1"
[1] "129/488 atik_2026_psych_resilience"
[1] "130/488 goldberg_2018_prs_pey"
[1] "131/488 mboya_2020_gds15"
[1] "132/488 wu_2024_achievement_emotions"
[1] "133/488 goldberg_2018_sdv_schwartz_values"
[1] "134/488 tang_2024_caregiver_child_communication"
[1] "135/488 wicherts_2023_5pft"
[1] "136/488 wang_2025_cognitive_fusion"
[1] "137/488 trang_2023_vocabulary_strategies"
[1] "138/488 goldberg_2018_bri_feel"
[1] "139/488 goldberg_2018_sdv_influ"
[1] "140/488 goldberg_2018_ppq_beliefs"
[1] "141/488 lee_2020_alcohol_use"
[1] "142/488 milson_2026_body_satisfaction"
[1] "143/488 woodall_2020_bfi44"
[1] "144/488 altman_2020_capq"
[1] "145/488 goldberg_2018_eps_s11"
[1] "146/488 kalczajanosi_2021_covid_risk"
[1] "147/488 baquerotomas_2026_pil"
[1] "148/488 alan_2018_teacher_warmth"
[1] "149/488 nguyen_2026_barthel"
[1] "150/488 alexandrowicz_2018_cesd"
[1] "151/488 eldor_2022_political_resilience"
[1] "152/488 onah_2021_covid_info_sources"
[1] "153/488 rodriguezsantero_2024_sats36"
[1] "154/488 wu_2025_drone_delivery"
[1] "155/488 hochsteiner_2026_sustainability_relevance"
[1] "156/488 baquerotomas_2026_ders"
[1] "157/488 kalczajanosi_2021_covid_fear"
[1] "158/488 lee_2020_empathy"
[1] "159/488 goldberg_2018_spa_bfi_forced_choice"
[1] "160/488 itemrandom_buchanan_2018_LPQ"
[1] "161/488 manolika_2021_dirty_dozen"
[1] "162/488 personalitychange_kramer_2025_sccs"
[1] "163/488 xu_2023_hi"
[1] "164/488 szabo_2025_work_conflict"
[1] "165/488 kotsou_2016_plc"
[1] "166/488 alloubani_2021_stai_trait"
[1] "167/488 milson_2026_self_esteem"
[1] "168/488 zhang_2026_tourist_wellbeing"
[1] "169/488 li_2026_sport_commitment"
[1] "170/488 doherty_2023_bfi10"
[1] "171/488 personalitychange_kramer_2025_bfi"
[1] "172/488 eldor_2022_violent_intentions"
[1] "173/488 rosyid_2025_academic_citizenship"
[1] "174/488 arabaci_2025_task_diversity"
[1] "175/488 chatzoudes_2021_emotional_exhaustion"
[1] "176/488 arabaci_2025_skill_diversity"
[1] "177/488 xu_2023_oic"
[1] "178/488 koksal_2023_work_depression"
[1] "179/488 atik_2026_climate_anxiety"
[1] "180/488 risticdedic_2025_dhq_expectation"
[1] "181/488 choi_2026_cmsce_2019_2"
[1] "182/488 sumner_2022_olife"
[1] "183/488 goldberg_2018_spa_spey"
[1] "184/488 tang_2024_swls"
[1] "185/488 goldberg_2018_ppq_via_strengths"
[1] "186/488 goldberg_2018_prs_gray_wilson"
[1] "187/488 baquerotomas_2026_phq9"
[1] "188/488 nurjanah_2019_hls47"
[1] "189/488 goldberg_2018_pda360"
[1] "190/488 zhang_2026_ecological_values"
[1] "191/488 szabo_2025_molbi"
[1] "192/488 teacherjudgements_lohmann_2026_selfconcept"
[1] "193/488 goldberg_2018_dop_ab5c_vignettes"
[1] "194/488 goldberg_2018_bri_curio"
[1] "195/488 zhang_2026_healthy_attitude"
[1] "196/488 chatzoudes_2021_turnover_intention"
[1] "197/488 manolika_2021_movie_preferences"
[1] "198/488 teacherjudgements_lohmann_2026_essayratings"
[1] "199/488 goldberg_2018_spa_speo"
[1] "200/488 aiquipa_2026_dgs"
[1] "201/488 kotsou_2016_happiness"
[1] "202/488 dalichaouche_2026_covid_knowledge"
[1] "203/488 lee_2020_burnout"
[1] "204/488 goldberg_2018_tci"
[1] "205/488 baquerotomas_2026_gad7"
[1] "206/488 goldberg_2018_sdv_happy"
[1] "207/488 matosaslopez_2024_questionnaire_quality"
[1] "208/488 alan_2018_teacher_gender_attitudes"
[1] "209/488 lee_2020_social_support"
[1] "210/488 eldor_2022_realistic_threat"
[1] "211/488 goldberg_2018_eps_life_events"
[1] "212/488 mthimkhulu_2023_pirls_reading"
[1] "213/488 kotsou_2016_life_satisfaction"
[1] "214/488 goldberg_2018_pda525"
[1] "215/488 balparda_2021_korq_activity_limitation"
[1] "216/488 goldberg_2018_prs_hexaco"
[1] "217/488 goldberg_2018_sdv_force"
[1] "218/488 sumner_2022_lshs"
[1] "219/488 alkhaldi_2023_whoqol_autism"
[1] "220/488 bialowolski_2024_financial_literacy"
[1] "221/488 lee_2020_sleep_quality"
[1] "222/488 cao_2026_cdss_professional_knowledge"
[1] "223/488 goldberg_2018_spa_beliefs_about_intelligence"
[1] "224/488 kermen_2022_self_efficacy"
[1] "225/488 goldberg_2018_spa_changeability"
[1] "226/488 baquerotomas_2026_spsi"
[1] "227/488 goldberg_2018_ciss"
[1] "228/488 goldberg_2018_sdv_views"
[1] "229/488 wang_2025_growth_mindset"
[1] "230/488 tang_2024_goal_progress"
[1] "231/488 tang_2024_self_efficacy"
[1] "232/488 tang_2024_panas_positive"
[1] "233/488 kumlander_2018_bdi"
[1] "234/488 ysladomendez_2023_mbi"
[1] "235/488 chatzoudes_2021_service_delivery"
[1] "236/488 tang_2024_caregiver_child_conflict"
[1] "237/488 alan_2018_teacher_modern_teaching"
[1] "238/488 benchelbi_2021_mtq48"
[1] "239/488 koksal_2023_life_satisfaction"
[1] "240/488 szabo_2025_bwas"
[1] "241/488 personalitychange_kramer_2025_sa"
[1] "242/488 goldberg_2018_prs_ipip"
[1] "243/488 alan_2018_student_gender_attitudes"
[1] "244/488 goldberg_2018_ppq_dream"
[1] "245/488 hahn_2025_sqc"
[1] "246/488 goldberg_2018_eps_ipip"
[1] "247/488 szabo_2025_passion"
[1] "248/488 nguyen_2026_mspss"
[1] "249/488 apaza_2026_self_esteem"
[1] "250/488 alloubani_2021_stai_state"
[1] "251/488 aditama_2024_strs"
[1] "252/488 cao_2026_cdss_cognitive_load"
[1] "253/488 okoro_2022_interest_inventory"
[1] "254/488 ilic_2019_whoqol_bref"
[1] "255/488 perales_2026_digital_financial_literacy"
[1] "256/488 goldberg_2018_bri_ofood"
[1] "257/488 goldberg_2018_eps_cesd"
[1] "258/488 goldberg_2018_cpi"
[1] "259/488 rosyid_2025_ethical_leadership"
[1] "260/488 szabo_2025_wellbeing"
[1] "261/488 goldberg_2018_sdv_likelihood"
[1] "262/488 sekowski_2025_pies"
[1] "263/488 goldberg_2018_spa_skill_proficiency"
[1] "264/488 chen_2026_mobile_phone_addiction"
[1] "265/488 goldberg_2018_dop_avocational_interests"
[1] "266/488 huang_2023_utaut_mobile_shopping"
[1] "267/488 prihastiwi_2026_adcap"
[1] "268/488 cao_2026_cdss_perceived_autonomy"
[1] "269/488 demirbag_2025_emotions"
[1] "270/488 trang_2023_vocabulary_beliefs"
[1] "271/488 perales_2026_financial_resilience"
[1] "272/488 doherty_2023_dass21"
[1] "273/488 wang_2025_impulse_control"
[1] "274/488 peng_2024_language_enjoyment"
[1] "275/488 goldberg_2018_pf16_p"
[1] "276/488 tang_2024_caregiver_child_attachment"
[1] "277/488 livacicrojas_2023_lvq"
[1] "278/488 goldberg_2018_hpi"
[1] "279/488 goldberg_2018_pas_ipip_scales"
[1] "280/488 peng_2024_grit"
[1] "281/488 kalczajanosi_2021_vaccine_skepticism"
[1] "282/488 redline_2026_prosbq"
[1] "283/488 senyurt_2023_burnout"
[1] "284/488 khoa_2023_assurance"
[1] "285/488 soderberg_2024_general_selfefficacy"
[1] "286/488 estevez_2021_actitu"
[1] "287/488 avci_2024_ikyoz_yeterlk"
[1] "288/488 hoai_2026_social_presence"
[1] "289/488 ribeiro_2019_academic_motivation"
[1] "290/488 figalova_2021_stai_trait"
[1] "291/488 avci_2024_sansdaykontrol_odak"
[1] "292/488 avci_2024_bskdaykontrol_odak"
[1] "293/488 baekgaard_2023_stress"
[1] "294/488 avci_2024_issahp_gir_yonel"
[1] "295/488 celik_2026_academic_motivation"
[1] "296/488 chen_2024_ec"
[1] "297/488 baekgaard_2023_autonomy_loss"
[1] "298/488 torok_2025_data_security"
[1] "299/488 avci_2024_statu_gir_yonel"
[1] "300/488 nguyen_2026_sdt_relatedness"
[1] "301/488 skarzauskiene_2026_fake_news_frequency"
[1] "302/488 avci_2024_belirsiz_kac"
[1] "303/488 lozano_2018_getting_along"
[1] "304/488 chen_2024_cc"
[1] "305/488 khulwa_2025_engagement"
[1] "306/488 petley_2025_flanker_study2_auditory"
[1] "307/488 torok_2025_discourse_responsibility"
[1] "308/488 chen_2024_je"
[1] "309/488 torok_2025_news_source_trust"
[1] "310/488 osorio_2023_dos"
[1] "311/488 ye_2025_tq"
[1] "312/488 nguyen_2026_sdt_mental_health"
[1] "313/488 skarzauskiene_2026_fake_news_agree"
[1] "314/488 soderberg_2024_esm_morning"
[1] "315/488 nguyen_2026_misfit_technostress"
[1] "316/488 chen_2026_bi"
[1] "317/488 yao_2020_ius"
[1] "318/488 darkfactorfrench_pischel_2026_callousness"
[1] "319/488 torok_2025_news_consumption"
[1] "320/488 lozano_2018_cognition"
[1] "321/488 khoa_2023_knowledge_use"
[1] "322/488 ye_2025_mm"
[1] "323/488 chen_2024_ts"
[1] "324/488 yao_2020_epq"
[1] "325/488 chen_2026_ie"
[1] "326/488 pham_2026_ktsth"
[1] "327/488 ventura_2025_quadrant_d"
[1] "328/488 khulwa_2025_motivation_3"
[1] "329/488 torok_2025_legality_beliefs"
[1] "330/488 estevez_2021_inter"
[1] "331/488 celik_2026_distance_ed_attitudes_26"
[1] "332/488 nguyen_2026_sdt_academic_motivation"
[1] "333/488 khulwa_2025_motivation_1"
[1] "334/488 fraijo_2022_mslq"
[1] "335/488 nguyen_2026_autonomy_student_choice"
[1] "336/488 avci_2024_guc_gir_yonel"
[1] "337/488 figalova_2021_pss"
[1] "338/488 nguyen_2026_misfit_academic_performance"
[1] "339/488 skarzauskiene_2026_social_trust"
[1] "340/488 darkfactorfrench_pischel_2026_normlessness"
[1] "341/488 nguyen_2026_autonomy_academic_pressure"
[1] "342/488 baekgaard_2023_learning"
[1] "343/488 nguyen_2026_misfit_learning_satisfaction"
[1] "344/488 nguyen_2026_sdt_autonomy"
[1] "345/488 pham_2026_ktslh"
[1] "346/488 avci_2024_oz_norm"
[1] "347/488 figalova_2021_bdi"
[1] "348/488 chen_2024_kc"
[1] "349/488 pham_2026_gp"
[1] "350/488 nguyen_2026_autonomy_family_factors"
[1] "351/488 nguyen_2026_autonomy_school_autonomy_support"
[1] "352/488 chen_2026_ai"
[1] "353/488 chen_2026_ch"
[1] "354/488 skarzauskiene_2026_information_sources"
[1] "355/488 darkfactorfrench_pischel_2026_exploitative"
[1] "356/488 lozano_2018_self_care"
[1] "357/488 hernandezmantilla_2024_cfni"
[1] "358/488 avci_2024_kimlik_miss"
[1] "359/488 lestari_2026_inhibitory_control"
[1] "360/488 pham_2026_bsth"
[1] "361/488 avci_2024_ickontrol_odak"
[1] "362/488 celik_2026_distance_ed_attitudes_16"
[1] "363/488 nguyen_2026_sdt_perceived_performance"
[1] "364/488 darkfactorfrench_pischel_2026_d70"
[1] "365/488 hoai_2026_instructional_design_quality"
[1] "366/488 chen_2024_ds"
[1] "367/488 skarzauskiene_2026_science_engagement"
[1] "368/488 petley_2025_flanker_study2_visual"
[1] "369/488 soderberg_2024_peer_support"
[1] "370/488 yao_2020_bai"
[1] "371/488 avci_2024_zorbasetoz_yeterlk"
[1] "372/488 torok_2025_manipulation_fear"
[1] "373/488 avci_2024_toplmfayd_gir_yonel"
[1] "374/488 avci_2024_risk_gir_yonel"
[1] "375/488 khulwa_2025_motivation_4"
[1] "376/488 ye_2025_xc"
[1] "377/488 chen_2026_ee"
[1] "378/488 ventura_2025_quadrant_b"
[1] "379/488 lozano_2018_mobility"
[1] "380/488 lozano_2018_life_activities"
[1] "381/488 darkfactorfrench_pischel_2026_dictator_game"
[1] "382/488 ventura_2025_quadrant_a"
[1] "383/488 nguyen_2026_misfit_learning_motivation"
[1] "384/488 lapietra_2026_volcanic_risk_perception"
[1] "385/488 chen_2024_cr"
[1] "386/488 ramadan_2026_ai_awareness"
[1] "387/488 soderberg_2024_teacher_support"
[1] "388/488 hernandezmantilla_2024_cmni"
[1] "389/488 nguyen_2026_autonomy_student_voice"
[1] "390/488 avci_2024_yatrmciliskoz_yeterlk"
[1] "391/488 avci_2024_sureklgel_gir_yonel"
[1] "392/488 hoai_2026_learning_experience"
[1] "393/488 darkfactorfrench_pischel_2026_crime_analog"
[1] "394/488 ramadan_2026_attitudes"
[1] "395/488 ramadan_2026_perceived_competence"
[1] "396/488 nguyen_2026_sdt_competence"
[1] "397/488 chen_2024_sc"
[1] "398/488 yao_2020_pswq"
[1] "399/488 pham_2026_bsgt"
[1] "400/488 ye_2025_jl"
[1] "401/488 skarzauskiene_2026_science_behaviors"
[1] "402/488 ventura_2025_quadrant_c"
[1] "403/488 petley_2025_flanker_study1_girlman"
[1] "404/488 figalova_2021_stai_state"
[1] "405/488 nguyen_2026_autonomy_academic_motivation"
[1] "406/488 estevez_2021_feepad"
[1] "407/488 soderberg_2024_esm_lecture"
[1] "408/488 avci_2024_aktif_gir_yonel"
[1] "409/488 pham_2026_thbt"
[1] "410/488 avci_2024_basrmaarzu_gir_yonel"
[1] "411/488 darkfactorfrench_pischel_2026_worldview_cj"
[1] "412/488 khoa_2023_teaching_materials"
[1] "413/488 estevez_2021_feepr"
[1] "414/488 chen_2026_in"
[1] "415/488 darkfactorfrench_pischel_2026_civic_behavior"
[1] "416/488 khoa_2023_knowledge_acquisition"
[1] "417/488 chen_2024_cotah"
[1] "418/488 chen_2024_cg"
[1] "419/488 baekgaard_2023_mastery"
[1] "420/488 chen_2024_uf"
[1] "421/488 baekgaard_2023_stigma"
[1] "422/488 pham_2026_bsyn"
[1] "423/488 darkfactorfrench_pischel_2026_sdo7s"
[1] "424/488 chen_2026_rf"
[1] "425/488 nguyen_2026_autonomy_student_ownership"
[1] "426/488 erguvan_2022_questionnaire"
[1] "427/488 chen_2024_kd"
[1] "428/488 yao_2020_bdi"
[1] "429/488 nguyen_2026_misfit_learning_misfit"
[1] "430/488 soderberg_2024_esm_affect"
[1] "431/488 khulwa_2025_algorithm_awareness"
[1] "432/488 hoai_2026_student_engagement"
[1] "433/488 lozano_2018_participation"
[1] "434/488 torok_2025_internet_use_frequency"
[1] "435/488 torok_2025_news_source_frequency"
[1] "436/488 saha_2026_cesd"
[1] "437/488 kay_2025_antonyms"
[1] "438/488 celik_2026_bfi"
[1] "439/488 khoa_2023_knowledge_dissemination"
[1] "440/488 pham_2026_ktscx"
[1] "441/488 estevez_2021_homework_engagement"
[1] "442/488 lestari_2026_cognitive_flexibility"
[1] "443/488 celik_2026_bpns"
[1] "444/488 avci_2024_bagmsz_gir_yonel"
[1] "445/488 avci_2024_kimlik_dar"
[1] "446/488 skarzauskiene_2026_big_five"
[1] "447/488 petley_2025_flanker_study1_manwoman"
[1] "448/488 chen_2026_ir"
[1] "449/488 avci_2024_kazanc_gir_yonel"
[1] "450/488 estevez_2021_gest"
[1] "451/488 petley_2025_flanker_study1_childwoman"
[1] "452/488 avci_2024_gecmis_gir_yonel"
[1] "453/488 hoai_2026_teaching_presence"
[1] "454/488 darkfactorfrench_pischel_2026_interp_dysfx"
[1] "455/488 chen_2024_ae"
[1] "456/488 baekgaard_2023_compliance"
[1] "457/488 chen_2024_spe"
[1] "458/488 yao_2020_gad"
[1] "459/488 avci_2024_yencevolsoz_yeterlk"
[1] "460/488 lestari_2026_working_memory"
[1] "461/488 avci_2024_urunpazgeloz_yeterlk"
[1] "462/488 silva_2022_crsy"
[1] "463/488 skarzauskiene_2026_attitudes_science"
[1] "464/488 skarzauskiene_2026_trust_science"
[1] "465/488 chen_2026_pr"
[1] "466/488 torok_2025_data_disclosure"
[1] "467/488 avci_2024_tmlamacoz_yeterlk"
[1] "468/488 avci_2024_zorunluluk_gir_yonel"
[1] "469/488 chen_2024_smu"
[1] "470/488 hoai_2026_academic_achievement"
[1] "471/488 soderberg_2024_academic_selfefficacy"
[1] "472/488 ramadan_2026_applied_practice"
[1] "473/488 clipa_2025_mslq"
[1] "474/488 celik_2026_tipi"
[1] "475/488 hoai_2026_cognitive_presence"
[1] "476/488 lee_2019_academic_motivation_scale"
[1] "477/488 dai_2025_music_motivation"
[1] "478/488 avci_2024_risk_algi"
[1] "479/488 estevez_2021_motiv"
[1] "480/488 chen_2026_il"
[1] "481/488 soderberg_2024_family_support"
[1] "482/488 khulwa_2025_motivation_2"
[1] "483/488 avci_2024_kimlik_com"
[1] "484/488 estevez_2021_math_attitudes"
[1] "485/488 torok_2025_social_media_effects"
[1] "486/488 torok_2025_facebook_uses"
[1] "487/488 chen_2024_tot"
[1] "488/488 torok_2025_ai_acceptance"
tibble [4,134 × 9] (S3: tbl_df/tbl/data.frame)
 $ table                    : chr [1:4134] "psiq_woelk2022" "estcrm_epia" "kfcovid_Li2020" "CPDMMC_Kunnari_2020_PDP" ...
 $ n_responses              : num [1:4134] 25725 5165 1320 18774 66726 ...
 $ n_categories             : int [1:4134] 11 111 2 2 2 2 2 2 2 2 ...
 $ n_participants           : num [1:4134] 735 1033 110 1043 337 ...
 $ n_items                  : num [1:4134] 35 5 12 18 198 20 20 22 11 24 ...
 $ responses_per_participant: num [1:4134] 35 5 12 18 198 20 20 22 22 24 ...
 $ responses_per_item       : num [1:4134] 735 1033 110 1043 337 ...
 $ density                  : num [1:4134] 1 1 1 1 1 1 1 1 2 1 ...
 $ variables                : chr [1:4134] "id| study| item| resp" "resp| item| id" "id| item| resp" "id| item| resp" ...
[1] 4134
refresh pass: 200 of 3646 existing table(s) this run (refresh.per.run=200)
  refresh 1/200 16_personalityfactors
Warning in getvars(tab) : NAs introduced by coercion
  refresh 2/200 2024_online_addiction_bsmas
  refresh 3/200 2024_online_addiction_igds
  refresh 4/200 2024_online_addiction_sabas
  refresh 5/200 360emergencymed_azami_2024
  refresh 6/200 4thgrade_math_sirt
  refresh 7/200 5personalityfactors
Warning in getvars(tab) : NAs introduced by coercion
  refresh 8/200 aa1_Silvia_2023
  refresh 9/200 aappss_malpas_2019_scl
Warning in getvars(tab) : NAs introduced by coercion
  refresh 10/200 abdullah_2024_blqol
  refresh 11/200 abdullah_2024_bsq_sev24
  refresh 12/200 abdullah_2024_bsq_sevgen
  refresh 13/200 abdullah_2024_hbbloat_attitude
  refresh 14/200 abdullah_2024_hbbloat_pbc
  refresh 15/200 abdullah_2024_hpbbloat_awareness
  refresh 16/200 abdullah_2024_hpbbloat_diet
  refresh 17/200 abdullah_2024_hpbbloat_physact
  refresh 18/200 abdullah_2024_hpbbloat_stress
  refresh 19/200 abdullah_2024_hpbbloat_treat
  refresh 20/200 abdullah_2024_ssbloat
  refresh 21/200 abortion
  refresh 22/200 abouhashish_2025_chatgpt_attitudes
  refresh 23/200 abramson_2026_israel_attachment
  refresh 24/200 abramson_2026_israel_policy
  refresh 25/200 abramson_2026_jewish_identity
  refresh 26/200 abramson_2026_mobilization
  refresh 27/200 abukhalaf_2025_disaster_prep
  refresh 28/200 abukhalaf_2025_housing_risk
  refresh 29/200 acl_mokken
  refresh 30/200 act_kay_2025
Warning in getvars(tab) : NAs introduced by coercion
  refresh 31/200 acunamora_2018_gypes
  refresh 32/200 ada_boredom_bieleke2022
  refresh 33/200 addy_2021_sdq_ghana
  refresh 34/200 Adherence_Zissette_2018_SDB
  refresh 35/200 aestheticfluency_cotter2023
Warning in getvars(tab) : NAs introduced by coercion
  refresh 36/200 afaya_2020_complications_knowledge
  refresh 37/200 afaya_2020_diet_knowledge
  refresh 38/200 afaya_2020_exercise_knowledge
  refresh 39/200 afaya_2020_footcare_knowledge
  refresh 40/200 afaya_2020_general_knowledge
  refresh 41/200 afaya_2020_medication_knowledge
  refresh 42/200 afaya_2020_monitoring_knowledge
  refresh 43/200 afps_vangsness_2019
  refresh 44/200 agarwal_2023_dreem
  refresh 45/200 agn_kay_2025
  refresh 46/200 agogue_2020_self_perceived_creativity
  refresh 47/200 aguirre_camacho_2021_champion
  refresh 48/200 aguirre_camacho_2021_shai
  refresh 49/200 ahmed_2019_food_consumption
  refresh 50/200 ahmed_2019_wellbeing
  refresh 51/200 ai_fear_dong_2026_ai
  refresh 52/200 ai_fear_dong_2026_incentive
  refresh 53/200 ai_fear_dong_2026_other_fear
  refresh 54/200 ai_fear_dong_2026_own_fear
  refresh 55/200 ai_fear_dong_2026_requirement
  refresh 56/200 aip_vangsness_2019
  refresh 57/200 ajaykumar_2023_experience
  refresh 58/200 ajaykumar_2023_nasa_tlx
  refresh 59/200 ajlan_2025_stemcell_knowledge
  refresh 60/200 akrawi_2025_sclc
  refresh 61/200 alasmari_2025_ai_trust_compare
  refresh 62/200 alasmari_2025_ai_trust_confidence
  refresh 63/200 albeitawi_2025_preceptor_needs
  refresh 64/200 alcoholhealthwarninglabel_brennan_2022_awareness_harms_followup
  refresh 65/200 alcoholhealthwarninglabel_brennan_2022_emotional_arousal_followup
  refresh 66/200 alcoholhealthwarninglabel_brennan_2022_intentions_postexposure
  refresh 67/200 alcoholresearch_sumscore
  refresh 68/200 alcoholstroop_jones2024
  refresh 69/200 alexander_2017_dsi
  refresh 70/200 alfort_2023_finger_fx_prom
  refresh 71/200 algner2022_cse
  refresh 72/200 algner2022_mimi_pool
  refresh 73/200 algner2022_mimi16
  refresh 74/200 algner2022_oss
  refresh 75/200 algner2022_psgbi
  refresh 76/200 algner2022_sia
  refresh 77/200 algner2022_tis
  refresh 78/200 algner2022_uwes
  refresh 79/200 algner2022_wis
  refresh 80/200 ali_2021_gad7
  refresh 81/200 ali_2021_iesr
  refresh 82/200 ali_2021_isi
  refresh 83/200 ali_2021_phq9
  refresh 84/200 ali_2021_spfi
  refresh 85/200 alkouri_2025_coping
  refresh 86/200 alkouri_2025_icu_stressors
  refresh 87/200 allen_2025_bis
  refresh 88/200 allen_2025_delaydiscount
  refresh 89/200 allen_2025_upps
  refresh 90/200 almuqbil_2022_epds
  refresh 91/200 ALSECYPIAMH_WU_2022_CPS
  refresh 92/200 ALSECYPIAMH_WU_2022_Empathy
  refresh 93/200 ALSECYPIAMH_WU_2022_MIL
  refresh 94/200 ALSECYPIAMH_WU_2022_NEI
  refresh 95/200 ALSECYPIAMH_WU_2022_PEI
  refresh 96/200 ALSECYPIAMH_WU_2022_PHQ
  refresh 97/200 ALSECYPIAMH_WU_2022_PIL
  refresh 98/200 ALSECYPIAMH_WU_2022_SDQ
  refresh 99/200 ALSECYPIAMH_WU_2022_SWEMWBS
  refresh 100/200 ALSECYPIAMH_WU_2022_SWLS
  refresh 101/200 alsuhibani_2022_consp_s1
  refresh 102/200 alsuhibani_2022_ecrs_s3
  refresh 103/200 alsuhibani_2022_gcbs
  refresh 104/200 alsuhibani_2022_gcbs_extra_s2
  refresh 105/200 alsuhibani_2022_loc
  refresh 106/200 alsuhibani_2022_npi_s3
  refresh 107/200 alsuhibani_2022_pads_s1
  refresh 108/200 alsuhibani_2022_pads_s2
  refresh 109/200 alsuhibani_2022_paranoia_s3
  refresh 110/200 alsuhibani_2022_sers
  refresh 111/200 alsyouf_2024_agreeableness
  refresh 112/200 alsyouf_2024_conscientiousness
  refresh 113/200 alsyouf_2024_continuance_intention
  refresh 114/200 alsyouf_2024_effort_expectancy
  refresh 115/200 alsyouf_2024_end_user_support
  refresh 116/200 alsyouf_2024_extraversion
  refresh 117/200 alsyouf_2024_facilitating_conditions
  refresh 118/200 alsyouf_2024_management_support
  refresh 119/200 alsyouf_2024_neuroticism
  refresh 120/200 alsyouf_2024_openness
  refresh 121/200 alsyouf_2024_performance_expectancy
  refresh 122/200 alsyouf_2024_social_influence
  refresh 123/200 altahla_2024_swls
  refresh 124/200 altahla_2024_whoqol
  refresh 125/200 alves_2017_hamd17
  refresh 126/200 amarilla_2020_barthel
  refresh 127/200 amarilla_2020_eq5d
  refresh 128/200 amarilla_2020_lawton_brody
  refresh 129/200 amarilla_2020_sf12
  refresh 130/200 amatus_cipora_2024_amas
  refresh 131/200 amatus_cipora_2024_arithmetic
  refresh 132/200 amatus_cipora_2024_bfi_n
  refresh 133/200 amatus_cipora_2024_fsmas_se
  refresh 134/200 amatus_cipora_2024_gad
  refresh 135/200 amatus_cipora_2024_pisa_me
  refresh 136/200 amatus_cipora_2024_sdq_l
  refresh 137/200 amatus_cipora_2024_sdq_m
  refresh 138/200 amatus_cipora_2024_stai
  refresh 139/200 amatus_cipora_2024_tai
  refresh 140/200 american_multiracial_face
  refresh 141/200 AMI_CV_Hewitt2024
Warning in getvars(tab) : NAs introduced by coercion
  refresh 142/200 amorim_2025_climej_climej
  refresh 143/200 amorim_2025_climej_desenhonotrabalho
  refresh 144/200 amorim_2025_climej_florescimentonotrabalho
  refresh 145/200 amorim_2025_climej_suporteorganizacional
  refresh 146/200 an_2020_efl_self_regulated
  refresh 147/200 andrich_mudfold
  refresh 148/200 anh_2026_ai_adoption
  refresh 149/200 anh_2026_digitaltrust
  refresh 150/200 anh_2026_finbehavior
  refresh 151/200 anh_2026_finliteracy
  refresh 152/200 anh_2026_finsocialization
  refresh 153/200 anh_2026_finwellbeing
  refresh 154/200 anjum_2022_gad7
  refresh 155/200 antes_2020_pdm
  refresh 156/200 anunciacao_2024_intelligence_gmi
  refresh 157/200 anunciacao_2025_emotional_management
  refresh 158/200 anunciacao_2025_emotional_relationships
  refresh 159/200 anunciacao_2025_emotional_responsibility
  refresh 160/200 anunciacao_2025_emotional_self-awareness
  refresh 161/200 anunciacao_2025_emotional_social-awareness
  refresh 162/200 anunciacao_2025_personality_achievement
Warning in getvars(tab) : NAs introduced by coercion
  refresh 163/200 anunciacao_2025_personality_affiliation
Warning in getvars(tab) : NAs introduced by coercion
  refresh 164/200 anunciacao_2025_personality_aggression
Warning in getvars(tab) : NAs introduced by coercion
  refresh 165/200 anunciacao_2025_personality_autonomy
Warning in getvars(tab) : NAs introduced by coercion
  refresh 166/200 anunciacao_2025_personality_change
Warning in getvars(tab) : NAs introduced by coercion
  refresh 167/200 anunciacao_2025_personality_deference
Warning in getvars(tab) : NAs introduced by coercion
  refresh 168/200 anunciacao_2025_personality_dominance
Warning in getvars(tab) : NAs introduced by coercion
  refresh 169/200 anunciacao_2025_personality_exhibition
Warning in getvars(tab) : NAs introduced by coercion
  refresh 170/200 anunciacao_2025_personality_intraception
Warning in getvars(tab) : NAs introduced by coercion
  refresh 171/200 anunciacao_2025_personality_nurturance
Warning in getvars(tab) : NAs introduced by coercion
  refresh 172/200 anunciacao_2025_personality_order
Warning in getvars(tab) : NAs introduced by coercion
  refresh 173/200 anunciacao_2025_personality_persistence
Warning in getvars(tab) : NAs introduced by coercion
  refresh 174/200 anunciacao_2025_personality_succorance
Warning in getvars(tab) : NAs introduced by coercion
  refresh 175/200 anxiety_gastro_symptoms
  refresh 176/200 anxiety_lordif
  refresh 177/200 AOMT_BR_SF_EDPANAB_Geiger_2021_AOT
  refresh 178/200 AOMT_BR_SF_EDPANAB_Geiger_2021_BRS
  refresh 179/200 AOMT_BR_SF_EDPANAB_Geiger_2021_RF
  refresh 180/200 APFCompact_Ptacek_2024_AAQ_II
  refresh 181/200 APFCompact_Ptacek_2024_SWLS
  refresh 182/200 aps_vangsness_2019
  refresh 183/200 arnulf_2022_conspiracy_thinking
  refresh 184/200 arnulf_2022_general_knowledge
  refresh 185/200 arora2025_blueq_asynchronous
  refresh 186/200 arora2025_blueq_pedagogical
  refresh 187/200 arora2025_blueq_synchronous
  refresh 188/200 art
  refresh 189/200 artistic_preferences
Warning in getvars(tab) : NAs introduced by coercion
  refresh 190/200 arzamoncunill_2023_epq_admin
  refresh 191/200 arzamoncunill_2023_epq_clinical
  refresh 192/200 aslec_insomnia_wang2025
  refresh 193/200 Aspirations_Sonmez_2022
Warning in getvars(tab) : NAs introduced by coercion
  refresh 194/200 assessment_time_fournier_2025_bscs
  refresh 195/200 assessment_time_fournier_2025_gad
  refresh 196/200 assessment_time_fournier_2025_phq
  refresh 197/200 assessment_time_fournier_2025_pmpuq
  refresh 198/200 assessment_time_fournier_2025_upps
  refresh 199/200 atmadjaja_2026_cultural_intelligence
  refresh 200/200 atmadjaja_2026_intention_to_stay
refresh: 5 table(s) had stats that no longer matched metadata.csv
                                                        table                    column
ALSECYPIAMH_WU_2022_SDQ.1             ALSECYPIAMH_WU_2022_SDQ               n_responses
ALSECYPIAMH_WU_2022_SDQ.4             ALSECYPIAMH_WU_2022_SDQ                   n_items
ALSECYPIAMH_WU_2022_SDQ.5             ALSECYPIAMH_WU_2022_SDQ responses_per_participant
alves_2017_hamd17.1                         alves_2017_hamd17               n_responses
alves_2017_hamd17.5                         alves_2017_hamd17 responses_per_participant
alves_2017_hamd17.6                         alves_2017_hamd17        responses_per_item
alves_2017_hamd17.7                         alves_2017_hamd17                   density
amatus_cipora_2024_arithmetic.1 amatus_cipora_2024_arithmetic               n_responses
amatus_cipora_2024_arithmetic.3 amatus_cipora_2024_arithmetic            n_participants
amatus_cipora_2024_arithmetic.5 amatus_cipora_2024_arithmetic responses_per_participant
amatus_cipora_2024_arithmetic.6 amatus_cipora_2024_arithmetic        responses_per_item
amatus_cipora_2024_arithmetic.7 amatus_cipora_2024_arithmetic                   density
american_multiracial_face.1         american_multiracial_face               n_responses
american_multiracial_face.4         american_multiracial_face                   n_items
american_multiracial_face.5         american_multiracial_face responses_per_participant
american_multiracial_face.6         american_multiracial_face        responses_per_item
american_multiracial_face.7         american_multiracial_face                   density
anjum_2022_gad7.1                             anjum_2022_gad7               n_responses
anjum_2022_gad7.4                             anjum_2022_gad7                   n_items
anjum_2022_gad7.5                             anjum_2022_gad7 responses_per_participant
                                 old_value  new_value
ALSECYPIAMH_WU_2022_SDQ.1        47046.000  39205.000
ALSECYPIAMH_WU_2022_SDQ.4            6.000      5.000
ALSECYPIAMH_WU_2022_SDQ.5            6.000      5.000
alves_2017_hamd17.1               4946.000   4937.000
alves_2017_hamd17.5                 16.997     16.966
alves_2017_hamd17.6                290.941    290.412
alves_2017_hamd17.7                  1.000      0.998
amatus_cipora_2024_arithmetic.1  44240.000  16492.000
amatus_cipora_2024_arithmetic.3   1106.000   1102.000
amatus_cipora_2024_arithmetic.5     40.000     14.966
amatus_cipora_2024_arithmetic.6   1106.000    412.300
amatus_cipora_2024_arithmetic.7      1.000      0.374
american_multiracial_face.1     117880.000 124082.000
american_multiracial_face.4       2252.000   2371.000
american_multiracial_face.5        102.952    108.369
american_multiracial_face.6         52.345     52.333
american_multiracial_face.7          0.046      0.046
anjum_2022_gad7.1                13878.000  16191.000
anjum_2022_gad7.4                    6.000      7.000
anjum_2022_gad7.5                    6.000      7.000
[1] 4134   10

-- Stage 01 diff --
-- metadata.csv
   added:   488
   removed: 4
   changed: 50
     + aditama_2024_strs, aiquipa_2026_dgs, alan_2018_student_gender_attitudes, alan_2018_teacher_extrinsic_motivation, alan_2018_teacher_gender_attitudes, alan_2018_teacher_growth_mindset, alan_2018_teacher_modern_teaching, alan_2018_teacher_warmth, alexandrowicz_2018_cesd, alkhaldi_2023_whoqol_autism (+478 more)
     - APFCompact_Ptacek_2024_DASS-21, alomari_2025_student_questionnaire, altahla_2024_whoqol_bref, eammi_grahe_2018_marriage_timing
   LONG-TEXT REVIEW FLAGS: 13 cell(s) -- see metadata.diff.csv
     ! tang_2024_academic_satisfaction / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_caregiver_child_attachment / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_caregiver_child_communication / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_caregiver_child_conflict / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_caregiver_child_regulation / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_environmental_support / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_goal_progress / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_outcome_expectations / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_panas_negative / variables: warn (727 chars) -- longer than expected, spot-check
     ! tang_2024_panas_positive / variables: warn (727 chars) -- longer than expected, spot-check
     ... (+3 more)
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/metadata.diff.csv

== Stage 02: Rscript 02_biblio.R ==

Attaching package: ‘dplyr’

The following objects are masked from ‘package:stats’:

    filter, lag

The following objects are masked from ‘package:base’:

    intersect, setdiff, setequal, union


Attaching package: ‘purrr’

The following object is masked from ‘package:jsonlite’:

    flatten

Warning: One or more parsing issues, call `problems()` on your data frame for details, e.g.:
  dat <- vroom(...)
  problems(dat)
[1] 1
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_meta:bdxt"
[1] "xie_2026_student_questionnaire"
[1] "dss_mouta_2021"
[1] "lee_2020_burnout"
[1] "lee_2020_empathy"
[1] "lee_2020_social_support"
[1] "lee_2020_sleep_quality"
[1] "lee_2020_alcohol_use"
[1] "teacherjudgements_lohmann_2026_conscientiousness"
[1] "teacherjudgements_lohmann_2026_essayratings"
[1] "teacherjudgements_lohmann_2026_motivation"
[1] "teacherjudgements_lohmann_2026_selfconcept"
[1] "alexandrowicz_2018_cesd"
[1] "sumner_2022_ftdss"
[1] "sumner_2022_olife"
[1] "sumner_2022_spq"
[1] "sumner_2022_asi"
[1] "sumner_2022_lshs"
[1] "sumner_2022_ipip_neo"
[1] "altman_2020_capq"
[1] "wang_2025_growth_mindset"
[1] "wang_2025_cognitive_fusion"
[1] "wang_2025_impulse_control"
[1] "wang_2025_automatic_thoughts"
[1] "senyurt_2023_burnout"
[1] "sokolovskii_2021_tfeq"
[1] "doherty_2023_dass21"
[1] "doherty_2023_burnout"
[1] "doherty_2023_bfi10"
[1] "daderman_2023_naqr"
[1] "chen_2026_mobile_phone_addiction"
[1] "chen_2026_self_control"
[1] "chen_2026_social_anxiety"
[1] "eldor_2022_political_resilience"
[1] "eldor_2022_anomie"
[1] "eldor_2022_violent_intentions"
[1] "eldor_2022_relative_deprivation"
[1] "eldor_2022_school_resilience"
[1] "eldor_2022_violent_extremism"
[1] "eldor_2022_symbolic_threat"
[1] "eldor_2022_realistic_threat"
[1] "eldor_2022_collective_anger"
[1] "milson_2026_self_esteem"
[1] "milson_2026_social_media_use"
[1] "milson_2026_body_satisfaction"
[1] "kermen_2022_self_efficacy"
[1] "kermen_2022_self_regulation"
[1] "kermen_2022_anxiety"
[1] "kermen_2022_attention"
[1] "gan_2024_depression"
[1] "gan_2024_alexithymia"
[1] "peng_2024_grit"
[1] "peng_2024_language_enjoyment"
[1] "peng_2024_language_boredom"
[1] "rosyid_2025_academic_citizenship"
[1] "rosyid_2025_ethical_leadership"
[1] "rosyid_2025_prosocial_motivation"
[1] "dalichaouche_2026_covid_knowledge"
[1] "dalichaouche_2026_covid_attitudes"
[1] "dalichaouche_2026_covid_practices"
[1] "colombia_2023_politics_network"
[1] "kemp_2019_mss_disorganized"
[1] "kemp_2019_mss_negative"
[1] "kemp_2019_mss_positive"
[1] "trang_2023_vocabulary_beliefs"
[1] "trang_2023_vocabulary_strategies"
[1] "sirventruiz_2025_pdat"
[1] "mthimkhulu_2023_pirls_reading"
[1] "goldberg_2018_bri_bri"
[1] "goldberg_2018_bri_curio"
[1] "goldberg_2018_bri_feel"
[1] "goldberg_2018_bri_food"
[1] "goldberg_2018_bri_ofood"
[1] "goldberg_2018_ciss"
[1] "goldberg_2018_cpi"
[1] "goldberg_2018_dop_ab5c_vignettes"
[1] "goldberg_2018_dop_avocational_interests"
[1] "goldberg_2018_eps_adjectives"
[1] "goldberg_2018_eps_cesd"
[1] "goldberg_2018_eps_ipip"
[1] "goldberg_2018_eps_life_events"
[1] "goldberg_2018_eps_s11"
[1] "goldberg_2018_eps_spirituality"
[1] "goldberg_2018_hpi"
[1] "goldberg_2018_hpq_h"
[1] "goldberg_2018_ipip"
[1] "goldberg_2018_jpir"
[1] "goldberg_2018_pas_adjectives"
[1] "goldberg_2018_pas_ipip_scales"
[1] "goldberg_2018_pda360"
[1] "goldberg_2018_pda525"
[1] "goldberg_2018_pf16_p"
[1] "goldberg_2018_ppq_beliefs"
[1] "goldberg_2018_ppq_dream"
[1] "goldberg_2018_ppq_music"
[1] "goldberg_2018_ppq_via_strengths"
[1] "goldberg_2018_prs_bas_bis"
[1] "goldberg_2018_prs_gray_wilson"
[1] "goldberg_2018_prs_hexaco"
[1] "goldberg_2018_prs_ipip"
[1] "goldberg_2018_prs_movie_preferences"
[1] "goldberg_2018_prs_music_preferences"
[1] "goldberg_2018_prs_peo"
[1] "goldberg_2018_prs_pey"
[1] "goldberg_2018_prs_reading_preferences"
[1] "goldberg_2018_prs_tv_preferences"
[1] "goldberg_2018_sbo"
[1] "goldberg_2018_sdv_adjectives"
[1] "goldberg_2018_sdv_desirability"
[1] "goldberg_2018_sdv_force"
[1] "goldberg_2018_sdv_happy"
[1] "goldberg_2018_sdv_influ"
[1] "goldberg_2018_sdv_ipip_temperament"
[1] "goldberg_2018_sdv_likelihood"
[1] "goldberg_2018_sdv_schwartz_values"
[1] "goldberg_2018_sdv_views"
[1] "goldberg_2018_spa_beliefs_about_intelligence"
[1] "goldberg_2018_spa_bfi_forced_choice"
[1] "goldberg_2018_spa_changeability"
[1] "goldberg_2018_spa_cultural_familiarity"
[1] "goldberg_2018_spa_ipip"
[1] "goldberg_2018_spa_medical_history"
[1] "goldberg_2018_spa_skill_proficiency"
[1] "goldberg_2018_spa_skills"
[1] "goldberg_2018_spa_speo"
[1] "goldberg_2018_spa_spey"
[1] "goldberg_2018_spa_talents"
[1] "goldberg_2018_tci"
[1] "itemrandom_buchanan_2018_LPQ"
[1] "itemrandom_buchanan_2018_PIL"
[1] "aditama_2024_strs"
[1] "aiquipa_2026_dgs"
[1] "alan_2018_student_gender_attitudes"
[1] "alan_2018_teacher_extrinsic_motivation"
[1] "alan_2018_teacher_gender_attitudes"
[1] "alan_2018_teacher_growth_mindset"
[1] "alan_2018_teacher_modern_teaching"
[1] "alan_2018_teacher_warmth"
[1] "alloubani_2021_stai_state"
[1] "alloubani_2021_stai_trait"
[1] "arabaci_2025_burnout"
[1] "arabaci_2025_skill_diversity"
[1] "arabaci_2025_task_diversity"
[1] "arabaci_2025_turnover_intention"
[1] "balparda_2021_kepaq_emotional"
[1] "balparda_2021_kepaq_functional"
[1] "balparda_2021_korq_activity_limitation"
[1] "balparda_2021_korq_symptoms"
[1] "baquerotomas_2026_ders"
[1] "baquerotomas_2026_emas"
[1] "baquerotomas_2026_gad7"
[1] "baquerotomas_2026_neoffi"
[1] "baquerotomas_2026_phq9"
[1] "baquerotomas_2026_pil"
[1] "baquerotomas_2026_spsi"
[1] "bialowolski_2024_financial_literacy"
[1] "cao_2026_cdss_cognitive_load"
[1] "cao_2026_cdss_intention_to_use"
[1] "cao_2026_cdss_perceived_autonomy"
[1] "cao_2026_cdss_professional_knowledge"
[1] "cavojova_2017_cfc"
[1] "choi_2026_cmsce_2019_1"
[1] "choi_2026_cmsce_2019_2"
[1] "choi_2026_cmsce_2020_1"
[1] "choi_2026_cmsce_2020_2"
[1] "choi_2026_cmsce_2021_1"
[1] "choi_2026_cmsce_2021_2"
[1] "cosenza_2015_cfc"
[1] "demirbag_2025_emotions"
[1] "demirbag_2025_epistemological_beliefs"
[1] "demirbag_2025_goal_orientations"
[1] "hochsteiner_2026_sustainability_relevance"
[1] "manolika_2021_dirty_dozen"
[1] "manolika_2021_mini_ipip"
[1] "manolika_2021_movie_preferences"
[1] "manolika_2021_reading_preferences"
[1] "okoro_2022_interest_inventory"
[1] "perales_2026_digital_financial_literacy"
[1] "perales_2026_financial_resilience"
[1] "redline_2026_prosbq"
[1] "rogers_2021_financial_knowledge"
[1] "xu_2023_hi"
[1] "xu_2023_mi"
[1] "xu_2023_oic"
[1] "xu_2023_pca"
[1] "tang_2024_swls"
[1] "tang_2024_academic_satisfaction"
[1] "tang_2024_self_efficacy"
[1] "tang_2024_outcome_expectations"
[1] "tang_2024_goal_progress"
[1] "tang_2024_panas_positive"
[1] "tang_2024_panas_negative"
[1] "tang_2024_environmental_support"
[1] "tang_2024_self_construal"
[1] "tang_2024_caregiver_child_conflict"
[1] "tang_2024_caregiver_child_communication"
[1] "tang_2024_caregiver_child_regulation"
[1] "mboya_2020_gds15"
[1] "eyrenci_2025_mental_health_literacy"
[1] "zhang_2026_ecosystem_services"
[1] "zhang_2026_tourist_wellbeing"
[1] "zhang_2026_healthy_attitude"
[1] "zhang_2026_ecological_values"
[1] "koksal_2023_psycap"
[1] "koksal_2023_life_satisfaction"
[1] "koksal_2023_work_depression"
[1] "szabo_2025_passion"
[1] "szabo_2025_wellbeing"
[1] "szabo_2025_molbi"
[1] "szabo_2025_work_addiction"
[1] "szabo_2025_family_conflict"
[1] "szabo_2025_work_conflict"
[1] "szabo_2025_pss4"
[1] "avci_2024_aktif_gir_yonel"
[1] "avci_2024_bagmsz_gir_yonel"
[1] "avci_2024_basrmaarzu_gir_yonel"
[1] "avci_2024_belirsiz_kac"
[1] "avci_2024_bskdaykontrol_odak"
[1] "avci_2024_gecmis_gir_yonel"
[1] "avci_2024_guc_gir_yonel"
[1] "avci_2024_ickontrol_odak"
[1] "avci_2024_ikyoz_yeterlk"
[1] "avci_2024_issahp_gir_yonel"
[1] "avci_2024_kazanc_gir_yonel"
[1] "avci_2024_kimlik_com"
[1] "avci_2024_kimlik_dar"
[1] "avci_2024_kimlik_miss"
[1] "avci_2024_oz_norm"
[1] "avci_2024_risk_algi"
[1] "avci_2024_risk_gir_yonel"
[1] "avci_2024_sansdaykontrol_odak"
[1] "avci_2024_statu_gir_yonel"
[1] "avci_2024_sureklgel_gir_yonel"
[1] "avci_2024_tmlamacoz_yeterlk"
[1] "avci_2024_toplmfayd_gir_yonel"
[1] "avci_2024_urunpazgeloz_yeterlk"
[1] "avci_2024_yatrmciliskoz_yeterlk"
[1] "avci_2024_yencevolsoz_yeterlk"
[1] "avci_2024_zorbasetoz_yeterlk"
[1] "avci_2024_zorunluluk_gir_yonel"
[1] "celik_2026_academic_motivation"
[1] "celik_2026_bfi"
[1] "celik_2026_bpns"
[1] "celik_2026_distance_ed_attitudes_16"
[1] "celik_2026_distance_ed_attitudes_26"
[1] "celik_2026_tipi"
[1] "chen_2026_ai"
[1] "chen_2026_bi"
[1] "chen_2026_ch"
[1] "chen_2026_ee"
[1] "chen_2026_ie"
[1] "chen_2026_il"
[1] "chen_2026_in"
[1] "chen_2026_ir"
[1] "chen_2026_pr"
[1] "chen_2026_rf"
[1] "clipa_2025_mslq"
[1] "dai_2025_music_motivation"
[1] "erguvan_2022_questionnaire"
[1] "figalova_2021_bdi"
[1] "figalova_2021_pss"
[1] "figalova_2021_stai_state"
[1] "figalova_2021_stai_trait"
[1] "fraijo_2022_mslq"
[1] "hoai_2026_academic_achievement"
[1] "hoai_2026_cognitive_presence"
[1] "hoai_2026_instructional_design_quality"
[1] "hoai_2026_learning_experience"
[1] "hoai_2026_social_presence"
[1] "hoai_2026_student_engagement"
[1] "hoai_2026_teaching_presence"
[1] "khoa_2023_assurance"
[1] "khoa_2023_knowledge_acquisition"
[1] "khoa_2023_knowledge_dissemination"
[1] "khoa_2023_knowledge_use"
[1] "khoa_2023_teaching_materials"
[1] "khulwa_2025_algorithm_awareness"
[1] "khulwa_2025_engagement"
[1] "khulwa_2025_motivation_1"
[1] "khulwa_2025_motivation_2"
[1] "khulwa_2025_motivation_3"
[1] "khulwa_2025_motivation_4"
[1] "lee_2019_academic_motivation_scale"
[1] "lestari_2026_cognitive_flexibility"
[1] "lestari_2026_inhibitory_control"
[1] "lestari_2026_working_memory"
[1] "lozano_2018_cognition"
[1] "lozano_2018_getting_along"
[1] "lozano_2018_life_activities"
[1] "lozano_2018_mobility"
[1] "lozano_2018_participation"
[1] "lozano_2018_self_care"
[1] "nguyen_2026_autonomy_academic_motivation"
[1] "nguyen_2026_autonomy_academic_pressure"
[1] "nguyen_2026_autonomy_family_factors"
[1] "nguyen_2026_autonomy_school_autonomy_support"
[1] "nguyen_2026_autonomy_student_choice"
[1] "nguyen_2026_autonomy_student_ownership"
[1] "nguyen_2026_autonomy_student_voice"
[1] "nguyen_2026_misfit_academic_performance"
[1] "nguyen_2026_misfit_learning_misfit"
[1] "nguyen_2026_misfit_learning_motivation"
[1] "nguyen_2026_misfit_learning_satisfaction"
[1] "nguyen_2026_misfit_technostress"
[1] "nguyen_2026_sdt_academic_motivation"
[1] "nguyen_2026_sdt_autonomy"
[1] "nguyen_2026_sdt_competence"
[1] "nguyen_2026_sdt_mental_health"
[1] "nguyen_2026_sdt_perceived_performance"
[1] "nguyen_2026_sdt_relatedness"
[1] "pham_2026_bsgt"
[1] "pham_2026_bsth"
[1] "pham_2026_bsyn"
[1] "pham_2026_gp"
[1] "pham_2026_ktscx"
[1] "pham_2026_ktslh"
[1] "pham_2026_ktsth"
[1] "pham_2026_thbt"
[1] "ramadan_2026_ai_awareness"
[1] "ramadan_2026_applied_practice"
[1] "ramadan_2026_attitudes"
[1] "ramadan_2026_perceived_competence"
[1] "ribeiro_2019_academic_motivation"
[1] "saha_2026_cesd"
[1] "ventura_2025_quadrant_a"
[1] "ventura_2025_quadrant_b"
[1] "ventura_2025_quadrant_c"
[1] "ventura_2025_quadrant_d"
[1] "yao_2020_bai"
[1] "yao_2020_bdi"
[1] "yao_2020_epq"
[1] "yao_2020_gad"
[1] "yao_2020_ius"
[1] "yao_2020_pswq"
[1] "onah_2021_covid_knowledge"
[1] "onah_2021_covid_info_sources"
[1] "floreskanter_2021_cerq"
[1] "emiral_2025_aips"
[1] "kalczajanosi_2021_covid_fear"
[1] "kalczajanosi_2021_vaccine_skepticism"
[1] "kalczajanosi_2021_covid_risk"
[1] "risticdedic_2025_dhq_importance"
[1] "risticdedic_2025_dhq_currentstate"
[1] "risticdedic_2025_dhq_expectation"
[1] "benchelbi_2021_mtq48"
[1] "huang_2023_medseq"
[1] "kumlander_2018_scs"
[1] "kumlander_2018_bdi"
[1] "ilic_2019_whoqol_bref"
[1] "livacicrojas_2023_lvq"
[1] "woodall_2020_bfi44"
[1] "rodriguezsantero_2024_sats36"
[1] "atik_2026_climate_anxiety"
[1] "atik_2026_psych_resilience"
[1] "daderman_2023_wis"
[1] "daderman_2023_naq_r"
[1] "hahn_2025_sqc"
[1] "alqerem_2024_diabetic_health_literacy"
[1] "antunez_2013_rmeq"
[1] "antunez_2013_tmms24"
[1] "apaza_2026_meim_r"
[1] "apaza_2026_sdo"
[1] "apaza_2026_self_esteem"
[1] "huang_2023_utaut_mobile_shopping"
[1] "kotsou_2016_bdi"
[1] "kotsou_2016_happiness"
[1] "kotsou_2016_life_satisfaction"
[1] "kotsou_2016_panas"
[1] "kotsou_2016_plc"
[1] "kotsou_2016_scs"
[1] "matosaslopez_2022_bars_teaching"
[1] "matosaslopez_2024_questionnaire_quality"
[1] "matosaslopez_2024_teacher_assessment"
[1] "nurjanah_2019_hls47"
[1] "prihastiwi_2026_adcap"
[1] "sekowski_2025_mast"
[1] "sekowski_2025_pies"
[1] "tu_2022_achievement_motivation"
[1] "wicherts_2023_5pft"
[1] "wu_2025_drone_delivery"
[1] "alkhaldi_2023_whoqol_autism"
[1] "chatzoudes_2021_emotional_exhaustion"
[1] "chatzoudes_2021_ethical_leadership"
[1] "chatzoudes_2021_job_satisfaction"
[1] "chatzoudes_2021_service_delivery"
[1] "chatzoudes_2021_trust"
[1] "chatzoudes_2021_turnover_intention"
[1] "li_2026_coach_leadership"
[1] "li_2026_sport_commitment"
[1] "li_2026_team_cohesion"
[1] "turpochaparro_2026_family_communication"
[1] "turpochaparro_2026_self_esteem"
[1] "turpochaparro_2026_social_network_addiction"
[1] "wu_2024_achievement_emotions"
[1] "ysladomendez_2023_mbi"
[1] "baekgaard_2023_autonomy_loss"
[1] "baekgaard_2023_compliance"
[1] "baekgaard_2023_learning"
[1] "baekgaard_2023_mastery"
[1] "baekgaard_2023_stigma"
[1] "baekgaard_2023_stress"
[1] "hernandezmantilla_2024_cfni"
[1] "hernandezmantilla_2024_cmni"
[1] "lapietra_2026_volcanic_risk_perception"
[1] "osorio_2023_dos"
[1] "silva_2022_crsy"
[1] "skarzauskiene_2026_attitudes_science"
[1] "skarzauskiene_2026_big_five"
[1] "skarzauskiene_2026_fake_news_agree"
[1] "skarzauskiene_2026_fake_news_frequency"
[1] "skarzauskiene_2026_information_sources"
[1] "skarzauskiene_2026_science_behaviors"
[1] "skarzauskiene_2026_science_engagement"
[1] "skarzauskiene_2026_social_trust"
[1] "skarzauskiene_2026_trust_science"
[1] "ye_2025_jl"
[1] "ye_2025_mm"
[1] "ye_2025_tq"
[1] "ye_2025_xc"
[1] "chen_2024_ae"
[1] "chen_2024_cc"
[1] "chen_2024_cg"
[1] "chen_2024_cotah"
[1] "chen_2024_cr"
[1] "chen_2024_ds"
[1] "chen_2024_ec"
[1] "chen_2024_je"
[1] "chen_2024_kc"
[1] "chen_2024_kd"
[1] "chen_2024_sc"
[1] "chen_2024_smu"
[1] "chen_2024_spe"
[1] "chen_2024_tot"
[1] "chen_2024_ts"
[1] "chen_2024_uf"
[1] "estevez_2021_actitu"
[1] "estevez_2021_feepad"
[1] "estevez_2021_feepr"
[1] "estevez_2021_gest"
[1] "estevez_2021_homework_engagement"
[1] "estevez_2021_inter"
[1] "estevez_2021_math_attitudes"
[1] "estevez_2021_motiv"
[1] "soderberg_2024_academic_selfefficacy"
[1] "soderberg_2024_esm_affect"
[1] "soderberg_2024_esm_lecture"
[1] "soderberg_2024_esm_morning"
[1] "soderberg_2024_family_support"
[1] "soderberg_2024_general_selfefficacy"
[1] "soderberg_2024_peer_support"
[1] "soderberg_2024_teacher_support"
[1] "torok_2025_ai_acceptance"
[1] "torok_2025_data_disclosure"
[1] "torok_2025_data_security"
[1] "torok_2025_discourse_responsibility"
[1] "torok_2025_facebook_uses"
[1] "torok_2025_internet_use_frequency"
[1] "torok_2025_legality_beliefs"
[1] "torok_2025_manipulation_fear"
[1] "torok_2025_news_consumption"
[1] "torok_2025_news_source_frequency"
[1] "torok_2025_news_source_trust"
[1] "torok_2025_social_media_effects"
[1] "mexico_2023_mobility_utilities"
[1] "mexico_2023_mobility_rooms"
[1] "mexico_2023_mobility_appliances"
[1] "mexico_2023_mobility_assets"
[1] "mexico_2023_mobility_neighborhood"
[1] "mexico_2023_mobility_spaces"
[1] "mexico_2023_mobility_services"
[1] "mexico_2023_mobility_articles"
[1] "mexico_2023_mobility_finances"
[1] "mexico_2023_mobility_community"
[1] "mexico_2023_mobility_necessities"
[1] "mexico_2023_mobility_mood"
[1] "mexico_2023_mobility_anxiety"
[1] "spain_2018_housing_neighborhood"
[1] "spain_2018_housing_problems"
[1] "spain_2018_housing_amenities"
[1] "spain_2018_housing_dwelling"
[1] "spain_2018_housing_building"
[1] "spain_2018_housing_ownership"
[1] "spain_2018_housing_rentals"
[1] "spain_2018_housing_opinions"
[1] "spain_2018_housing_measures"
[1] "spain_2017_politics_wellbeing"
[1] "spain_2017_politics_citizenship"
[1] "spain_2017_politics_services"
[1] "spain_2017_politics_spending"
[1] "spain_2017_politics_burden"
[1] "spain_2017_politics_fraud"
[1] "spain_2017_politics_conscience"
[1] "spain_2017_politics_agreement"
[1] "spain_2017_politics_attitudes"
[1] "spain_2017_politics_discussion"
[1] 2
No missing BibTeX entries found.
[1] 3
[1] "goldberg_2018_spa_computer_use"
[1] "mthimkhulu_2023_pirls_reading_mc"
[1] "enem_2013_1mil_lc"
[1] "enem_2013_1mil_ch"
[1] "enem_2013_1mil_cn"
[1] "enem_2013_1mil_mt"
[1] "enem_2014_1mil_lc"
[1] "enem_2014_1mil_ch"
[1] "enem_2014_1mil_cn"
[1] "enem_2014_1mil_mt"
[1] "enem_2015_1mil_lc"
[1] "enem_2015_1mil_ch"
[1] "enem_2015_1mil_cn"
[1] "enem_2015_1mil_mt"
[1] "enem_2016_1mil_lc"
[1] "enem_2016_1mil_ch"
[1] "enem_2016_1mil_cn"
[1] "enem_2016_1mil_mt"
[1] "enem_2017_1mil_lc"
[1] "enem_2017_1mil_ch"
[1] "enem_2017_1mil_cn"
[1] "enem_2017_1mil_mt"
[1] "enem_2018_1mil_lc"
[1] "enem_2018_1mil_ch"
[1] "enem_2018_1mil_cn"
[1] "enem_2018_1mil_mt"
[1] "enem_2019_1mil_lc"
[1] "enem_2019_1mil_ch"
[1] "enem_2019_1mil_cn"
[1] "enem_2019_1mil_mt"
[1] "enem_2020_1mil_lc"
[1] "enem_2020_1mil_ch"
[1] "enem_2020_1mil_cn"
[1] "enem_2020_1mil_mt"
[1] "enem_2021_1mil_lc"
[1] "enem_2021_1mil_ch"
[1] "enem_2021_1mil_cn"
[1] "enem_2021_1mil_mt"
[1] "enem_2022_1mil_lc"
[1] "enem_2022_1mil_ch"
[1] "enem_2022_1mil_cn"
[1] "enem_2022_1mil_mt"
[1] "enem_2023_1mil_lc"
[1] "enem_2023_1mil_ch"
[1] "enem_2023_1mil_cn"
[1] "enem_2023_1mil_mt"
[1] "enem_2024_1mil_lc"
[1] "enem_2024_1mil_ch"
[1] "enem_2024_1mil_cn"
[1] "enem_2024_1mil_mt"
[1] "enem_2025_1mil_lc"
[1] "enem_2025_1mil_ch"
[1] "enem_2025_1mil_cn"
[1] "enem_2025_1mil_mt"
No missing BibTeX entries found.
[1] 4
No missing BibTeX entries found.

-- Stage 02 diff --
-- biblio.csv
   added:   494
   removed: 0
   changed: 0
     + aditama_2024_strs, aiquipa_2026_dgs, alan_2018_student_gender_attitudes, alan_2018_teacher_extrinsic_motivation, alan_2018_teacher_gender_attitudes, alan_2018_teacher_growth_mindset, alan_2018_teacher_modern_teaching, alan_2018_teacher_warmth, alexandrowicz_2018_cesd, alkhaldi_2023_whoqol_autism (+484 more)
   LONG-TEXT REVIEW FLAGS: 112 cell(s) -- see biblio.diff.csv
     ! aditama_2024_strs / BibTex: warn (502 chars) -- longer than expected, spot-check
     ! aiquipa_2026_dgs / BibTex: warn (565 chars) -- longer than expected, spot-check
     ! arabaci_2025_burnout / BibTex: warn (515 chars) -- longer than expected, spot-check
     ! arabaci_2025_skill_diversity / BibTex: warn (515 chars) -- longer than expected, spot-check
     ! arabaci_2025_task_diversity / BibTex: warn (515 chars) -- longer than expected, spot-check
     ! arabaci_2025_turnover_intention / BibTex: warn (515 chars) -- longer than expected, spot-check
     ! balparda_2021_kepaq_emotional / BibTex: warn (508 chars) -- longer than expected, spot-check
     ! balparda_2021_kepaq_functional / BibTex: warn (508 chars) -- longer than expected, spot-check
     ! benchelbi_2021_mtq48 / BibTex: warn (593 chars) -- longer than expected, spot-check
     ! cao_2026_cdss_cognitive_load / BibTex: warn (719 chars) -- longer than expected, spot-check
     ... (+102 more)
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/biblio.diff.csv
-- comps_biblio.csv
   added:   0
   removed: 0
   changed: 0
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/comps_biblio.diff.csv
-- nominal_biblio.csv
   added:   54
   removed: 0
   changed: 0
     + enem_2013_1mil_ch, enem_2013_1mil_cn, enem_2013_1mil_lc, enem_2013_1mil_mt, enem_2014_1mil_ch, enem_2014_1mil_cn, enem_2014_1mil_lc, enem_2014_1mil_mt, enem_2015_1mil_ch, enem_2015_1mil_cn (+44 more)
   LONG-TEXT REVIEW FLAGS: 1 cell(s) -- see nominal_biblio.diff.csv
     ! mthimkhulu_2023_pirls_reading_mc / BibTex: warn (719 chars) -- longer than expected, spot-check
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/nominal_biblio.diff.csv
-- simsyn_biblio.csv
   added:   0
   removed: 0
   changed: 0
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/simsyn_biblio.diff.csv

== Stage 03: Rscript 03_tags.R ==
[1] "core: 2480 rows -> tags.csv (5 named but untagged)"
[1] "core: +6 auto rows from ../tags/tags_auto.csv (4 superseded by the sheet)"
[1] "nom: 66 rows -> nominal_tags.csv (13 named but untagged)"

-- Stage 03 diff --
   ! tags.csv: dropped 1 duplicate-key row(s) before diffing (source CSV had >1 row for the same 'table', e.g. ['threat_isler_2024_exp1_incentive_crt']) -- check the upstream source (Google Sheet fetches have been flaky today)
   ! tags.csv: dropped 1 duplicate-key row(s) before diffing (source CSV had >1 row for the same 'table', e.g. ['threat_isler_2024_exp1_incentive_crt']) -- check the upstream source (Google Sheet fetches have been flaky today)
-- tags.csv
   added:   38
   removed: 0
   changed: 0
     + dpt_noncog__emotional_intelligence, enkavi_2019_ant_flanker, enkavi_2019_navon, gao2025_spiritual_wellbeing, jordan_2020_mindfulness, mexico_2023_mobility_anxiety, mexico_2023_mobility_appliances, mexico_2023_mobility_articles, mexico_2023_mobility_assets, mexico_2023_mobility_community (+28 more)
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/tags.diff.csv
-- nominal_tags.csv
   added:   0
   removed: 0
   changed: 0
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/nominal_tags.diff.csv

== Stage 05: Rscript 05_comps.R ==
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_meta:bdxt"
[1] 23  3
[1] 23
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_competitions:cmd7"
[1] "add"
character(0)
[1] "remove"
character(0)
[1] 23  3
[1] 23  3

-- Stage 05 diff --
-- comps_metadata.csv
   added:   0
   removed: 0
   changed: 0
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/comps_metadata.diff.csv

== Stage 06: Rscript 06_nominal.R ==
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_meta:bdxt"
[1] 66  6
[1] 66
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_nominal:614n"
[1] "add"
character(0)
[1] "remove"
character(0)
[1] 66  6
[1] 66  6

-- Stage 06 diff --
-- nominal_metadata.csv
   added:   0
   removed: 0
   changed: 0
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/nominal_metadata.diff.csv

== Stage 07: Rscript 07_simsyn.R ==
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_meta:bdxt"
[1] 8 8
[1] 8
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_simsyn:0btg"
[1] "add"
character(0)
[1] "remove"
character(0)
[1] 8 8
[1] 8 8
tibble [8 × 8] (S3: tbl_df/tbl/data.frame)
 $ table                    : chr [1:8] "gilbert_meta_3" "heller2013_probability" "tirt_sim_trt" "mudfoldsim" ...
 $ n_responses              : int [1:8] 90338 4140 7000 10000 10000 5000 12000 12000
 $ n_categories             : int [1:8] 2 2 4 2 3 0 2 3
 $ n_participants           : int [1:8] 5314 345 500 1000 1000 1000 2000 2000
 $ n_items                  : int [1:8] 17 12 14 10 10 5 6 6
 $ responses_per_participant: int [1:8] 17 12 14 10 10 5 6 6
 $ responses_per_item       : int [1:8] 5314 345 500 1000 1000 1000 2000 2000
 $ density                  : int [1:8] 1 1 1 1 1 1 1 1
[1] 8

-- Stage 07 diff --
-- simsyn_metadata.csv
   added:   0
   removed: 0
   changed: 0
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/simsyn_metadata.diff.csv

== Stage 08: Rscript 08_itemtext.R ==
Package version: 4.4
Unicode version: 15.1
ICU version: 74.2
Parallel computing: disabled
See https://quanteda.io for tutorials and examples.
Note: IRW item text is reconstructed from published sources using a largely
automated pipeline and is provided for research purposes only. We make no
guarantee as to its accuracy, completeness, or alignment with the `item`
identifiers in the response data; verify against the original source.
Inclusion here implies no license to reuse an instrument; copyright remains
with the original rights holders.
See https://itemresponsewarehouse.org/itemtext_issues.html
(silence with options(irw.itemtext_disclaimer = FALSE))
Warning: No reference id was provided for the dataset, which may cause your code to break if the name changes. Consider using the qualified reference "irw_meta:bdxt"
[1/140] 16_personalityfactors
[2/140] abdullah_2024_bsq_sev24
[3/140] abdullah_2024_bsq_sevgen
[4/140] abouhashish_2025_chatgpt_attitudes
[5/140] abukhalaf_2025_disaster_prep
[6/140] addy_2021_sdq_ghana
[7/140] agogue_2020_self_perceived_creativity
[8/140] aguirre_camacho_2021_champion
[9/140] aguirre_camacho_2021_shai
[10/140] ahmed_2019_food_consumption
[11/140] ahmed_2019_wellbeing
[12/140] ajaykumar_2023_nasa_tlx
[13/140] alasmari_2025_ai_trust_compare
[14/140] alasmari_2025_ai_trust_confidence
[15/140] albeitawi_2025_preceptor_needs
[16/140] alcoholhealthwarninglabel_brennan_2022_awareness_harms_followup
[17/140] alcoholhealthwarninglabel_brennan_2022_emotional_arousal_followup
[18/140] alcoholstroop_jones2024
[19/140] alexander_2017_dsi
[20/140] algner2022_cse
[21/140] algner2022_mimi16
[22/140] algner2022_uwes
[23/140] ali_2021_gad7
[24/140] ali_2021_iesr
[25/140] ali_2021_isi
[26/140] ali_2021_spfi
[27/140] alkouri_2025_coping
[28/140] alkouri_2025_icu_stressors
[29/140] allen_2025_delaydiscount
[30/140] almuqbil_2022_epds
[31/140] ALSECYPIAMH_WU_2022_PHQ
[32/140] ALSECYPIAMH_WU_2022_SDQ
[33/140] alsuhibani_2022_consp_s1
[34/140] alsuhibani_2022_ecrs_s3
[35/140] alsuhibani_2022_gcbs
[36/140] alsuhibani_2022_loc
[37/140] alsuhibani_2022_npi_s3
[38/140] alsuhibani_2022_pads_s1
[39/140] alsuhibani_2022_pads_s2
[40/140] alsuhibani_2022_sers
[41/140] altahla_2024_swls
[42/140] altahla_2024_whoqol
[43/140] altman_2020_capq
[44/140] alves_2017_hamd17
[45/140] amarilla_2020_barthel
[46/140] amarilla_2020_eq5d
[47/140] amarilla_2020_lawton_brody
[48/140] amarilla_2020_sf12
[49/140] american_multiracial_face
[50/140] an_2020_efl_self_regulated
[51/140] andrich_mudfold
[52/140] anh_2026_finbehavior
[53/140] anjum_2022_gad7
[54/140] AOMT_BR_SF_EDPANAB_Geiger_2021_AOT
[55/140] AOMT_BR_SF_EDPANAB_Geiger_2021_BRS
[56/140] arnulf_2022_general_knowledge
[57/140] arora2025_blueq_pedagogical
[58/140] arora2025_blueq_synchronous
[59/140] art
[60/140] artistic_preferences
[61/140] arzamoncunill_2023_epq_clinical
[62/140] audretsch_2021_entrepreneurial_ecosystems
[63/140] autonomysupport_mokken
[64/140] avilesgonzalez2019_ces
[65/140] baaziz_2023_sms2
[66/140] baka2023_bpnsf
[67/140] baka2023_jcs
[68/140] baka2023_olbi
[69/140] baka2023_uwes
[70/140] bakker_2020_pss10
[71/140] bakker_2020_rses
[72/140] bakumenko_2023_adyghe_values
[73/140] bang_2023_self_esteem
[74/140] bartoli_2022_badge_notifications
[75/140] beck_2021_iesr
[76/140] beck_2021_pss10
[77/140] benitezsillero_2021_bullying
[78/140] bitew_2020_lte
[79/140] bitew_2020_osss3
[80/140] bitew_2020_phq9
[81/140] bitew_2020_self_efficacy
[82/140] boyd_prism_2024
[83/140] brain_hemisphere
[84/140] brederecke_2020_phq4
[85/140] brederecke_2020_sis
[86/140] broadband_inventories
[87/140] buczel_2022_inoculation_belief
[88/140] bukurov_2022_sf36
[89/140] burgess_2025_soas
[90/140] burkert_2019_whoqol_bref
[91/140] busch_2022_course_alleviate
[92/140] busch_2023_stigma
[93/140] butt_2022_actual_usage
[94/140] butt_2022_cognitive_absorption
[95/140] butt_2022_institutional_factors
[96/140] butt_2022_task_tech_fit
[97/140] butt_2022_user_satisfaction
[98/140] buzgova_2023_gai
[99/140] buzgova_2023_gds
[100/140] buzgova_2023_lsita
[101/140] buzgova_2023_rses
[102/140] buzgova_2023_soc
[103/140] cacciatore_2021_crisis_care_satisfaction
[104/140] chen_2022_sasc
[105/140] close_relationships
[106/140] condon_2024_sapa_personality
[107/140] criticalperiod_syntax
[108/140] depression_anxiety_stress
[109/140] dumas_Organisciak_2022
[110/140] emidy2024_fevs
[111/140] fcv19s_hossain_2022_fear
[112/140] ftna_kasper_2022
[113/140] geography
[114/140] machivallianism_test_main
[115/140] pedroso_2021_ifsq_pressuring
[116/140] preussmattsson_2022_ownership
[117/140] riasec
[118/140] sapa_personality
[119/140] soderberg_2024_academic_selfefficacy
[120/140] soderberg_2024_esm_affect
[121/140] soderberg_2024_esm_lecture
[122/140] soderberg_2024_esm_morning
[123/140] soderberg_2024_family_support
[124/140] soderberg_2024_general_selfefficacy
[125/140] soderberg_2024_peer_support
[126/140] soderberg_2024_teacher_support
[127/140] torok_2025_ai_acceptance
[128/140] torok_2025_data_disclosure
[129/140] torok_2025_data_security
[130/140] torok_2025_discourse_responsibility
[131/140] torok_2025_facebook_uses
[132/140] torok_2025_internet_use_frequency
[133/140] torok_2025_legality_beliefs
[134/140] torok_2025_manipulation_fear
[135/140] torok_2025_news_consumption
[136/140] torok_2025_news_source_frequency
[137/140] torok_2025_news_source_trust
[138/140] torok_2025_social_media_effects
[139/140] twod_rotation_mather2023
[140/140] xie_2026_student_questionnaire

-- Stage 08 diff --
   ! itemtext_metadata.csv: dropped 1 duplicate-key row(s) before diffing (source CSV had >1 row for the same 'table', e.g. ['dumas_organisciak_2022']) -- check the upstream source (Google Sheet fetches have been flaky today)
-- itemtext_metadata.csv
   added:   560
   removed: 0
   changed: 0
     + 16_personalityfactors, 360emergencymed_azami_2024, ALSECYPIAMH_WU_2022_PHQ, ALSECYPIAMH_WU_2022_SDQ, AOMT_BR_SF_EDPANAB_Geiger_2021_AOT, AOMT_BR_SF_EDPANAB_Geiger_2021_BRS, abdullah_2024_bsq_sev24, abdullah_2024_bsq_sevgen, abouhashish_2025_chatgpt_attitudes, abukhalaf_2025_disaster_prep (+550 more)
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/itemtext_metadata.diff.csv

== Stage 10: Rscript 10_collections.R ==
collections            : 22
membership rows        : 1961
tables reached         : 1253 of 4134
in >1 collection       : 491
tags rows w/o a table  : 194

by coverage:
  curated-only: 1
  metadata-complete: 9
  tagged-subset-only: 12

counts by collection:
  rct                      metadata-complete      185
  longitudinal             metadata-complete      686
  intensive_longitudinal   metadata-complete       90
  response_time            metadata-complete      147
  rater_mediated           metadata-complete       30
  multistage               metadata-complete      107
  clustered                metadata-complete       81
  item_position            metadata-complete       61
  q_matrix                 metadata-complete       11
  continuous_response      curated-only            19
  big_five                 tagged-subset-only      64
  dark_triad               tagged-subset-only      35
  promis                   tagged-subset-only      33
  intl_assessment          tagged-subset-only      33
  affect_panas             tagged-subset-only      21
  self_esteem              tagged-subset-only      20
  mindfulness              tagged-subset-only      20
  math                     tagged-subset-only      71
  anxiety                  tagged-subset-only      72
  depression               tagged-subset-only      70
  reading_vocab            tagged-subset-only      47
  wellbeing                tagged-subset-only      58

dropped (tags row names no table in metadata.csv):
  big_five                    3 matching tags row(s) dropped: no such table in metadata.csv
  dark_triad                  1 matching tags row(s) dropped: no such table in metadata.csv
  math                       25 matching tags row(s) dropped: no such table in metadata.csv
  anxiety                     6 matching tags row(s) dropped: no such table in metadata.csv
  depression                  4 matching tags row(s) dropped: no such table in metadata.csv
  reading_vocab              19 matching tags row(s) dropped: no such table in metadata.csv
  wellbeing                   4 matching tags row(s) dropped: no such table in metadata.csv 

wrote collections.csv and collection_members.csv and collections_report.txt 

-- Stage 10 diff --
-- collections.csv
   added:   0
   removed: 0
   changed: 15
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/collections.diff.csv
-- collection_members.csv
   added:   32
   removed: 2
   changed: 0
     + alloubani_2021_stai_trait / longitudinal, cao_2026_cdss_cognitive_load / rct, cao_2026_cdss_intention_to_use / rct, cao_2026_cdss_perceived_autonomy / rct, cao_2026_cdss_professional_knowledge / rct, itemrandom_buchanan_2018_LPQ / rct, itemrandom_buchanan_2018_PIL / rct, lozano_2018_cognition / longitudinal, lozano_2018_getting_along / longitudinal, lozano_2018_life_activities / longitudinal (+22 more)
     - eammi_grahe_2018_marriage_timing / longitudinal, eammi_grahe_2018_marriage_timing / response_time
   diff written: /home/ben/Dropbox/projects/irw/src/metadata/collection_members.diff.csv

== Stage 09: Rscript 09_hero_status.R ==

Attaching package: ‘dplyr’

The following objects are masked from ‘package:stats’:

    filter, lag

The following objects are masked from ‘package:base’:

    intersect, setdiff, setequal, union

Wrote hero stats to ../../irw_site/data/hero_stats.json:
List of 3
 $ generated_at      : chr "2026-08-31T13:59:07Z"
 $ totals            :List of 4
  ..$ n_tables      : int 4134
  ..$ n_responses   : num 3.53e+09
  ..$ n_participants: int 91698680
  ..$ n_items       : num 890645
 $ category_breakdown:List of 6
  ..$ :List of 3
  .. ..$ n_categories: int 2
  .. ..$ n_items     : num 582346
  .. ..$ n_responses : num 2.52e+09
  ..$ :List of 3
  .. ..$ n_categories: int 3
  .. ..$ n_items     : num 5142
  .. ..$ n_responses : num 1.69e+08
  ..$ :List of 3
  .. ..$ n_categories: int 4
  .. ..$ n_items     : num 8547
  .. ..$ n_responses : num 49646253
  ..$ :List of 3
  .. ..$ n_categories: int 5
  .. ..$ n_items     : num 65040
  .. ..$ n_responses : num 2.8e+08
  ..$ :List of 3
  .. ..$ n_categories: int 6
  .. ..$ n_items     : num 6066
  .. ..$ n_responses : num 77617745
  ..$ :List of 3
  .. ..$ n_categories: chr "7+"
  .. ..$ n_items     : num 221566
  .. ..$ n_responses : num 4.3e+08

-- Stage 09 diff --
hero_stats.json written -- not a keyed CSV, review the file directly
(default path: /home/ben/Dropbox/projects/irw/src/../irw_site/data/hero_stats.json, or check 09's stdout above).

Done. Nothing here uploads to Redivis or touches irw_site -- review the
.diff.csv files above, then merge into Redivis / commit by hand.
```

## Workflow 2: cross-table audit (audit_tables.R)
```
Fetching live Redivis table lists (irw::irw_list_tables) ...
Fetching dictionary sheets ...
Warning: One or more parsing issues, call `problems()` on your data frame for details, e.g.:
  dat <- vroom(...)
  problems(dat)

Wrote:
  ./table_audit_report.md
  ./table_audit_report_incomplete.csv
  ./table_audit_report_incomplete.txt

Summary: 1694 incomplete, 0 urgent.
```

_Workflow 3 (upload_meta.py) intentionally NOT run -- review the diffs
and /home/ben/Dropbox/projects/irw/src/metadata/table_audit_report.md above, then run it by hand if the
changes look right._

https://github.com/ben-domingue/irw/issues/1747
