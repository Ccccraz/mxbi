from mxbi.tasks.GNGSiD.models import BaseTrialConfig, BaseTrialData


class TrialConfig(BaseTrialConfig): ...


class TrialData(BaseTrialData):
    trial_config: TrialConfig
