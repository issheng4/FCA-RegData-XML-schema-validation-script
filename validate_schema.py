"""XML Schema Validation Script"""

import sys
import os
from lxml import etree

def check_and_get_paths(schema_folder_path: str, submission_xml_path: str) -> tuple[str, str, str]:
    """Verify and retrieve paths for required schema files, returning these paths."""
    if not os.path.isdir(schema_folder_path):
        print(f'Error: schema folder not found at {schema_folder_path}')
        sys.exit(1)
    
    schema_files = [f for f in os.listdir(schema_folder_path) if f.endswith('.xsd')]

    # Ensure we don't pick up a CommonTypes file name that contains FSA029
    fsa029_schema_file = next((f for f in schema_files 
                              if 'FSA029' in f.upper() 
                              and 'COMMONTYPES' not in f.upper()), None)
    if not fsa029_schema_file:
        print(f'Error: FSA029 schema file (*.xsd) not found in {schema_folder_path}')
        sys.exit(1)

    common_types_file = next((f for f in schema_files 
                             if 'COMMONTYPES' in f.upper()), None)
    if not common_types_file:
        print(f'Error: CommonTypes schema file (*.xsd) not found in {schema_folder_path}')
        sys.exit(1)

    fsa029_schema_path = os.path.join(schema_folder_path, fsa029_schema_file)
    common_types_schema_path = os.path.join(schema_folder_path, common_types_file)

    if not os.path.isfile(submission_xml_path):
        print(f'Error: submission file not found at {submission_xml_path}')
        sys.exit(1)

    return fsa029_schema_path, common_types_schema_path, submission_xml_path

def fix_schema_includes_programmatically(fsa029_schema_path: str, common_types_schema_path: str) -> etree.XMLSchema:
    """Update schema includes to reference CommonTypes schema in same directory, returning the updated schema."""
    parser = etree.XMLParser(remove_blank_text=True)

    try:
        with open(fsa029_schema_path, 'rb') as f:
            schema_doc = etree.parse(f, parser)
        
        for include in schema_doc.xpath('//xs:include', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'}):
            if 'CommonTypes' in include.get('schemaLocation', ''):
                relative_common_types_path = os.path.basename(common_types_schema_path)
                include.set('schemaLocation', relative_common_types_path)

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
        print('Run in command line: python validate_fsa029.py <path_to_schema_folder> <path_to_submission_XML>')
        sys.exit(1)
    
    fsa029_schema_path, common_types_schema_path, submission_xml_path = check_and_get_paths(sys.argv[1], sys.argv[2])
    fixed_fsa029_schema = fix_schema_includes_programmatically(fsa029_schema_path, common_types_schema_path)
    validate_submission_xml(fixed_fsa029_schema, submission_xml_path)

if __name__ == '__main__':
    main()