"""Run the full assignment pipeline (Q1-Q4) in order; all figures, tables and printed results go to output/."""

import Q1
import Q2
import Q3
import Q4

if __name__ == "__main__":
    for number, question in enumerate([Q1, Q2, Q3, Q4], start=1):
        print(f"\n{'=' * 30} Q{number} {'=' * 30}\n")
        question.main()
