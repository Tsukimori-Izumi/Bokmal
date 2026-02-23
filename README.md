# Bokmål - Project Manager

<p align="center">
  <strong>Python 3.13 + PySide6 で構築されたデスクトップ型プロジェクト管理ツール</strong>
</p>

---

## 概要

**Bokmål** は、ガントチャート・ネットワーク図・バーンダウンチャートなどを備えた、ローカル動作のプロジェクト管理アプリケーションです。CPM（クリティカルパスメソッド）によるスケジュール自動計算、WBS 管理、リソース管理など、本格的なプロジェクト管理機能を提供します。

## 主な機能

| カテゴリ | 機能 |
|---|---|
| **ガントチャート** | タスクバー表示、ドラッグによる日程変更、マイルストーン・サマリータスク対応 |
| **ネットワーク図** | タスク依存関係の可視化、ドラッグ＆ドロップで依存関係作成 |
| **バーンダウンチャート** | 進捗率の推移をグラフ表示 |
| **CPMスケジューリング** | フォワード／バックワードパスによるクリティカルパス自動計算 |
| **WBS管理** | インデント／アウトデントによる階層構造、サマリータスクの自動集計 |
| **リソース管理** | リソースの登録・編集・タスクへの割り当て |
| **Undo / Redo** | 操作履歴の取り消し・やり直し |
| **エクスポート** | CSV / PowerPoint (.pptx) 形式で出力 |
| **インポート** | CSV からのタスク読み込み |
| **ダークテーマ** | モダンなダーク UI |

## スクリーンショット

<!-- アプリケーションのスクリーンショットをここに追加 -->

## 動作環境

- **Python** 3.13+
- **OS** Windows 10 / 11

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/Tsukimori-Izumi/unitk.git
cd unitk

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 依存パッケージ

| パッケージ | バージョン |
|---|---|
| PySide6 | >= 6.6.0 |
| SQLAlchemy | >= 2.0.0 |

## 使い方

```bash
python main.py
```

## プロジェクト構成

```
Bokmål/
├── main.py              # エントリーポイント
├── config.py            # アプリケーション設定
├── requirements.txt     # 依存パッケージ
├── engine/              # スケジューリングエンジン
│   ├── scheduler.py     #   CPM スケジューラ
│   ├── date_utils.py    #   営業日計算ユーティリティ
│   └── wbs.py           #   WBS 管理
├── models/              # データモデル
│   ├── task.py          #   タスク
│   ├── dependency.py    #   依存関係
│   ├── resource.py      #   リソース
│   ├── assignment.py    #   リソース割り当て
│   ├── project.py       #   プロジェクト
│   └── calendar.py      #   カレンダー設定
├── ui/                  # ユーザーインターフェース
│   ├── main_window.py   #   メインウィンドウ
│   ├── gantt_widget.py  #   ガントチャートウィジェット
│   ├── gantt_items.py   #   ガントチャート描画アイテム
│   ├── task_table.py    #   タスク一覧テーブル
│   ├── task_dialog.py   #   タスク編集ダイアログ
│   ├── network_chart.py #   ネットワーク図
│   ├── burndown_chart.py#   バーンダウンチャート
│   ├── resource_sheet.py#   リソースシート
│   ├── toolbar.py       #   ツールバー
│   └── theme.py         #   テーマ・スタイルシート
├── utils/               # ユーティリティ
│   ├── export_import.py #   CSV エクスポート / インポート
│   ├── pptx_export.py   #   PowerPoint エクスポート
│   └── sample_data.py   #   サンプルデータ生成
└── data/                # データ保存ディレクトリ
```

## ライセンス

<!-- ライセンス情報をここに記載 -->
