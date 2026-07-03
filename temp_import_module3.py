import sys, os, traceback
sys.path.insert(0, os.getcwd())
print('cwd', os.getcwd())
try:
    import module3_shap_explainability
    print('imported module3_shap_explainability OK')
except Exception:
    traceback.print_exc()
