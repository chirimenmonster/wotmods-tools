# wotmods-tools

## wottool

python wottool.py [-h] [-b _WoT_install_dir_] {version | xml | unzip | wotmod | decompile} <_command_specific_args_>

WoT の pkg ファイル展開、pyc デコンパイル、packed xml のテキスト化、wotmod 作成支援などを行うツールです。
実行には Python 2 が必要です。

### コマンド

* __version__: WoT のバージョン情報を表示します。
* __xml__: packed XML のファイルを通常の XML ファイル（テキスト形式）に変換します。
* __unzip__:　zip, pkg, wotmod ファイル、またはその一部を展開します。
* __wotmod__: wotmod パッケージを作成します。
* __decompile__: pyc ファイルをデコンパイルします。

### 共通オプション

* __-b__ _Wot_install_dir_:
    WoT がインストールされているディレクトリを指定します。
    デフォルトは `C:/Games/World_of_Tanks` です。

## wottool version

python wottool.py [-b _WoT_install_dir_] version [-b] [-s]

WoT のバージョン情報を表示します。

* __-b__:
    バージョン文字列のうち、ビルド番号（# に続く数値）を表示します。
* __-s__:
    バージョン文字列のうち、バージョン番号（v. に続く文字列で # の前まで）を表示します。
    res_mods や mods フォルダ下のバージョン別サブフォルダ名に相当します。

### 使用例

```
> py -2 wottool.py version
v.1.3.0.1 #1111
```

```
> py -2 wottool.py version -s
1.3.0.1
```

```
> py -2 wottool.py -b c:/Games/World_of_Tanks_CT version -s
1.4.0.0 Common Test
```

## wottool xml

python wottool.py [-b _WoT_install_dir_] xml [-p _package_] [-e _regex_] [-x _xpath_] [-H] [-s] [_file_]

packed XML のファイルを通常の XML ファイル（テキスト形式）に変換します。

* __-p__ _package_:
    指定の package から XML ファイルを抽出します。
    package 名は WoT インストールフォルダの `res/package` 内から選択します。
* __-e__ _regex_:
    `regex` で指定した正規表現にマッチするものだけを対象とします。
    -e オプションを指定した場合 `file` は無視されます。
* __-x__ _xpath_:
    表示する XML ファイル内のサブツリーを指定します。
    書式は xpath のサブセットです。
* __-H__:
    出力の各行にファイル名を表示します。
* __-s__:
    xml を整形せずに表示します。
* _file_:
    変換対象の XML ファイルを指定します。
    絶対パス、相対パス、package ファイル内のパスが指定可能です。
    (必須)

### 使用例

```
> py -2 wottool.py xml -x './/consoleFonts' resources.xml
<consoleFonts>
  <font>system_tiny.font</font>
  <font>system_small.font</font>
  <font>system_medium.font</font>
  <font>system_large.font</font>
</consoleFonts>
```

```
> py -2 wottool.py xml -p gui.pkg -x './/setting[name="rememberPassVisible"]' gui/gui_settings.xml
<setting>
  <name>rememberPassVisible</name>
  <type>bool</type>
  <value>False</value>
</setting>
```

```
> py -2 wottool.py xml -p scripts.pkg -e 'scripts/item_defs/vehicles/.*\.xml' -x './/gunCamPosition' -H
scripts/item_defs/vehicles/germany/G110_Typ_205.xml: <gunCamPosition>0.001302 0.629715 1.201</gunCamPosition>
scripts/item_defs/vehicles/germany/G113_SP_I_C.xml: <gunCamPosition>0.000000 0.27598 0.762</gunCamPosition>
scripts/item_defs/vehicles/germany/G134_PzKpfw_VII.xml: <gunCamPosition>0.000492 0.62573 1.007</gunCamPosition>
scripts/item_defs/vehicles/germany/G138_VK168_02.xml: <gunCamPosition>-0.022609 0.641567 1.267</gunCamPosition>
scripts/item_defs/vehicles/germany/G138_VK168_02_Mauerbrecher.xml: <gunCamPosition>-0.022609 0.641567 1.267</gunCamPosition>
scripts/item_defs/vehicles/germany/G42_Maus.xml: <gunCamPosition>0.073553 0.661651 1.402</gunCamPosition>
scripts/item_defs/vehicles/germany/G42_Maus_IGR.xml: <gunCamPosition>0.073553 0.661651 1.402</gunCamPosition>
scripts/item_defs/vehicles/germany/G48_E-25.xml: <gunCamPosition>0.000005 -0.108257 -0.1</gunCamPosition>
scripts/item_defs/vehicles/germany/G48_E-25_IGR.xml: <gunCamPosition>0.000005 -0.108257 -0.1</gunCamPosition>
scripts/item_defs/vehicles/germany/G58_VK4502P.xml: <gunCamPosition>0.000000 0.4625 0.977</gunCamPosition>
scripts/item_defs/vehicles/germany/G58_VK4502P.xml: <gunCamPosition>0.000000 0.446848 0.977</gunCamPosition>
scripts/item_defs/vehicles/poland/Pl15_60TP_Lewandowskiego.xml: <gunCamPosition>0.000000 0.43685 1.589</gunCamPosition>
scripts/item_defs/vehicles/ussr/R144_K_91.xml: <gunCamPosition>-0.010206 0.268306 1.146</gunCamPosition>
```


## wottool unzip

python wottool.py [-b _WoT_install_dir_] unzip [-d _dest_dir_] [-e _regex_] [-l] _file_

zip ファイル、またはその一部を展開、またはファイル一覧を取得します。

* __-d__ _dest_dir_:
    指定のディレクトリ `dest_dir` にファイルを展開します。
* __-e__ _regex_:
    `regex` で指定した正規表現にマッチするものだけを対象とします。
* __-l__:
    ファイルを展開せず、ファイル名のリストを出力します。
    このオプションが指定されたとき、オプション -d は無視されます。
* _file_:
    展開対象の zip ファイルを指定します。package ファイル、wotmod ファイルも指定できます。
    絶対パス、相対パスの指定のほか、パッケージ名のみの指定も有効です。

### 使用例

```
> py -2 wottool.py unzip -l -e 'gui/manual' gui.pkg
gui/manual/
gui/manual/chapter-1.xml
gui/manual/chapter-2.xml
gui/manual/chapter-3.xml
gui/manual/chapter-4.xml
gui/manual/chapter-5.xml
gui/manual/chapter-6.xml
gui/manual/chapter-7.xml
gui/manual/chapters_list.xml
```

## wottool wotmod

python wottool.py wotmod _target_ _file_

`target` で指定したディレクトリツリーを
wotmod 形式（非圧縮ZIP）に変換し、`file` に出力します。
`target` は wotmod 内の `res` ディレクトリの下に配置されます。


## wottool decompile

python wottool.py [-b _WoT_install_dir_] decompile _target_ _destdir_

`target` で指定した pyc ファイルをデコンパイルし、
指定のディレクトリ `destdir` 内に出力します。
デコンパイルには uncompyle2 が使われます。

* _target_:
    デコンパイル対象のファイル群の起点となるディレクトリを指定します。
    （必須）
* _destdir_:
    デコンパイル結果を出力するディレクトリを指定します。
    （必須）
