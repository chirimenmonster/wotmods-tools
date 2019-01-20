# wotmods-tools

## wottool

python wottool.py [-b _WoT_install_dir_] {version | xml | list | wotmod | decompile} <_command_specific_args_>

WoT の pkg ファイル展開、pyc デコンパイル、packed xml のテキスト化、wotmod 作成支援などを行うツールです。
実行には Python 2 が必要です。


### 共通オプション

* __-b__ _Wot_install_dir_:
    WoT がインストールされているディレクトリを指定します。
    デフォルトは `C:/Games/World_of_Tanks` です。

## wottool version

python wottool.py [-b _WoT_install_dir_] version

WoT のバージョン情報を表示します。

### 使用例

```
> py -2 wottool.py version
{'version': '1.3.0.1', 'string': 'v.1.3.0.1 #1111', 'build': '1111'}
```

## wottool xml

python wottool.py [-b _WoT_install_dir_] xml [-p _package_] [-x _xpath_] _file_

packed XML のファイルを通常の XML ファイル（テキスト形式）に変換します。

* __-p__ _package_:
    指定の package から XML ファイルを抽出します。
    package 名は WoT インストールフォルダの `res/package` 内から選択します。
* __-x__ _xpath_:
    表示する XML ファイル内のサブツリーを指定します。
    書式は xpath のサブセットです。
* __file__:
    変換対象の XML ファイルを指定します。
    絶対パス、相対パス、package ファイル内のパスが指定可能です。
    (必須)

### 使用例

```
> py -2 wottool.py xml -p gui.pkg -x './/setting[name="rememberPassVisible"]' gui/gui_settings.xml
<setting>
  <name>rememberPassVisible</name>
  <type>bool</type>
  <value>False</value>
</setting>
```

## wottool list

python wottool.py [-b _WoT_install_dir_] xml -p _package_

package 内のファイル一覧を取得します

### 使用例

```
$ python2 wottool.py list -p gui.pkg | head
gui/
gui/ability_tooltips.xml
gui/avatar_input_handler.xml
gui/bc_vehicle_messages_panel.xml
gui/bootcamp_blocked_settings.xml
gui/EULA_templates.xml
gui/flash/
gui/flash/academyView.swf
gui/flash/accountPopover.swf
gui/flash/Achievements.swf
...
```

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
