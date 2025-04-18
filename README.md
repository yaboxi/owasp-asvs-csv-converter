# OWASP ASVS CSV Converter

OWASP Application Security Verification Standard (ASVS) 5.0 の英語版および日本語コミュニティ翻訳版から、CSVファイルを生成するツールです。
さらに、生成した日本語版と英語版のCSVファイルをマージする機能も備えています。

**参照元リポジトリ:**

-   [https://github.com/OWASP/ASVS](https://github.com/OWASP/ASVS)
-   [https://github.com/coky-t/owasp-asvs-ja](https://github.com/coky-t/owasp-asvs-ja)

## Features

-   公式のOWASP ASVSリポジトリと日本語翻訳リポジトリを自動でクローンまたは更新します。
-   ASVSリポジトリ内で提供されているツールを利用し、両言語版のCSVファイルを生成します（現在はASVS v5.0に対応しています）。
-   `req_id` をキーとして、英語と日本語のCSVファイルをマージし、`output/asvs_5.0_merged.csv` を作成します。

## Requirements

-   Python 3.13+
-   `git`
-   `uv`

## Setup

1.  **リポジトリのクローン:**
    ```shell
    git clone yaboxi/owasp-asvs-csv-converter
    cd owasp-asvs-csv-converter
    ```

2.  **仮想環境の作成と有効化 (推奨):**
    ```shell
    uv venv
    source .venv/bin/activate
    ```

3.  **依存関係のインストール:**
    ```shell
    uv pip install -e '.[dev]'
    ```

## Usage

プロジェクトのルートディレクトリで、以下のコマンドを実行します:

```shell
uv run python -m src.main
```

このコマンドは、以下の処理を自動的に行います:
-   必要なASVSリポジトリ (`ASVS/` および `owasp-asvs-ja/`) をプロジェクトディレクトリ内にクローンまたは更新します。
-   OWASP/ASVSリポジトリに含まれるCSV生成ツールが必要とする依存関係 (`dicttoxml`, `dicttoxml2`) を、`uv pip install` を使って現在の仮想環境にインストールします。
-   `output/asvs_5.0_en.csv` および `output/asvs_5.0_ja.csv` を生成します。
-   生成された2つのCSVファイルを `output/asvs_5.0_merged.csv` としてマージします。

最終的にマージされたCSVファイルは `output/` ディレクトリに出力されます。

## Disclaimer

生成されるCSVファイルに含まれるOWASP ASVSの要求事項、その日本語訳の内容、およびCSV生成ツール自体は、それぞれ上記の参照元リポジトリのプロジェクトとその貢献者に帰属します。
このツールは、公開されているこれらの情報を基に、各言語版CSVファイルの生成とマージを行うものです。

ASVSの正確な内容、ライセンス、およびCSV生成ツールに関する詳細は、必ずオリジナルのOWASP/ASVSプロジェクトをご参照ください。

日本語訳の内容については、coky-t/owasp-asvs-jaリポジトリをご参照ください。

## Acknowledgements

このツールは、OWASP ASVS プロジェクトおよび coky-t/owasp-asvs-ja プロジェクトの成果物を利用しています。
素晴らしい標準と翻訳を提供してくださる各プロジェクトの貢献者の皆様に感謝いたします。
