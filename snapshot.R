lf<-NULL 
f<-function(fn,nsamp=25000) { 
    print(fn)
    load(fn)
    ##
    person.n<-length(unique(df$id))
    item.n<-length(unique(df$item))
    n<-length(df$resp)
    ncat<-length(unique(df$resp[!is.na(df$resp)]))
    per<-(sqrt(n)/person.n)*(sqrt(n)/item.n)
    resp.per.person<-mean(as.numeric(table(df$id)))
    resp.per.item<-mean(as.numeric(table(df$item)))
    ##
    if (is.numeric(nsamp)) {
        nn<-nrow(df)
        if (nn>nsamp) {
            ii<-sample(1:nn,nsamp)
            df<-df[ii,]
        }
    }
    df<-df[!is.na(df$resp),]
    tmp<-df[,c("item","resp")]
    tmp$resp<-as.numeric(tmp$resp)
    L<-split(tmp,tmp$item)
    ff<-function(x) x$resp/max(x$resp,na.rm=TRUE)
    L<-lapply(L,ff)
    mean.resp<-mean(unlist(L),na.rm=TRUE)
    ##
    date.index<-('date' %in% names(df))
    rater.index<-('rater' %in% names(df))
    rt.index<-('rt' %in% names(df))
    ##
    c(nresp=n,ncat=ncat,person.n=person.n,item.n=item.n,sparse=per,resp.per.person=resp.per.person,resp.per.item=resp.per.item,mean=mean.resp,rt=rt.index,date=date.index,rater=rater.index)
}



##v1,2-15-2023
## lf <-
## c("4thgrade_math_sirt.Rdata", "abortion.Rdata", "acl_mokken.Rdata", 
## "andrich_mudfold.Rdata", "anxiety_lordif.Rdata", "autonomysupport_mokken.Rdata", 
## "balance_mokken.Rdata", "big5_sirt.Rdata", "cavalini_mokken.Rdata", 
## "cdm_ecpe.Rdata", "cdm_hr.Rdata", "cdm_pisa00R.Rdata", "cdm_timss03.Rdata", 
## "cdm_timss07.Rdata", "cdm_timss11.Rdata", "chess_lnirt.Rdata", 
## "coomansaddition.Rdata", "coomansdivision.Rdata", "coomansletterchaos.Rdata", 
## "coomansmultiplication.Rdata", "coomansset.Rdata", "coomanssubtraction.Rdata", 
## "credentialform_lnirt.Rdata", "criticalperiod.Rdata", "dd_rotation.Rdata", 
## "difNLR_msatb.Rdata", "ds14_mokken.Rdata", "duolingo__listen.Rdata", 
## "duolingo__reverse_tap.Rdata", "duolingo__reverse_translate.Rdata", 
## "duval4.Rdata", "duval8.Rdata", "emotion_pcmrs.Rdata", "enem.Rdata", 
## "eurpar2_mudfold.Rdata", "ffm_AGR.Rdata", "ffm_CSN.Rdata", "ffm_EST.Rdata", 
## "ffm_EXT.Rdata", "ffm_OPN.Rdata", "fims_tam.Rdata", "frac20.Rdata", 
## "g308_sirt.Rdata", "gatech_cappunish.Rdata", "gatech_censor.Rdata", 
## "geiser_tam.Rdata", "geography.Rdata", "grit.Rdata", "hads_multilcirt.Rdata", 
## "immer09_immer.Rdata", "immer10_immer.Rdata", "immer12_immer.Rdata", 
## "janssen2_tam.Rdata", "lessR_Mach4.Rdata", "loneliness_mudfold.Rdata", 
## "lsat.Rdata", "mcmi_mokken.Rdata", "mobility.Rdata", "motion.Rdata", 
## "mpsycho_asti.Rdata", "mpsycho_avlancheprep.Rdata", "mpsycho_bsss.Rdata", 
## "mpsycho_ceaq.Rdata", "mpsycho_condom.Rdata", "mpsycho_lakes.Rdata", 
## "mpsycho_learnemo.Rdata", "mpsycho_Rmotivation.Rdata", "mpsycho_Rogers_adolescent.Rdata", 
## "mpsycho_Rogers.Rdata", "mpsycho_rwdq.Rdata", "mpsycho_wenchuan.Rdata", 
## "mpsycho_wilmer.Rdata", "mpsycho_wilpat.Rdata", "mpsycho_YouthDep.Rdata", 
## "mpsycho_zareki.Rdata", "mq_supremecourt.Rdata", "naep_multilcirt.Rdata", 
## "pirlsmissing_sirt.Rdata", "pks_probability.Rdata", "ptam1_immer.Rdata", 
## "quantshort.Rdata", "RLMS_MLCIRTwithin.Rdata", "roar_lexical.Rdata", 
## "rollcall_house.Rdata", "rollcall_senate.Rdata", "rr98_accuracy.Rdata", 
## "sds.Rdata", "sem_cnes.Rdata", "SF12_MLCIRTwithin.Rdata", "si09_sirt.Rdata", 
## "smacof_pvq40.Rdata", "state_c1_2007_10_responses.Rdata", "state_c1_2007_3_responses.Rdata", 
## "state_c1_2007_4_responses.Rdata", "state_c1_2007_5_responses.Rdata", 
## "state_c1_2007_6_responses.Rdata", "state_c1_2007_7_responses.Rdata", 
## "state_c1_2007_8_responses.Rdata", "state_c1_2007_9_responses.Rdata", 
## "state_c3_2007_5_responses.Rdata", "state_c3_2007_6_responses.Rdata", 
## "state_c3_2007_7_responses.Rdata", "state_c3_2007_8_responses.Rdata", 
## "state_c3_2007_9_responses.Rdata", "swmd_mokken.Rdata", "tenseness_pcmrs.Rdata", 
## "timss_tam.Rdata", "tma.Rdata", "transreas_mokken.Rdata", "trees_sirt.Rdata", 
## "verbagg.Rdata", "wirs.Rdata", "wordsum.Rdata")



lf<-c("artistic_preferences.Rdata","depression_anxiety_stress.Rdata","fisher_temperment.Rdata","nature_relatedness.Rdata","protestant_workethic.Rdata")
if (is.null(lf)) lf<-list.files(pattern="*.Rdata")
tab<-t(sapply(lf,f))
tab<-data.frame(tab)
ss<-tab[order(tab$sparse),]


write.csv(ss,'')

save(ss,file="~/Dropbox/projects/irw/src/snapshot.Rdata")












