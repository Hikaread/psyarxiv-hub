#!/usr/bin/env python3
"""Fix 9 curation notes that had placeholder summaries."""
import os

CURATION_DIR = os.path.expanduser("~/my-project/psyarxiv-hub/curation/inbox")

notes = {
    "403-6a72c.md": """---
title: Parenting and children's ADHD symptoms: A longitudinal twin-difference study
authors: Sophie von Stumm
osf_id: 6a72c_v1
number: 403
date_posted: 2026-06-28
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/6a72c_v1
published: false
categories: Neurodivergence
---

## Summary
Using a population-based sample of 7,429 children (including 2,762 MZ and 2,393 same-sex DZ twins) assessed at ages 8, 12, and 14, this study tested whether associations between parenting practices and children's ADHD symptoms reflect genuine environmental effects or shared genetic confounding. At the population level, random-intercept cross-lagged panel models (RI-CLPM) suggested significant bidirectional effects between ADHD symptoms and harsh discipline, constructive parenting, and negative parent-child feelings. However, twin-difference models that controlled for family-level genetic and shared-environment confounds revealed that all parenting-ADHD associations were attenuated to non-significance. The genetic confounding was substantial: MZ twin correlations for ADHD symptoms were .73-.80 across waves, compared to .40-.49 for DZ twins, indicating strong heritability. Parenting measures also showed moderate heritability (.30-.50). The study concludes that the observed parenting-ADHD associations at the population level are largely spurious, driven by gene-environment correlations rather than causal parenting effects.

## Clinical Insight
This finding has direct implications for psychoeducation and family therapy with ADHD families. Clinicians should be cautious about attributing children's ADHD symptoms to parenting quality, as this study provides strong evidence that such associations reflect genetic confounding rather than causal environmental influence. Family interventions for ADHD should focus on accommodating the child's neurodevelopmental needs and reducing family stress rather than modifying parenting practices as a primary treatment target, though supportive parenting remains valuable for broader child wellbeing. The findings also underscore the importance of genetic-informed designs in clinical research before drawing causal inferences about parenting and child psychopathology.

## Relevant For
Clinicians working with ADHD families, family therapists, and researchers studying gene-environment interplay in neurodevelopmental conditions.

## Notes
Twin-difference design effectively controls for shared family confounds. Single-author paper from University of York. DOCX source file.
""",

    "410-m3sud.md": """---
title: Emotional and physical abuse have dissociable impacts on punishment learning and task engagement during adolescence
authors: Holly Sullivan-Toole, Jeremy Haynes, John McClellan France, Suzanne C. Perkins, Monica Luciana, Bart Larsen, Thomas Olino
osf_id: m3sud_v1
number: 410
date_posted: 2026-07-01
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/m3sud_v1
published: false
categories: Trauma & Stressor-Related
---

## Summary
This longitudinal study (N=166, ages 9-17) examined how specific subtypes of childhood adversity — emotional abuse and physical abuse — differentially impact reinforcement learning processes during adolescence. Using a probabilistic reward/punishment task combined with computational reinforcement learning modeling, the study decomposed learning into distinct component processes: reward learning rate, punishment learning rate, win/loss frequency sensitivity, and go bias. Emotional abuse specifically attenuated normative developmental increases in punishment learning rate (FDR < .05), meaning emotionally abused adolescents showed blunted learning from negative feedback compared to typically-developing peers. Physical abuse attenuated normative increases in both go bias (general tendency to engage) and a summary score of reward learning, indicating reduced behavioral engagement and reward sensitivity. Crucially, adversity did not predict differences in net task success, suggesting that abused youth reach similar behavioral outcomes through compensatory but divergent learning strategies. Broad composite adversity measures obscured these subtype-specific effects, highlighting the need for fine-grained characterization in both research and clinical assessment.

## Clinical Insight
The dissociable effects of emotional versus physical abuse on learning processes have important implications for case formulation and treatment planning. Adolescents with emotional abuse histories may have specific difficulty learning from negative consequences — a pattern that could manifest as repeating maladaptive behaviors despite apparent awareness of repercussions. This aligns with clinical observations of patients who seem resistant to behavioral feedback. In contrast, physically abused adolescents may show more generalized motivational withdrawal. Clinicians should assess specific adversity subtypes rather than relying on composite trauma scores, as the intervention targets differ: emotionally abused youth may benefit from cognitive restructuring around feedback interpretation, while physically abused youth may need motivational enhancement and reward-based engagement strategies. The finding that abused youth achieve similar outcomes through different strategies also suggests inherent resilience that can be leveraged therapeutically.

## Relevant For
Trauma-focused clinicians, adolescent psychologists, and researchers studying adversity-specific mechanisms in psychopathology.

## Notes
Longitudinal design with RL modeling. Multi-site study (University of Minnesota, Georgia Southern, Temple). DOCX source file.
""",

    "411-z329b.md": """---
title: Bringing together health and education with lived experience to co-produce a new pathway of assessment and support for Developmental Coordination Disorder
authors: Lucy H. Eddy, Cara E. Staniforth, Maryam I. Shuaib, Nell Schofield, Nat K. Merrick, Jade Jukes, Rebecca Murray
osf_id: z329b_v3
number: 411
date_posted: 2026-06-28
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/z329b_v3
published: false
categories: Neurodivergence
---

## Summary
Developmental Coordination Disorder (DCD) affects approximately 5-6% of school-age children but remains significantly under-diagnosed, with existing assessment pathways described as convoluted and difficult to navigate. This study used a Double Diamond design approach (diverge-converge cycles) in a half-day co-production workshop with 13 stakeholders spanning lived experience, paediatrics, physiotherapy, occupational therapy, school leadership, SEN teaching, school nursing, and inequality management. Thematic analysis of workshop discussions and post-workshop questionnaires identified consensus on a new four-element DCD pathway: (1) identifying and mobilising key leaders across health and education systems; (2) embedding evidence-based DCD screening tools in routine educational assessments; (3) creating clear, simplified referral routes that reduce the current multi-step complexity; and (4) establishing joint health-education oversight to monitor pathway fidelity. Participants rated the co-produced pathway as highly acceptable but identified potential barriers including resource constraints, professional boundary issues between health and education sectors, and variability in school-level capacity. The study demonstrates that structured co-production with diverse stakeholders can generate practical, systems-level solutions for neurodevelopmental assessment pathways.

## Clinical Insight
The identified pathway offers a practical template for clinical services working to improve DCD identification, particularly in underserved populations where current diagnostic delays average 4-5 years. The emphasis on embedding screening within educational settings rather than relying solely on clinical referral is noteworthy — many children with DCD never present to clinical services but are visible in schools. Clinicians involved in neurodevelopmental assessment should advocate for cross-sector collaboration and consider whether their local pathways replicate the barriers identified here. The co-production methodology itself is also instructive: including lived experience alongside professionals generated solutions that single-sector working groups typically miss, particularly around reducing pathway complexity and addressing inequalities in access.

## Relevant For
Neurodevelopmental assessment teams, paediatric occupational therapists, educational psychologists, and service designers working on DCD or similar neurodevelopmental pathways.

## Notes
Co-production study using Double Diamond methodology. Conducted in Bradford, UK. DOCX source file.
""",

    "412-m2vw4.md": """---
title: Regulation Without Regulating? Exploring Misalignment Between Self-Reported Emotion Regulation Attempts and Strategy Use
authors: Aya Uchida, Katharine Greenaway, Valentina Bianchi, Maya Tamir, Elise Kalokerinos
osf_id: m2vw4_v2
number: 412
date_posted: 2026-06-29
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/m2vw4_v2
published: false
categories: Therapeutic Modalities
---

## Summary
Across three studies (total N > 600), this pre-registered investigation examined whether people who report regulating their emotions actually use specific regulation strategies. Study 1 (N=242) found that 72% of participants who reported attempting to regulate their emotions during a negative mood induction did not subsequently use any of the eight measured cognitive reappraisal or distraction strategies, as captured by both open-ended responses and forced-choice selection. Study 2 (N=218) conceptually replicated this misalignment using a different mood induction and expanded strategy set, showing the effect was not task-specific. Study 3 (N=203) demonstrated that the misalignment was not explained by regulation success, motivation, or difficulty ratings. Computational modeling revealed that self-reported regulation attempts predicted increased positive affect change only when participants actually deployed strategies; mere reported intention without strategy use had no effect on mood. The authors propose that self-report measures of emotion regulation conflate intention with execution, leading to systematic overestimation of regulatory behavior in both research and clinical contexts.

## Clinical Insight
This finding has significant implications for clinical assessment and therapy outcomes measurement. Many widely-used measures (e.g., ERQ, CERQ) ask patients whether they typically use certain regulation strategies, but this research suggests such self-reports may capture intentions rather than actual behavior. In CBT and other therapies that target emotion regulation, clinicians should be aware that patients may genuinely believe they are using techniques while failing to implement them effectively. Therapeutic homework that includes specific behavioral tracking (e.g., momentary strategy use logs) may provide more accurate assessment than retrospective questionnaires. The dissociation between intention and execution also parallels clinical observations of patients who understand regulation concepts intellectually but struggle with in-the-moment application — suggesting that therapy should focus on building procedural skill and automaticity rather than just conceptual understanding.

## Relevant For
CBT practitioners, emotion regulation researchers, and clinicians using self-report measures of coping and regulation in assessment or outcome monitoring.

## Notes
Three-study pre-registered investigation. University of Melbourne and Hebrew University of Jerusalem. DOCX source file.
""",

    "413-zdm4c.md": """---
title: Anxiety modulates sensitivity and response bias in the AX CPT task
authors: Garima Joshi, Bhoomika R. Kar
osf_id: zdm4c_v1
number: 413
date_posted: 2026-07-01
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/z329b_v1
published: false
categories: Anxiety & OCD
---

## Summary
This study investigated how anxiety differentially affects proactive and reactive cognitive control using the AX Continuous Performance Task (AX-CPT) across two experiments. In Experiment 1a, healthy young adults grouped into low, medium, and high trait anxiety categories showed that high trait anxious participants maintained intact overall task performance and contextual sensitivity, but exhibited stronger cue-based expectancy bias (B_dprime = .73 vs .50 for low anxiety) and greater susceptibility to probe-level interference. This suggests high trait anxiety enhances strategic reliance on predictive cues without impairing the proactive control mechanism itself. In Experiment 1b, participants with generalized anxiety disorder (GAD) were compared directly with high trait anxious participants. The GAD group demonstrated fundamentally different patterns: reduced contextual sensitivity (A_prime = .84 vs .90), lower cue and probe discriminability, and poorer overall accuracy (d_prime = 2.14 vs 2.86), despite comparable strategic response bias. The authors argue that high trait anxiety and GAD involve qualitatively distinct cognitive control alterations: trait anxiety modulates the strategic weighting of contextual cues, while GAD is associated with a generalized degradation in the fidelity of context representation, suggesting a threshold effect at the clinical disorder level.

## Clinical Insight
The qualitative distinction between trait anxiety and GAD in cognitive control has direct implications for case formulation and treatment targeting. Patients with high trait anxiety but without GAD may have intact cognitive control capacity but strategically over-rely on predictive cues — a pattern that could manifest as hypervigilance to threat cues in social situations while maintaining adequate overall functioning. In contrast, GAD patients appear to have a more fundamental deficit in maintaining and using contextual information, which could underlie the pervasive worry characteristic of the disorder. For CBT, this suggests that cognitive restructuring targeting cue-interpretation biases may be sufficient for high trait anxiety, while GAD may require more intensive cognitive control training alongside standard therapeutic approaches. The AX-CPT paradigm could also serve as a potential cognitive marker for differentiating normal-range anxiety from clinical GAD.

## Relevant For
Anxiety clinicians, neuropsychologists, and researchers studying cognitive control in anxiety spectrum conditions.

## Notes
Two-experiment design comparing trait anxiety and GAD. University of Allahabad, India. DOCX source file.
""",

    "414-zbwsx.md": """---
title: What do people believe about artificial intelligence chatbots for mental health support? Evidence from Greece
authors: Aglaia Katsiroumpa, Parisis Gallos, Paschalina Lialiou, Ioannis Moisoglou, Olga Galani, Panagiota Peleka, Angeliki Triantafillaki, Maria Tsiachri, Petros Galanis
osf_id: zbwsx_v1
number: 414
date_posted: 2026-06-30
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/zbwsx_v1
published: false
categories: Therapeutic Modalities
---

## Summary
This cross-sectional study (conducted January 2026) examined public attitudes toward AI chatbots for mental health support using a convenience sample in Greece. Two validated instruments were administered: the Artificial Intelligence in Mental Health Scale (AIMHS) measuring attitudes toward AI mental health chatbots specifically, and the Artificial Intelligence Attitude Scale (AIAS-4) measuring general attitudes toward AI. Results showed moderate positive attitudes toward AI chatbots for mental health (AIMHS mean scores in the neutral-to-positive range), with a significant positive correlation between AIMHS and AIAS-4 scores (r = .56, p < .001), indicating that general AI acceptance partially transfers to the mental health domain. Multivariable regression revealed that male gender (beta = .12, p < .05), higher education (beta = .15, p < .001), and older age (beta = .14, p < .01) were independently associated with more positive attitudes toward AI mental health chatbots. Daily social media use and digital competence predicted more positive general AI attitudes but did not significantly predict AI mental health chatbot attitudes when other variables were controlled. The authors conclude that while the Greek public shows moderate acceptance of AI in mental health, demographic factors create meaningful variation that should be considered in implementation strategies.

## Clinical Insight
For clinicians and services considering integrating AI chatbots into mental health care pathways, this study provides actionable data on patient populations most likely to engage. The moderate positive attitudes suggest readiness for carefully implemented AI tools, but the demographic variability highlights equity concerns: younger, less educated, and female patients — groups with high mental health need — showed less positive attitudes, potentially creating access disparities if AI tools become a primary point of contact. Clinicians should view AI chatbots as supplements to, not replacements for, therapeutic relationships. The finding that digital competence predicted general but not mental-health-specific AI attitudes suggests that trust in AI for sensitive psychological concerns involves factors beyond technical comfort — likely including concerns about privacy, empathy, and clinical validity that clinicians are well-positioned to address in psychoeducation.

## Relevant For
Mental health service designers, clinicians considering AI-augmented practice, and implementation researchers.

## Notes
Cross-sectional survey using AIMHS and AIAS-4. Greek population sample. National and Kapodistrian University of Athens. DOCX source file.
""",

    "415-xpfjz.md": """---
title: Identification of mental illness in maternity settings and care pathways to mental health services during pregnancy in a diverse urban UK population
authors: Sam Burton, Claire Wilson, Fiona Challacombe, Paul Seed, Jane Sandall, Louise Howard, eLIXIR Born in South London Partnership, Abigail Easter
osf_id: xpfjz_v1
number: 415
date_posted: 2026-06-28
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/xpfjz_v1
published: false
categories: Mood Disorders
---

## Summary
Using linked maternity and mental health records from 67,308 pregnancies (56,426 women) in South London (2018-2023), this study examined the pathway from antenatal mental health screening to actual service engagement. Three screening indicators were analyzed: positive Whooley depression questions, self-reported mental health conditions, and family history of severe mental illness. Among women already in contact with mental health services, 30.74% were not identified as at-risk by any of the three screening questions, while 38.39% were flagged by one, 24.73% by two, and 6.14% by all three. More screening indicators endorsed predicted higher referral and engagement odds (3 indicators vs 1: OR = 6.73 for referral). Significant ethnic disparities emerged: Asian and Asian British women had substantially lower odds of referral (OR = 0.51, 95% CI [0.42, 0.61]) and engagement (OR = 0.73, 95% CI [0.59, 0.91]) compared to White women. Black, African, Caribbean, and Black British women had higher referral odds (OR = 1.45) but lower engagement (OR = 0.73). Women requiring an interpreter had lower referral odds (OR = 0.69). Less deprived women (IMD quintile 5) had markedly lower referral rates (OR = 0.26 vs most deprived), suggesting socioeconomic detection bias.

## Clinical Insight
This large-scale data linkage study exposes critical gaps in the perinatal mental health care pathway that clinicians and service leads should address urgently. Nearly a third of women with known mental health contact were not detected by standard antenatal screening, indicating significant sensitivity limitations in current screening tools. The ethnic and language-based disparities in referral and engagement point to systemic rather than individual-level barriers: culturally insensitive screening approaches, insufficient interpreter services, and possible implicit bias in clinical decision-making. For perinatal mental health clinicians, these findings support routine re-screening beyond the booking appointment, advocacy for culturally adapted assessment tools, and systematic follow-up to ensure screening-positive results translate into actual care. The socioeconomic gradient in referral (more deprived women more likely referred) may reflect either higher prevalence or lower threshold for concern among clinicians working with disadvantaged populations — both warrant attention.

## Relevant For
Perinatal mental health teams, midwifery leads, and health system administrators responsible for maternity mental health pathways.

## Notes
Population-level data linkage study. eLIXIR Born in South London database. 67,308 pregnancies. DOCX source file.
""",

    "416-djkcz.md": """---
title: Self-reports of personality functioning and depression are practically interchangeable
authors: Josh Miller, Colin Vize, Nathaniel L. Phillips, Donald Lynam
osf_id: djkcz_v2
number: 416
date_posted: 2026-06-29
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/djkcz_v2
published: false
categories: Psychopathology & Assessment
---

## Summary
This commentary critically evaluates Kerber et al. (2026), which used bifactor-(S-1) modeling in a large EMA study (N > 16,000) to argue that personality functioning (PF) and depression (DEP) have distinct affective signatures with different treatment implications. Miller and colleagues present three counterarguments. First, the raw latent correlation between PF and DEP was r = .75-.87 — as high as convergent validity correlations used to establish measure equivalence — and the original (non-residualized) constructs produced nearly identical empirical profiles across outcomes (profile agreement r = .95). Second, the "perils of partialing" are demonstrated: residualized PF scores yielded an empirical profile unrelated to the original PF (r = -.06), with 53% of regression coefficients changing direction. The specific PF factor from bifactor models showed poor psychometric properties (ECVSS mean = .21; H mean = .39, well below the .70 threshold), indicating it is not a reliable or replicable construct. Third, interpretational confounding was evident across models, with PF factor loadings shifting by over .30 between analyses. The authors conclude that current PF measures are essentially markers of general distress and negative self-regard, and that claims of distinct treatment implications for PF versus depression are unsupported by the data.

## Clinical Insight
This commentary has direct implications for the ICD-11 and DSM-5 Alternative Model personality disorder frameworks, both of which position personality functioning as the central distinguishing criterion. If PF measures are practically interchangeable with depression measures (r = .87), their diagnostic utility for differentiating personality disorders from other conditions is fundamentally undermined. For clinicians using personality functioning assessments (e.g., OPD-SQS, LPFS), this research suggests that elevated scores may primarily reflect general distress rather than personality pathology per se. Treatment decisions should not be based on distinctions between PF and depression as measured by current instruments. The broader methodological critique of bifactor partialing in clinical measurement also serves as a caution for researchers interpreting residualized constructs in treatment outcome studies.

## Relevant For
Personality disorder researchers, clinicians using the ICD-11 or DSM-5 AMPD frameworks, and psychometricians working with bifactor models.

## Notes
Commentary on Kerber et al. (2026) in Journal of Psychopathology and Clinical Science. University of Georgia, Pittsburgh, Purdue. DOCX source file.
""",

    "417-x5gnq.md": """---
title: The Expression of Self-Conscious Emotions and Their Motivational and Communicative Function in Early Development
authors: Milica Nikolic, Robert Hepach
osf_id: x5gnq_v2
number: 417
date_posted: 2026-06-30
source_date: 2026-07-03
link: https://osf.io/preprints/psyarxiv/x5gnq_v2
published: false
categories: Psychopathology & Assessment
---

## Summary
This narrative review synthesizes emerging evidence on the developmental emergence of self-conscious emotions (embarrassment, guilt, shame, and pride) in infancy and early childhood. Drawing on advanced methodologies including manual and automated micro-coding of non-verbal behavior, depth sensor imaging, and physiological measures, the review documents that self-conscious emotions may be observed earlier than previously assumed — potentially within the first months and years of life. The evidence suggests these emotions serve dual functions from early on: motivating socially appropriate behaviors (e.g., guilt promoting helping and reparative actions even in toddlers) and communicating adherence to social norms (e.g., embarrassment signaling awareness of norm violations). Longitudinal data indicate that individual differences in early self-conscious emotion expression predict later social competence and prosocial behavior. The review highlights that guilt and shame, while often conflated, show divergent developmental trajectories and social consequences — guilt tends to motivate reparative action while shame is more associated with social withdrawal. The authors call for more experimental and longitudinal research, integration of multi-modal data streams, and naturalistic paradigms to advance the field.

## Clinical Insight
Understanding the normative development of self-conscious emotions provides essential reference points for clinical work with both children and adults. In young children, atypical patterns of guilt, shame, or empathy may signal early risk for psychopathology: excessive shame is linked to later depression and social anxiety, while blunted guilt responses are associated with conduct problems and callous-unemotional traits. For adult clinical practice, the developmental perspective informs case formulation — patients with personality disorders, depression, or social anxiety often present with distorted self-conscious emotion processing (e.g., pervasive shame, absence of healthy guilt, or pride deficits) that may trace back to early attachment experiences. The review's emphasis on the motivational and communicative functions of these emotions also supports therapeutic approaches that help patients differentiate adaptive guilt (which prompts repair) from maladaptive shame (which prompts withdrawal), a distinction central to compassion-focused therapy and schema therapy.

## Relevant For
Developmental psychopathologists, child mental health clinicians, and therapists working with shame and guilt in adult populations.

## Notes
Narrative review published in Philosophical Transactions of the Royal Society B. University of Amsterdam and University of Oxford. DOCX source file.
""",
}

for filename, content in notes.items():
    filepath = os.path.join(CURATION_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Written {filename}")

print(f"\nAll {len(notes)} curation notes updated.")