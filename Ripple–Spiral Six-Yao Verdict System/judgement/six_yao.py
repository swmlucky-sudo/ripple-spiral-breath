class SixYaoVerdict:
    def __init__(self):
        self.yao_states = []

    def observe(self, metrics: dict):
        """
        metrics:
          ripple
          spiral
          phase
          guard
        """
        yao = self.evaluate(metrics)
        self.yao_states.append(yao)

        if len(self.yao_states) > 6:
            self.yao_states.pop(0)

    def evaluate(self, metrics):
        # Return True / False / None
        pass

    def verdict(self):
        if len(self.yao_states) < 6:
            return "INCOMPLETE"
        if all(self.yao_states):
            return "PASS"
        return "FAIL"
