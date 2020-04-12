#%%
import xlrd
import json
import jsonschema

# デフォルトを設定する関数
def set_default(value,default,type):
    if value == "":
        out = default
    else:
        if type == "str":
            out = str(value)
        elif type == "float":
            out = float(value)
        elif type == "int":
            out = int(value)
        else:
            out = value
    return out

# 計算対象設備があるかどうかを判定する関数
def set_isCalculatedEquipment(input):
    if input == "■":
        isEquip = True
    else:
        isEquip = False

    return isEquip


#%% メイン関数
def inputdata_make(inputfileName):

    # 入力シートの読み込み
    wb = xlrd.open_workbook(inputfileName)

    # テンプレートjsonの読み込み
    with open('./builelib/inputdata/template.json', 'r') as f:
        data = json.load(f)

    # スキーマの読み込み
    with open('./builelib/inputdata/webproJsonSchema.json', 'r') as f:
        schema_data = json.load(f)
        
    # %%
    # 様式BLの読み込み
    if "様式BL" in wb.sheet_names():

        # シートの読み込み
        sheet_BL = wb.sheet_by_name("様式BL")

        # BL-1	建築物の名称
        data["Building"]["Name"] = str(sheet_BL.cell(10, 4).value)
        # BL-2	都道府県	(選択)
        data["Building"]["BuildingAddress"]["Prefecture"] = str(sheet_BL.cell(11, 4).value)
        # BL-3	建築物所在地	市区町村	(選択)
        data["Building"]["BuildingAddress"]["City"]  = str(sheet_BL.cell(12, 4).value)
        # BL-4	丁目、番地等
        data["Building"]["BuildingAddress"]["Address"]  = str(sheet_BL.cell(13, 4).value)
        # BL-5	地域の区分		(自動)
        data["Building"]["Region"] = str(int(sheet_BL.cell(14, 4).value))
        # BL-6	年間日射地域区分		(自動)
        data["Building"]["AnnualSolarRegion"] = str(sheet_BL.cell(15, 4).value)
        # BL-7	延べ面積 	[㎡]	(数値)
        data["Building"]["BuildingFloorArea"] = float(sheet_BL.cell(16, 4).value)
        # BL-8	「他人から供給された熱」	冷熱	(数値)
        data["Building"]["Coefficient_DHC"]["Cooling"] = float(sheet_BL.cell(17, 4).value)
        # BL-9	の一次エネルギー換算係数	温熱	(数値)
        data["Building"]["Coefficient_DHC"]["Heating"] = float(sheet_BL.cell(18, 4).value)

    #%%
    # 様式RMの読み込み
    if "様式RM" in wb.sheet_names():

        # シートの読み込み
        sheet_BL = wb.sheet_by_name("様式RM")
        # 初期化
        roomKey = None

        # 行のループ
        for i in range(10,sheet_BL.nrows):

            # シートから「行」の読み込み
            dataBL = sheet_BL.row_values(i)

            # 階と室名が空欄でない場合
            if (dataBL[0] != "") and (dataBL[1] != ""):

                # 階＋室をkeyとする
                roomKey = str(dataBL[0]) + '_' + str(dataBL[1])

                data["Rooms"][roomKey] = {
                        "buildingType": str(dataBL[2]),               
                        "roomType": str(dataBL[3]),
                        "roomArea": float(dataBL[4]),
                        "floorHeight": float(dataBL[5]),
                        "ceilingHeight": float(dataBL[6]),
                        "isCal_AC": set_isCalculatedEquipment(dataBL[7]),
                        "isCal_V": set_isCalculatedEquipment(dataBL[8]),
                        "isCal_L": set_isCalculatedEquipment(dataBL[9]),
                        "isCal_HW": set_isCalculatedEquipment(dataBL[10]),
                        "isCal_EV": set_isCalculatedEquipment(dataBL[11]),
                        "modelBuildingType": str(dataBL[12]),  
                        "buildingGroup": str(dataBL[13])
                }

    #%% 
    ## 外皮
    if "様式BE1" in wb.sheet_names():

        # シートの読み込み
        sheet_BE1 = wb.sheet_by_name("様式BE1")
        # 初期化
        roomKey = None

        # 行のループ
        for i in range(10,sheet_BE1.nrows):

            # シートから「行」の読み込み
            dataBE1 = sheet_BE1.row_values(i)

            # 階と室名が空欄でない場合
            if (dataBE1[0] != "") and (dataBE1[1] != ""):

                # 階＋室をkeyとする（上書き）
                roomKey = str(dataBE1[0]) + '_' + str(dataBE1[1])

                data["EnvelopeSet"][roomKey] = {
                        "isAirconditioned": set_default(str(dataBE1[2]),'無', "str"),
                        "WallList": [
                            {
                                "Direction": str(dataBE1[3]),
                                "EnvelopeArea": set_default(str(dataBE1[4]),None, "float"),
                                "EnvelopeWidth": set_default(str(dataBE1[5]),None, "float"),
                                "EnvelopeHeight": set_default(str(dataBE1[6]),None, "float"),
                                "WallSpec": set_default(str(dataBE1[7]),"無","str"),
                                "WallType": set_default(str(dataBE1[8]),"無","str"),
                                "WindowList":[
                                    {
                                        "WindowID": set_default(str(dataBE1[9]),"無","str"),
                                        "WindowNumber": set_default(str(dataBE1[10]),None, "float"),
                                        "isBlind": set_default(str(dataBE1[11]),"無","str"),
                                        "EavesID": set_default(str(dataBE1[12]),"無","str"),
                                        "Info": set_default(str(dataBE1[13]),"無","str"),
                                    }
                                ]       
                            }
                        ],
                    }

            else: # 階と室名が空欄である場合

                if (str(dataBE1[3]) == "") and (str(dataBE1[9]) != ""): ## 方位に入力がなく、建具種類に入力がある場合

                    data["EnvelopeSet"][roomKey]["WallList"][-1]["WindowList"].append(
                        {
                            "WindowID": str(dataBE1[9]),
                            "WindowNumber": set_default(str(dataBE1[10]),None, "float"),
                            "isBlind": set_default(str(dataBE1[11]),"無","str"),
                            "EavesID": set_default(str(dataBE1[12]),"無","str"),
                            "Info": set_default(str(dataBE1[13]),"無","str")
                        }
                    )                     

                elif (str(dataBE1[3]) != ""):  ## 方位に入力がある場合

                    data["EnvelopeSet"][roomKey]["WallList"].append(
                        {
                            "Direction": str(dataBE1[3]),
                            "EnvelopeArea": set_default(str(dataBE1[4]),None, "float"),
                            "EnvelopeWidth": set_default(str(dataBE1[5]),None, "float"),
                            "EnvelopeHeight": set_default(str(dataBE1[6]),None, "float"),
                            "WallSpec": set_default(str(dataBE1[7]),"無","str"),
                            "WallType": set_default(str(dataBE1[8]),"無","str"),
                            "WindowList":[
                                {
                                    "WindowID": set_default(str(dataBE1[9]),"無","str"),
                                    "WindowNumber": set_default(str(dataBE1[10]),None, "float"),
                                    "isBlind": set_default(str(dataBE1[11]),"無","str"),
                                    "EavesID": set_default(str(dataBE1[12]),"無","str"),
                                    "Info": set_default(str(dataBE1[13]),"無","str")
                                }
                            ]       
                        }
                    )

    if "様式BE2" in wb.sheet_names():

        # シートの読み込み
        sheet_BE2 = wb.sheet_by_name("様式BE2")
        # 初期化
        eltKey = None
        inputMethod = None

        # 行のループ
        for i in range(10,sheet_BE2.nrows):

            # シートから「行」の読み込み
            dataBE2 = sheet_BE2.row_values(i)

            # 断熱仕様名称が空欄でない場合
            if (dataBE2[0] != ""):

                # 断熱仕様名称をkeyとする（上書き）
                eltKey = str(dataBE2[0]) 

                # 入力方法を識別
                if dataBE2[9] != "":
                    inputMethod = "熱貫流率を入力"
                elif (dataBE2[6] != "") or (dataBE2[7] != ""):
                    inputMethod = "建材構成を入力"
                elif (dataBE2[3] != "") or (dataBE2[4] != ""):
                    inputMethod = "断熱材種類を入力"
                else:
                    raise Exception('Error!')
                
                if inputMethod == "熱貫流率を入力":

                    data["WallConfigure"][eltKey] = {
                            "structureType": str(dataBE2[1]),
                            "solarAbsorptionRatio": set_default(dataBE2[2], None, "float"),
                            "inputMethod": inputMethod,
                            "Uvalue": set_default(dataBE2[9], None, "float"),
                            "Info": set_default(dataBE2[10], "無","str"),
                        }

                elif inputMethod == "建材構成を入力":

                    data["WallConfigure"][eltKey] = {
                            "structureType": str(dataBE2[1]),
                            "solarAbsorptionRatio": set_default(dataBE2[2], None, "float"),
                            "inputMethod": inputMethod,
                            "layers": [
                                {
                                "materialID": set_default(dataBE2[6], None, "str"),
                                "Rvalue": set_default(dataBE2[7], None, "float"),
                                "thickness": set_default(dataBE2[8], None, "float"),
                                "Info": set_default(dataBE2[10], "無", "str")
                                }
                            ]
                        }

                elif inputMethod == "断熱材種類を入力":

                    data["WallConfigure"][eltKey] = {
                            "structureType": str(dataBE2[1]),
                            "solarAbsorptionRatio": set_default(dataBE2[2], None, "float"),
                            "inputMethod": inputMethod,
                            "materialID": set_default(dataBE2[3], None, "str"),
                            "Rvalue": set_default(dataBE2[4], None, "float"),
                            "thickness": set_default(dataBE2[5], None, "float"),
                            "Info": set_default(dataBE2[10], "無","str"),
                        }
            else:

                if inputMethod == "建材構成を入力":

                    data["WallConfigure"][eltKey]["layers"].append(
                        {
                            "materialID": set_default(dataBE2[6], None, "str"),
                            "Rvalue": set_default(dataBE2[7], None, "float"),
                            "thickness": set_default(dataBE2[8], None, "float"),
                            "Info": set_default(dataBE2[10], "無", "str")
                        }
                    )

    if "様式BE3" in wb.sheet_names():

        # シートの読み込み
        sheet_BE3 = wb.sheet_by_name("様式BE3")
        # 初期化
        eltKey = None
        inputMethod = None

        # 行のループ
        for i in range(10,sheet_BE3.nrows):

            # シートから「行」の読み込み
            dataBE3 = sheet_BE3.row_values(i)

            # 開口部仕様名称が空欄でない場合
            if (dataBE3[0] != ""):

                # 開口部仕様名称をkeyとする（上書き）
                eltKey = str(dataBE3[0]) 

                # 入力方法を識別
                if (dataBE3[9] != "") and (dataBE3[10] != ""):
                    inputMethod = "性能値を入力"
                elif (dataBE3[7] != "") and (dataBE3[8] != ""):
                    inputMethod = "ガラスの性能を入力"
                elif (dataBE3[5] != ""):
                    inputMethod = "ガラスの種類を入力"
                else:
                    raise Exception('Error!')

                if inputMethod == "性能値を入力":

                    data["WindowConfigure"][eltKey] = {
                            "windowArea": set_default(str(dataBE3[1]),None, "float"),
                            "windowWidth": set_default(str(dataBE3[2]),None, "float"),
                            "windowHeight": set_default(str(dataBE3[3]),None, "float"),
                            "inputMethod": inputMethod,
                            "windowUvalue": set_default(dataBE3[9], None, "float"),
                            "windowIvalue": set_default(dataBE3[10], None, "float"),
                            "Info": set_default(dataBE3[11], "無","str"),
                        }

                elif inputMethod == "ガラスの性能を入力":

                    data["WindowConfigure"][eltKey] = {
                            "windowArea": set_default(str(dataBE3[1]),None, "float"),
                            "windowWidth": set_default(str(dataBE3[2]),None, "float"),
                            "windowHeight": set_default(str(dataBE3[3]),None, "float"),
                            "inputMethod": inputMethod,
                            "frameType": set_default(dataBE3[4], "金属製", "str"),
                            "layerType": set_default(dataBE3[6], "単層", "str"),
                            "glassUvalue": set_default(dataBE3[7], None, "float"),
                            "glassIvalue": set_default(dataBE3[8], None, "float"),
                            "Info": set_default(dataBE3[11], "無","str"),
                        }

                elif inputMethod == "ガラスの種類を入力":

                    data["WindowConfigure"][eltKey] = {
                            "windowArea": set_default(str(dataBE3[1]),None, "float"),
                            "windowWidth": set_default(str(dataBE3[2]),None, "float"),
                            "windowHeight": set_default(str(dataBE3[3]),None, "float"),
                            "inputMethod": inputMethod,
                            "frameType": set_default(dataBE3[4], "金属製", "str"),
                            "glassID": set_default(dataBE3[5], None, "str"),
                            "Info": set_default(dataBE3[11], "無","str"),
                        }

    if "様式BE4" in wb.sheet_names():

        # シートの読み込み
        sheet_BE4 = wb.sheet_by_name("様式BE4")
        # 初期化
        eltKey = None

        # 行のループ
        for i in range(10,sheet_BE4.nrows):

            # シートから「行」の読み込み
            dataBE4 = sheet_BE4.row_values(i)

            # 日よけの名称が空欄でない場合
            if (dataBE4[0] != ""):

                # 日よけの名称名称をkeyとする（上書き）
                eltKey = str(dataBE4[0]) 

                data["ShadingConfigure"][eltKey] = {
                        "shadingEffect_C": set_default(str(dataBE4[1]),None, "float"),
                        "shadingEffect_H": set_default(str(dataBE4[2]),None, "float"),
                        "x1": set_default(str(dataBE4[3]),None, "float"),
                        "x2": set_default(str(dataBE4[4]),None, "float"),
                        "x3": set_default(str(dataBE4[5]),None, "float"),
                        "y1": set_default(str(dataBE4[6]),None, "float"),
                        "y2": set_default(str(dataBE4[7]),None, "float"),
                        "y3": set_default(str(dataBE4[8]),None, "float"),
                        "zxPlus": set_default(str(dataBE4[9]),None, "float"),
                        "zxMinus": set_default(str(dataBE4[10]),None, "float"),
                        "zyPlus": set_default(str(dataBE4[11]),None, "float"),
                        "zyMinus": set_default(str(dataBE4[12]),None, "float"),
                        "Info": set_default(dataBE4[13], "無","str"),
                    }

    #%% 
    ## 機械換気設備
    if "様式V1" in wb.sheet_names():
        
        # シートの読み込み
        sheet_V1 = wb.sheet_by_name("様式V1")
        # 初期化
        roomKey = None

        # 行のループ
        for i in range(10,sheet_V1.nrows):

            # シートから「行」の読み込み
            dataV = sheet_V1.row_values(i)

            # 階と室名が空欄でない場合
            if (dataV[0] != "") and (dataV[1] != ""):

                # 階＋室をkeyとする
                roomKey = str(dataV[0]) + '_' + str(dataV[1])

                data["VentilationRoom"][roomKey] = {
                        "VentilationType": str(dataV[2]),
                        "VentilationUnitRef":{
                            str(dataV[4]):{
                                "UnitType": str(dataV[3]),
                                "Info": str(dataV[5])
                            }
                        }
                }

            # 階と室名が空欄であり、かつ、機器名称に入力がある場合
            # 上記 if文 内で定義された roomKey をkeyとして、機器を追加する。
            elif (dataV[0] == "") and (dataV[1] == "") and (dataV[4] != ""):

                data["VentilationRoom"][roomKey]["VentilationUnitRef"][str(dataV[4])]  = {
                    "UnitType": str(dataV[3]),
                    "Info": str(dataV[5])
                }               


    if "様式V2" in wb.sheet_names():
        
        # シートの読み込み
        sheet_V2 = wb.sheet_by_name("様式V2")
        # 初期化
        unitKey = None

        # 行のループ
        for i in range(10,sheet_V2.nrows):

            # シートから「行」の読み込み
            dataV = sheet_V2.row_values(i)

            # 換気機器名称が空欄でない場合
            if (dataV[0] != ""):
                
                data["VentilationUnit"][str(dataV[0])] = {
                    "Number": set_default(dataV[1], 1, "float"),
                    "FanAirVolume": set_default(dataV[2], None, "float"),
                    "MoterRatedPower": set_default(dataV[3], None, "float"),
                    "PowerConsumption": set_default(dataV[4], None, "float"),
                    "HighEfficiencyMotor": set_default(str(dataV[5]),'無', "str"),
                    "Inverter": set_default(str(dataV[6]),'無', "str"),
                    "AirVolumeControl": set_default(str(dataV[7]),'無', "str"),
                    "VentilationRoomType": set_default(str(dataV[8]),None, "str"),
                    "AC_CoolingCapacity": set_default(dataV[9], None, "float"),
                    "AC_RefEfficiency": set_default(dataV[10], None, "float"),
                    "AC_PumpPower": set_default(dataV[11], None, "float"),
                    "Info": str(dataV[12])
                }


    #%% 
    if "様式L" in wb.sheet_names():
        
        # シートの読み込み
        sheet_L = wb.sheet_by_name("様式L")
        # 初期化
        roomKey = None

        # 行のループ
        for i in range(10,sheet_L.nrows):

            # シートから「行」の読み込み
            dataL = sheet_L.row_values(i)

            # 階と室名が空欄でない場合
            if (dataL[0] != "") and (dataL[1] != ""):

                # 階＋室をkeyとする
                roomKey = str(dataL[0]) + '_' + str(dataL[1])

                data["LightingSystems"][roomKey] = {
                    "roomWidth": set_default(dataL[2],None, "float"),
                    "roomDepth": set_default(dataL[3],None, "float"),
                    "unitHeight": set_default(dataL[4],None, "float"),
                    "roomIndex": set_default(dataL[5],None, "float"),
                    "lightingUnit": {
                        str(dataL[6]): {
                            "RatedPower": float(dataL[7]),
                            "Number": float(dataL[8]),
                            "OccupantSensingCTRL": set_default(str(dataL[9]),schema_data["definitions"]["Lighting_OccupantSensingCTRL"]["default"], "str"),
                            "IlluminanceSensingCTRL": set_default(str(dataL[10]),schema_data["definitions"]["Lighting_IlluminanceSensingCTRL"]["default"], "str"),
                            "TimeScheduleCTRL": set_default(str(dataL[11]),schema_data["definitions"]["Lighting_TimeScheduleCTRL"]["default"], "str"),
                            "InitialIlluminationCorrectionCTRL": set_default(str(dataL[12]),schema_data["definitions"]["Lighting_InitialIlluminationCorrectionCTRL"]["default"], "str")
                        }
                    }
                }

            # 階と室名が空欄であり、かつ、消費電力の入力がある場合
            elif (dataL[0] == "") and (dataL[1] == "") and (dataL[7] != ""):

                data["LightingSystems"][roomKey]["lightingUnit"][str(dataL[6])] = {
                    "RatedPower": float(dataL[7]),
                    "Number": float(dataL[8]),
                    "OccupantSensingCTRL": set_default(str(dataL[9]),schema_data["definitions"]["Lighting_OccupantSensingCTRL"]["default"], "str"),
                    "IlluminanceSensingCTRL": set_default(str(dataL[10]),schema_data["definitions"]["Lighting_IlluminanceSensingCTRL"]["default"], "str"),
                    "TimeScheduleCTRL": set_default(str(dataL[11]),schema_data["definitions"]["Lighting_TimeScheduleCTRL"]["default"], "str"),
                    "InitialIlluminationCorrectionCTRL": set_default(str(dataL[12]),schema_data["definitions"]["Lighting_InitialIlluminationCorrectionCTRL"]["default"], "str")
                }


    #%% 
    if "様式EV" in wb.sheet_names():

        # シートの読み込み
        sheet_EV = wb.sheet_by_name("様式EV")
        # 初期化
        roomKey = None

        # 行のループ
        for i in range(10,sheet_EV.nrows):

            # シートから「行」の読み込み
            dataEV = sheet_EV.row_values(i)

            # 階と室名が空欄でない場合
            if (dataEV[0] != "") and (dataEV[1] != "") :

                # 階＋室をkeyとする
                roomKey = str(dataEV[0]) + '_' + str(dataEV[1])

                data["Elevators"][roomKey] = {
                    "Elevator": [
                        {
                            "ElevatorName": set_default(str(dataEV[2]),"-","str"),
                            "Number": float(dataEV[3]),
                            "LoadLimit": float(dataEV[4]),
                            "Velocity": float(dataEV[5]),
                            "TransportCapacityFactor": set_default(str(dataEV[6]),1,"float"),
                            "ControlType": set_default(str(dataEV[7]),"交流帰還制御","str"),
                            "Info": str(dataEV[8])
                        }
                    ]
                }

            elif (dataEV[3] != "") or (dataEV[4] != ""):

                data["Elevators"][roomKey]["Elevator"].append(
                    {
                        "ElevatorName": set_default(str(dataEV[2]),"-","str"),
                        "Number": float(dataEV[3]),
                        "LoadLimit": float(dataEV[4]),
                        "Velocity": float(dataEV[5]),
                        "TransportCapacityFactor": set_default(str(dataEV[6]),1,"float"),
                        "ControlType": set_default(str(dataEV[7]),"交流帰還制御","str"),
                        "Info": str(dataEV[8])
                    }
                )


    # バリデーションの実行
    jsonschema.validate(data, schema_data)

    return data


#%%
if __name__ == '__main__':
    
    inputfileName = './sample/WEBPRO_inputSheet_for_Ver3.xlsx'

    inputdata = inputdata_make(inputfileName)

    # json出力
    fw = open('./sample/inputdata_test.json','w')
    json.dump(inputdata,fw,indent=4,ensure_ascii=False)
