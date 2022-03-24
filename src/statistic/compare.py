
import json

class compareValue:
    
    def __init__(self, ref_median: float, ref_std: float, data_median: float):
        self.ref_median = ref_median
        self.ref_std = ref_std
        self.data_median = data_median

    def __iqr(self):
        if ((self.ref_median - 5*self.ref_std) > self.data_median):
                return "too_low"
            
        if ((self.ref_median + 5*self.ref_std) < self.data_median):
            return "too_high"
            
        return "ok"

    def compare_value(self):
        return self.__iqr()

class compareData:

    def __init__(self, ref_data: json, new_data: json):
        self.ref_data = ref_data
        self.new_data = new_data

    def __compare_temp(self):
        return (compareValue(self.ref_data['temperature'], self.ref_data['temp_std'], self.new_data['temperature']).compare_value())

    def __compare_humidity(self):
        return (compareValue(self.ref_data['humidity'], self.ref_data['humi_std'], self.new_data['humidity']).compare_value())

    def __compare_illuminance(self):
        return (compareValue(self.ref_data['illuminance'], self.ref_data['illu_std'], self.new_data['illuminance']).compare_value())

    def __compare_sound(self):
        return (compareValue(self.ref_data['sound'], self.ref_data['sound_std'], self.new_data['sound']).compare_value())

    def result(self):
        err = []
        if (self.__compare_temp() != "ok"):
            err.append("temperature is " + self.__compare_temp())
        if (self.__compare_humidity() != "ok"):
            err.append("humidity is "+ self.__compare_humidity())
        if (self.__compare_illuminance() != "ok"):
            err.append("illuminance is " + self.__compare_illuminance())
        if (self.__compare_sound() != "ok"):
            err.append("sound is " + self.__compare_sound())

        if (err == []):
            return "ok"
        else:
            msg = ""
            for i in err:
                msg += i
                msg += ". "
            return msg





if __name__ == '__main__':
    dataA =  {'temperature': 29.55, 'temp_std': 0.023199898579899528, 'humidity': 30.73, 'humi_std': 0.07814014559073405, 'illuminance': 9.68, 'illu_std': 0.22804798256713707, 'sound': 0.0, 'sound_std': 7.437484552628546, 'data_size': 18}
    dataB =  {'temperature': 29.84, 'temp_std': 0.10357125880145247, 'humidity': 30.54, 'humi_std': 0.10636999704421563, 'illuminance': 203.87, 'illu_std': 0.495811239597026, 'sound': 7.5, 'sound_std': 10.13874093744436, 'data_size': 61}
    dataC =  {'temperature': 30.0, 'temp_std': 0.05066130140765692, 'humidity': 30.49, 'humi_std': 0.05657358426428288, 'illuminance': 204.52, 'illu_std': 0.474498795723299, 'sound': 3.0, 'sound_std': 10.903436184750229, 'data_size': 65}
    dataD =  {'temperature': 28.895000000000003, 'temp_std': 0.38717539802861045, 'humidity': 36.045, 'humi_std': 0.6682647606651934, 'illuminance': 127.1, 'illu_std': 0.6058501561976378, 'sound': 6.0, 'sound_std': 9.631110819938822, 'data_size': 53}
    print(compareData(dataA, dataB).result())
    print(compareData(dataA, dataB).result())
    print(compareData(dataA, dataC).result())
    print(compareData(dataC, dataB).result())