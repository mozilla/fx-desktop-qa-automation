## CI Dry Run
The goal is to Enable a safe “dry run” mode for CI while skipping costly or side-effecting actions
(downloads, installs, test execution, artifact upload, notifications, publishing/deploying). 
This allows developers to validate CI behavior for workflow/code changes before running full CI.

### DTE Automation Dispatch workflow
DTE Automation Dispatch workflow is changed in such a way that it could be manually triggered via
workflow_dispatch. This workflow can be executed from navigating to `Actions` from the repository > 
select `DTE Automation Dispatch` and click on `Run workflow` to pass the parameters.Three parameters
are being passed to this workflow.

#### dry_run flag
A boolean flag that is passed to workflows along with conditional execution to skip expensive
or side-effecting steps. Full CI remains unchanged when dry_run=false.

#### preview_only flag
A boolean flag that is passed to workflow to print a summary of what would run: selected channels,
planned jobs, and which steps are skipped.

#### split
A string input parameter for DTE Automation Dispatch, which enables us to select a split to run.
The default value for split is `smoke`. It accepts string values for instance: `functional1`, 
`functional2`, etc.


### Other workflows
Aside from DTE Automation Dispatch workflow, the dry_run flag is being available for few other 
workflows such as: Check new beta version - Functional, Check new beta version - Smoke, and
Check new devedition version. These workflow can be executed by:

Select `Actions` from the repository >  select `Check new beta version - Functional` and click
on `Run workflow` to pass the `dry_run` parameter.

Select `Actions` from the repository >  select `Check new beta version - Smoke` and click
on `Run workflow` to pass the `dry_run` parameter.

Select `Actions` from the repository >  select `Check new devedition version` and click
on `Run workflow` to pass the `dry_run` parameter.

