# 69S — ELTI 발생지 노출 민감도(2026-11-19, 설계메모 사전 지정): 주모형(NB BYM2 593 + RW1 + 연도 iid, S1 가설 7 + 강제통제 5, offset E_std)을
#  (a) 그대로 재적합(기준), (b) 전체 교통사고율(주민 1,000명당, 발생지 통행·관광·통과 교통 대리) z를 추가, (c) 14년 전체 사고율 상위 10%(23곳) 제외, (d) 사고 기준 E_crash를 offset으로.
#  (e) offset = E_crash + 65세 이상 인구 비중(z) 추가(2026-11-19 검토 반영: 사고 기준 비는 노인 비중과 구조적으로 연동).
#  사용(01_스크립트/에서): Rscript 69S_elti_exposure_sens.R   산출: 04_분석/ELTI/results_std3/S69S_exposure_sens.csv
suppressPackageStartupMessages({library(INLA);library(jsonlite);library(sf)})
inla.setOption(num.threads="1:1")
D<-file.path("..","04_분석","ELTI");OUT<-file.path(D,"results_std3")
S<-fromJSON(file.path(D,"config_ELTI_std3.json"))
DD<-read.csv(file.path(D,"panel_ELTI_std3.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE)
g<-inla.read.graph(file.path(D,"graph_593.graph"))
SHP<-Sys.getenv("ST_SHP",file.path(normalizePath(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),"..")),"data","boundary","final.shp"))
G<-st_read(SHP,quiet=TRUE);G$region<-enc2utf8(G$region);DD$fbd_region<-enc2utf8(DD$fbd_region);stopifnot(g$n==nrow(G),all(DD$fbd_region%in%G$region))
DD$area<-match(DD$fbd_region,G$region);DD$time<-DD$year-min(DD$year)+1;DD$yiid<-DD$time
HYP<-S$sets_after_vif$S1_narrative_full;FORCED<-S$forced;stopifnot(length(HYP)==7)
acc<-"ext__all_crash_per1000";stopifnot(acc%in%names(DD));DD$acc_z<-as.numeric(scale(log(DD[[paste0(acc,"_raw")]])))
E2<-read.csv(file.path("..","02_패널","ELTI_E69.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE);E2$fbd_region<-enc2utf8(E2$fbd_region)
DD$E_crash<-E2$E_crash[match(paste(DD$year,DD$fbd_region),paste(E2$year,E2$fbd_region))];stopifnot(!any(is.na(DD$E_crash)))
DD$E_crash<-DD$E_crash*sum(DD$cases)/sum(DD$E_crash)
DD$old_z<-as.numeric(scale(E2$pop65[match(paste(DD$year,DD$fbd_region),paste(E2$year,E2$fbd_region))]/E2$pop_all[match(paste(DD$year,DD$fbd_region),paste(E2$year,E2$fbd_region))]))
ar<-aggregate(cbind(a=DD[[paste0(acc,"_raw")]])~fbd_region,DD,mean);top<-ar$fbd_region[ar$a>=quantile(ar$a,0.9)]
pc<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)),phi=list(prior="pc",param=c(0.5,2/3)));pcp<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)))
fit<-function(vars,data,ecol="E",label){f<-as.formula(paste("cases ~ 1 +",paste(sprintf("`%s`",vars),collapse="+"),
  "+ f(area,model='bym2',graph=g,scale.model=TRUE,constr=TRUE,hyper=pc) + f(time,model='rw1',scale.model=TRUE,hyper=pcp) + f(yiid,model='iid',hyper=pcp)"))
  m<-inla(f,family="nbinomial",data=data,E=data[[ecol]],control.fixed=list(mean=0,prec=4,mean.intercept=0,prec.intercept=0.001),control.compute=list(waic=TRUE),control.inla=list(control.vb=list(emergency=50)))
  s<-m$summary.fixed[-1,c("mean","0.025quant","0.975quant")];data.frame(analysis=label,cov=gsub("`","",rownames(s)),IRR=exp(s[,1]),lo=exp(s[,2]),hi=exp(s[,3]),cred=exp(s[,2])>1|exp(s[,3])<1,WAIC=round(m$waic$waic,1),n=nrow(data),row.names=NULL)}
R<-rbind(fit(c(HYP,FORCED),DD,label="refit_principal"),fit(c(HYP,FORCED,"acc_z"),DD,label="plus_all_crash_rate"),
         fit(c(HYP,FORCED),DD[!DD$fbd_region%in%top,],label=sprintf("exclude_top10pct_crash_rate_%d",length(top))),fit(c(HYP,FORCED),DD,ecol="E_crash",label="E_per_crash"),fit(c(HYP,FORCED,"old_z"),DD,ecol="E_crash",label="E_per_crash_plus_older_share"))
write.csv(R,file.path(OUT,"S69S_exposure_sens.csv"),row.names=FALSE);writeLines(top,file.path(OUT,"S69S_top10pct_districts.txt"));print(R[R$cov%in%c(HYP,"acc_z","old_z"),c("analysis","cov","IRR","lo","hi","cred")])
