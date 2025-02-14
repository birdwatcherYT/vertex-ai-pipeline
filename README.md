# vertex-ai-pipeline

## terraform
terraformインストール
``bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

初期化
```bash
cd terraform/
terraform init
terraform plan -var-file=terraform-dev.tfvars
terraform apply -var-file=terraform-dev.tfvars
```


## pipeline
### Dockerイメージの準備
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
uv run python vertex_ai_kfp.py
```

パイプラインの実行
```bash
uv run python run.py
```
