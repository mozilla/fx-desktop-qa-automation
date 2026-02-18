## CI Dry Run
The goal is to Enable a safe “dry run” mode for CI while skipping costly or side-effecting actions
(downloads, installs, test execution, artifact upload, notifications, publishing/deploying). 
This allows developers to validate CI behavior for workflow/code changes before running full CI.

### DTE Automation Dispatch workflow
DTE Automation Dispatch workflow is changed in such a way that it could be manually triggered via
workflow_dispatch. Three parameters are being passed to this workflow.

#### drun_run flag
A boolean flag that is passed to workflows along with conditional execution to skip expensive
or side-effecting steps. Full CI remains unchanged when dry_run=false.

#### preview_only flag
A boolean flag that is passed to workflow to print a summary of what would run: selected channels,
planned jobs, and which steps are skipped.

#### split
A string input parameter for DTE Automation Dispatch, which enables us to select a split to run.
The default value for split is "smoke".


### Other workflows
Aside from DTE Automation Dispatch workflow, the dryn_run flag is being available for few other 
workflows such as: Check new beta version - Functional, Check new beta version - Smoke,
Check new devedition version. 
