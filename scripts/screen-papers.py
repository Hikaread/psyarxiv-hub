import json, re, sys

papers = json.load(open("/home/z/my-project/psyarxiv-hub/data/discovered-run3.json"))
print(f"Total to screen: {len(papers)}")

# Psychology-relevant keywords (broad but targeted)
psy_kw = [
    r'psycholog', r'mental\b', r'depress', r'anxiet', r'anxious',
    r'therapy\b', r'therapeuti', r'psychotherap',
    r'cogniti', r'behavior', r'behaviour', r'emotio', r'mood\b',
    r'stress\b', r'trauma\b', r'PTSD\b', r'autism\b', r'ASD\b',
    r'ADHD\b', r'schizophreni', r'psychosis\b', r'psychotic\b',
    r'personality\b', r'attachment\b', r'well.?being\b', r'wellbeing\b',
    r'mindful', r'meditation\b', r'sleep\b', r'addict', r'substance\b',
    r'alcohol\b', r'suicid', r'self.?harm\b', r'body\s+image',
    r'neurodiverg', r'neurodevelop', r'dissociati',
    r'obsessive', r'compulsi', r'phobia\b', r'resilien', r'coping\b',
    r'grief\b', r'bereave', r'parent', r'child\b', r'adolescent', r'infant\b',
    r'scale\b', r'measure', r'instrumen', r'questionnaire',
    r'validat', r'reliabil', r'psychometr',
    r'confirmatory factor', r'exploratory factor', r'structural equation',
    r'mediat', r'moderat', r'longitudin', r'prospective',
    r'meta.?analy', r'systematic review',
    r'clinical\b', r'diagnos', r'symptom', r'intervention\b',
    r'treatment\b', r'randomi', r'control.?group',
    r'CBT\b', r'DBT\b', r'acceptance and commitment',
    r'exposure\b', r'dialectical', r'psychodynamic', r'psychoanaly',
    r'narrative\b', r'identity\b', r'self.?esteem',
    r'self.?compass', r'self.?efficacy', r'motivat',
    r'stigma\b', r'prejudice\b', r'discrimina',
    r'prosocial\b', r'aggressi', r'violence\b',
    r'memory\b', r'attention\b', r'percept', r'decision.?making',
    r'creativit', r'reasoning\b',
    r'brain\b', r'neural\b', r'fMRI\b', r'EEG\b',
    r'neurosci', r'cortisol\b', r'physiolog', r'biomark',
    r'genetic\b', r'epigenetic', r'temperament\b',
    r'Big Five\b', r'emotion.?regulat', r'affect\b',
    r'lonelin', r'social support', r'peer\b', r'bullying\b',
    r'relationship\b', r'romantic\b', r'couple', r'family\b',
    r'student', r'teacher', r'classroom', r'academic\b',
    r'occupational\b', r'burnout\b', r'organizational\b', r'leadership\b',
    r'health\b', r'chronic\b', r'pain\b',
    r'ageing\b', r'aging\b', r'older adult', r'dementia\b',
    r'gender\b', r'race\b', r'ethnic', r'culture\b', r'cultural\b',
    r'sexual', r'LGBT', r'transgender', r'immigrant', r'migrat', r'refugee',
    r'social media\b', r'internet\b', r'smartphone\b',
    r'gaming\b', r'AI\b', r'artificial intelligence\b', r'chatbot\b', r'LLM\b',
    r'meaning\b', r'purpose\b', r'existen', r'spiritual', r'religi',
    r'death\b', r'mortality\b', r'empathy\b', r'compassion\b',
    r'procrastinat', r'perfection', r'impuls', r'risk.?tak',
    r'gambling\b', r'somati', r'psychosomat',
    r'narcissi', r'psychopath', r'machiavelli',
    r'postpartum\b', r'perinatal\b', r'maternal\b', r'paternal\b',
    r'virtual reality\b', r'teletherapy\b', r'telehealth\b',
    r'forensic\b', r'eyewitness\b', r'false memor',
    r'dream\b', r'nightmare\b', r'insomnia\b',
    r'bipolar\b', r'manic\b', r'borderline\b',
    r'eating disorder', r'anorexi', r'bulimi', r'binge\b',
    r'panic\b', r'dyslexi',
    r'epidemi', r'prevalence\b', r'public health\b',
    r'exercise\b', r'physical activ', r'obesity\b',
    r'smoking\b', r'cannab', r'opioid\b',
    r'mixed.?method', r'qualitative\b', r'thematic anal',
    r'interview', r'focus group', r'participant\b',
    r'case stud', r'therapeutic alliance\b',
    r'transdiagnos', r'comorbid', r'recovery\b', r'relapse\b',
    r'help.?seeking\b', r'mental health',
    r'veteran\b', r'military\b',
    r'climate\b.*anxiet', r'child abuse', r'neglect\b', r'maltreat',
    r'diversity\b', r'inclusion\b', r'equity\b',
    r'microaggress', r'implicit bias',
    r'replicat', r'preregist', r'Bayesian\b',
    r'machine learn', r'deep learn', r'classificat',
    r'predict', r'natural language process', r'NLP\b',
    r'respon', r'reaction time', r'Stroop\b',
    r'working memory\b', r'priming\b', r'framing\b',
    r'heuristic', r'cognitive bias', r'dual.?process',
    r'self.?determin', r'self.?regulat',
    r'behavior change', r'health belief\b',
    r'social cognit', r'cross.?cultural\b',
    r'executive function', r'cognitive flexib',
    r'theory of mind\b', r'mentaliz',
    r'sexual orient', r'sexual identit', r'minority stress',
    r'job satisfact', r'work engagement\b', r'workahol',
    r'socioeconomic\b', r'homeless', r'incarcerat', r'recidivism',
    r'trauma.?inform', r'child.?welfare',
    r'homicide\b', r'domestic violen',
    r'foetal\b', r'fetal\b', r'prenatal\b',
    r'dyslexi', r'dyscalculi', r'dyspraxi',
    r'disability\b', r'rehabilit',
    r'self.?concept', r'self.?schema',
    r'gratitud', r'forgiv', r'shame\b', r'guilt\b',
    r'anger\b', r'fear\b', r'trust\b', r'envy\b', r'jealousy\b',
    r'moral\b', r'conspiracy\b', r'misinformation\b',
    r'growth mindset', r'salutogen', r'posttraumatic growth',
    r'sensemak', r'sense.?making',
    r'addiction', r'dependenc', r'withdrawal',
    r'assessment', r'screening tool', r'diagnostic tool',
    r'psychiatric', r'psychopathol',
    r'speech.?therap', r'language.?disorder',
    r'social.?emotional', r'emotion.?recogni',
    r'play.?therap', r'art.?therap', r'music.?therap',
    r'human.?computer', r'eyetrack', r'eye.?track',
    r'neurofeedback', r'biofeedback',
    r'placebo\b', r'nocebo',
    r'perinatal mental', r'paternal mental', r'maternal mental',
    r'community psychology', r'critical psychology',
    r'health psychology', r'sport psychology', r'forensic psycholog',
    r'counseling', r'counselling', r'counselor', r'counsellor',
    r'psychoeducation', r'psychoeducational',
    r'resilience', r'post.?traumatic',
    r'cognitive.?behavior', r'cognitive behavio',
    r'emotion.?focus', r'emotionally focus',
    r'strengths.?based', r'recovery.?orient',
    r'peer.?support', r'self.?help',
    r'object relations?', r'defense mechanism',
    r'psychometric', r'factor analy', r'item respons', r'Rasch\b',
    r'scale develop', r'validation stud',
    r'gender.?role', r'gender.?identity', r'gender.?norm',
    r'racial.?bias', r'racial.?discrim',
    r'weight.?bias', r'weight.?stigma',
    r'ageism', r'ableism', r'sexism', r'heterosexism',
    r'cultural.?adapt', r'cultural.?valid',
    r'indigenous', r'decolonial',
    r'climate.?anxiet', r'eco.?anxiet',
    r'tech.?based interven', r'digital.?therap', r'digital mental',
    r'app.?based interven', r'mobile.?health',
    r'augment.*reality', r'VR\b.*therap',
    r'phenomenolog', r'hermeneutic', r'grounded theor',
    r'service.?user', r'survivor', r'lived.?experience',
    r'family.?violence', r'intimate.?partner',
    r'child.?protective', r'foster.?care', r'kinship',
    r'school.?based', r'community.?based',
    r'pregnan', r'postnatal',
    r'breast.?cancer', r'chronic.?illness', r'chronic.?pain',
    r'sleep.?disorder', r'sleep.?quality',
    r'depressive\b', r'anxiety\b', r'psychological\b',
    r'substance.?use', r'alcohol.?use',
    r'body.?mass', r'dietary',
    r'psychosocial', r'socio.?emotional',
    r'self.?report', r'self.?rated',
    r'well.?being',
    r'social.?determinant',
    r'community.?mental',
    r'drug.?use\b', r'alcohol.?disorder',
    r'trauma.?expos',
    r'adverse child', r'ACE',
]

# Hard non-psychology excludes
exclude_kw = [
    r'^fuel\b', r'^oil\b', r'gas pric', r'petrol',
    r'acceleromet', r'microbridge', r'sensor.*harsh',
    r'human resource.*procurement', r'neoliberal reform',
    r'civic footprint', r'party elite', r'associational tie',
    r'cloud comput', r'blockchain.*supply',
    r'concrete.*strength', r'steel.*beam',
    r'compiler\b', r'debugg',
    r'foreign exchange\b', r'cryptocurrency.*trad',
    r'solar panel\b', r'wind turbine\b',
    r'bridge.*structur', r'soil.*mechanic', r'water treatment\b',
    r'traffic.*congest', r'power grid\b', r'battery.*manag',
    r'power.*transmission', r'voltage.*stability',
    r'concrete.*mix', r'cement\b',
    r'rooftop.*solar', r'photovoltaic',
    r'wastewater', r'sewage', r'desalination',
    r'earthquake.*resist', r'seismic.*design',
    r'3D print.*manufactur', r'additive manufactur',
    r'deep learning.*image classif.*satellite',
    r'robot.*path.*plann', r'robot.*control',
    r'convolutional.*object.*detect.*drone',
    r'federated learning.*IoT',
    r'voltage.*source.*converter',
    r'load.*forecast.*power',
    r'transmission.*loss.*optim',
    r'reinforcement.*learn.*robot',
    r'drug.*delivery.*nanoparticle',
    r'cancer.*immunotherapy',
    r'vaccine.*efficacy.*clinical trial',
    r'antibiotic.*resist.*bacteri',
    r'protein.*structure.*predict',
    r'gene.*editing.*CRISPR',
    r'climate.*model.*precipit',
    r'crop.*yield.*predict',
    r'stock.*price.*predict',
    r'portfolio.*optimization.*risk',
    r'credit.*scoring.*machine',
    r'fraud.*detect.*transaction',
    r'network.*intrusion.*detect',
    r'manufactur.*quality.*control',
    r'supply.*chain.*disrupt',
    r'autonomous.*driving',
    r'natural.*language.*process.*legal.*document',
]

candidates = []
excluded_count = 0

for p in papers:
    title_lower = p["title"].lower()
    
    # Check hard excludes
    hard_exclude = False
    for kw in exclude_kw:
        if re.search(kw, title_lower, re.IGNORECASE):
            hard_exclude = True
            excluded_count += 1
            break
    
    if hard_exclude:
        continue
    
    # Check psychology keywords
    matched = []
    for kw in psy_kw:
        if re.search(kw, title_lower, re.IGNORECASE):
            matched.append(kw.replace(r'\b', '').replace(r'\s+', ' ').replace(r'.?', ''))
            if len(matched) >= 3:
                break
    
    if matched:
        candidates.append({
            "compact_id": p["compact_id"],
            "osf_id": p["osf_id"],
            "title": p["title"],
            "date_modified": p["date_modified"],
            "date_created": p["date_created"],
            "matched_kw": matched[:5]
        })

print(f"=== SCREENING RESULTS ===")
print(f"Candidates (matched psy keywords): {len(candidates)}")
print(f"Hard excluded: {excluded_count}")
print(f"No match (will discard): {len(papers) - len(candidates) - excluded_count}")

print(f"\n--- CANDIDATES ({len(candidates)}) ---")
for c in candidates:
    print(f"  [{c['compact_id']}] {c['date_modified']} | {c['title'][:130]}")

with open("/home/z/my-project/psyarxiv-hub/data/candidates-run3.json", "w") as f:
    json.dump(candidates, f, indent=2, ensure_ascii=False)
print(f"\nSaved to data/candidates-run3.json")