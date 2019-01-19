# wotmods-tools

## wottool

WoT の pkg ファイル展開、pyc デコンパイル、packed xml のテキスト化、wotmod 作成支援などを行うツールです。

### 使い方

python wottool.py [-b <WoT_install_dir>] command

### version

WoT のバージョン情報を表示します。

python wottool.py [-b <WoT_install_dir>] version

```
> py -2 wottool.py version
{'version': '1.3.0.1', 'string': 'v.1.3.0.1 #1111', 'build': '1111'}
```

### xml

packed XML のファイルを通常の XML ファイル（テキスト形式）に変換します。

python wottool.py [-b <WoT_install_dir>] xml [-p package] [-x xpath] file

#### -p package

package 名です。
WoT のインストールフォルダの `res/package` 内から選択します。

#### -x xpath

XML 内のサブツリーを指定します。
書式は xpath のサブセットです。

#### file

変換対象の XML ファイルを指定します。
絶対パス、相対パス、package ファイル内のパスが指定可能です。


```
> py -2 wottool.py xml -p gui.pkg -x './/setting[name="rememberPassVisible"]' gui/gui_settings.xml
<setting>
  <name>rememberPassVisible</name>
  <type>bool</type>
  <value>False</value>
</setting>
```
