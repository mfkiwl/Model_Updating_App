from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Callable
import numpy as np

class Parameter(BaseModel):
    ''' Parameter class to generate propose distribution values'''
    name: Optional[str] = None
    initval: float
    mean: float
    std: float
    distribution: Callable[[float, float, int], np.ndarray]
    sample_size: Optional[int] = 1

    def get_value(self) -> float:
        return float(self.distribution(self.mean, self.std, self.sample_size)[0])
    
    def set_mean(self, mean: float):
        self.mean = mean
    
    def set_initval(self, initval: float):
        self.initval = initval

class ProposalParameters(BaseModel):
    ''' ParameterList class to generate propose distribution values'''
    parameters: List[Parameter]

    def append(self, parameter: Parameter):
        self.parameters.append(parameter)
    
    def get_values(self) -> List[float]:
        return [parameter.get_value() for parameter in self.parameters]
    
    def get_init_values(self) -> List[float]:
        return [parameter.initval for parameter in self.parameters]
    
    def set_means(self, means: List[float]):
        for parameter, mean in zip(self.parameters, means):
            parameter.set_mean(mean)

class ParameterRecorder(BaseModel):
    ''' ParameterRecorder class to record the values of the parameters'''
    parameter: Parameter
    values: Optional[List[float]] = []

    def append(self, value: float):
        self.values.append(value)

class RecorderList(BaseModel):
    ''' RecorderList class to record the values of the parameters'''
    recorders: List[ParameterRecorder]

    def append_multiple(self, values: List[float]):
        for recorder, value in zip(self.recorders, values):
            recorder.append(value)

    def append(self, recorder: ParameterRecorder):
        self.recorders.append(recorder)

    def get_values(self) -> List[float]:
        return [recorder.values for recorder in self.recorders]

class TargedParameter(BaseModel):
    ''' Set the target valuse of the parameter to minimize'''
    name: str
    target_value: float
    function_to_update: Callable

    posterior_distribution: List[float] = []

    def append_posterior(self, value: float):
        self.posterior_distribution.append(value)


# if __name__ == '__main__':
#     mas_param = Parameter(name = "masa",initval=0, mean=-4.6, std=0.5, distribution=np.random.normal)
#     mass_recorder = ParameterRecorder(parameter=mas_param,values=[])
    # mas_param = Parameter(mean=-4.6, std=0.5, distribution=np.random.normal)
    # et_param = Parameter(mean=1.5, std=0.2, distribution=np.random.lognormal)

    # mas_value: float = mas_param.get_value()
    # et_value: float = et_param.get_value()

    # print(mas_value)
    # print(et_value)