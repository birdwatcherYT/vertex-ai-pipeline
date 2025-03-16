# vertex-ai-pipeline


## terraform
terraformはクラウド環境を簡単に構築できる設定ファイルです。  
IAM設定やGCSバケットの作成、サービスアカウントの作成を一気に実行できます。

terraformインストール
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

初期化（実行前に`dev.tfvars`を環境に合わせて変えてください）
```bash
cd terraform/
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```


## pipeline

利用の流れ:
1. Dockerイメージの作成
1. パイプラインのビルド（jsonが出力される）
1. パイプラインの実行

### Dockerイメージの作成
クラウド
```bash
uv run inv cloud-build
```
ローカル
```bash
uv run inv docker-build
uv run inv docker-push
```

### パイプライン
パイプラインをコンパイル
```bash
uv run inv build-pipeline
```

パイプラインの実行
```bash
uv run inv run-pipeline
```

パイプライン実行関数のデプロイ(コンパイル後行う)
```bash
uv run inv deploy-pipeline
```

デプロイしたパイプラインの実行
```bash
uv run inv run-pipeline-via-cloud-function
```
