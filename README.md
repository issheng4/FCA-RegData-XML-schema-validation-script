# FCA RegData XML schema validation script

## Background

A Python script which validates an XML submission against the Bank of England's schema to ensure compliance (from the Financial Conduct Authority https://regdata.fca.org.uk/).

The script is currently tailored to validate Balance Sheet submissions against the Bank of England FSA029 schema. It ensures that:

- FSA029 submissions are validated against the FSA029 schema
- CommonTypes schema dependencies are handled programmatically
- Schema files remain unmodified before and after execution

The script and folder contents can be editted to validate any different schema.

This script is useful for firms to confirm that their accounts submitted to the FCA are in a valid format.

## Structure

- `validate_schema.py` The script, currently to validate the FSA029 schema. The script contains notes with where to edit if you wish to validate other schemas.
- `/schemas` Contains the FSA029 schema plus a CommonTypes external resource file which is imported into the FSA029 schema. These schemas can be swapped out for other XSD files from the FCA for whichever schemas you wish to validate .
- `/samples` Contains one valid FSA029 XML sample which will return successful, and one XML sample which contains full sample data for all fields and thus will fail the validation as the Capital element with the `<xs:choice>` tag contains all possible options rather than just 1. These samples can be swapped out with a relevant data sample depending on what schemas are to be validated.

## How to run

1. Ensure requirements are installed:
   - Python 3.8+
   - lxml library (`pip install lxml`)

2. Place the following files in a schema folder:
   - FSA029-Schema.xsd
   - CommonTypes-Schema.xsd

   *Both schema files must be in the same directory.*

3. Run the script from command line:
   ```
   python validate_schema.py <path_to_schema_folder> <path_to_submission_XML>
   ```

   Example:
   ```
   python validate_schema.py ./schemas ./samples/FSA029-Sample-Full.xml
   ```

## Output

The script will output one of:
- `Validation successful` if the submission XML is valid
- `Validation failed` followed by the first instance of a validation error, if the submission XML is invalid
- Error messages for missing files or other issues