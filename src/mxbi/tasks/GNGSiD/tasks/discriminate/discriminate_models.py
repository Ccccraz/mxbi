from mxbi.tasks.GNGSiD.models import BaseTrialConfig, BaseTrialData


class TrialConfig(BaseTrialConfig):
    go: bool
    visual_stimulus_delay: int

    attention_duration: int

    stimulus_freq_high: int
    stimulus_freq_high_duration: int
    stimulus_freq_low: int
    stimulus_freq_low_duration: int
    stimulus_interval: int


class TrialData(BaseTrialData):
    trial_config: TrialConfig
