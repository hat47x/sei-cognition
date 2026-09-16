package interactionprobe

import (
	"errors"
	"fmt"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// SemanticChangePlan は、一つのProduct操作でcanonicalへ反映したい変更候補を
// Product-localに束ねます。portable ContractやUniversal transaction型ではありません。
type SemanticChangePlan struct {
	Records []semanticruntime.RuntimeRecord
}

// CommitCoordinator は、複数canonical changeをstagingした後に一括公開する
// interaction probe用の最小Commit Coordinatorです。
//
// current probeはsingle-process / single-userを前提とします。ここでのatomicityを
// distributed transactionやUniversal Persistence requirementへ一般化しません。
type CommitCoordinator struct {
	store *CanonicalStore
}

func NewCommitCoordinator(store *CanonicalStore) *CommitCoordinator {
	return &CommitCoordinator{store: store}
}

// Commit はplan全体を既存canonical stateの複製へstagingし、全変更が受理された場合だけ
// 元storeへ公開します。途中のvalidation failure等で、staging済みの一部だけを
// successful canonical stateとして露出させません。
func (c *CommitCoordinator) Commit(plan SemanticChangePlan) error {
	return c.commit(plan, -1)
}

// commitWithProbeFault はE6 fault injection専用のprobe-local入口です。
// failAfterStaged=0なら最初のchangeをstagingした直後、公開前にfailureを返します。
// production APIやUniversal failure modelではありません。
func (c *CommitCoordinator) commitWithProbeFault(plan SemanticChangePlan, failAfterStaged int) error {
	if failAfterStaged < 0 {
		return errors.New("probe fault position must be non-negative")
	}
	return c.commit(plan, failAfterStaged)
}

func (c *CommitCoordinator) commit(plan SemanticChangePlan, failAfterStaged int) error {
	if c == nil || c.store == nil {
		return errors.New("commit coordinator requires a canonical store")
	}
	if len(plan.Records) == 0 {
		return errors.New("semantic change plan requires at least one record")
	}

	base, err := c.store.Records()
	if err != nil {
		return err
	}
	staged := &CanonicalStore{records: base}

	for i, record := range plan.Records {
		if err := staged.Add(record); err != nil {
			return fmt.Errorf("stage semantic change %d: %w", i, err)
		}
		if failAfterStaged == i {
			return fmt.Errorf("injected commit failure after staging semantic change %d", i)
		}
	}

	published, err := staged.Records()
	if err != nil {
		return err
	}
	c.store.records = published
	return nil
}
