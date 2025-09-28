import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.workflow_manager import WorkflowManager

# Test the combined analysis method
wm = WorkflowManager()
print('Combined analysis method exists:', hasattr(wm, '_analyze_with_gemini_combined'))