"""
Seed command: populates InventoryItem and LabTest records with a comprehensive
infirmary laboratory panel. Safe to re-run — uses get_or_create throughout.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import InventoryItem, LabTest, TestConsumption


# ---------------------------------------------------------------------------
# Master reagent/consumable catalogue
# ---------------------------------------------------------------------------
INVENTORY = [
    # Haematology reagents
    ("CBC Reagent Pack (Sysmex)", "REAGENT", "pack", 20, 5),
    ("WBC Lyse Reagent", "REAGENT", "mL", 500, 100),
    ("ESR Reagent (Westergren)", "REAGENT", "mL", 200, 50),
    ("Reticulocyte Stain", "REAGENT", "mL", 100, 20),
    ("Blood Film Stain (Giemsa)", "REAGENT", "mL", 200, 40),
    ("Peripheral Blood Smear Stain (Wright)", "REAGENT", "mL", 150, 30),
    ("EDTA Tubes (3 mL)", "CONSUMABLE", "tubes", 500, 100),

    # Coagulation
    ("PT Reagent (Thromboplastin)", "REAGENT", "mL", 100, 20),
    ("APTT Reagent", "REAGENT", "mL", 100, 20),
    ("Fibrinogen Reagent", "REAGENT", "mL", 50, 10),
    ("D-Dimer Reagent", "REAGENT", "mL", 50, 10),
    ("Sodium Citrate Tubes (2.7 mL)", "CONSUMABLE", "tubes", 200, 40),

    # Clinical chemistry
    ("Glucose Reagent", "REAGENT", "mL", 300, 60),
    ("HbA1c Reagent Kit", "REAGENT", "kit", 10, 2),
    ("Urea Reagent (BUN)", "REAGENT", "mL", 200, 40),
    ("Creatinine Reagent (Jaffe)", "REAGENT", "mL", 200, 40),
    ("Uric Acid Reagent", "REAGENT", "mL", 150, 30),
    ("Total Protein Reagent", "REAGENT", "mL", 150, 30),
    ("Albumin Reagent (BCG)", "REAGENT", "mL", 150, 30),
    ("Total Bilirubin Reagent", "REAGENT", "mL", 150, 30),
    ("Direct Bilirubin Reagent", "REAGENT", "mL", 100, 20),
    ("ALT (SGPT) Reagent", "REAGENT", "mL", 150, 30),
    ("AST (SGOT) Reagent", "REAGENT", "mL", 150, 30),
    ("Alkaline Phosphatase Reagent", "REAGENT", "mL", 150, 30),
    ("GGT Reagent", "REAGENT", "mL", 100, 20),
    ("LDH Reagent", "REAGENT", "mL", 100, 20),
    ("Amylase Reagent", "REAGENT", "mL", 100, 20),
    ("Lipase Reagent", "REAGENT", "mL", 100, 20),
    ("CK (CPK) Reagent", "REAGENT", "mL", 100, 20),
    ("CK-MB Reagent", "REAGENT", "mL", 80, 15),
    ("Troponin I Rapid Test Kit", "REAGENT", "tests", 50, 10),
    ("BNP / NT-proBNP Reagent", "REAGENT", "mL", 50, 10),
    ("Cholesterol Reagent", "REAGENT", "mL", 200, 40),
    ("HDL Cholesterol Reagent", "REAGENT", "mL", 150, 30),
    ("LDL Cholesterol Reagent", "REAGENT", "mL", 150, 30),
    ("Triglycerides Reagent", "REAGENT", "mL", 200, 40),
    ("Sodium Reagent (ISE)", "REAGENT", "mL", 200, 40),
    ("Potassium Reagent (ISE)", "REAGENT", "mL", 200, 40),
    ("Chloride Reagent (ISE)", "REAGENT", "mL", 150, 30),
    ("Bicarbonate / CO2 Reagent", "REAGENT", "mL", 100, 20),
    ("Calcium Reagent (Arsenazo)", "REAGENT", "mL", 150, 30),
    ("Phosphorus Reagent", "REAGENT", "mL", 100, 20),
    ("Magnesium Reagent", "REAGENT", "mL", 100, 20),
    ("Iron Reagent (Ferrozine)", "REAGENT", "mL", 100, 20),
    ("TIBC Reagent", "REAGENT", "mL", 80, 15),
    ("Ferritin Reagent", "REAGENT", "mL", 80, 15),
    ("Lithium Reagent (ISE)", "REAGENT", "mL", 80, 15),
    ("Plain Serum Tubes (SST 5 mL)", "CONSUMABLE", "tubes", 500, 100),

    # Thyroid / hormones
    ("TSH Reagent", "REAGENT", "mL", 80, 15),
    ("Free T3 Reagent", "REAGENT", "mL", 80, 15),
    ("Free T4 Reagent", "REAGENT", "mL", 80, 15),
    ("Anti-TPO Reagent", "REAGENT", "mL", 50, 10),
    ("Anti-Tg Reagent", "REAGENT", "mL", 50, 10),
    ("Cortisol Reagent", "REAGENT", "mL", 80, 15),
    ("Prolactin Reagent", "REAGENT", "mL", 80, 15),
    ("FSH Reagent", "REAGENT", "mL", 80, 15),
    ("LH Reagent", "REAGENT", "mL", 80, 15),
    ("Estradiol Reagent", "REAGENT", "mL", 80, 15),
    ("Testosterone Reagent", "REAGENT", "mL", 80, 15),
    ("Progesterone Reagent", "REAGENT", "mL", 80, 15),
    ("Beta-hCG Reagent", "REAGENT", "mL", 80, 15),
    ("PSA Reagent", "REAGENT", "mL", 80, 15),
    ("AFP Reagent", "REAGENT", "mL", 80, 15),
    ("CEA Reagent", "REAGENT", "mL", 80, 15),
    ("CA-125 Reagent", "REAGENT", "mL", 80, 15),
    ("CA 19-9 Reagent", "REAGENT", "mL", 80, 15),
    ("Vitamin D (25-OH) Reagent", "REAGENT", "mL", 80, 15),
    ("Vitamin B12 Reagent", "REAGENT", "mL", 80, 15),
    ("Folate Reagent", "REAGENT", "mL", 80, 15),
    ("Insulin Reagent", "REAGENT", "mL", 80, 15),
    ("C-Peptide Reagent", "REAGENT", "mL", 50, 10),
    ("Parathyroid Hormone (PTH) Reagent", "REAGENT", "mL", 50, 10),

    # Serology / immunology
    ("CRP Reagent (Quantitative)", "REAGENT", "mL", 100, 20),
    ("hs-CRP Reagent", "REAGENT", "mL", 80, 15),
    ("ESR Tube (Westergren)", "CONSUMABLE", "tubes", 200, 40),
    ("RF Reagent (Latex)", "REAGENT", "mL", 100, 20),
    ("ASO Reagent (Latex)", "REAGENT", "mL", 100, 20),
    ("ANA Screening Kit", "REAGENT", "kit", 10, 2),
    ("Anti-dsDNA Reagent", "REAGENT", "mL", 50, 10),
    ("Widal Antigen Set", "REAGENT", "kit", 10, 2),
    ("VDRL Antigen", "REAGENT", "mL", 50, 10),
    ("TPHA Kit", "REAGENT", "kit", 10, 2),
    ("HBsAg Rapid Kit", "REAGENT", "tests", 50, 10),
    ("Anti-HBs Reagent", "REAGENT", "mL", 50, 10),
    ("Anti-HCV Reagent", "REAGENT", "mL", 50, 10),
    ("HIV 1/2 Rapid Kit", "REAGENT", "tests", 50, 10),
    ("Malaria RDT Kit", "REAGENT", "tests", 50, 10),
    ("Dengue NS1 / IgM / IgG Kit", "REAGENT", "tests", 50, 10),
    ("Typhoid IgM Rapid Test", "REAGENT", "tests", 50, 10),
    ("H. pylori Stool Antigen Kit", "REAGENT", "tests", 50, 10),
    ("Strep A Rapid Test Kit", "REAGENT", "tests", 50, 10),

    # Urinalysis
    ("Urine Dipstick Strips (10-param)", "REAGENT", "strips", 500, 100),
    ("Urine Sediment Stain", "REAGENT", "mL", 100, 20),
    ("Universal Urine Cups", "CONSUMABLE", "cups", 500, 100),
    ("Centrifuge Tubes (15 mL)", "CONSUMABLE", "tubes", 500, 100),
    ("Urine Pregnancy Test (hCG)", "REAGENT", "tests", 100, 20),
    ("24h Urine Protein Reagent", "REAGENT", "mL", 100, 20),
    ("Urine Microalbumin Reagent", "REAGENT", "mL", 80, 15),
    ("Urine Creatinine Reagent", "REAGENT", "mL", 80, 15),
    ("Urine Urea Reagent", "REAGENT", "mL", 80, 15),

    # Stool / parasitology
    ("Stool Collection Container", "CONSUMABLE", "containers", 200, 40),
    ("Formol-Ether Concentration Reagent", "REAGENT", "mL", 100, 20),
    ("Lugol's Iodine Stain", "REAGENT", "mL", 50, 10),
    ("Occult Blood Reagent (gFOBT)", "REAGENT", "tests", 100, 20),
    ("Ziehl-Neelsen Carbol Fuchsin", "REAGENT", "mL", 100, 20),

    # Microbiology / culture
    ("Blood Culture Bottles (Aerobic)", "CONSUMABLE", "bottles", 50, 10),
    ("Blood Culture Bottles (Anaerobic)", "CONSUMABLE", "bottles", 50, 10),
    ("Mueller-Hinton Agar Plates", "CONSUMABLE", "plates", 100, 20),
    ("MacConkey Agar Plates", "CONSUMABLE", "plates", 100, 20),
    ("Blood Agar Plates", "CONSUMABLE", "plates", 100, 20),
    ("CLED Agar Plates (Urine)", "CONSUMABLE", "plates", 100, 20),
    ("Gram Stain Kit", "REAGENT", "kit", 10, 2),
    ("KOH (10%) Reagent", "REAGENT", "mL", 50, 10),
    ("India Ink", "REAGENT", "mL", 20, 5),
    ("Antibiotic Sensitivity Discs (set)", "CONSUMABLE", "sets", 20, 4),
    ("Normal Saline 0.9% (10 mL vials)", "REAGENT", "vials", 200, 40),

    # Sputum / AFB
    ("AFB Sputum Collection Cup", "CONSUMABLE", "cups", 100, 20),
    ("ZN Decoloriser (Acid-Alcohol)", "REAGENT", "mL", 100, 20),
    ("ZN Methylene Blue Counterstain", "REAGENT", "mL", 100, 20),

    # General consumables
    ("Lancets (safety, 21G)", "CONSUMABLE", "pieces", 500, 100),
    ("Capillary Tubes (hematocrit)", "CONSUMABLE", "pieces", 500, 100),
    ("Microscope Slides", "CONSUMABLE", "pieces", 1000, 200),
    ("Cover Slips (22×22 mm)", "CONSUMABLE", "pieces", 1000, 200),
    ("Gloves (nitrile, M)", "CONSUMABLE", "pairs", 500, 100),
    ("Gloves (nitrile, L)", "CONSUMABLE", "pairs", 500, 100),
    ("Biohazard Disposal Bags", "CONSUMABLE", "bags", 100, 20),
    ("Sharps Container (5 L)", "CONSUMABLE", "pieces", 20, 4),
    ("Immersion Oil (microscopy)", "REAGENT", "mL", 50, 10),
    ("Distilled Water (500 mL)", "REAGENT", "mL", 2000, 500),
    ("Methanol (absolute)", "REAGENT", "mL", 500, 100),
    ("Ethanol 70%", "REAGENT", "mL", 1000, 200),
    ("Coombs Serum (Direct)", "REAGENT", "mL", 50, 10),
    ("Coombs Serum (Indirect)", "REAGENT", "mL", 50, 10),
    ("Blood Grouping Antisera (Anti-A, B, D)", "REAGENT", "mL", 50, 10),
    ("Dipstick QC Solution (Level 1)", "REAGENT", "mL", 30, 5),
    ("Dipstick QC Solution (Level 2)", "REAGENT", "mL", 30, 5),
    ("Analyzer QC Material (Low)", "REAGENT", "vials", 10, 2),
    ("Analyzer QC Material (High)", "REAGENT", "vials", 10, 2),
]

# ---------------------------------------------------------------------------
# Lab tests: (name, description, [(reagent_name, qty_per_test), ...])
# ---------------------------------------------------------------------------
TESTS = [
    # ── Haematology ──────────────────────────────────────────────────────────
    ("Complete Blood Count (CBC)", "Full blood count including WBC differential, RBC, Hb, Hct, platelets.", [
        ("CBC Reagent Pack (Sysmex)", "0.5"),
        ("WBC Lyse Reagent", "1.0"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Erythrocyte Sedimentation Rate (ESR)", "Westergren method.", [
        ("ESR Reagent (Westergren)", "2.0"),
        ("ESR Tube (Westergren)", "1"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Peripheral Blood Film (PBF)", "Morphology + manual differential.", [
        ("Blood Film Stain (Giemsa)", "1.0"),
        ("Peripheral Blood Smear Stain (Wright)", "1.0"),
        ("Microscope Slides", "2"),
        ("Cover Slips (22×22 mm)", "2"),
        ("Immersion Oil (microscopy)", "0.1"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Reticulocyte Count", "Supravital stain method.", [
        ("Reticulocyte Stain", "0.5"),
        ("Microscope Slides", "2"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Haematocrit (PCV)", "Microhematocrit centrifuge method.", [
        ("Capillary Tubes (hematocrit)", "3"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Blood Group & Rh Typing", "ABO and Rh(D) determination.", [
        ("Blood Grouping Antisera (Anti-A, B, D)", "0.3"),
        ("Microscope Slides", "3"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Direct Coombs Test (DAT)", "Direct antiglobulin test.", [
        ("Coombs Serum (Direct)", "0.5"),
        ("Normal Saline 0.9% (10 mL vials)", "1"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Indirect Coombs Test (IAT)", "Indirect antiglobulin / cross-match.", [
        ("Coombs Serum (Indirect)", "0.5"),
        ("Normal Saline 0.9% (10 mL vials)", "1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Sickling Test", "Sodium metabisulphite screening for sickle cells.", [
        ("Microscope Slides", "2"),
        ("Cover Slips (22×22 mm)", "2"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Malaria Rapid Test (RDT)", "Rapid antigen detection for P. falciparum / pan-malaria.", [
        ("Malaria RDT Kit", "1"),
        ("Lancets (safety, 21G)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Coagulation ──────────────────────────────────────────────────────────
    ("Prothrombin Time (PT / INR)", "Extrinsic pathway; warfarin monitoring.", [
        ("PT Reagent (Thromboplastin)", "1.0"),
        ("Sodium Citrate Tubes (2.7 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Activated Partial Thromboplastin Time (APTT)", "Intrinsic pathway; heparin monitoring.", [
        ("APTT Reagent", "1.0"),
        ("Sodium Citrate Tubes (2.7 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Fibrinogen Level", "Clauss method.", [
        ("Fibrinogen Reagent", "1.0"),
        ("Sodium Citrate Tubes (2.7 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("D-Dimer", "Latex immunoassay for fibrin degradation products.", [
        ("D-Dimer Reagent", "1.0"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Bleeding Time (Duke)", "Capillary bleeding time screen.", [
        ("Lancets (safety, 21G)", "1"),
        ("Microscope Slides", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Glycaemia / Diabetes ─────────────────────────────────────────────────
    ("Fasting Blood Glucose (FBG)", "Enzymatic glucose oxidase method.", [
        ("Glucose Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Random Blood Glucose (RBG)", "Enzymatic glucose oxidase method.", [
        ("Glucose Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("HbA1c (Glycated Haemoglobin)", "Ion-exchange HPLC / immunoassay.", [
        ("HbA1c Reagent Kit", "0.1"),
        ("EDTA Tubes (3 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Oral Glucose Tolerance Test (OGTT 2h)", "Fasting + 2h post-load glucose.", [
        ("Glucose Reagent", "1.0"),
        ("Plain Serum Tubes (SST 5 mL)", "2"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Insulin Level", "ELISA / CLIA.", [
        ("Insulin Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("C-Peptide", "Fasting C-peptide; beta-cell function.", [
        ("C-Peptide Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Renal Function ───────────────────────────────────────────────────────
    ("Blood Urea Nitrogen (BUN)", "Urease method.", [
        ("Urea Reagent (BUN)", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Creatinine", "Jaffe / enzymatic method.", [
        ("Creatinine Reagent (Jaffe)", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Uric Acid", "Uricase method.", [
        ("Uric Acid Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Renal Function Panel (BUN + Creatinine + Uric Acid + Electrolytes)", "Combined renal panel.", [
        ("Urea Reagent (BUN)", "0.5"),
        ("Creatinine Reagent (Jaffe)", "0.5"),
        ("Uric Acid Reagent", "0.5"),
        ("Sodium Reagent (ISE)", "0.3"),
        ("Potassium Reagent (ISE)", "0.3"),
        ("Chloride Reagent (ISE)", "0.3"),
        ("Bicarbonate / CO2 Reagent", "0.3"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Urine Microalbumin/Creatinine Ratio (ACR)", "Random urine ACR.", [
        ("Urine Microalbumin Reagent", "0.5"),
        ("Urine Creatinine Reagent", "0.5"),
        ("Universal Urine Cups", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("24h Urine Protein", "Biuret / turbidimetric method.", [
        ("24h Urine Protein Reagent", "1.0"),
        ("Universal Urine Cups", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Liver Function ───────────────────────────────────────────────────────
    ("Liver Function Tests (LFT)", "Full liver panel: ALT, AST, ALP, GGT, total/direct bilirubin, total protein, albumin.", [
        ("ALT (SGPT) Reagent", "0.5"),
        ("AST (SGOT) Reagent", "0.5"),
        ("Alkaline Phosphatase Reagent", "0.5"),
        ("GGT Reagent", "0.5"),
        ("Total Bilirubin Reagent", "0.5"),
        ("Direct Bilirubin Reagent", "0.5"),
        ("Total Protein Reagent", "0.5"),
        ("Albumin Reagent (BCG)", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("ALT (SGPT)", "Alanine aminotransferase only.", [
        ("ALT (SGPT) Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("AST (SGOT)", "Aspartate aminotransferase only.", [
        ("AST (SGOT) Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Bilirubin (Total + Direct)", "Diazo method.", [
        ("Total Bilirubin Reagent", "0.5"),
        ("Direct Bilirubin Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("LDH", "Lactate dehydrogenase.", [
        ("LDH Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Amylase", "EPS substrate method.", [
        ("Amylase Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Lipase", "Turbidimetric method.", [
        ("Lipase Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Cardiac Markers ──────────────────────────────────────────────────────
    ("Troponin I (Rapid)", "Point-of-care cardiac troponin.", [
        ("Troponin I Rapid Test Kit", "1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("CK (CPK)", "Total creatine kinase.", [
        ("CK (CPK) Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("CK-MB", "CK-MB isoenzyme.", [
        ("CK-MB Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("BNP / NT-proBNP", "Heart failure biomarker.", [
        ("BNP / NT-proBNP Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Lipid Profile ────────────────────────────────────────────────────────
    ("Fasting Lipid Profile", "Total cholesterol, HDL, LDL, triglycerides.", [
        ("Cholesterol Reagent", "0.5"),
        ("HDL Cholesterol Reagent", "0.5"),
        ("LDL Cholesterol Reagent", "0.5"),
        ("Triglycerides Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Electrolytes & Minerals ──────────────────────────────────────────────
    ("Serum Electrolytes (Na / K / Cl / HCO3)", "ISE panel.", [
        ("Sodium Reagent (ISE)", "0.3"),
        ("Potassium Reagent (ISE)", "0.3"),
        ("Chloride Reagent (ISE)", "0.3"),
        ("Bicarbonate / CO2 Reagent", "0.3"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Calcium", "Arsenazo III method.", [
        ("Calcium Reagent (Arsenazo)", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Phosphorus", "Ammonium molybdate method.", [
        ("Phosphorus Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Magnesium", "Xylidyl blue method.", [
        ("Magnesium Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Iron + TIBC", "Ferrozine + TIBC.", [
        ("Iron Reagent (Ferrozine)", "0.5"),
        ("TIBC Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Ferritin", "Immunoturbidimetry.", [
        ("Ferritin Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Lithium", "ISE method; therapeutic monitoring.", [
        ("Lithium Reagent (ISE)", "0.3"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Thyroid Panel ────────────────────────────────────────────────────────
    ("Thyroid Function Tests (TFT — TSH + FT3 + FT4)", "Full thyroid panel.", [
        ("TSH Reagent", "0.5"),
        ("Free T3 Reagent", "0.5"),
        ("Free T4 Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("TSH Only", "Thyroid-stimulating hormone screening.", [
        ("TSH Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Anti-TPO Antibodies", "Thyroid peroxidase antibodies.", [
        ("Anti-TPO Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Vitamins & Nutrition ─────────────────────────────────────────────────
    ("Vitamin D (25-OH)", "Immunoassay / CLIA.", [
        ("Vitamin D (25-OH) Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Vitamin B12", "CLIA.", [
        ("Vitamin B12 Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Folate (Folic Acid)", "CLIA.", [
        ("Folate Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Hormones ─────────────────────────────────────────────────────────────
    ("Cortisol (AM)", "Morning cortisol; adrenal function.", [
        ("Cortisol Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Prolactin", "CLIA.", [
        ("Prolactin Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("FSH", "Follicle-stimulating hormone.", [
        ("FSH Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("LH", "Luteinizing hormone.", [
        ("LH Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Estradiol (E2)", "CLIA.", [
        ("Estradiol Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Testosterone (Total)", "CLIA.", [
        ("Testosterone Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Progesterone", "CLIA.", [
        ("Progesterone Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Serum Beta-hCG (Quantitative)", "Quantitative pregnancy test.", [
        ("Beta-hCG Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Parathyroid Hormone (PTH)", "Intact PTH assay.", [
        ("Parathyroid Hormone (PTH) Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Tumour Markers ───────────────────────────────────────────────────────
    ("PSA (Prostate Specific Antigen)", "Total PSA; prostate cancer screening.", [
        ("PSA Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("AFP (Alpha-Fetoprotein)", "HCC / germ-cell tumour marker.", [
        ("AFP Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("CEA (Carcinoembryonic Antigen)", "Colorectal / GI tumour marker.", [
        ("CEA Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("CA-125", "Ovarian cancer marker.", [
        ("CA-125 Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("CA 19-9", "Pancreatic / biliary tumour marker.", [
        ("CA 19-9 Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Inflammation / Immunology ────────────────────────────────────────────
    ("CRP (Quantitative)", "C-reactive protein; acute inflammation.", [
        ("CRP Reagent (Quantitative)", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("hs-CRP", "High-sensitivity CRP; cardiovascular risk.", [
        ("hs-CRP Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Rheumatoid Factor (RF)", "Latex agglutination.", [
        ("RF Reagent (Latex)", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Anti-Streptolysin O (ASO)", "Latex agglutination.", [
        ("ASO Reagent (Latex)", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("ANA Screen", "Anti-nuclear antibody screening.", [
        ("ANA Screening Kit", "0.1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Anti-dsDNA", "Anti-double-stranded DNA antibodies (SLE).", [
        ("Anti-dsDNA Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Infectious Disease Serology ──────────────────────────────────────────
    ("Widal Test", "Febrile agglutinins for Salmonella typhi.", [
        ("Widal Antigen Set", "0.1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("VDRL (Syphilis Screen)", "Venereal Disease Research Laboratory.", [
        ("VDRL Antigen", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("TPHA (Syphilis Confirm)", "Treponema pallidum haemagglutination assay.", [
        ("TPHA Kit", "0.1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("HBsAg (Hepatitis B Surface Antigen)", "Rapid / ELISA.", [
        ("HBsAg Rapid Kit", "1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Anti-HBs (Hepatitis B Antibody)", "Immunity / vaccination check.", [
        ("Anti-HBs Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Anti-HCV (Hepatitis C Antibody)", "HCV screening.", [
        ("Anti-HCV Reagent", "0.5"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("HIV 1/2 Rapid Test", "Point-of-care HIV antibody/antigen.", [
        ("HIV 1/2 Rapid Kit", "1"),
        ("Lancets (safety, 21G)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Dengue NS1 / IgM / IgG (Rapid)", "Dengue rapid combo test.", [
        ("Dengue NS1 / IgM / IgG Kit", "1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Typhoid IgM Rapid Test", "Typhi IgM immunochromatography.", [
        ("Typhoid IgM Rapid Test", "1"),
        ("Plain Serum Tubes (SST 5 mL)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("H. pylori Stool Antigen", "Immunochromatographic stool test.", [
        ("H. pylori Stool Antigen Kit", "1"),
        ("Stool Collection Container", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Strep A Rapid Test", "Group A streptococcal throat swab.", [
        ("Strep A Rapid Test Kit", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Urinalysis ───────────────────────────────────────────────────────────
    ("Urinalysis (Dipstick + Microscopy)", "10-parameter dipstick + sediment examination.", [
        ("Urine Dipstick Strips (10-param)", "1"),
        ("Urine Sediment Stain", "0.2"),
        ("Universal Urine Cups", "1"),
        ("Centrifuge Tubes (15 mL)", "1"),
        ("Microscope Slides", "1"),
        ("Cover Slips (22×22 mm)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Urine Pregnancy Test (hCG)", "Qualitative beta-hCG in urine.", [
        ("Urine Pregnancy Test (hCG)", "1"),
        ("Universal Urine Cups", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Urine Culture & Sensitivity (C&S)", "Midstream urine culture + antibiogram.", [
        ("CLED Agar Plates (Urine)", "1"),
        ("Blood Agar Plates", "1"),
        ("Mueller-Hinton Agar Plates", "1"),
        ("Antibiotic Sensitivity Discs (set)", "0.05"),
        ("Universal Urine Cups", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Urine Protein (Spot)", "Turbidimetric / dipstick quantification.", [
        ("24h Urine Protein Reagent", "0.5"),
        ("Universal Urine Cups", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Stool ────────────────────────────────────────────────────────────────
    ("Stool Microscopy (Ova & Parasites)", "Formol-ether concentration + wet mount.", [
        ("Formol-Ether Concentration Reagent", "2.0"),
        ("Lugol's Iodine Stain", "0.2"),
        ("Stool Collection Container", "1"),
        ("Microscope Slides", "2"),
        ("Cover Slips (22×22 mm)", "2"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Occult Blood Test (gFOBT)", "Guaiac-based faecal occult blood.", [
        ("Occult Blood Reagent (gFOBT)", "1"),
        ("Stool Collection Container", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Stool Culture", "Culture for enteric pathogens.", [
        ("MacConkey Agar Plates", "1"),
        ("Blood Agar Plates", "1"),
        ("Mueller-Hinton Agar Plates", "1"),
        ("Antibiotic Sensitivity Discs (set)", "0.05"),
        ("Stool Collection Container", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── Microbiology ─────────────────────────────────────────────────────────
    ("Blood Culture (Aerobic + Anaerobic)", "Culture for bacteraemia/fungaemia.", [
        ("Blood Culture Bottles (Aerobic)", "1"),
        ("Blood Culture Bottles (Anaerobic)", "1"),
        ("Normal Saline 0.9% (10 mL vials)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Wound Swab Culture & Sensitivity", "Culture + antibiogram.", [
        ("Blood Agar Plates", "1"),
        ("Mueller-Hinton Agar Plates", "1"),
        ("MacConkey Agar Plates", "1"),
        ("Antibiotic Sensitivity Discs (set)", "0.05"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Throat Swab Culture", "Culture for pharyngeal pathogens.", [
        ("Blood Agar Plates", "1"),
        ("Mueller-Hinton Agar Plates", "1"),
        ("Antibiotic Sensitivity Discs (set)", "0.05"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Gram Stain (Smear)", "Gram stain of direct specimen.", [
        ("Gram Stain Kit", "0.1"),
        ("Microscope Slides", "2"),
        ("Cover Slips (22×22 mm)", "1"),
        ("Immersion Oil (microscopy)", "0.1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("KOH Preparation (Fungal)", "Direct fungal mount.", [
        ("KOH (10%) Reagent", "0.5"),
        ("Microscope Slides", "1"),
        ("Cover Slips (22×22 mm)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("India Ink Preparation (Cryptococcus)", "CSF / specimen for Cryptococcus.", [
        ("India Ink", "0.05"),
        ("Microscope Slides", "1"),
        ("Cover Slips (22×22 mm)", "1"),
        ("Immersion Oil (microscopy)", "0.1"),
        ("Gloves (nitrile, M)", "1"),
    ]),

    # ── AFB / Sputum ─────────────────────────────────────────────────────────
    ("Sputum AFB Smear (ZN Stain)", "Acid-fast bacilli smear for TB.", [
        ("Ziehl-Neelsen Carbol Fuchsin", "1.0"),
        ("ZN Decoloriser (Acid-Alcohol)", "1.0"),
        ("ZN Methylene Blue Counterstain", "0.5"),
        ("AFB Sputum Collection Cup", "1"),
        ("Microscope Slides", "2"),
        ("Immersion Oil (microscopy)", "0.1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Sputum Culture for TB (MGIT / LJ slope)", "Culture for M. tuberculosis.", [
        ("AFB Sputum Collection Cup", "1"),
        ("Normal Saline 0.9% (10 mL vials)", "1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
    ("Cryptosporidium / Cyclospora Stain (Modified ZN)", "Modified acid-fast stain for oocysts.", [
        ("Ziehl-Neelsen Carbol Fuchsin", "0.5"),
        ("ZN Decoloriser (Acid-Alcohol)", "0.5"),
        ("ZN Methylene Blue Counterstain", "0.3"),
        ("Stool Collection Container", "1"),
        ("Microscope Slides", "2"),
        ("Immersion Oil (microscopy)", "0.1"),
        ("Gloves (nitrile, M)", "1"),
    ]),
]


class Command(BaseCommand):
    help = "Seed database with a comprehensive infirmary lab test catalogue."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing InventoryItem, LabTest, and TestConsumption records first.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            TestConsumption.objects.all().delete()
            LabTest.objects.all().delete()
            InventoryItem.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing data."))

        # 1. Upsert inventory items
        item_map = {}
        for name, category, unit, qty, threshold in INVENTORY:
            item, created = InventoryItem.objects.get_or_create(
                name=name,
                defaults={
                    "category": category,
                    "unit": unit,
                    "quantity_in_stock": Decimal(str(qty)),
                    "reorder_threshold": Decimal(str(threshold)),
                },
            )
            item_map[name] = item
            if created:
                self.stdout.write(f"  + Inventory: {name}")

        self.stdout.write(self.style.SUCCESS(f"Inventory: {len(item_map)} items ready."))

        # 2. Upsert lab tests + consumptions
        tests_created = 0
        consumptions_created = 0
        for test_name, description, consumptions in TESTS:
            test, t_created = LabTest.objects.get_or_create(
                name=test_name,
                defaults={"description": description},
            )
            if t_created:
                tests_created += 1

            for reagent_name, qty_str in consumptions:
                reagent = item_map.get(reagent_name)
                if reagent is None:
                    self.stdout.write(
                        self.style.WARNING(f"  ! Missing reagent '{reagent_name}' for test '{test_name}' — skipped.")
                    )
                    continue
                _, c_created = TestConsumption.objects.get_or_create(
                    lab_test=test,
                    inventory_item=reagent,
                    defaults={"quantity_consumed_per_test": Decimal(qty_str)},
                )
                if c_created:
                    consumptions_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {tests_created} new tests, {consumptions_created} new consumption entries seeded."
            )
        )
