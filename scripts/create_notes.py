#!/usr/bin/env python3
"""Create curation notes for the 12 accepted papers."""
import os

INBOX = "/home/z/my-project/psyarxiv-hub/curation/inbox"

notes = [
    {
        "number": 516,
        "osf_id": "9thkv_v2",
        "title": "Developing the AAA Assessment Battery and a Multimodal Diagnostic Model for Stress-Related Disorders",
        "authors": "Sedric A Newman, Ashley Spencer, Caleb Anthony Rios",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/9thkv_v2",
        "categories": "Trauma & Stressor-Related",
        "summary": """This paper proposes an **RDoC-aligned precision psychiatry framework** called the **AAA (Affect, Autonomic, Attention) Assessment Battery**, designed to support multimodal diagnosis and treatment planning for **stress-related disorders**. The framework integrates findings from **neurobiology, genetics, and psychology** to create a standardized approach to identifying psychological profiles associated with differential treatment responsiveness to psychotherapy and pharmacology. The authors explain how **epigenetic regulation** through molecular pathways associated with stress-related biological dysfunctions, learning, and neural plasticity can influence individual responses to treatment. The AAA battery combines **epigenetic markers, neural circuit assessments, and behavioral measures** to provide a comprehensive profile of each patient. A key contribution is the framework's ability to capture how **early life adversity, attachment patterns, and individual differences** interact to shape treatment response, offering a pathway toward more individualized and effective care. The paper also addresses common **ethical, clinical, and implementation concerns** surrounding precision psychiatry, including risks of stigmatization, limited generalizability, and barriers to real-world clinical adoption. The authors propose practical strategies to reduce these barriers, including standardized protocols and clinician training frameworks.""",
        "clinical_insight": """The AAA framework offers clinicians a structured approach to **treatment selection** based on biological and psychological profiling rather than diagnosis alone. For therapists working with trauma and stress-related disorders, this model suggests that assessing patients across **affective, autonomic, and attentional domains** can identify who is most likely to benefit from specific interventions — for example, patients with particular epigenetic profiles or neural circuit patterns may respond better to certain psychotherapy approaches. The emphasis on **early life adversity and attachment** as modulators of treatment response aligns well with formulation-based clinical practice. Clinicians should be aware that precision psychiatry approaches are emerging but still face significant implementation barriers; the paper's discussion of how to reduce these barriers in everyday practice is particularly relevant for services considering adopting biomarker-informed treatment matching.""",
        "relevant_for": "Clinicians working with stress-related disorders and PTSD, particularly those interested in precision psychiatry and treatment matching. Also relevant for clinical psychologists involved in assessment and formulation of complex trauma presentations.",
    },
    {
        "number": 517,
        "osf_id": "n6skr_v2",
        "title": "Electroconvulsive Therapy (ECT) in Depression: The Role of Anhedonia",
        "authors": "Sandro Menegola, Sarah Ulrich, Magdalena D. Ridder, Gunnar Deuring, Annette Bruhl, Else Schneider",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/n6skr_v2",
        "categories": "Mood Disorders",
        "summary": """This **retrospective observational study** (N = 67 patients with depression, mean age 50.5 years) evaluated the effectiveness of **ECT in reducing anhedonia** and explored its temporal relationship with general depressive symptoms across four time points: pre-ECT, after session 6, post-treatment, and 2-3 month follow-up. Anhedonia was measured with the **Snaith-Hamilton Pleasure Scale (SHAPS)** and depression severity with the **MADRS** and **BDI-II**.

Key findings show **rapid, clinically meaningful improvements** in anhedonia: by session 6, the effect size was **d = -0.73** (p < .001), peaking post-treatment at **d = -1.07** (p < .001), and largely sustained at follow-up (**d = -0.84**, p < .001). **SHAPS response rates** rose from **44.9%** at session 6 to **61.7%** post-treatment and **63.9%** at follow-up, while **remission rates** reached **67.2%** post-ECT. Notably, anhedonia response/remission rates **exceeded** those for overall depression (e.g., post-ECT SHAPS remission 67.2% vs. MADRS remission 28.8%). Exploratory cross-lagged panel models suggested anhedonia improvements may **precede and predict** subsequent broader symptom relief (SHAPS -> BDI-II path: 0.24 vs. BDI-II -> SHAPS: 0.15). Baseline anhedonia did **not** moderate ECT's effect on general depression (interaction p = .518), and baseline SHAPS and MADRS shared only **9% of variance** (R-squared = .09).""",
        "clinical_insight": """ECT should be **considered earlier in treatment algorithms** for patients with pronounced anhedonia rather than reserved as a last resort. The rapid onset of benefit (by session 6, approximately 2 weeks) is particularly relevant for severe or urgent presentations including suicidality. The finding that anhedonia improvements may **precede and catalyze** broader symptom relief suggests ECT could break a core maintenance cycle in depression. Clinicians should note that standard antidepressants show limited antianhedonic efficacy and serotonergic agents may even worsen emotional blunting — ECT represents a viable alternative for patients with **treatment-resistant, anhedonia-predominant depression**. The SHAPS is recommended as a routine measure to track anhedonia separately from general depression severity, as the two are largely independent (only 9% shared variance).""",
        "relevant_for": "Psychiatrists and clinical psychologists working with treatment-resistant depression, particularly patients with prominent anhedonia. Also relevant for clinicians involved in ECT treatment decisions and psychoeducation.",
    },
    {
        "number": 518,
        "osf_id": "4yhev_v1",
        "title": "A network approach to examining alcohol use and AUD risk factors across adolescence and adulthood",
        "authors": "Karis Colyer-Patel, Emese Kroon, Christophe Romein, ajay handa, Janna Cousijn",
        "date_posted": "2026-07-05",
        "source_date": "2026-07-05",
        "link": "https://osf.io/preprints/psyarxiv/4yhev_v1",
        "categories": "Addiction & Substance Use",
        "summary": """This cross-sectional **network analysis** (N = 933; adolescents aged 16-25, n = 421; adults aged 35-65, n = 252) examined the **item-level structure of the AUDIT** and the **interconnections among AUD risk factors** including age of onset, craving, drinking motives, mental health symptoms, impulsivity, and tobacco use.

In the AUDIT item network, **binge drinking** was the most central node (strength = 1.42), acting as the key bridge between consumption and use-related problems. The strongest edges were binge drinking <-> drinks/day (**r = 0.52**) and frequency <-> binge drinking (**r = 0.37**). In the risk factor network, **AUDIT-C** (consumption) was most central (strength = 1.42), while **enhancement motives** showed the highest expected influence (1.15). **Mental health symptoms were linked to executive functioning** (r = 0.47), and **coping motives connected to both AUDIT-P and mental health** (r = 0.20 and 0.27 respectively). Critically, **no significant network differences** were found between adolescents and adults in either the AUDIT structure or risk factor network, though adolescents reported significantly higher levels of alcohol use, problems, impulsivity, and mental health symptoms.""",
        "clinical_insight": """**Binge drinking is the primary bridge** between consumption patterns and alcohol-related problems across the lifespan, making it a prime target for early intervention. The finding that **network structure is stable across age groups** suggests the same intervention frameworks may be broadly applicable from adolescence through mid-adulthood. Two distinct clinical pathways emerge: (1) a **positive-reinforcement pathway** (enhancement and social motives -> consumption), suggesting interventions providing alternative reward sources may be effective; and (2) a **negative-reinforcement pathway** (coping motives -> problems, linked to mental health symptoms), indicating a need for targeted CBT addressing comorbid anxiety/depression. The strong **mental health <-> executive functioning link** (r = 0.47) underscores the importance of integrating cognitive assessments into AUD screening. Clinicians should routinely assess drinking motives to identify which pathway predominates for each patient.""",
        "relevant_for": "Addiction specialists, clinical psychologists treating alcohol use disorder, and therapists working with comorbid anxiety/depression and substance use.",
    },
    {
        "number": 519,
        "osf_id": "uc63x_v2",
        "title": "EEG Predictors of Transition from Clinical High Risk to Psychotic Disorders: A Systematic Review with Implications for Data Harmonisation",
        "authors": "Finn Brady, Anja Stanojlovic, Sean Naughton, Mary Clarke, Keith Gaynor, Klaus Kessler",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/uc63x_v2",
        "categories": "Psychosis & Schizophrenia",
        "summary": """This **PRISMA-guided systematic review** (34 studies, PROSPERO-registered) examined baseline EEG differences between CHR individuals who later transitioned to psychosis (CHR-T) and those who did not (CHR-NT). Random-effects meta-analyses of Event-Related Potentials yielded the most consistent findings for two markers:

- **Duration Mismatch Negativity (MMN)**: k = 9, **Hedges' g = 0.54** (95% CI [0.17, 0.92], p = .004) — CHR-T individuals showed significantly reduced MMN amplitudes
- **P3b**: k = 5, **Hedges' g = -0.52** (95% CI [-0.89, -0.14], p = .007) — reduced P3b in converters
- **P3a**: k = 4, **g = -0.28** (p = .004) — smaller but significant effect
- **N100**: k = 2, g = 0.26 (p = .005)

P50 sensory gating, N200, and P200 showed no significant group differences. The review highlights substantial **methodological inconsistency** across studies (different CHR instruments, EEG paradigms, outcome definitions) and proposes the **TRIDENT framework** for standardizing future biomarker research. The authors recommend expanding beyond sensory ERPs to include higher-order cognitive tasks and treating specific diagnoses as secondary rather than primary outcomes.""",
        "clinical_insight": """**Duration MMN and P300 are the most promising EEG prognostic markers** for psychosis transition in CHR populations. Duration MMN is particularly clinically practical because it is **pre-attentional, passively elicited**, and reflects early sensory prediction error processing. These biomarkers could inform **risk stratification** within CHR services, helping allocate intensive early intervention (CBT for psychosis, antipsychotic medication) to those most likely to benefit. However, the substantial methodological heterogeneity and small CHR-T subgroups in many studies mean these markers are **not yet ready for routine clinical use**. Clinicians in early psychosis services should be aware that CHR diagnostic instruments vary considerably (CAARMS, SIPS/COPS, BSABS, SPI-A) and that comorbidities (especially autism spectrum disorder) can reverse the P300-transition relationship. The field would benefit from standardized EEG acquisition protocols and shared data repositories.""",
        "relevant_for": "Clinicians in early psychosis intervention services, clinical psychologists conducting risk assessments, and researchers interested in biomarker-based treatment stratification.",
    },
    {
        "number": 520,
        "osf_id": "fdb2u_v1",
        "title": "Internal Structure, Reliability, and Gender-Related Item Functioning of the Borderline Personality Inventory",
        "authors": "Emilia Soroko, Pawel Kleka, Lidia W. Cierpiatkowska, Falk Leichsenring",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/fdb2u_v1",
        "categories": "Personality Disorders",
        "summary": """This study provides the **first formal psychometric validation** of the Polish version of Leichsenring's **Borderline Personality Inventory (BPI)**, a 51-item self-report measure grounded in **Kernberg's object relations theory** of borderline personality organization (BPO). The validation sample comprised **N = 600** adults (300 women, 300 men; mean age ~23.8), assembled via optimal pair matching from seven datasets.

Confirmatory factor analysis supported a **four-factor model** with excellent fit: **CFI = .995, TLI = .995, RMSEA = .039**. The four factors — **Identity Diffusion, Primitive Defences, Impaired Reality Testing, and Fear of Fusion** — showed substantial inter-correlations (.46-.88), consistent with Kernberg's view of interrelated BPO dimensions. Overall reliability was strong (**alpha = .90, omega = .92, CR = .84**), with subscale alphas ranging from .68 (Fear of Fusion) to .79 (Identity Diffusion). IRT analysis revealed **greater measurement precision at higher BPO severity levels**. After Holm correction, **no item showed significant gender-related DIF**, supporting equitable use across women and men. However, AVE values were below .50 for three of four factors, and no external clinical validity criteria were collected.""",
        "clinical_insight": """The BPI offers a **theory-grounded, brief screening tool** for assessing borderline personality organization within object relations-based clinical frameworks. The four-factor structure maps directly onto Kernberg's theoretical model, giving clinicians a **dimensional severity indicator** rather than a binary diagnostic decision. The absence of gender DIF is particularly important given longstanding concerns about gender bias in BPD diagnosis. However, clinicians should note significant limitations: the validation used a **non-clinical, young-adult sample** (mean age ~24) with no external clinical criteria, so the BPI **should not replace clinician-administered interviews** such as the STIPO-R. The Impaired Reality Testing subscale showed a severely restricted range (80.8% scored zero) in this community sample, suggesting it may only differentiate in more severe populations. The instrument may complement severity-based approaches aligned with ICD-11 and DSM-5 Alternative Model frameworks.""",
        "relevant_for": "Clinicians and researchers working with personality disorders, particularly those using psychodynamic or object relations-based approaches to BPD assessment and formulation.",
    },
    {
        "number": 521,
        "osf_id": "7mxn3_v2",
        "title": "Advancing Idiographic Methodology for Data-Driven Treatment Personalization: Comparing ARIMAX, Network, and Tree-Based Approaches",
        "authors": "William Li, Cristobal Hernandez Contreras, Joseph Ciarrochi, Madeleine I. Fraser, Steven C. Hayes, Clarissa W. Ong, Baljinder K. Sahdra",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/7mxn3_v2",
        "categories": "Therapeutic Modalities",
        "summary": """This study compared **six idiographic (person-specific) methods** for identifying individual-level process-outcome relationships in longitudinal psychotherapy data: two ARIMAX-based time series models (**bivariate and multivariate i-ARIMAX**), two network approaches (**GIMME, indSEM**), and two tree-based algorithms (**Boruta and the novel Time Series Boruta / tsBoruta**). Simulations tested these across diverse conditions varying in linear/nonlinear effects, autoregressive patterns, trends, interactions, predictor counts, and sample sizes.

For **linear effects**, i-ARIMAX, iBoruta, and tsBoruta achieved the highest F1 scores and specificity. **Tree-based approaches excelled at detecting nonlinear effects and interactions**. Methods failing to account for time-series dependencies showed significant performance drops as autoregressive patterns increased. In an empirical application, i-ARIMAX and tsBoruta **replicated the group-level loneliness-depressed mood link** while revealing **substantial individual-level heterogeneity** and distinct predictor patterns. The authors recommend **combining i-ARIMAX and tsBoruta** as a practical workflow that balances sensitivity and specificity, captures both linear and nonlinear processes, and supports data-driven, idiographic psychological treatment planning.""",
        "clinical_insight": """This paper provides **practical guidance for clinicians and researchers** seeking to personalize psychological treatment using intensive longitudinal data (e.g., experience sampling, daily diaries). The recommended **i-ARIMAX + tsBoruta workflow** allows clinicians to identify which specific processes drive symptom change for **individual patients**, moving beyond one-size-fits-all treatment protocols. For example, while group-level data might suggest loneliness drives depression, an individual patient's data might reveal that sleep disruption is their primary driver — allowing the therapist to adjust the treatment focus accordingly. The finding that tree-based methods better capture **nonlinear relationships** is clinically important because many psychological processes (e.g., emotion regulation, therapeutic alliance ruptures) operate non-linearly. Clinicians collecting routine outcome monitoring data can use these methods to create **personalized case formulations** and track treatment progress at the individual level.""",
        "relevant_for": "Clinicians and researchers interested in personalized psychotherapy, routine outcome monitoring, intensive longitudinal data analysis, and data-driven treatment planning.",
    },
    {
        "number": 522,
        "osf_id": "ydepn_v1",
        "title": "Psychometric Validation of the Azerbaijani Version of the Attitudes Towards Mental Health Problems Scale (ATMHPS-AZ) Among University Students: The Role of Cultural Factors",
        "authors": "Nigar Shahhuseynbayova, Aynur Bunyatova, Mushviq Mustafayev, Yasuhiro Kotera",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/ydepn_v1",
        "categories": "Psychopathology & Assessment",
        "summary": """This study developed and psychometrically validated the **Azerbaijani version of the 35-item Attitudes Towards Mental Health Problems Scale (ATMHPS)** among **N = 946 undergraduates**, following WHO translation and cultural adaptation guidelines. The ATMHPS assesses attitudes and shame around mental health problems, which are significant barriers to help-seeking.

Analyses confirmed excellent total reliability (**alpha = 0.954, omega = 0.956**) and supported the **original seven-factor structure** through both EFA and CFA. Convergent validity was established with the Self-Compassion Scale, and criterion-related validity with the Stigma-9 Questionnaire. Stigma levels were **moderate overall**, with the **highest stigma in Disclosure Concerns** and the **lowest in Family Attitudes and Family Burden**. **Year of study** emerged as the only statistically significant (albeit weak) predictor of stigma, with students in later years reporting slightly higher levels after controlling for demographics. The scale is positioned as a reliable tool for research and **stigma-reduction efforts** in the Azerbaijani context and potentially other post-Soviet societies with similar cultural dynamics around mental health.""",
        "clinical_insight": """The ATMHPS-AZ provides a **culturally validated instrument** for assessing mental health stigma in Azerbaijani and similar cultural contexts where family expectations, social norms, and concerns about disclosure shape help-seeking behavior. The finding that **Disclosure Concerns** are the highest stigma domain suggests that interventions targeting fear of social consequences and privacy breaches may be most impactful in this population. The relatively lower stigma in **Family Attitudes** and **Family Burden** domains indicates that families may be more supportive than patients assume — an important insight for **family-inclusive treatment approaches**. For clinicians working with culturally diverse populations, this study demonstrates the necessity of **culturally adapting assessment tools** rather than simply translating them. The seven-factor structure allows clinicians to identify specific stigma domains to target in psychoeducation and anti-stigma interventions, supporting more precise and culturally sensitive clinical practice.""",
        "relevant_for": "Clinicians working with culturally diverse populations, particularly post-Soviet communities. Relevant for those involved in stigma reduction, psychoeducation, and increasing help-seeking in university settings.",
    },
    {
        "number": 523,
        "osf_id": "se5af_v1",
        "title": "Is everyone looking at me? The perception of direct gaze in social anxiety and its moderation by emotional expression",
        "authors": "Madeleine Moses-Payne, Georgina Krebs, Raphaelle Delpech, Tosia Przyborowska, Argyris Stringaris",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/se5af_v1",
        "categories": "Anxiety & OCD",
        "summary": """This study investigated the **Cone of Gaze (CoG)** — the range of gaze angles perceived as looking at oneself — as a proposed **biobehavioural marker** of social anxiety disorder. The research combined **meta-analysis** with **well-powered experimental replications** (total N = 514) to examine: (1) individual differences in CoG between socially anxious and non-anxious individuals, (2) CoG differences in response to angry vs. neutral facial expressions, and (3) the interaction between these factors.

The meta-analyses revealed significantly **wider CoG for socially anxious individuals** (10 studies, 403 participants) and **wider CoG for angry vs. neutral expressions** (9 studies, 523 participants). However, the existing evidence was **sparse, highly heterogeneous**, and often involved small samples. Critically, the **experimental replications (N = 514) did not replicate either effect** — neither social anxiety nor emotional expression significantly influenced CoG. The authors highlight the need for **larger, more transparent datasets** to accurately estimate CoG effects and assess the translational potential of gaze perception as a clinical marker for social anxiety.""",
        "clinical_insight": """This study delivers an important **cautionary message** about prematurely adopting putative cognitive markers in clinical practice. The Cone of Gaze had been proposed as a biobehavioural marker for social anxiety, but well-powered replications **failed to support** this claim. For clinicians, this underscores that **small-sample findings in cognitive psychopathology research should not be directly translated into clinical tools** without adequate replication. The study's integrated approach — combining meta-analysis with large-scale experimental replication — provides a methodological template for evaluating other proposed markers (e.g., attentional bias, interpretive bias) before clinical adoption. While gaze perception may still play a role in social anxiety phenomenology, it does not appear to operate through a consistently wider Cone of Gaze. Clinicians should continue to rely on established assessments and be skeptical of novel cognitive markers until robustly replicated.""",
        "relevant_for": "Clinical psychologists and researchers working with social anxiety disorder. Particularly relevant for those interested in cognitive biases and translational cognitive neuroscience in mental health.",
    },
    {
        "number": 524,
        "osf_id": "thqgu_v1",
        "title": "Relational Specificity of Mentalizing and Structural Personality Functioning in Adult Attachment Relationships",
        "authors": "Karolin Holy, Tobias Nolte, Sebastian Walther, Sarah Kittel-Schneider, Martin Walter, Anna Linda Leutritz",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/thqgu_v1",
        "categories": "Personality Disorders",
        "summary": """This **preregistered cross-sectional study** (N = 100 German-speaking adults in romantic relationships) examined within-person differences in **reflective functioning (mentalizing)** and **structural personality functioning** across romantic partner vs. primary parental attachment contexts. Context-adapted measures included the PRFQ (Interest and Curiosity, Certainty about Mental States) and OPD-SQ (Self-Regulation, Regulation of Object Relations, Experiencing Affect).

Using linear mixed-effects models, participants showed significantly **higher mentalizing in the partner context**: Interest and Curiosity (**d = 0.53**, p < .001) and Certainty about Mental States (**d = 0.23**, p = .023). **Self-regulation difficulties** (d = -0.30) and **affect experiencing impairments** (d = -0.25) were lower in the partner context. **Relationship-specific stress** showed the largest effect (d = -0.67, p < .001).

In regression analyses, **relationship-specific self-efficacy** was the strongest and most consistent predictor across contexts — particularly in the parental context where it predicted Certainty about Mental States with **beta = .73** (p < .001). In partner contexts, **attachment insecurity, mentalizing deficits, and relational stress** predicted regulatory difficulties. The findings demonstrate that mentalizing and personality functioning are **relationally specific** rather than fixed traits, supporting mentalization-based therapy's emphasis on context-dependent profiles.""",
        "clinical_insight": """This study has direct implications for **mentalization-based therapy (MBT)** and **attachment-informed clinical practice**. The key finding is that **relationship-specific self-efficacy is the primary therapeutic lever**, especially for entrenched parental relationships (beta = .73 for predicting certainty about mental states). This suggests that strengthening patients' perceived competence in managing relational challenges — rather than targeting mentalizing directly — may be the most effective clinical strategy. The relational specificity of mentalizing supports **context-sensitive case formulation**: therapeutic focus should be calibrated to the relational domain being addressed. In couple-focused work, addressing **attachment insecurity and relational stress** is productive; in work on parental dynamics, building **agency and relational confidence** may be more critical. The moderate effect sizes (d = 0.23-0.67) indicate that mentalizing is expressed differently depending on relational dynamics — clinicians should assess mentalizing **across specific attachment relationships** rather than using global measures.""",
        "relevant_for": "Clinicians practicing mentalization-based therapy, attachment-informed psychotherapy, and psychodynamic therapy. Particularly relevant for work with personality pathology and complex attachment trauma.",
    },
    {
        "number": 525,
        "osf_id": "7xvbd_v1",
        "title": "Visuospatial Orienting in Working Memory is Preserved in Adults with ADHD Symptoms",
        "authors": "Luisa Superbia-Guimaraes, Amy Atkinson, Richard Allen, Valerie Camos",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/7xvbd_v1",
        "categories": "Neurodivergence",
        "summary": """Two well-powered online experiments (total N = 191 adults aged 18-35) tested whether deficient **visuospatial orienting** during encoding (pre-cues) and maintenance (retro-cues) underlies working memory deficits in adults with ADHD symptoms. Experiment 1 used colour stimuli (47 ADHD-symptomatic, 59 controls); Experiment 2 used unfamiliar shapes to increase difficulty (37 symptomatic, 48 controls). ADHD symptoms were assessed with the **6-item ASRS screener**.

Across both experiments, **strong cueing benefits** emerged for both groups on accuracy (d') and reaction time. However, **Bayesian analyses provided evidence against group differences** and group x cueing interactions. In Experiment 1: BF_excl(group) = 2.94, BF_excl(interaction) = 7.3. In Experiment 2: BF_excl(group) = 3.45, BF_excl(interaction) = 5.74. No significant correlations were found between ASRS scores and performance measures. Despite robust symptom differences between groups (ADHD total ~19 vs. ~8.5 in controls), **no baseline WM deficit** emerged even in neutral-cue trials. The authors propose that ADHD-related WM difficulties may stem from impaired **intentional disengagement** (removing irrelevant information) rather than from orienting attention to relevant information.""",
        "clinical_insight": """This study challenges common assumptions about ADHD-related cognitive deficits. Adults with ADHD symptoms showed **intact visuospatial orienting** in working memory, suggesting that attentional mechanisms for directing focus are preserved. The proposed alternative explanation — that the deficit lies in **intentional disengagement** (suppression of irrelevant, outdated representations) rather than orienting — has important clinical implications. It suggests that compensatory strategies should focus on **reducing interference** (e.g., structured environments, clear task prioritization, minimizing distractions) rather than on improving attentional orienting per se. The finding that WM performance was comparable under controlled, low-interference conditions suggests that **external structure** — cues, clear priorities, organized environments — may allow individuals with ADHD to perform effectively. This aligns with occupational and educational accommodations that provide scaffolding rather than trying to train attention directly. Clinicians should be cautious about over-pathologizing ADHD cognition and instead focus on **environmental modifications and compensatory strategies**.""",
        "relevant_for": "Clinicians working with adult ADHD, occupational therapists, and those providing psychoeducation about ADHD cognitive functioning. Relevant for workplace and educational accommodation planning.",
    },
    {
        "number": 526,
        "osf_id": "72duz_v2",
        "title": "Comparing the Beta-Binomial and the Linear Models to Analyze Discrete, Bounded Scores for Normative Data from Neuropsychological Tests",
        "authors": "Javier Oltra-Cucarella, Rafael de Andrade Moral, Ruben Perez-Elvira, Beatriz Bonete-Lopez, Miriam Sanchez-Sansegundo, Esther Sitges-Macia",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/72duz_v2",
        "categories": "Psychopathology & Assessment",
        "summary": """This methodological study (N = 165 cognitively healthy individuals) compared the **linear model** with the **binomial** and **beta-binomial models** for analyzing discrete, bounded scores from neuropsychological tests, using verbal memory test data. The beta-binomial model showed substantially better fit than the linear model (**BIC = 463.6 vs. 583.4**) and superior model adequacy as assessed by half-normal plots with simulated envelopes (points outside the envelope: **1.82%** for beta-binomial vs. **32.73%** for linear). The beta-binomial model did not predict scores outside the real range (a common problem with linear models for bounded data), and four worked examples demonstrated its practical advantages. The authors provide **R scripts** for researchers and clinicians to calculate randomized quantile residuals from beta-binomial models, facilitating adoption in clinical and research settings.""",
        "clinical_insight": """Neuropsychological test scores are inherently **discrete and bounded** (e.g., 0-50 on a word list recall), yet are almost universally analyzed with linear models that can predict impossible scores and poorly fit the data at extremes. The beta-binomial model provides a **more appropriate statistical framework** that respects the bounded nature of these scores, leading to more accurate normative data and better clinical decision-making. For clinicians interpreting neuropsychological results, this means that cut-off scores, confidence intervals, and percentile rankings derived from linear models may be **inaccurate — particularly at the extremes** where clinical decisions often matter most. The provided R scripts make it practical for neuropsychology services to adopt this approach. This is especially relevant for **mild cognitive impairment and dementia screening**, where accurate boundary performance estimation is critical for clinical decisions.""",
        "relevant_for": "Clinical neuropsychologists, researchers developing normative data, and clinicians interpreting neuropsychological test scores in dementia and cognitive disorder assessments.",
    },
    {
        "number": 527,
        "osf_id": "4uacf_v2",
        "title": "Meta analysis shows video-based monitoring technology (Oxevision) has no statistically significant association with four of five measures of patient safety",
        "authors": "Hat Porter",
        "date_posted": "2026-06-18",
        "source_date": "2026-06-18",
        "link": "https://osf.io/preprints/psyarxiv/4uacf_v2",
        "categories": "Psychopathology & Assessment",
        "summary": """This critical appraisal re-examines a meta-analysis by Kekic, Rose, and Bayley (2026) that evaluated **Oxevision** (now rebranded as 'LIO') — a video-based monitoring technology using cameras, infrared, and video analytics installed in mental health patient bedrooms — across six NHS Mental Health Trusts. The original study claimed "notable reductions across all five outcome measures" (self-harm, falls, assaults, restraint, rapid tranquilisation). However, Porter identifies **serious methodological and reporting problems**:

- **Non-significant results presented as positive**: For restraint (95% CI: -50.2%, 15.2%) and rapid tranquilisation (95% CI: -60.1%, 10.3%), confidence intervals cross zero, indicating non-significance. P-values were systematically omitted.
- **Flawed control comparisons for self-harm**: Relative risk calculations obscured vast baseline differences; self-harm **increased on six of twelve wards** post-installation.
- **Data integrity issues**: Half of patient IDs were missing for one Trust; an anomalous standard deviation (17,484.28 vs. typical 0.31-1.56) suggests dataset errors.
- **Inappropriate fixed effects model** despite large heterogeneity, and no pre-registered protocol.

After correcting for these issues, **four of five outcomes show no statistically significant association** with Oxevision installation. Only falls retained nominal significance, undermined by contaminated data from partially-equipped wards.""",
        "clinical_insight": """This critique is essential reading for clinicians and service leaders in **inpatient psychiatric settings**. Video-recording patients in their bedrooms constitutes a serious infringement on the right to private space, and the evidence base **does not support** Oxevision's claimed safety benefits. The original meta-analysis — conducted "in partnership" between the company and NHS customers — overstates its conclusions by omitting p-values and presenting non-significant results as positive findings. This case illustrates the importance of **critical appraisal skills** when evaluating industry-partnered research. Given that Oxevision was adopted by half of NHS Trusts in England (now reduced to 36% following concerns), and that the 2024 Griffiths et al. systematic review also found "insufficient evidence," clinicians and Trust leaders should exercise significant caution. The ethical, legal, and clinical governance concerns about continuous video surveillance of vulnerable patients are substantial, and the supposed evidence base does not justify the practice.""",
        "relevant_for": "Psychiatrists, mental health nurses, and service leaders in inpatient psychiatric settings. Also relevant for clinicians involved in clinical governance and evidence-based practice evaluation.",
    },
]

for note in notes:
    filename = f"{note['number']}-{note['osf_id']}.md"
    filepath = os.path.join(INBOX, filename)
    content = f"""---
osf_id: {note['osf_id']}
title: {note['title']}
authors: {note['authors']}
date_posted: {note['date_posted']}
source_date: {note['source_date']}
link: {note['link']}
categories: {note['categories']}
peer_reviewed: false
number: {note['number']}
---

## Summary

{note['summary']}

## Clinical Insight

{note['clinical_insight']}

## Relevant For

{note['relevant_for']}

## Notes

Curated from PsyArXiv preprint. Based on {"full PDF text" if note['osf_id'] in ['n6skr_v2','4yhev_v1','uc63x_v2','fdb2u_v1','thqgu_v1','7xvbd_v1','4uacf_v2'] else "abstract and description"}.
"""
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created {filename}")

print(f"\nTotal: {len(notes)} curation notes created")