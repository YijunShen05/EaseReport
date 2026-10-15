"""Synthetic Mendelian-count example. No biological experiment is performed."""
import itertools
import math
import random
from collections import Counter
SEED=20261015

def offspring(g1,g2):
    return ''.join(''.join(sorted((a,b),key=lambda x:(x.islower(),x))) for a,b in zip(g1,g2))

def phenotype(genotype,kind):
    a='A' in genotype
    if kind=='mono':return 'normal' if a else 'vestigial'
    b='B' in genotype
    return 'wild' if a and b else 'ebony' if a else 'vestigial' if b else 'double'

def predictions(spec):
    counts=Counter(phenotype(offspring(a,b),spec['kind']) for a,b in itertools.product(spec['gametes_a'],spec['gametes_b']))
    total=sum(counts.values())
    return [counts[c['id']]/total for c in spec['classes']]

def chi_square(observed,probabilities):
    n=sum(observed)
    if not n:return {'n':0,'expected':[0.0 for _ in observed],'chi2':None,'df':len(observed)-1,'p':None,'minimum_expected':None,'approximation_valid':False,'contributions':[None for _ in observed],'decision':'无合格可判读计数，不检验。'}
    expected=[n*p for p in probabilities]
    terms=[(o-e)**2/e for o,e in zip(observed,expected)]
    value=sum(terms);df=len(observed)-1;z=value/2
    p=math.erfc(math.sqrt(z))
    if df==3:p+=2/math.sqrt(math.pi)*math.sqrt(z)*math.exp(-z)
    elif df!=1:raise ValueError('This example supports chi-square df=1 or 3 only')
    valid=min(expected)>=5
    return {'n':n,'expected':expected,'chi2':value,'df':df,'p':min(1,max(0,p)) if valid else None,'minimum_expected':min(expected),'approximation_valid':valid,'contributions':terms,'decision':('期望频数不足 5，仅展示描述性偏差，不报告近似 p 值。' if not valid else '在预设 0.05 水平下未拒绝此理论比例；不等于证明。' if p>=.05 else '在预设 0.05 水平下出现偏离提示；应检查设计与误差，不能据此否定普遍定律。')}

def summarize(data,experiment,vial='all'):
    spec=next(s for s in data['experiments'] if s['id']==experiment)
    registered=[v for v in data['vials'] if v['experiment']==experiment and (vial=='all' or v['id']==vial)]
    included=[v for v in registered if v['status']=='accepted']
    counts=[sum(v['counts'][i] for v in included) for i in range(len(spec['classes']))]
    result=chi_square(counts,predictions(spec))
    result.update({'experiment':experiment,'vial':vial,'counts':counts,'registered_vials':len(registered),'accepted_vials':len(included),'excluded_vials':sum(v['status']=='excluded' for v in registered),'pending_vials':sum(v['status']=='pending' for v in registered),'unclassified':sum(v['unclassified'] for v in included),'excluded_classified':sum(sum(v['counts']) for v in registered if v['status']=='excluded'),'excluded_unclassified':sum(v['unclassified'] for v in registered if v['status']=='excluded')})
    return result

def build_data():
    rng=random.Random(SEED)
    classes=[{'id':'wild','label':'正常翅 · 常规体色','genotype':'A_B_'},{'id':'ebony','label':'正常翅 · 黑檀体色','genotype':'A_bb'},{'id':'vestigial','label':'残翅 · 常规体色','genotype':'aaB_'},{'id':'double','label':'残翅 · 黑檀体色','genotype':'aabb'}]
    experiments=[{'id':'mono','label':'单因子 F2','kind':'mono','question':'一对等位基因如何分离？','ratio':'3 : 1','parental':'AA × aa','f1':'Aa，预期正常翅','cross':'Aa ♀ × Aa ♂','hypothesis':'F2 正常翅 : 残翅 = 3 : 1','gametes_a':['A','a'],'gametes_b':['A','a'],'classes':[{'id':'normal','label':'正常翅','genotype':'A_'},{'id':'vestigial','label':'残翅','genotype':'aa'}],'f1_scored':120,'f1_wild':120},
    {'id':'dihybrid','label':'双因子 F2','kind':'di','question':'两对非连锁基因如何组合？','ratio':'9 : 3 : 3 : 1','parental':'AABB × aabb','f1':'AaBb，预期正常翅与常规体色','cross':'AaBb ♀ × AaBb ♂','hypothesis':'四种表型按 9 : 3 : 3 : 1 分离','gametes_a':['AB','Ab','aB','ab'],'gametes_b':['AB','Ab','aB','ab'],'classes':classes,'f1_scored':144,'f1_wild':144},
    {'id':'testcross','label':'双因子测交','kind':'di','question':'用隐性亲本读出 F1 配子类型','ratio':'1 : 1 : 1 : 1','parental':'沿用双因子亲本家系','f1':'选取 AaBb 雌性进行测交','cross':'AaBb ♀ × aabb ♂','hypothesis':'四类后代等频；并非所有测交都如此','gametes_a':['AB','Ab','aB','ab'],'gametes_b':['ab'],'classes':classes,'f1_scored':None,'f1_wild':None}]
    sizes={'mono':[96,104,100],'dihybrid':[128,112,120,136],'testcross':[80,84,88,12]};unknown={'mono':[2,1,0],'dihybrid':[2,4,1,3],'testcross':[1,2,0,1]};prefix={'mono':'M','dihybrid':'D','testcross':'T'};vials=[]
    for spec in experiments:
        probs=predictions(spec)
        for index,n in enumerate(sizes[spec['id']]):
            sampled=[0]*len(probs)
            for _ in range(n):
                u=rng.random();cum=0
                for k,p in enumerate(probs):
                    cum+=p
                    if u<cum:sampled[k]+=1;break
            vials.append({'id':f"{prefix[spec['id']]}-{index+1:02}",'experiment':spec['id'],'status':'accepted','counts':sampled,'unclassified':unknown[spec['id']][index],'scored_day':28+index,'note':'按预设 QC 规则纳入；难以判读个体单列，不分配表型。' if n>=80 else '小样本瓶仍保留；单独查看时每类期望数仅 3，不适用 χ² 近似。','record_origin':'synthetic'})
    vials.extend([{'id':'D-05','experiment':'dihybrid','status':'excluded','counts':[32,8,4,4],'unclassified':2,'scored_day':31,'note':'合成质控事件：亲本基因型瓶签缺失；按事先规则排除，不因 p 值筛除。','record_origin':'synthetic'},{'id':'D-06','experiment':'dihybrid','status':'pending','counts':None,'unclassified':None,'scored_day':None,'note':'计数未登记。缺测不是 0，保留在登记目录。','record_origin':'synthetic'}])
    logs=[]
    milestones=[(0,'亲本登记','建系','核对亲本表型、品系标签与未交配雌性记录；建立瓶号。','亲本组合写入记录，遗传假设在计数前固定。'),(3,'移出亲本','世代控制','记录亲本转移，避免后续世代混杂。','本例只模拟操作日志，不代表实际饲养。'),(7,'幼虫观察','发育观察','记录幼虫活动及培养状态，暂不据此判断成虫性状。','发育迹象不作为表型分离计数。'),(14,'F1 表型记录','F1','登记 F1 表型并为 F2 / 测交分配后续培养瓶。','F1 表型记录不重复加入 F2 / 测交的统计分母。'),(17,'移出 F1 亲本','世代控制','核对新瓶标签，记录亲本移出。','不同世代及测交群体分别统计。'),(21,'蛹期记录','发育观察','记录蛹期进展和异常，尚无成虫计数的瓶保持待计数。','没有观测记录不补零。'),(28,'首轮成虫计数','计数','按已确定的表型类别计数；难以判读个体单列。','每只后代只登记一次；分次计数不重复相加。'),(35,'汇总与复核','汇总','保留全部瓶号、排除理由与缺测；对合格可判读计数作理论对照。','模拟符合理论不能作为真实验证；瓶间差异及存活选择需在真实实验中另查。')]
    for day,title,stage,action,result in milestones:
        logs.append({'id':f'L-{day:02}','day':day,'title':title,'stage':stage,'experiment':'all','vial':None,'status':'recorded','action':action,'observation':result,'origin':'synthetic'})
    for spec in experiments:
        logs.append({'id':'F1-'+spec['id'],'day':14,'title':spec['label']+' · F1 记录','stage':'F1','experiment':spec['id'],'vial':None,'status':'recorded','action':spec['cross'],'observation':(f"模拟 F1 共 {spec['f1_scored']} 只，预期显性表型 {spec['f1_wild']} 只；此演示中不是新增的 F2 证据。" if spec['f1_scored'] is not None else '测交使用双因子家系的 F1 雌性；不重复登记该家系的 F1 样本量。'),'origin':'synthetic'})
    for v in vials:
        logs.append({'id':'COUNT-'+v['id'],'day':v['scored_day'] or 35,'title':v['id']+' · '+('计数待登记' if v['status']=='pending' else '质控排除' if v['status']=='excluded' else '计数记录'),'stage':'QC' if v['status']!='accepted' else '计数','experiment':v['experiment'],'vial':v['id'],'status':v['status'],'action':'保留原始计数、难判读数与 QC 状态。','observation':v['note'],'origin':'synthetic'})
    data={'schemaVersion':1,'title':'孟德尔遗传规律 · 果蝇实验日志','synthetic':True,'seed':SEED,'simulation_policy':'按理论概率逐只抽样，固定 seed；不按 p 值重抽或调参。QC、难判读数和小样本瓶是预设教学情景。','organism':'Drosophila melanogaster','timeline':'虚拟 D0–D35；不是现实日期或已执行实验','conditions':'合成培养设定 25°C，采用约两周一代的教学记录节奏','alleles':'教学简写：A/a = vg⁺/vg（翅型）；B/b = e⁺/e（体色）。选用教学常染色体隐性模型；不泛化到这些基因的所有等位型。','experiments':experiments,'vials':vials,'logs':sorted(logs,key=lambda r:(r['day'],r['id'])),'analysis_policy':{'alpha':.05,'expected_minimum':5,'inclusion':'status=accepted 且 counts 已登记；仅可判读后代进入表型分母。','selection':'实验/培养瓶决定检验范围；表型高亮和日志搜索只改变明细，不改变检验分母。','assumptions':'理论指定概率；将后代视作独立抽样以演示 χ² 近似，真实数据需另外考察瓶间异质性、存活差异和观察偏差。','not_proof':'合成数据来自待展示的理论，因此不能用于独立验证该理论；p≥0.05 也不证明定律成立。'},'analysis':{}}
    for s in experiments:
        for key in ['all']+[v['id'] for v in vials if v['experiment']==s['id']]:data['analysis'][s['id']+'|'+key]=summarize(data,s['id'],key)
    return data
