"""
XML Schema Validation Script

This script checks an XML submission against a main schema (and optionally a supplementary schema) to ensure compliance.
Supplementary schema dependencies are handled programmatically, and schema files remain unmodified.

The script currently uses FSA029 as the main schema and CommonTypes as the supplementary schema.
These can be changed, detailed in comments in the code below.

Usage:
    python validate_schema.py <path_to_schema_folder> <path_to_submission_XML>
"""

import sys
import os
from lxml import etree

def check_and_get_paths(schema_folder_path: str, submission_xml_path: str) -> tuple[str, str | None, str]:
    """Verify and retrieve paths for required schema files, returning these paths."""
    if not os.path.isdir(schema_folder_path):
        print(f'Error: schema folder not found at {schema_folder_path}')
        sys.exit(1)

    main_schema_path = None
    supplementary_schema_path = None
    
    for filename in os.listdir(schema_folder_path):
        if not filename.lower().endswith('.xsd'):
            continue

        lower_name = filename.lower()

        # Recognise 'fsa029' as main schema, 'commontypes' as supplementary schema for demo purposes. Swap out for relevant schemas.
        if 'fsa029' in lower_name and 'commontypes' not in lower_name:
            main_schema_path = os.path.join(schema_folder_path, filename)
        elif 'commontypes' in lower_name:
            supplementary_schema_path = os.path.join(schema_folder_path, filename)

        if main_schema_path and supplementary_schema_path:
            break

    if not main_schema_path:
        print(f'Error: main schema file (*.xsd, e.g. fsa029) not found in {schema_folder_path}')
        sys.exit(1)

    if not os.path.isfile(submission_xml_path):
        print(f'Error: submission file not found at {submission_xml_path}')
        sys.exit(1)

    return main_schema_path, supplementary_schema_path, submission_xml_path

def fix_schema_includes_programmatically(main_schema_path: str, supplementary_schema_path: str | None) -> etree.XMLSchema:
    """Update schema includes to reference supplementary schema in same directory, returning the updated schema."""
    parser = etree.XMLParser(remove_blank_text=True)

    try:
        with open(main_schema_path, 'rb') as f:
            schema_doc = etree.parse(f, parser)
        
        if supplementary_schema_path:
            for include in schema_doc.xpath('//xs:include', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'}):
                # Recognise 'CommonTypes' for demo, but replace with relevant supplementary schema.
                if 'CommonTypes' in include.get('schemaLocation', ''):
                    relative_supplementary_schema_path = os.path.basename(supplementary_schema_path)
                    include.set('schemaLocation', relative_supplementary_schema_path)

        fixed_schema = etree.XMLSchema(schema_doc)
        return fixed_schema
    
    except Exception as e:
        print(f'Error creating XMLSchema: {e}')
        sys.exit(1)


def validate_submission_xml(schema: etree.XMLSchema, submission_xml_path: str) -> bool:
    """Validate XML submission against provided schema, returning validation status."""
    try:
        with open(submission_xml_path, 'rb') as f:
            submission_xml_doc = etree.parse(f)

        schema.assertValid(submission_xml_doc)
        print('Validation successful')
        return True
    except etree.DocumentInvalid as e:
        print('Validation failed')
        print(e)
        return False
    except Exception as e:
        print(f'Error reading submission: {e}')
        return False


def main() -> None:
    """Process command line arguments and validate submission."""
    if len(sys.argv) != 3:
        print('Run in command line: python validate_schema.py <path_to_schema_folder> <path_to_submission_XML>')
        sys.exit(1)
    
    main_schema_path, supplementary_schema_path, submission_xml_path = check_and_get_paths(sys.argv[1], sys.argv[2])
    fixed_main_schema = fix_schema_includes_programmatically(main_schema_path, supplementary_schema_path)
    validate_submission_xml(fixed_main_schema, submission_xml_path)

if __name__ == '__main__':
    main()