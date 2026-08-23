# Pre-ISEF Testing Checklist

Use this checklist to verify everything works before your ISEF presentation.

---

## ✅ Installation Check

- [ ] Navigate to project directory: `cd /Users/elliottdong/Desktop/isef`
- [ ] Python environment active (check: `which python`)
- [ ] Dependencies installed: `pip install -e .`
- [ ] No import errors: `python -c "from solver.app_backend import RunParams; print('OK')"`

---

## ✅ New App Functionality

### Startup
- [ ] App starts without errors: `streamlit run backend/app/streamlit_app.py`
- [ ] Opens in browser at `http://localhost:8501`
- [ ] Header displays correctly with institutional branding
- [ ] About section expands and shows abstract

### Navigation
- [ ] Overview page loads (default page)
- [ ] Solver page loads
- [ ] Verification page loads
- [ ] Documentation page loads
- [ ] Navigation between pages preserves state

### Overview Page
- [ ] Quick start guide displays (3 steps)
- [ ] Physical background section readable
- [ ] Theory boxes show LaTeX equations correctly
- [ ] Citation block displays BibTeX

### Solver Page
- [ ] Sidebar shows all parameter sections
- [ ] Preset selector appears at top of sidebar
- [ ] Selecting "Ethanol (standard)" populates parameters
- [ ] Selecting "Water (standard)" populates parameters
- [ ] Selecting "Formamide (standard)" populates parameters
- [ ] Parameter tooltips work (hover over ⓘ icons)
- [ ] Theory boxes expand and show LaTeX

### Solver - Run Test (Ethanol Preset)
- [ ] Select "Ethanol (standard)" preset
- [ ] Click "▶️ Run Solver"
- [ ] Progress spinner appears
- [ ] Solver completes in < 2 seconds
- [ ] Success message appears
- [ ] Scalar diagnostics display (8 metric cards)
- [ ] RMS residual is between 0.1–1 Pa
- [ ] Peak field is between 0.5–2 MV/m
- [ ] Converged = "✓ Yes"

### Solver - Plot Spacing Check (IMPORTANT!)
- [ ] **Row 1:** Potential and Field Magnitude are side-by-side with visible gap
- [ ] **Each plot looks tall** (should be noticeably larger than before)
- [ ] **Row 2:** Interface and Residual are side-by-side with visible gap
- [ ] Plots have white backgrounds (not gray)
- [ ] Figure captions appear below each plot
- [ ] Hover over plots shows values (Plotly interactivity)
- [ ] Can zoom and pan on plots

### Solver - Export
- [ ] "📥 Download JSON" button works
- [ ] "📋 Copy Parameters" shows parameter block
- [ ] Results file written to `backend/results/latest_solver_run.json`

### Verification Page
- [ ] Sidebar shows verification config
- [ ] Apex radius input works
- [ ] Grid resolution selector works
- [ ] Explanation sections display ("What This Test Does")
- [ ] Theory boxes available in expander

### Verification - Run Test
- [ ] Click "▶️ Run Verification" (Fine grid)
- [ ] Progress message appears
- [ ] Verification completes in 10–60 seconds
- [ ] Success message appears
- [ ] Recovered angle displays (should be 49.0°–49.3°)
- [ ] Delta from Taylor angle (49.29°) shows
- [ ] Identity ratio displays (should be 0.99–1.01)
- [ ] Interpretation box appears (✅/ℹ️/⚠️)

### Verification - Plot Spacing Check (IMPORTANT!)
- [ ] **Verification landscape plot is LARGE** (600px, centered)
- [ ] **Imposed Taylor field plot is LARGE** (600px, centered)
- [ ] Plots have generous spacing around them
- [ ] Captions explain what each plot shows

### Documentation Page
- [ ] Table of contents displays
- [ ] All sections load (Governing Equations, Numerical Methods, etc.)
- [ ] LaTeX equations render correctly
- [ ] Parameter reference tables display
- [ ] Troubleshooting section readable
- [ ] References section lists papers

---

## ✅ Legacy App (Should Still Work)

- [ ] Legacy app starts: `streamlit run backend/app/streamlit_app_legacy.py`
- [ ] Opens at `http://localhost:8502` (different port)
- [ ] Runs solver successfully
- [ ] Plots appear (will be smaller/more cramped than new app)

---

## ✅ Documentation Files

- [ ] `backend/app/docs/SCIENTIST_USER_GUIDE.md` exists and is readable
- [ ] `backend/app/README.md` exists
- [ ] `backend/app/IMPLEMENTATION_SUMMARY.md` exists
- [ ] `backend/app/VISUAL_COMPARISON.md` exists
- [ ] `backend/app/COMPLETE_SUMMARY.md` exists
- [ ] Main `README.md` mentions new app

---

## ✅ Visual Quality Check

### Compare to Legacy (Side-by-Side Test)
1. Open legacy app in one browser window
2. Open new app in another browser window
3. Run same test (Ethanol preset) in both
4. Compare plot sizes:
   - [ ] New app plots are visibly **larger**
   - [ ] New app plots have more **spacing** between them
   - [ ] New app has **cleaner styling** (white backgrounds, serif font)

### Professional Appearance
- [ ] Fonts are serif (look like academic papers)
- [ ] Primary color is blue (not default Streamlit colors)
- [ ] Metric cards have borders
- [ ] Headers have dividers
- [ ] Icons are consistent throughout

---

## ✅ Performance Check

### Solver Performance
- [ ] Coarse grid (21×31) runs in < 0.5 seconds
- [ ] Medium grid (31×51) runs in < 1 second
- [ ] Fine grid (41×71) runs in < 2 seconds
- [ ] Cache hit (rerun with same params) is instant

### Verification Performance
- [ ] Fast grid (31×45) runs in < 5 seconds
- [ ] Fine grid (121×177) runs in 10–30 seconds
- [ ] Very Fine grid (241×353) runs in 30–60 seconds
- [ ] Cache hit is instant

---

## ✅ Edge Cases

### Parameter Validation
- [ ] Setting electrode spacing < nozzle radius shows warning
- [ ] Very Fine grid shows computational cost warning
- [ ] Invalid space-charge parameters handled gracefully

### Error Handling
- [ ] Non-converging space charge shows error message with suggestions
- [ ] Changed parameters show "parameters changed, rerun" message
- [ ] Failed solver run doesn't crash app

### Cache
- [ ] Cache clear button works
- [ ] Running new parameters doesn't use cached result
- [ ] Running same parameters uses cache (instant)

---

## ✅ Export and Files

- [ ] Results directory exists: `backend/results/`
- [ ] Latest solver run saved: `latest_solver_run.json`
- [ ] Latest verification saved: `latest_verification_run.json`
- [ ] JSON files are valid (can open in text editor)
- [ ] JSON files contain all parameters and results

---

## ✅ Browser Compatibility (Optional)

Test in multiple browsers if possible:
- [ ] Chrome/Chromium
- [ ] Safari
- [ ] Firefox
- [ ] Edge

Common issues to watch for:
- LaTeX rendering (should work in all modern browsers)
- Plot interactivity (Plotly should work everywhere)
- Layout (columns should be side-by-side, not stacked)

---

## ✅ ISEF Presentation Prep

### Demo Flow Practice
- [ ] Can navigate through app smoothly
- [ ] Can explain what each page does
- [ ] Can run solver in real-time during presentation
- [ ] Can show verification results
- [ ] Can point out enhanced plot spacing

### Talking Points Prepared
- [ ] Why Taylor cones matter (electrospray, thrusters)
- [ ] What the solver does (onset prediction, not full CFD)
- [ ] How verification works (recovered angle → 49.29°)
- [ ] What makes it accessible (presets, documentation, professional UI)
- [ ] Future work (experimental validation)

### Backup Plan
- [ ] Screenshots of all pages (in case of demo failure)
- [ ] PDF of key results (solver run, verification)
- [ ] Legacy app as fallback (if new app has issues)

---

## 🐛 Known Issues / Limitations

Document any issues you find during testing:

**Issue 1:**
- Observed: 
- Impact: 
- Workaround: 

**Issue 2:**
- Observed: 
- Impact: 
- Workaround: 

---

## ✅ Final Checks

Before ISEF:
- [ ] All tests above passed
- [ ] No critical bugs found
- [ ] Presentation flow practiced
- [ ] Backup materials prepared
- [ ] Python environment can be recreated (requirements.txt works)
- [ ] Can explain any part of the app if asked

---

## 📝 Notes

Use this space for notes during testing:

**What worked well:**


**What needs improvement:**


**Questions to resolve:**


---

## ✅ Sign-Off

- [ ] Testing complete
- [ ] All critical issues resolved
- [ ] Ready for ISEF presentation

**Tested by:** ___________________  
**Date:** ___________________  
**Status:** ☐ Ready  ☐ Needs work  ☐ Not ready

---

**Good luck with your ISEF presentation! 🎓🚀**
