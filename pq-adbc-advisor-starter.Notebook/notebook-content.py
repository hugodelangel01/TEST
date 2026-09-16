# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # pq-adbc-advisor — starter notebook
# 
# Scans the currently-attached Fabric workspace and returns an item-by-item impact report for the ODBC → ADBC migration.
# 
# **This is a starting-point diagnostic, not a final audit.** Treat the report as the first pass to find the bulk of the work. For high-value production reports, validate the ADBC path in a copy of the item before flipping production over.
# 
# For per-connector dates and the migration timeline, the source of truth is the public migration guide at [aka.ms/adbc-migration](https://aka.ms/adbc-migration).
# 
# ---
# 
# ## What this notebook does
# 
# 1. Installs the `pq-adbc-advisor` package into this notebook session.
# 2. Runs `scan_workspace()` against the currently-attached workspace.
# 3. Renders the impact report inline.
# 4. Saves an HTML copy of the report to the default lakehouse (if one is attached).
# 
# Runtime: ~90 seconds on a 200-artifact workspace, longer for larger workspaces.
# 
# ---

# MARKDOWN ********************

# ## Step 1 — Install the package
# 
# The tool ships as a Python package installed directly from GitHub. This installs it into the current notebook session only. A PyPI release will follow once the tool graduates from public preview.

# CELL ********************

%pip install git+https://github.com/MichaelaIsaacs/pq-adbc-advisor.git@main --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 2 — Scan the current workspace
# 
# `scan_workspace()` auto-detects the workspace this notebook is attached to. It reads item definitions, walks every M expression it finds, and classifies every migrating connector call by cutover risk. It does not rewrite any M and does not trigger any refreshes.

# CELL ********************

from pq_adbc_advisor import scan_workspace

report = scan_workspace()
report

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 3 — Save the report
# 
# This writes a self-contained HTML file that you can download from the lakehouse Files pane and share inside your org. Excerpts are secret-redacted before rendering, so it's safe to share.
# 
# If no default lakehouse is attached, the report is saved to `/tmp/` and the path is printed.

# CELL ********************

output_path = report.to_html("/lakehouse/default/Files/pq_adbc_advisor_impact.html")
print(f"Report saved to: {output_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Optional — Tenant-wide scan (admin only)
# 
# If you have Fabric admin permissions and want to inventory every workspace in the tenant, uncomment and run the cell below. Tenant scans use the Fabric admin Scanner API and take 15–30 minutes for a mid-sized tenant.

# CELL ********************

# from pq_adbc_advisor import scan_tenant
#
# tenant_report = scan_tenant()
# tenant_report.to_html("/lakehouse/default/Files/pq_adbc_advisor_tenant.html")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Optional — Opt out of anonymous telemetry
# 
# Every scan sends anonymous counts to the Power Query team so we can measure adoption and prioritize connector coverage — SHA-256-hashed tenant and user identifiers only, no raw values by default. To opt out at any time, run the cell below. The opt-out is persisted across kernel restarts.

# CELL ********************

# from pq_adbc_advisor import disable_telemetry
# disable_telemetry()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Optional — Verify your telemetry pipeline is landing events
# 
# If you want to confirm that anonymous counts from your scan actually reached App Insights (helpful when running behind a corporate proxy or in a locked-down enterprise environment), run the health check below. It shows the last successful send, any recent failures, and the number of events waiting to be flushed.
# 
# You can also fire a synthetic canary event yourself to test end-to-end ingestion without running a full scan.

# CELL ********************

from pq_adbc_advisor import telemetry_health, send_canary

# 1. Check what the pipeline has been doing this session
health = telemetry_health()
print("Last successful send:", health.get("last_ok_at"))
print("Most recent failure:", health.get("last_failure"))
print("Buffered (waiting to flush):", health.get("buffered_envelopes"))
print("Opt-out active:", health.get("opt_out_active"))

# 2. Fire a fresh canary and confirm it landed
outcome = send_canary(source="customer-audit")
print("\nCanary outcome:", outcome)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ---
# 
# ## Where to file
# 
# - **Bugs and feature requests:** [github.com/microsoft/fabric-toolbox/issues](https://github.com/microsoft/fabric-toolbox/issues) — tag with `pq-adbc-advisor`
# - **Corner cases the tool flags but the standard connector doesn't cover:** adbcmigration@microsoft.com
# - **Public migration guide:** [aka.ms/adbc-migration](https://aka.ms/adbc-migration)
