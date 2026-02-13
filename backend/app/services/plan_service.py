

class PlanConfig:
    def __init__(self):
        self._plans = {}

    def load(self, plans):
        for plan in plans:
            self._plans[plan.name] = {
                "capacity": plan.capacity,
                "refill_rate": plan.refill_rate
            }
    
    def get(self, plan_name):
        return self._plans.get(plan_name)
    
plan_service = PlanConfig()