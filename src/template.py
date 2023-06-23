import re
import traceback

class Template:
    def __init__(self, args, logger, template):
        self.logger = logger
        self.args = args
        self.template = template

    def _safe_eval(self, expr, variables):
        safe_env = {
            '__builtins__': {},
            'min': min,
            'max': max
        }
        safe_env.update(variables)
        try:
            return eval(expr, safe_env)
        except Exception as e:
            self.logger.log(f"Error evaluating expression: {expr}")
            self.logger.log(traceback.format_exc())
            raise e

    def expand(self, variables):
        result = self.template
        for expr in re.findall(r'\{([^}]+)\}', self.template):
            val = self._safe_eval(expr, variables)
            result = re.sub(r'\{%s\}' % re.escape(expr), str(val), result)
        return result

