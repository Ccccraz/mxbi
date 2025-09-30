from tkinter.ttk import Entry, Frame, Label


class LabeledEntry(Frame):
    def __init__(
        self, master, label_text: str, default_value: str, width: int = 15
    ) -> None:
        super().__init__(master)

        label = Label(self, text=label_text, width=width)
        label.grid(row=0, column=0, padx=(10, 0), pady=2, sticky="w")

        self._entry = Entry(self)
        self._entry.grid(row=0, column=1, padx=(0, 10), pady=2, sticky="ew")
        self._entry.insert(0, default_value)

        self.columnconfigure(1, weight=1)

    def get(self) -> str:
        return self._entry.get()


def create_entry(
    master, label_text: str, default_value: str = "", width: int = 15
) -> LabeledEntry:
    entry = LabeledEntry(master, label_text, default_value, width)

    return entry
