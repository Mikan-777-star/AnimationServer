# --- ビルドステージ ---
FROM golang:1.23-alpine AS builder

WORKDIR /app

# 依存関係定義があればキャッシュを活用（今回は最小コードなのでそのままコピー）
COPY . .

# CGOを無効化し、静的リンクされたスタンドアロンバイナリを生成
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o server main.go

# --- 実行ステージ ---
FROM scratch

WORKDIR /

# ビルドステージから生成物のみコピー
COPY --from=builder /app/server /server

EXPOSE 8080

ENTRYPOINT ["/server"]
