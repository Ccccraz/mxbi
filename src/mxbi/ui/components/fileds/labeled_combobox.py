from tkinter.ttk import Combobox, Frame, Label


class LabeledCombobox(Frame):
    def __init__(
        self,
        master,
        label_name: str,
        values: list[str],
        default_value: str,
        width: int = 15,
        state: str = "readonly",
    ) -> None:
        super().__init__(master)

        label = Label(self, text=label_name, width=width)
        label.grid(row=0, column=0, padx=(10, 0), pady=2, sticky="w")

        self._combo = Combobox(self, values=values, state=state)
        self._combo.grid(row=0, column=1, padx=(0, 10), pady=2, sticky="ew")
        self._combo.set(default_value)

        self.columnconfigure(1, weight=1)

    def get(self) -> str:
        return self._combo.get()


def create_cobmbo(
    master,
    label_text: str,
    values: list[str],
    default_value: str,
    width: int = 15,
    state: str = "readonly",
) -> LabeledCombobox:
    combo = LabeledCombobox(master, label_text, values, default_value, width, state)

    return combo
