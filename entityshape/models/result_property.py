from pydantic import BaseModel


class ResultProperty(BaseModel):
    label: str = ""
    pid: str = ""

    def __str__(self):
        return f"{self.label} ({self.pid})"
