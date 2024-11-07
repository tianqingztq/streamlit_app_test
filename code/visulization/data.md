1. Data Clean
* Remove duplicate patient ID
* Patient: patient_nbr  
  * race
    * Person.race
        '?': 'Unknown',
        'Caucasian': 'White',
        'AfricanAmerican': 'Black or African American',
        'Hispanic': 'Hispanic or Latino',
        'Asian': 'Asian',
        'Other': 'Other'
   * gender
    * Person.gender: 
        Male ->male
        Female -> female 
        Unknown/Invalid -> unknown
   * age
    * Person.age

* Observation: 
  * Weight, 
  * diag_1，diag_2，diag_3
Simulation vs real data

Observation（检查结果）

max_glu_serum: 作为 Observation 的 code（例如，LOINC 代码）和 valueQuantity 或 valueString。
A1Cresult: 作为 Observation 的 code 和 valueQuantity。
num_lab_procedures, num_procedures, num_medications, number_outpatient, number_emergency, number_inpatient, number_diagnoses: 这些可以映射为单独的 Observation 资源，每个字段对应一个 Observation 记录。
MedicationStatement（用药信息）

metformin, repaglinide, nateglinide, chlorpropamide, glimepiride, acetohexamide, glipizide, glyburide, tolbutamide, pioglitazone, rosiglitazone, acarbose, miglitol, troglitazone, tolazamide, insulin, glyburide-metformin, glipizide-metformin, glimepiride-pioglitazone, metformin-rosiglitazone, metformin-pioglitazone: 每种药物可以作为一个单独的 MedicationStatement 资源，其中药物名称作为 medicationCodeableConcept。
其他字段

change（是否改变药物）: 可以映射到 MedicationStatement 的 status 或 note。
diabetesMed（是否有糖尿病药物治疗）: 也可以添加到 MedicationStatement 中作为备注。
readmitted（是否再次入院）: 可以作为 Encounter 的扩展字段，或作为一个单独的观察，用于记录再入院情况。