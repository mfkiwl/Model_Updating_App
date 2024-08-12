from sqlalchemy import select
from sqlalchemy.orm import aliased
from pydantic import BaseModel
from typing import List, Dict

from create_database import create_session, PointLoads

session = create_session()

stmt = (
    select(
        PointLoads.id,
        PointLoads.node_list,
        PointLoads.PX,
        PointLoads.PY,
        PointLoads.PZ,
        PointLoads.MX,
        PointLoads.MY,
        PointLoads.MZ
           )
)

result = session.execute(stmt).fetchall()

class PointLoad(BaseModel):
        id: int
        node_list: str
        PX: float
        PY: float
        PZ: float
        MX: float
        MY: float
        MZ: float

class AllLoads(BaseModel):
        loads: List[PointLoad]

        def append_load(self, new_load: PointLoad):
            self.loads.append(new_load)

all_loads = AllLoads(loads=[])
for row in result:
    ponit_load = PointLoad(id=row[0], node_list=row[1], PX=row[2], PY=row[3], PZ=row[4], MX=row[5], MY=row[6], MZ=row[7])
    all_loads.append_load(ponit_load)

print(all_loads)


