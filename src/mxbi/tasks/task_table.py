from mxbi.models.task import TaskEnum
from mxbi.tasks.GNGSiD.stages.double_touch_introduce_stage.stage import (
    GNGSiDDoubleTouchIntroduceStage,
)
from mxbi.tasks.GNGSiD.stages.final_stage.stage import GNGSiDFinalStage
from mxbi.tasks.GNGSiD.stages.size_reduction_stage.stage import (
    SizeReductionStage,
)
from mxbi.tasks.GNGSiD.stages.visual_delay_stage.stage import (
    GNGSiDVisualDelayStage,
)
from mxbi.tasks.task import Task

task_table: dict[TaskEnum, type[Task]] = {
    TaskEnum.GNGSiD_SIZE_REDUCTION_STAGE: SizeReductionStage,
    TaskEnum.GNGSiD_VISUAL_DELAY_STAGE: GNGSiDVisualDelayStage,
    TaskEnum.GNGSiD_DOUBLE_TOUCH_INTRODUCE: GNGSiDDoubleTouchIntroduceStage,
    TaskEnum.GNGSiD_FINAL_STAGE: GNGSiDFinalStage,
}
