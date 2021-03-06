"""
Builds FHIR HPO (Observation) entries

Links a Patient, Study, Disease with HPO (which is either present or absent)
"""

from ncpi_fhir_plugin.shared import join, make_identifier
from ncpi_fhir_plugin.common import CONCEPT, constants

from ncpi_fhir_plugin.target_api_builders.ncpi_patient import Patient
from ncpi_fhir_plugin.target_api_builders.disease import Disease
from ncpi_fhir_plugin.target_api_builders import TargetBase

import pdb

# https://www.hl7.org/fhir/valueset-observation-interpretation.html
interpretation = {
    constants.PHENOTYPE.OBSERVED.ABSENT: [{
        "coding": [ 
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "NEG",
                "display": "Negative"
            }
        ],
        "text": "Absent"
    }],
    constants.PHENOTYPE.OBSERVED.PRESENT: [{
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "POS",
                "display": "Positive",
            }
        ],
        "text": "Present"
    }],
}

observation_code = {
    constants.PHENOTYPE.OBSERVED.PRESENT: {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "373573001",
                "display": "Clinical finding present (situation)"
            }
        ],
        "text": "Phenotype Present"
    },   
    constants.PHENOTYPE.OBSERVED.ABSENT: {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "373572006",
                "display": "Clinical finding absent (situation)"
            }
        ],
        "text": "Phenotype Absent"
    }
}


class HumanPhenotype(TargetBase):
    class_name = "human_phenotype"
    resource_type = "Observation"
    target_id_concept = CONCEPT.STUDY.PROVIDER.SUBJECT.TARGET_SERVICE_ID

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        # These are required for the variant
        assert None is not record[CONCEPT.PARTICIPANT.ID]
        assert None is not record[CONCEPT.STUDY.NAME]
        assert None is not record[CONCEPT.PHENOTYPE.HPO_ID]
        assert None is not record[CONCEPT.PHENOTYPE.OBSERVED]

        return {
            "identifier":  join(
                record[CONCEPT.STUDY.NAME],
                record[CONCEPT.PARTICIPANT.ID],
                record[CONCEPT.PHENOTYPE.HPO_ID],
                record[CONCEPT.PHENOTYPE.OBSERVED]
            )
        }

    @classmethod
    def build_entity(cls, record, get_target_id_from_record):
        key = cls.get_key_components(record, get_target_id_from_record)['identifier']
        family_id = record[CONCEPT.FAMILY.ID]
        study_name = record[CONCEPT.STUDY.NAME]
        hpo_id = record[CONCEPT.PHENOTYPE.HPO_ID]
        pheno_name = record[CONCEPT.PHENOTYPE.NAME]
        observed = record[CONCEPT.PHENOTYPE.OBSERVED]

        #if record[CONCEPT.PARTICIPANT.ID] == "BH9825_1" and hpo_id == "HP:0004325":
            # pdb.set_trace()

        # "code": {"coding": [{"code": hpo_id}], "text": pheno_name},
        #    "interpretation": [
        #        {"coding": [interpretation[observed]], "text": observed}
        #    ],

        entity = {
            "resourceType": HumanPhenotype.resource_type,
            "id": get_target_id_from_record(HumanPhenotype, record),
            "meta": {
                "profile": [
                     f"http://fhir.ncpi-project-forge.io/StructureDefinition/ncpi-phenotype"
                ]
            },
            "identifier": [
                {
                    "system" : f"{cls.identifier_system}",
                    "value": key,
                }
            ],
            "status": "preliminary",
            "code":     {
                "coding": [
                    {
                        "system": "http://purl.obolibrary.org/obo/hp.owl",
                        "code": hpo_id,
                        "display": pheno_name
                    }
                ],
                "text": f"{observed}: {pheno_name}"
            },
            "subject": {
                "reference": f"Patient/{get_target_id_from_record(Patient, record)}"
            },

            "valueCodeableConcept": observation_code[observed],
            "interpretation": interpretation[observed]
        }

        return entity

