import sys
from tkinter import Tk
from tkinter.ttk import Button, Frame, Label

from mxbi.config import session_config, session_options
from mxbi.models.reward import RewardEnum
from mxbi.models.session import ScreenTypeEnum, SessionConfig
from mxbi.ui.components.animal_card import AnimalCard
from mxbi.ui.components.fileds.labeled_checkbox import create_checkbox
from mxbi.ui.components.fileds.labeled_combobox import create_cobmbo
from mxbi.ui.components.fileds.labeled_textbox import create_textbox
from mxbi.utils.detect_platform import Platform


class LaunchPanel:
    def __init__(
        self,
    ) -> None:
        self._root = Tk()
        self._root.title("mxbi")
        self._init_ui()
        self._root.mainloop()

    def _init_ui(self) -> None:
        self._frame = Frame(self._root)
        self._frame.pack()

        self._init_general_ui()
        self._init_animals_ui()
        self._init_buttons_ui()

        self._bind_events()

    def _init_general_ui(self) -> None:
        frame_general = Frame(self._frame)
        frame_general.pack(fill="x")
        frame_general.columnconfigure(0, weight=1)

        self.label_title = Label(frame_general, text="General")
        self.label_title.pack()

        self.combo_experimenter = create_cobmbo(
            frame_general,
            "Experimenter: ",
            session_options.value.experimenter,
            session_config.value.experimenter,
        )
        self.combo_experimenter.pack(fill="x", expand=True)

        self.combo_xbi = create_cobmbo(
            frame_general,
            "XBI: ",
            session_options.value.xbi_id,
            session_config.value.xbi_id,
        )
        self.combo_xbi.pack(fill="x", expand=True)

        self.combo_reward = create_cobmbo(
            frame_general,
            "Reward: ",
            [i for i in session_options.value.reward_type],
            session_config.value.reward_type,
        )
        self.combo_reward.pack(fill="x", expand=True)

        self.combo_platform = create_cobmbo(
            frame_general,
            "Platform: ",
            [i for i in session_options.value.platform],
            session_config.value.platform,
        )
        self.combo_platform.pack(fill="x", expand=True)

        self.checkbox_rfid = create_checkbox(
            frame_general, "RFID", session_config.value.RFID
        )
        self.checkbox_rfid.pack(fill="x", expand=True)

        self.combo_screen = create_cobmbo(
            frame_general,
            "Screen: ",
            [i.name for i in session_options.value.screen_type],
            session_config.value.screen_type.name,
        )
        self.combo_screen.pack(fill="x", expand=True)

        self.entry_comments = create_textbox(frame_general, "Comments: ", height=8)
        self.entry_comments.pack(fill="x")

    def _init_animals_ui(self) -> None:
        frame_animals = Frame(self._frame)
        frame_animals.pack(fill="x")
        frame_animals.columnconfigure(0, weight=1)
        frame_animals.columnconfigure(1, weight=1)

        self._animal_cards: list[AnimalCard] = []
        for index, animal in enumerate(session_config.value.animals.values()):
            animal_card = AnimalCard(
                frame_animals, session_options.value.animal, animal, index
            )
            animal_card.grid(
                row=index // 2, column=index % 2, padx=2, pady=2, sticky="ew"
            )
            self._animal_cards.append(animal_card)

    def _init_buttons_ui(self) -> None:
        frame_button = Frame(self._frame)
        frame_button.pack(fill="x")
        frame_button.columnconfigure(0, weight=1)

        button_cancel = Button(frame_button, text="Cancel", command=sys.exit)
        button_cancel.grid(row=0, column=0, padx=2, pady=2, sticky="w")

        button_start = Button(frame_button, text="Start", command=self.save)
        button_start.grid(row=0, column=1, padx=2, pady=2, sticky="e")

    def _bind_events(self) -> None:
        self._root.protocol("WM_DELETE_WINDOW", sys.exit)

    def save(self) -> None:
        animals = {
            animal_card.data.name: animal_card.data
            for animal_card in self._animal_cards
        }

        config = SessionConfig(
            experimenter=self.combo_experimenter.get(),
            xbi_id=self.combo_xbi.get(),
            reward_type=RewardEnum(self.combo_reward.get()),
            platform=Platform(self.combo_platform.get()),
            RFID=self.checkbox_rfid.get(),
            screen_type=session_options.value.screen_type[
                ScreenTypeEnum(self.combo_screen.get())
            ],
            comments=self.entry_comments.get(),
            animals=animals,
        )

        session_config.save(config)
        self._root.destroy()


if __name__ == "__main__":
    panel = LaunchPanel()
