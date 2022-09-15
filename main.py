import uvicorn as uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# - Find and fix the errors in the following program
# - Refactor the program to make it more modular (using a Pythonic style, e.g. numpy)
# - Implement an additional function geometric_series_sum() which takes an input parameter a and r
#   to calculate the sum of the first N elements of: a + a*r + a*r^2 + a*r^3 + ...
# - Test the application (what approach would you use for test?)


class Msg(BaseModel):
    msg: str


class GenerateData:
    pass


@app.post("/isGeometricSeries")
async def is_geometric_series_post(inp: Msg):
    values_list = inp.msg.split(",")
    result = check_if_geometric_series(values_list)
    return {"The input sequence is geometric": result}


async def geometric_series_sum(inp: GenerateData):
    pass


def check_if_geometric_series(series: list) -> bool:
    """
    Example:
    check_if_geometric_series([3, 6, 12, 24])
    True
    check_if_geometric_series([1, 2, 3, 4])
    False
    """
    common_ratio = series[1] / series[0]
    for index in range(len(series) - 1):
        if series[index + 1] / series[index] != common_ratio:
            return False

    return True


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
