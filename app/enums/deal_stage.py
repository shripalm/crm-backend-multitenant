from enum import Enum


class DealStage(str, Enum):
    """Enum representing the lifecycle stages of a deal"""
    PRESALES = "presales"
    SALES = "sales"
    SITE_VISIT = "site_visit"
    CORE_TEAM = "core_team"

    @classmethod
    def get_all_stages(cls):
        """Return list of all stages in order"""
        return [cls.PRESALES, cls.SALES, cls.SITE_VISIT, cls.CORE_TEAM]
    
    @classmethod
    def get_next_stage(cls, current_stage):
        """Get the next stage in the lifecycle"""
        stages = cls.get_all_stages()
        try:
            current_index = stages.index(current_stage)
            if current_index < len(stages) - 1:
                return stages[current_index + 1]
            return None  # Already at final stage
        except ValueError:
            return None
