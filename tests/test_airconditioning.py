import pandas as pd
import csv
from builelib import airconditioning
import pytest
import json
import openpyxl

### テストファイル名 ###
# 辞書型 テスト名とファイル名

testcase_dict = {
    "AHU_basic": "./tests/airconditioning/★空調設備テストケース一覧.xlsx",
}


def convert2number(x, default):
    '''
    空欄にデフォルト値を代入する
    '''
    if x == "":
        x = default
    else:
        x = float(x)
    return x


def read_testcasefile(filename):
    '''
    テストケースファイルを読み込む関数
    '''
    wb = openpyxl.load_workbook(filename)
    sheet = wb["Sheet1"]
    testdata = [row for row in sheet.iter_rows(values_only=True) if row[0]]

    return testdata


#### テストケースファイルの読み込み

test_to_try  = []  # テスト用入力ファイルと期待値のリスト
testcase_id  = []  # テスト名称のリスト

for case_name in testcase_dict:

    # テストファイルの読み込み
    testfiledata = read_testcasefile(testcase_dict[case_name])

    # ヘッダーの削除
    testfiledata.pop(0)

    # テストケース（行）に対するループ
    for testdata in testfiledata:

        filename = "./tests/airconditioning/ACtest_" + testdata[0] + ".json"
        # 入力データの作成
        with open(filename, 'r', encoding='utf-8') as f:
            inputdata = json.load(f)

        # 期待値
        expectedvalue = (testdata[4])

        # テストケースの集約
        test_to_try.append( (inputdata, expectedvalue) )
        # テストケース名
        testcase_id.append(case_name + testdata[0])


# テストの実施
@pytest.mark.parametrize('inputdata, expectedvalue', test_to_try, ids=testcase_id)
def test_calc(inputdata, expectedvalue):

    # 検証用
    with open("inputdata.json",'w', encoding='utf-8') as fw:
        json.dump(inputdata, fw, indent=4, ensure_ascii=False)

    # 計算実行        
    resultJson = airconditioning.calc_energy(inputdata)

    diff_Eac = (abs(resultJson["E_airconditioning"] - expectedvalue)) / abs( expectedvalue )

    # 比較（0.01%まで）
    assert diff_Eac < 0.0001


if __name__ == '__main__':
    print('--- test_airconditioning.py ---')
