package main

import (
	_ "embed"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// frames.txt の内容をコンパイル時に文字列として埋め込む
//go:embed frames.txt
var rawFrames string

const (
	cursorHome  = "\033[H"      // 左上に戻るだけ（画面消去しない）
	syncStart   = "\033[?2026h" // 同期更新開始（チラつき防止）
	syncEnd     = "\033[?2026l" // 同期更新終了（一括描画）
	hideCursor  = "\033[?25l"
	showCursor  = "\033[?25h"
)

var frames []string

func init() {
	// 区切り文字で分割してフレーム配列を生成
	parts := strings.Split(rawFrames, "===FRAME===")
	for _, part := range parts {
		trimmed := strings.Trim(part, "\r\n")
		if trimmed != "" {
			frames = append(frames, trimmed+"\n")
		}
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain; charset=utf-8")

	// 接続開始時にカーソルを非表示にする
	fmt.Fprint(w, hideCursor)
	fmt.Fprint(w, "\033[2J TIN TIN")
	flusher.Flush()

	ctx := r.Context()
	frameIdx := 0

	for {
		select {
		case <-ctx.Done():
			// クライアント切断時、カーソル再表示を試みて終了
			fmt.Fprint(w, showCursor)
			flusher.Flush()
			return
		default:
			if len(frames) > 0 {
				fmt.Fprintf(w, "%s%s%s%s", syncStart, cursorHome, frames[frameIdx], syncEnd)
				flusher.Flush()
				frameIdx = (frameIdx + 1) % len(frames)
			}
			time.Sleep(30 * time.Millisecond)
		}
	}
}

func main() {
	if len(frames) == 0 {
		panic("No animation frames loaded from frames.txt")
	}

	http.HandleFunc("/", handler)
	fmt.Println("Server listening on :8080...")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}
