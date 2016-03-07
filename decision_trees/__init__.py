import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from decision_trees.tree import main


def run():
    """Entry point for the application script"""
    main()
