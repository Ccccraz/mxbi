from mxbi.tasks.GNGSiD.models import BaseTrialConfig, BaseTrialData


class TrialConfig(BaseTrialConfig):
    min_stimulus_duration: int
    max_stimulus_duration: int
    visual_stimulus_delay: int


class TrialData(BaseTrialData):
    trial_config: TrialConfig
