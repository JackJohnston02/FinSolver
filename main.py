import sys
from PyQt6.QtWidgets import QApplication
from finsolver.gui import FinSolverMainWindow


def main():
    app = QApplication(sys.argv)
    window = FinSolverMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
