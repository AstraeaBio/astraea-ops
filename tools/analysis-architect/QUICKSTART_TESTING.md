# Quick Start Testing Guide - Phase 1 Features

## Prerequisites

Ensure you have the required dependencies:
```bash
pip install streamlit tomli tomli-w pandas
```

## Step 1: Start the UI

From the `analysis-architect` directory:

```bash
cd T:\0_Organizational\analysis-architect
streamlit run project_tracker_ui.py
```

The UI should open at `http://localhost:8501`

## Step 2: Test Script Inventory Tab

### Test with 7Hills Project

1. **Select the 7Hills project** from the sidebar dropdown
   - Look for "251119_7Hills" in the project selector

2. **Navigate to the "📜 Script Inventory" tab**

3. **Scan the scripts directory**:
   - The scripts directory should auto-populate to: `T:\0_Organizational\analysis-architect\251119_7Hills`
   - Click **"🔄 Scan Scripts"**

4. **Expected results**:
   - Should find scripts in `Newer_Scripts/scripts/` subfolder
   - Should detect `.groovy` files (QuPath scripts)
   - Should detect `.ipynb` files (Python notebooks)
   - Version detection should work:
     - `Script_01_rev3_ThresholdAdjustment.groovy` → **latest**
     - Any `.old` files → **deprecated**

5. **Link a script to a component**:
   - Expand one of the discovered scripts
   - Multi-select components (e.g., `threshold-adjustment`)
   - Click **"➕ Add to Inventory"**
   - Should see success message and script appears in "Current Inventory" table

6. **Check the closeout scripts**:
   - The 7Hills project has a `[closeout]` section with script inventory
   - Should see these scripts in the "Current Inventory" table with Source: "closeout"

## Step 3: Test Output Tracking Tab

### Test with 7Hills Project Components

1. **Navigate to the "📊 Output Tracking" tab**

2. **Select a component** from the dropdown:
   - Try "Marker Threshold Adjustment" or "Cell Phenotype Export"

3. **Check the outputs**:
   - Should see metrics: Total Outputs, Completed, Completion %
   - For 7Hills (completed project), may show N/A if outputs defined with cloud paths

4. **Try bulk check**:
   - Click **"🔄 Check All Component Outputs"**
   - Should see a table with all components and their output completion status

## Step 4: Test Manual Script Addition

1. **Stay on the "📜 Script Inventory" tab**

2. **Scroll to "➕ Add Script Manually" section**

3. **Fill in the form**:
   - Script Name: `test_script.py`
   - Script Location: `scripts/test_script.py`
   - Language: `python`
   - Link to Components: (select any component)

4. **Click "➕ Add Script"**

5. **Verify**:
   - Should see success message
   - Script should appear in "Current Inventory" table
   - Open `project.toml` in text editor to verify `[[code_repository]]` entry was added

## Step 5: Verify TOML Update

Open `T:\0_Organizational\analysis-architect\251119_7Hills\project.toml` in a text editor.

Look for new `[[code_repository]]` entries at the end:

```toml
[[code_repository]]
script = "test_script.py"
location = "scripts/test_script.py"
component_ids = ["threshold-adjustment"]
last_modified = "2025-01-21"
language = "python"
```

## Common Issues & Solutions

### Issue: "No scripts found"
- **Cause**: Directory path is incorrect or has no script files
- **Solution**:
  - Verify the path exists
  - Try using absolute path: `T:\0_Organizational\analysis-architect\251119_7Hills`
  - Check if scripts are in a subfolder (e.g., `Newer_Scripts/`)

### Issue: Scripts appear but can't add to inventory
- **Cause**: Component list is empty or not loading
- **Solution**:
  - Check that project has `[[components]]` defined in `project.toml`
  - Reload the page (F5)

### Issue: Output tracking shows all "N/A"
- **Cause**: Component doesn't have `[[components.outputs]]` defined, or paths are cloud storage
- **Solution**:
  - Normal for components without output definitions
  - Cloud storage paths (gs://, s3://) will show ☁️ icon

### Issue: Can't see Script Inventory or Output Tracking tabs
- **Cause**: May have old cached version
- **Solution**:
  - Hard refresh browser (Ctrl+Shift+R)
  - Restart Streamlit server
  - Check for Python syntax errors in terminal

## Expected UI Layout

When viewing tabs, you should see (in order):

**Without Portfolio:**
1. 📊 Overview
2. ✏️ Update Components
3. 📜 Script Inventory ← **NEW**
4. 📊 Output Tracking ← **NEW**
5. 📝 Client Summary
6. ➕ Add Component

**With Portfolio:**
1. 🌐 Portfolio Overview
2. 📊 Project Overview
3. ✏️ Update Components
4. 📜 Script Inventory ← **NEW**
5. 📊 Output Tracking ← **NEW**
6. 📝 Client Summary
7. ➕ Add Component

## Testing Checklist

- [ ] UI starts without errors
- [ ] Can select 7Hills project from sidebar
- [ ] Script Inventory tab appears
- [ ] Can scan scripts directory
- [ ] Scripts are discovered and listed
- [ ] Version detection works (latest/deprecated/development)
- [ ] Can filter scripts by version status and language
- [ ] Can link scripts to components
- [ ] Scripts appear in Current Inventory table
- [ ] Can add scripts manually via form
- [ ] Closeout scripts are shown (for 7Hills)
- [ ] Output Tracking tab appears
- [ ] Can select component and see outputs
- [ ] Output existence is checked correctly (✅/❌)
- [ ] Bulk output check works
- [ ] Changes persist after page refresh
- [ ] `project.toml` is updated correctly

## Next Steps After Testing

Once you've verified Phase 1 works:

1. **Test with your own projects**:
   - Point to your active project directories
   - Scan your actual analysis scripts
   - Link scripts to components

2. **Provide feedback**:
   - What works well?
   - What's confusing or needs improvement?
   - Which Phase 2 features are most valuable?

3. **Start using it in your workflow**:
   - Scan scripts as you develop them
   - Check output completion before client updates
   - Use script inventory for project close-out documentation

## Support

If you encounter issues:
1. Check the terminal where Streamlit is running for error messages
2. Review `SCRIPT_TRACKING_GUIDE.md` for detailed usage instructions
3. Check `PHASE1_IMPLEMENTATION_SUMMARY.md` for known limitations

---

*Testing Guide for Analysis Architect v1.2 (Phase 1)*
