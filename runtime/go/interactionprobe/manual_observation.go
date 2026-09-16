package interactionprobe

import "github.com/hat47x/sei-cognition/runtime/go/semanticruntime"

// RecordManualObservation は、AI / external Cognitive Methodが利用できない場合でも
// 人間が観測内容をcanonical stateへ追加するためのProduct-localな最小経路です。
//
// current Universal Contractには汎用Observation型を追加せず、このprobeではopaqueな
// not_verified recordとして保存します。人間が入力したこと自体をverified factへ読み替えません。
func (s *HumanSurface) RecordManualObservation(id, text string) (semanticruntime.LogicalReference, error) {
	return s.recordOpaque("observation", id, text)
}
