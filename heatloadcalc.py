import numpy as np
import json
import json

# 負荷計算モジュール
import builelib.heat_load_calculation.common as common
from builelib.heat_load_calculation.Gdata import Gdata
from builelib.heat_load_calculation.Main import calc_Hload
from builelib.heat_load_calculation.Weather import enmWeatherComponent, Weather
from builelib.heat_load_calculation.Sunbrk import SunbrkType
from builelib.heat_load_calculation.Space import create_spaces

# 建物入力データの読み込み
filename = "./sample/example_one_room.json"

# 入力ファイルの読み込み
with open(filename, 'r') as f:
    inputdata = json.load(f)

# 空調スケジュール
HourlySchedule_AC = np.ones(8760)

# 設定温度
setpoint_room_temperature = np.ones(8760) * 24
setpoint_room_humidity = np.ones(8760) * 50

# 内部発熱スケジュール（時刻別）の読み込み [Wh/m2]
HourlySchedule_LT = np.ones(8760)
HourlySchedule_HM = np.ones(8760)
HourlySchedule_OA = np.ones(8760)

roomArea   = inputdata["Rooms"]["1F_事務室"]["roomArea"]
roomHeight = inputdata["Rooms"]["1F_事務室"]["ceilingHeight"]


##----------------------------------------------------------------------------------
## 負荷計算用の入力の作成 （室の設定）
##----------------------------------------------------------------------------------

# テンプレートの読み込み
with open('./builelib/heat_load_calculation/input_template.json', 'r') as f:
    hc_input = json.load(f)

hc_input["rooms"][0]["name"] = "room"  # 室名
hc_input["rooms"][0]["volume"] = np.round(roomArea * roomHeight, 4)   # 気積 [m3]

# 空調スケジュール（室用途で異なる）
hc_input["rooms"][0]["schedule"]["is_lower_temp_limit_set"] = HourlySchedule_AC
hc_input["rooms"][0]["schedule"]["is_upper_temp_limit_set"] = HourlySchedule_AC
hc_input["rooms"][0]["schedule"]["is_lower_humidity_limit_set"] = HourlySchedule_AC
hc_input["rooms"][0]["schedule"]["is_upper_humidity_limit_set"] = HourlySchedule_AC

# 設定温度（地域によって決定）
hc_input["rooms"][0]["schedule"]["temperature_lower_limit"] = setpoint_room_temperature  # 室温下限
hc_input["rooms"][0]["schedule"]["temperature_upper_limit"] = setpoint_room_temperature   # 室温上限
hc_input["rooms"][0]["schedule"]["relative_humidity_lower_limit"] = setpoint_room_humidity  # 湿度下限
hc_input["rooms"][0]["schedule"]["relative_humidity_upper_limit"] = setpoint_room_humidity  # 湿度上限
hc_input["rooms"][0]["schedule"]["local_vent_amount"] = np.zeros(8760)   # 局所換気量（0とする）

# 内部発熱量
hc_input["rooms"][0]["schedule"]["heat_generation_lighting"] = np.round(HourlySchedule_LT * roomArea, 5)    # 照明発熱スケジュール [W]
hc_input["rooms"][0]["schedule"]["number_of_people"] = np.round(HourlySchedule_HM / 119 * roomArea, 3)       # 人員密度スケジュール [人]
hc_input["rooms"][0]["schedule"]["heat_generation_appliances"] = np.round(HourlySchedule_OA * roomArea, 5)  # 機器発熱スケジュール [W]
hc_input["rooms"][0]["schedule"]["heat_generation_cooking"] = np.zeros(8760)   # 調理発熱（顕熱）スケジュール
hc_input["rooms"][0]["schedule"]["vapor_generation_cooking"] = np.zeros(8760)   # 調理発熱（水分）スケジュール

# 内壁（床）の設定
hc_input["rooms"][0]["boundaries"][0] = {
    "name": "floor",
    "boundary_type": "external_general_part",
    "area": roomArea,
    "is_sun_striked_outside": False,
    "temp_dif_coef": 0,
    "is_solar_absorbed_inside": True,
    "general_part_spec": {
        "outside_emissivity": 0.9,
        "outside_solar_absorption": 0.8,
        "inside_heat_transfer_resistance": 0.11,
        "outside_heat_transfer_resistance": 0.11,
        "layers": [
            {
                "name": 'カーペット類',
                "thermal_resistance": 0.0875,
                "thermal_capacity": 2.24
            },
            {
                "name": '鋼',
                "thermal_resistance": 0.000066667,
                "thermal_capacity": 10.86
            },
            {
                "name": '非密閉中空層',
                "thermal_resistance": 0.086,
                "thermal_capacity": 0
            },
            {
                "name": '普通コンクリート',
                "thermal_resistance": 0.107142857,
                "thermal_capacity": 289.5
            },
            {
                "name": '非密閉中空層',
                "thermal_resistance": 0.086,
                "thermal_capacity": 0
            },
            {
                "name": 'せっこうボード',
                "thermal_resistance": 0.052941176,
                "thermal_capacity": 9.27
            },
            {
                "name": 'ロックウール化粧吸音板',
                "thermal_resistance": 0.1875,
                "thermal_capacity": 3.0
            }
        ]
    },
    "solar_shading_part": {
        "existence": False
    }
}

# 内壁（天井）の設定
hc_input["rooms"][0]["boundaries"][1] = {
    "name": "ceil",
    "boundary_type": "external_general_part",
    "area": roomArea,
    "is_sun_striked_outside": False,
    "temp_dif_coef": 0,
    "is_solar_absorbed_inside": True,
    "general_part_spec": {
        "outside_emissivity": 0.9,
        "outside_solar_absorption": 0.8,
        "inside_heat_transfer_resistance": 0.11,
        "outside_heat_transfer_resistance": 0.11,
        "layers": [
            {
                "name": 'ロックウール化粧吸音板',
                "thermal_resistance": 0.1875,
                "thermal_capacity": 3.0
            },
            {
                "name": 'せっこうボード',
                "thermal_resistance": 0.052941176,
                "thermal_capacity": 9.27
            },
            {
                "name": '非密閉中空層',
                "thermal_resistance": 0.086,
                "thermal_capacity": 0
            },
            {
                "name": '普通コンクリート',
                "thermal_resistance": 0.107142857,
                "thermal_capacity": 289.5
            },
            {
                "name": '非密閉中空層',
                "thermal_resistance": 0.086,
                "thermal_capacity": 0
            },
            {
                "name": '鋼',
                "thermal_resistance": 0.000066667,
                "thermal_capacity": 10.86
            },
            {
                "name": 'カーペット類',
                "thermal_resistance": 0.0875,
                "thermal_capacity": 2.24
            }
        ]
    },
    "solar_shading_part": {
        "existence": False
    }
}

##----------------------------------------------------------------------------------
## 負荷計算用の入力の作成 （外皮の設定）
##----------------------------------------------------------------------------------

for wall_id, wall_configure in enumerate(inputdata["EnvelopeSet"]["1F_事務室"]["WallList"]):

    # 方位
    if wall_configure["Direction"] == "南":
        direction = "s"
    elif wall_configure["Direction"] == "南西":
        direction = "sw"
    elif wall_configure["Direction"] == "西":
        direction = "w"
    elif wall_configure["Direction"] == "北西":
        direction = "nw"
    elif wall_configure["Direction"] == "北":
        direction = "n"
    elif wall_configure["Direction"] == "北東":
        direction = "ne"
    elif wall_configure["Direction"] == "東":
        direction = "e"
    elif wall_configure["Direction"] == "南東":
        direction = "se"
    elif wall_configure["Direction"] == "上":
        direction = "top"
    elif wall_configure["Direction"] == "下":
        direction = "bottom"
    else:
        raise Exception("方位が不正です")

    if wall_configure["WallType"] == "日の当たる外壁":
        is_sun_striked_outside = True
    else:
        is_sun_striked_outside = False


    hc_input["rooms"][0]["boundaries"].append( {
        "name": "wall",
        "boundary_type": "external_general_part",
        "area": wall_configure["EnvelopeArea"],
        "is_sun_striked_outside": is_sun_striked_outside,
        "direction": direction,
        "temp_dif_coef": 1,
        "is_solar_absorbed_inside": False,
        "general_part_spec": {
            "outside_emissivity": 0.9,
            "outside_solar_absorption": 0.8,
            "inside_heat_transfer_resistance": 0.11,
            "outside_heat_transfer_resistance": 0.11,
            "layers": [
                {
                    "name": '普通コンクリート',
                    "thermal_resistance": 0.10,
                    "thermal_capacity": 300
                },
                {
                    "name": '断熱材',
                    "thermal_resistance": 0.001,
                    "thermal_capacity": 1.00
                }
            ]
        },
        "solar_shading_part": {
            "existence": False
        }
    })

    for window_id, window_configure in enumerate(wall_configure["WindowList"]):

        hc_input["rooms"][0]["boundaries"].append( 
            {
                "name": "window",
                "boundary_type": "external_transparent_part",
                "area": window_configure["WindowNumber"],
                "is_sun_striked_outside": is_sun_striked_outside,
                "direction": direction,
                "temp_dif_coef": 1,
                "is_solar_absorbed_inside": False,
                "transparent_opening_part_spec": {
                    "u_value": 2.5,
                    "eta_value": 0.8,
                    "outside_emissivity": 0.9,
                    "inside_heat_transfer_resistance": 0.11,
                    "outside_heat_transfer_resistance": 0.11,
                    "incident_angle_characteristics": 1
                },
                "solar_shading_part": {
                    "existence": False
                }
            }
        )


##----------------------------------------------------------------------------------
## 負荷計算実行
##----------------------------------------------------------------------------------

# シミュレーション全体の設定条件の読み込み
cdata = Gdata(**hc_input['common'])

# スペースの読み取り
spaces = create_spaces(cdata, hc_input['rooms'])

# 気象データの読み込み
weather = Weather(cdata.Latitude, cdata.Longitude, cdata.StMeridian)

# 熱負荷計算の実行
result = calc_Hload(cdata, spaces, weather)

resultdata = np.array(result)


##----------------------------------------------------------------------------------
## 計算結果の集計
##----------------------------------------------------------------------------------

Qroom_cnv_sens = resultdata[1:8760, 16] # 対流空調顕熱負荷[W]
Qroom_rad_sens = resultdata[1:8760, 17] # 放射空調顕熱負荷[W]
Qroom_cnv_late = resultdata[1:8760, 18] # 対流空調潜熱負荷[W]

# 室の全熱負荷 [W]
Qroom = (Qroom_cnv_sens.astype(float) + Qroom_rad_sens.astype(float) + Qroom_cnv_late.astype(float))

# 日積算化（冷房負荷と暖房負荷に分離）
QroomDc = np.zeros(365)  # 日積算冷房負荷 [MJ/day]
QroomDh = np.zeros(365)  # 日積算暖房負荷 [MJ/day]

for dd in range(0,365):
    for hh in range(0,24):
        
        num = 24*(dd-1)+hh
        
        if Qroom[num] <0:
            QroomDc[dd] += (-1) * Qroom[num]*3600/1000000  
        else:
            QroomDh[dd] += Qroom[num]*3600/1000000  

# print('--------------------------------------------')
# print(QroomDc)
# print('--------------------------------------------')
# print(QroomDh)
# print('--------------------------------------------')
