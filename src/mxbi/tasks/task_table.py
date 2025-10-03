from mxbi.models.task import TaskEnum
from mxbi.tasks.GNGSiD.stages.detect_stage.detect_stage import GNGSiDDetectStage
from mxbi.tasks.GNGSiD.stages.discriminate_stage.discriminate_stage import GNGSiDDiscriminateStage
from mxbi.tasks.GNGSiD.stages.size_reduction_stage.size_reduction_stage import SizeReductionStage
from mxbi.tasks.task_protocol import Task

task_table: dict[TaskEnum, type[Task]] = {
    TaskEnum.GNGSiD_SIZE_REDUCTION_STAGE: SizeReductionStage,
    TaskEnum.GNGSiD_DETECT_STAGE: GNGSiDDetectStage,
    TaskEnum.GNGSiD_DISCRIMINATE_STAGE: GNGSiDDiscriminateStage,
}
