# Test Harness Documentation: L10N Test Framework

## Overview

This test harness is designed to automate testing of the Credential Management Autofill feature across different websites and regions combinations. It supports running tests for different combinations of sites (like Amazon, Walmart, etc.) and regions (US, CA, DE, FR), with optional configuration flags.

## Key Features

- **Multi-Region Testing**: Run tests across US, CA, DE, and FR regions
- **Multi-Site Testing**: Support for multiple sites including demo, amazon, walmart, mediamarkt, and others
- **Local Server**: Automatically starts and manages a local HTTP server for testing
- **Test Filtering**: Automatically skips tests based on configuration in JSON files
- **Configurable Test Execution**: Supports various pytest flags and options

## Configuration Files

The harness relies on several configuration files:

- **Region Test Configuration**: Located in `region/{region_name}.json`, defining tests for specific regions and also the sites supported for the region.
```aiignore
# example for CA region
{
    "region": "CA",
    "sites": [
    "amazon",
    "walmart",
    "demo",
    "etsy"
  ],
    "tests": [
    ]
}
```
- **Site Test Configuration**: Located in `constants/{site_name}.json` or `constants/{site_name}/{region}.json`, defining site-specific test configurations and skipped tests. Here we map the attributes for either `AutofillAddressBase` or `CreditCardBase` to the corresponding selectors.

```aiignore
{
  # example for calvinklein address site
  "url": "http://127.0.0.1:8080/calvinklein_ad.html",
  # map class attributes to selector values.
  "field_mapping": {
    "given_name": "7d7a6c7c-7084-477e-afda-b27c826032a8",
    "family_name": "179a5ec2-4a98-45e9-9806-abb5496700d0",
    "street_address": "a9506204-8cee-4723-acb0-91307b9ae8ef",
    "address_level_2": "3fdac58a-13b3-4ca5-a5fb-8b5cc9712360",
    "address_level_1": "d7171e42-f617-4093-bca7-d655ac58f2c9",
    "postal_code": "a2d9e97a-4dab-44cf-960f-f5bbc1db447a",
    "email": "e4ebe951-0ed1-4ea9-b2c2-518b7b2ec034",
    "telephone": "57aab032-b31d-4bf9-8b7a-3fc5f265f6fc"
  },
  # define the selector key
  "form_field": "*[data-moz-autofill-inspect-id='{given_name}']",
  # state whether to skip all tests for this section (address or credit card)
  "skip": "True",
  # list of selector values for easy access
  "fields": [
    "7d7a6c7c-7084-477e-afda-b27c826032a8",
    "179a5ec2-4a98-45e9-9806-abb5496700d0",
    "a9506204-8cee-4723-acb0-91307b9ae8ef",
    "3fdac58a-13b3-4ca5-a5fb-8b5cc9712360",
    "d7171e42-f617-4093-bca7-d655ac58f2c9",
    "a2d9e97a-4dab-44cf-960f-f5bbc1db447a",
    "e4ebe951-0ed1-4ea9-b2c2-518b7b2ec034",
    "57aab032-b31d-4bf9-8b7a-3fc5f265f6fc"
  ],
  # list of individual tests to skip for this configuration run.
  "skipped": []
}

```
## Usage

```bash
python -m l10n_CM.run_l10n [FLAGS] [REGIONS] [SITES]
```

### Parameters

- **FLAGS**: Additional flags for customizing test execution
- **REGIONS**: One or more region codes (US, CA, DE, FR)
- **SITES**: One or more site names (demo, amazon, walmart, etc.)

### Supported Flags

- `--run-headless`: Run tests in headless mode
- `-n [num]`: Specify number of parallel workers
- `--reruns [num]`: Specify number of test reruns on failure
- `--fx-executable`: Specify Firefox executable path
- `--ci`: Enable CI mode

### Examples

```bash
# Run tests for all regions and sites
python -m l10n_CM.run_l10n

# Run all tests for US region only across all available sites
python -m l10n_CM.run_l10n US

# Run all tests for amazon site only across all regions
python -m l10n_CM.run_l10n US

# Run tests for US region on amazon site
python -m l10n_CM.run_l10n US amazon

# Run tests for US and CA regions with 4 parallel workers
python -m l10n_CM.run_l10n -n 4 US CA

# Run tests for US region on amazon site in headless mode
python -m l10n_CM.run_l10n --run-headless US amazon
```

## Architecture

### Core Components

1. **Test Runner**: Orchestrates test execution with proper environment variables and pytest flags
2. **Local HTTP Server**: Serves site-specific HTML files for testing
3. **Test Selector**: Selects appropriate tests based on region and site configuration
4. **Flag Processor**: Validates and processes command-line arguments

### Test Execution Flow

1. Command-line arguments are parsed and validated
2. Site and region combinations are determined
3. For each combination:
   - Required tests are identified from configuration files
   - Tests to be skipped are filtered out
   - A local HTTP server is started (except for "demo" site)
   - Tests are executed with specified flags
   - Results are logged

## Environment Variables

The framework sets the following environment variables during test execution:

- `CM_SITE`: The site being tested
- `FX_REGION`: The region being tested
- `TEST_EXIT_CODE`: Exit code of the test execution
- `FX_L10N`: Flag to check whether l10n workflow is being run.

## Adding New Tests

1. Create test files in the `Unified` directory
2. Update the region configuration in `region/{region_name}.json` if new test is region specific.
3. If needed, update site-specific configurations to handle skipped tests.

## Adding New Regions/Sites

1. Add the new region/site to `valid_region`/`valid_sites` in the script
2. If new region, add a new mapping file to `region/` (must be capitalized abbreviation of the region `US.json`).
3. If new site, create a directory with the name of the site in `constants/` and another subdirectory for the region supported for that site.
4. Create necessary HTML files in `sites/{site_name}/{region}/` directory.
5. Create the necessary mapping files in `constants/{site_name}/{region}/`
   * The naming convention for both the mapping files and the HTML files are `{site}_ad` for Address Pages and `{site}_cc` for Credit Card Pages.

## Useful Documents
- [Sites/Regions to Automate](https://docs.google.com/spreadsheets/d/15_ejIC3YABnMGHafgkLeuuu_wakfpiLapOmUdBF2pVI/edit?usp=sharing)
- [Skipped Automation Test Combinations](https://docs.google.com/document/d/18zYICZ3lbtUK7-LC-2Gt8jRbxQp0w0Is0ytM2BrcD7w/edit?usp=sharing)

## Troubleshooting

- **Invalid Arguments**: Ensure all region codes, site names, and flags are valid
- **Missing HTML Files**: Verify that HTML files exist at `sites/{site_name}/{region}/`
- **Missing JSON Files**: Check for proper configuration files in `region/` and `constants/` directories
- **Test Failures**: Review test execution logs for details on failures
