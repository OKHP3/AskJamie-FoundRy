# AskJamie Repository Inventory

## Capture boundary

**Snapshot date:** 2026-07-26  
**Scope:** AskJamie-named GitHub repositories and adjacent local clones.  
**Excluded:** `OKHP3/AskJamie`, the GitHub Pages primary website, and
`OKHP3/AskJamie-FoundRy`, this FoundRy relay.  
**Source:** GitHub connector repository metadata and read-only local Git
configuration under `C:\Users\jamie\OKH-Local\04_GitHub_Mirrors`.

All 19 scoped repositories are private, active, and use `main` as their default
branch. The connected GitHub account has `admin`, `maintain`, `pull`, `push`,
and `triage` permissions on each. All matching local worktrees were clean at
the time of capture.

This is an operational inventory, not a public-graduation decision. The two
client overlays remain subject to their permanent-private controls.

## Repository and clone crosswalk

| Capability | Canonical GitHub repository | Local clone | Local `origin` | State |
|---|---|---|---|---|
| AJ01 Resume Representative | `OKHP3/askjamie-aj01-resume-representative` | `askjamie-aj01-resume-representative` | `OKHP3/AskJamie-GPT-AJ01` | clean, legacy origin name |
| AJ02 Professional Portfolio | `OKHP3/askjamie-aj02-professional-portfolio` | `askjamie-aj02-professional-portfolio` | `OKHP3/AskJamie-GPT-AJ02` | clean, legacy origin name |
| AJ03 Enterprise Sleuth | `OKHP3/askjamie-aj03-enterprise-sleuth` | `askjamie-aj03-enterprise-sleuth` | `OKHP3/AskJamie-GPT-AJ03` | clean, legacy origin name |
| AJ04 BrandGuard | `OKHP3/askjamie-aj04-brandguard` | `askjamie-aj04-brandguard` | `OKHP3/AskJamie-GPT-AJ04` | clean, legacy origin name |
| BRG00 Builders FirstSource | `OKHP3/askjamie-brg00-builders-firstsource` | `askjamie-brg00-builders-firstsource` | `OKHP3/AskJamie-GPT-BRG00` | clean, legacy origin name, permanently private |
| BRG01 LEGO | `OKHP3/askjamie-brg01-lego` | `askjamie-brg01-lego` | `OKHP3/AskJamie-GPT-BRG01` | clean, legacy origin name |
| BRG02 Starbucks | `OKHP3/askjamie-brg02-starbucks` | `askjamie-brg02-starbucks` | `OKHP3/AskJamie-GPT-BRG02` | clean, legacy origin name |
| BRG03 Brooks Running | `OKHP3/askjamie-brg03-brooks-running` | `askjamie-brg03-brooks-running` | `OKHP3/AskJamie-GPT-BRG03` | clean, legacy origin name |
| BRG04 PING | `OKHP3/askjamie-brg04-ping` | `askjamie-brg04-ping` | `OKHP3/AskJamie-GPT-BRG04` | clean, legacy origin name |
| BRG05 Costco | `OKHP3/askjamie-brg05-costco` | `askjamie-brg05-costco` | `OKHP3/AskJamie-GPT-BRG05` | clean, legacy origin name |
| BRG06 Hershey | `OKHP3/askjamie-brg06-hershey` | `askjamie-brg06-hershey` | `OKHP3/AskJamie-GPT-BRG06` | clean, legacy origin name |
| BRG07 LVMH | `OKHP3/askjamie-brg07-lvmh` | `askjamie-brg07-lvmh` | `OKHP3/AskJamie-GPT-BRG07` | clean, legacy origin name |
| BRG08 Dollar General | `OKHP3/askjamie-brg08-dollar-general` | `askjamie-brg08-dollar-general` | `OKHP3/AskJamie-GPT-BRG08` | clean, legacy origin name |
| BRG09 Coca-Cola | `OKHP3/askjamie-brg09-coca-cola` | `askjamie-brg09-coca-cola` | `OKHP3/AskJamie-GPT-BRG09` | clean, legacy origin name |
| BRG10 Discount Tire | `OKHP3/askjamie-brg10-discount-tire` | `askjamie-brg10-discount-tire` | `OKHP3/AskJamie-GPT-BRG10` | clean, legacy origin name |
| BRG11 Scheels | `OKHP3/askjamie-brg11-scheels` | `askjamie-brg11-scheels` | `OKHP3/AskJamie-GPT-BRG11` | clean, legacy origin name |
| BRG12 Mathews Archery | `OKHP3/askjamie-brg12-mathews-archery` | `askjamie-brg12-mathews-archery` | `OKHP3/AskJamie-GPT-BRG12` | clean, legacy origin name |
| BFS AJ03 Enterprise Sleuth | `OKHP3/buildersfirstsource-askjamie-aj03-enterprise-sleuth` | `buildersfirstsource-askjamie-aj03-enterprise-sleuth` | canonical | clean, permanently private client overlay |
| CVS Health AJ03 Enterprise Sleuth | `OKHP3/cvshealth-askjamie-aj03-enterprise-sleuth` | `cvshealth-askjamie-aj03-enterprise-sleuth` | canonical | clean, permanently private client overlay |

## Reconciliation finding

Seventeen local clones use origin URLs with legacy `AskJamie-GPT-AJ##` or
`AskJamie-GPT-BRG##` names. Their local folder names and the GitHub connector
both identify the canonical repository slugs listed above. This snapshot does
not establish whether GitHub redirects those older URLs, nor does it alter any
remote configuration.

Before a bulk fetch, push, migration, or automation rollout, verify the
canonical remote for each affected clone and change it only under an explicit,
reviewed migration decision.

## Approved interaction boundary

The inventory establishes that the connected GitHub account can inspect and
perform repository-level operations for every scoped remote. Read-only
interrogation may include repository metadata, files, branches, commits,
issues, pull requests, workflows, and differences between local and remote
state. Changes to a GitHub remote, its settings, or a sibling local clone still
require a specifically authorized task and should be performed repository by
repository or through a reviewed bulk plan.
