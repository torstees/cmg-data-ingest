"""
Doc Resource associated with a file containing sequencing data."""
import pandas as pd
import sys

from ncpi_fhir_plugin.shared import join, make_identifier
from ncpi_fhir_plugin.common import constants, CONCEPT
from ncpi_fhir_plugin.target_api_builders.sequencing_center import SequencingCenter
from ncpi_fhir_plugin.target_api_builders.specimen import Specimen
from ncpi_fhir_plugin.target_api_builders.ncpi_patient import Patient
from ncpi_fhir_plugin.target_api_builders import TargetBase

class SequencingFileNoDrs(TargetBase):
    class_name = "sequencing_file_no_drs"
    resource_type = "DocumentReference"
    target_id_concept = CONCEPT.SEQUENCING.TARGET_SERVICE_ID

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        # These are required for the variant
        assert None is not record[CONCEPT.SEQUENCING.ID]

        drs_uri = record.get(CONCEPT.SEQUENCING.DRS_URI)
        assert drs_uri is None or drs_uri.strip() == ""

        return {
            "identifier":  join(
                "NO-DRS", 
                record[CONCEPT.SEQUENCING_GENOMIC_FILE.ID]
            )
        }


    @classmethod
    def build_entity(cls, record, get_target_id_from_record):
        key = cls.get_key_components(record, get_target_id_from_record)['identifier']
        study_id = record[CONCEPT.STUDY.NAME]
        seq_filename = record.get(CONCEPT.SEQUENCING_GENOMIC_FILE.ID)
        seq_id = record.get(CONCEPT.SEQUENCING.ID)
        file_format = record.get(CONCEPT.GENOMIC_FILE.FILE_FORMAT)
        seq_center = record.get(CONCEPT.SEQUENCING.CENTER.ID)
        specimen = get_target_id_from_record(Specimen, record)
        data_date_generation = record.get(CONCEPT.SEQUENCING.DATE)
        drs_uri = record.get(CONCEPT.SEQUENCING.DRS_URI)

        entity = {
            "resourceType": SequencingFileNoDrs.resource_type,
            "id": get_target_id_from_record(SequencingFileNoDrs, record),
            "meta": {
                "profile": [
                    f"http://hl7.org/fhir/StructureDefinition/{SequencingFileNoDrs.resource_type}"
                ]
            },            
            "status": "current",
            "author" : [
                {
                    "reference": f"{SequencingCenter.resource_type}/{get_target_id_from_record(SequencingCenter, record)}",
                    "display": seq_center
                }
            ],
            "subject": {
            	"reference": f"Patient/{get_target_id_from_record(Patient, record)}",
            	"display" : f"{record.get(CONCEPT.PARTICIPANT.ID)}"
            },

            "identifier": [
                {
                    "system" : f"{cls.identifier_system}",
                    "value": key,
                },
            ],
            "description": "production of sequence data",
        	"content": [
        		{
                    "attachment": {
                        "title": seq_filename
                    },
                    "format": {
                        "display": "Sequence Filename"
                    }
        		}
        	]
        }

        if data_date_generation:
            entity['date'] = data_date_generation + "T00:00:00+06:00"

        return entity
