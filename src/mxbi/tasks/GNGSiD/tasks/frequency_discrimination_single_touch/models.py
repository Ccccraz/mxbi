from mxbi.tasks.GNGSiD.models import BaseTrialConfig, BaseTrialData


class TrialConfig(BaseTrialConfig):
    min_stimulus_duration: int
    max_stimulus_duration: int
    freq_match: tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
    sound_attention_duration: int


class TrialData(BaseTrialData):
    trial_config: TrialConfig
