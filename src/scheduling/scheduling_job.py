from typing import Any, Optional

from auth import user
from auth.user import User
from scheduling import schedule_config
from scheduling.schedule_config import ScheduleConfig


class SchedulingJob:
    def __init__(
        self,
        id: Any,
        user: User,
        schedule_config: ScheduleConfig,
        script_name: str,
        parameter_values: dict,
        description: Optional[str] = None,
        enabled: bool = True
    ) -> None:
        self.id: str = str(id)
        self.user: User = user
        self.schedule: ScheduleConfig = schedule_config
        self.script_name: str = script_name
        self.parameter_values: dict = parameter_values
        self.description: Optional[str] = description
        self.enabled: bool = enabled

    def as_serializable_dict(self) -> dict:
        result = {
            'id': self.id,
            'user': self.user.as_serializable_dict(),
            'schedule': self.schedule.as_serializable_dict(),
            'script_name': self.script_name,
            'parameter_values': self.parameter_values,
            'enabled': self.enabled
        }
        if self.description:
            result['description'] = self.description
        return result

    def get_log_name(self) -> str:
        return 'Job#' + str(self.id) + '-' + self.script_name


def from_dict(job_as_dict: dict) -> SchedulingJob:
    id = job_as_dict['id']
    parsed_user = user.from_serialized_dict(job_as_dict['user'])
    schedule = schedule_config.read_schedule_config(job_as_dict['schedule'])
    script_name = job_as_dict['script_name']
    parameter_values = job_as_dict['parameter_values']
    description = job_as_dict.get('description')
    enabled = job_as_dict.get('enabled', True)  # Default to enabled for backwards compatibility

    return SchedulingJob(id, parsed_user, schedule, script_name, parameter_values, description, enabled)
