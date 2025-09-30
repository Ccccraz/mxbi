from tkinter import BooleanVar
from tkinter.ttk import Checkbutton, Frame, Label


class LabeledCheckbox(Frame):
    def __init__(
        self, master, label_name: str, state: bool = False, width: int = 15
    ) -> None:
        super().__init__(master)
        self._value = BooleanVar(value=state)

        label = Label(self, text=label_name, width=width)
        label.grid(row=0, column=0, padx=(10, 0), pady=2, sticky="w")

        self._checkbox = Checkbutton(self, variable=self._value)
        self._checkbox.grid(row=0, column=1, padx=(0, 10), pady=2, sticky="e")

        self.columnconfigure(1, weight=1)

    def get(self) -> bool:
        return self._value.get()


def create_checkbox(
    master, label_text: str, state: bool = False, width: int = 15
) -> LabeledCheckbox:
    checkbox = LabeledCheckbox(master, label_text, state, width)

    return checkbox


if __name__ == "__main__":
    from tkinter import Tk

    main = Tk()
    main.geometry("300x200")

    create_checkbox(main, "test").pack()

    main.mainloop()
