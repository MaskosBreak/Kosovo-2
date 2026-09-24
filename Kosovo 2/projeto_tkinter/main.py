import tkinter as tk
from interface import LojaApp


def main():
    root = tk.Tk()
    app = LojaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()