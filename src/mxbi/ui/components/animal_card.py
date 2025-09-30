from tkinter.ttk import Frame, Label

from mxbi.models.session import AnimalConfig, AnimalOptions
from mxbi.models.task import TaskEnum
from mxbi.ui.components.fileds.labeled_combobox import create_cobmbo


class AnimalCard(Frame):
    def __init__(
        self,
        master,
        schema: AnimalOptions,
        animal: AnimalConfig,
        animal_index: int,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._init_ui(schema, animal, animal_index)
        self.__animal = animal

    def _init_ui(
        self, schema: AnimalOptions, animal: AnimalConfig, animal_index: int
    ) -> None:
        self.configure(width=200, height=150, relief="ridge", borderwidth=5)

        self.title_label = Label(self, text=f"Animal {animal_index}")
        self.title_label.pack()

        self.combo_name = create_cobmbo(self, "Name:", schema.name, animal.name, 8)
        self.combo_name.pack(fill="x", expand=True)

        self.combo_step = create_cobmbo(
            self,
            "Level:",
            [str(i) for i in schema.level],
            str(animal.level),
            8,
        )
        self.combo_step.pack(fill="x", expand=True)

        self.combo_task = create_cobmbo(
            self, "Task:", [i for i in schema.task], animal.task, 8
        )
        self.combo_task.pack(fill="x", expand=True)

    @property
    def data(self) -> AnimalConfig:
        self.__animal.name = self.combo_name.get()
        self.__animal.level = int(self.combo_step.get())
        self.__animal.task = TaskEnum(self.combo_task.get())

        return self.__animal


if __name__ == "__main__":
    from tkinter import Tk

    from mxbi.config import session_options
    from mxbi.utils.logger import logger

    root = Tk()
    root.title("Animal Card Test")

    animal = AnimalConfig(name="mock", level=0, task=TaskEnum.IDEL)

    animal_card = AnimalCard(root, session_options.value.animal, animal, 1)
    animal_card.pack(padx=20, pady=20)

    logger.info(animal_card.data)
    root.mainloop()
