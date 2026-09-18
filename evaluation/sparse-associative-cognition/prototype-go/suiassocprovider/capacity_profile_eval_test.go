package suiassocprovider

import (
	"fmt"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/capacityprofile"
	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

func capacityBaseProfile() capacityprofile.Profile {
	return capacityprofile.Profile{
		ID: "medium",
		Sparse: sparseassoc.Config{
			Dimensions: 4096,
			Fanout:     8,
			Active:     64,
			Seed:       47,
		},
	}
}

func capacityEvalItems() (Item, Item, Item) {
	anchor := Item{
		Ref:  "anchor",
		Kind: "card",
		Channels: Channels{
			Text: "確認作業の増加は現場負荷と引継ぎ時間に影響するため追加記録を残す",
			Graph: &GraphChannel{
				RelationTypes: []string{"causal", "related"},
				NeighborKinds: []string{"artifact", "card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1", "s2"},
				ActorRefs:  []string{"human:a", "ai:b"},
			},
			Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
		},
	}
	desired := Item{
		Ref:  "desired",
		Kind: "card",
		Channels: Channels{
			Text: "構造上は同じ関連と出典を持つ別の観察",
			Graph: &GraphChannel{
				RelationTypes: []string{"causal", "related"},
				NeighborKinds: []string{"artifact", "card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1", "s2"},
				ActorRefs:  []string{"human:a", "ai:b"},
			},
			Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
		},
	}
	distractor := Item{
		Ref:  "distractor",
		Kind: "card",
		Channels: Channels{
			Text: "確認作業の増加は現場負荷と引継ぎ時間に影響する確認作業の増加は現場負荷と引継ぎ時間に影響する",
			Graph: &GraphChannel{
				RelationTypes: []string{"contrast"},
				NeighborKinds: []string{"note"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s9"},
				ActorRefs:  []string{"human:z"},
			},
			Grouping: &GroupingChannel{IslandRef: "i9", HoldState: "none"},
		},
	}
	return anchor, desired, distractor
}

func structureHeavyCapacityEvalItems() (Item, Item, Item) {
	values := func(prefix string, n int) []string {
		out := make([]string, n)
		for i := range out {
			out[i] = fmt.Sprintf("%s%d", prefix, i+1)
		}
		return out
	}
	anchor := Item{
		Ref: "structure-anchor", Kind: "card",
		Channels: Channels{
			Text: "監査記録",
			Graph: &GraphChannel{
				RelationTypes: values("r", 8),
				NeighborKinds: values("k", 8),
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: values("s", 8),
				ActorRefs: values("a", 8),
			},
			Grouping: &GroupingChannel{IslandRef: "is-struct", HoldState: "hold"},
		},
	}
	desired := anchor
	desired.Ref = "structure-desired"
	desired.Channels.Text = "別件確認"
	distractor := Item{
		Ref: "structure-distractor", Kind: "card",
		Channels: Channels{
			Text: "監査記録",
			Graph: &GraphChannel{
				RelationTypes: []string{"other1", "other2"},
				NeighborKinds: []string{"otherk"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"sx"},
				ActorRefs: []string{"ax"},
			},
			Grouping: &GroupingChannel{IslandRef: "is-other", HoldState: "none"},
		},
	}
	return anchor, desired, distractor
}

func textHeavyCapacityEvalItems() (Item, Item, Item) {
	anchor := Item{
		Ref: "text-heavy-anchor", Kind: "card",
		Channels: Channels{
			Text: "確認記録統合作業では担当者間の引継ぎ手順と例外処理条件を整理し監査証跡と変更履歴を保持しながら再確認工程を減らす",
			Graph: &GraphChannel{
				RelationTypes: []string{"causal", "related"},
				NeighborKinds: []string{"artifact", "card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1", "s2"},
				ActorRefs: []string{"human:a", "ai:b"},
			},
			Grouping: &GroupingChannel{IslandRef: "it", HoldState: "hold"},
		},
	}
	desired := Item{
		Ref: "text-heavy-desired", Kind: "card",
		Channels: Channels{
			Text: "異なる表現で同じ構造と出典を保持する観察",
			Graph: &GraphChannel{
				RelationTypes: []string{"causal", "related"},
				NeighborKinds: []string{"artifact", "card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1", "s2"},
				ActorRefs: []string{"human:a", "ai:b"},
			},
			Grouping: &GroupingChannel{IslandRef: "it", HoldState: "hold"},
		},
	}
	distractor := Item{
		Ref: "text-heavy-distractor", Kind: "card",
		Channels: Channels{
			Text: anchor.Channels.Text,
			Graph: &GraphChannel{
				RelationTypes: []string{"contrast"},
				NeighborKinds: []string{"note"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s9"},
				ActorRefs: []string{"human:z"},
			},
			Grouping: &GroupingChannel{IslandRef: "ix", HoldState: "none"},
		},
	}
	return anchor, desired, distractor
}

func softLocalPolicyForProfile(profile capacityprofile.Profile) (*LocalCompetitionPolicy, error) {
	localEach, residual, err := capacityprofile.EqualLocalHalfResidual(profile.Sparse.Active, 4)
	if err != nil {
		return nil, err
	}
	return &LocalCompetitionPolicy{
		FamilyActive: map[string]uint16{
			"text":       localEach,
			"graph":      localEach,
			"provenance": localEach,
			"grouping":   localEach,
		},
		GlobalResidualActive: residual,
	}, nil
}

func softLocalCappedPolicyForProfile(
	profile capacityprofile.Profile,
	residualCap uint16,
) (*LocalCompetitionPolicy, error) {
	localEach, residual, err := capacityprofile.EqualLocalHalfResidualCapped(
		profile.Sparse.Active,
		4,
		residualCap,
	)
	if err != nil {
		return nil, err
	}
	return &LocalCompetitionPolicy{
		FamilyActive: map[string]uint16{
			"text":       localEach,
			"graph":      localEach,
			"provenance": localEach,
			"grouping":   localEach,
		},
		GlobalResidualActive: residual,
	}, nil
}

func capacitySimilarityPair(
	t *testing.T,
	profile capacityprofile.Profile,
	normalization FeatureNormalizationMode,
) (desiredSimilarity, distractorSimilarity float32) {
	t.Helper()
	local, err := softLocalPolicyForProfile(profile)
	if err != nil {
		t.Fatal(err)
	}
	return capacitySimilarityPairWithPolicy(t, profile, normalization, local)
}

func capacitySimilarityPairWithPolicy(
	t *testing.T,
	profile capacityprofile.Profile,
	normalization FeatureNormalizationMode,
	local *LocalCompetitionPolicy,
) (desiredSimilarity, distractorSimilarity float32) {
	t.Helper()
	anchor, desired, distractor := capacityEvalItems()
	return capacitySimilarityForItemsWithPolicy(
		t, profile, normalization, local, anchor, desired, distractor,
	)
}

func capacitySimilarityForItemsWithPolicy(
	t *testing.T,
	profile capacityprofile.Profile,
	normalization FeatureNormalizationMode,
	local *LocalCompetitionPolicy,
	anchor Item,
	desired Item,
	distractor Item,
) (desiredSimilarity, distractorSimilarity float32) {
	t.Helper()
	cfg := Config{
		Sparse:                profile.Sparse,
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "capacity-profile-eval",
		FeatureNormalization:  normalization,
		LocalCompetition:      local,
	}
	if normalization != FeatureNormalizationNone {
		cfg.NormalizationFloor = 1
	}
	p, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	encoder, err := newProviderEncoder(p.cfg)
	if err != nil {
		t.Fatal(err)
	}
	encode := func(item Item) sparseassoc.Signature {
		features, err := p.preparedFeatures(item)
		if err != nil {
			t.Fatal(err)
		}
		sig, err := encoder.Encode(features)
		if err != nil {
			t.Fatal(err)
		}
		return sig
	}

	anchorSignature := encode(anchor)
	return sparseassoc.Similarity(anchorSignature, encode(desired)),
		sparseassoc.Similarity(anchorSignature, encode(distractor))
}

func capacityObservedStats(
	t *testing.T,
	profile capacityprofile.Profile,
	item Item,
) (sparseassoc.Signature, providerEncodeStats) {
	t.Helper()
	local, err := softLocalPolicyForProfile(profile)
	if err != nil {
		t.Fatal(err)
	}
	return capacityObservedStatsWithPolicy(t, profile, item, local)
}

func capacityObservedStatsWithPolicy(
	t *testing.T,
	profile capacityprofile.Profile,
	item Item,
	local *LocalCompetitionPolicy,
) (sparseassoc.Signature, providerEncodeStats) {
	t.Helper()
	p, err := New(Config{
		Sparse:                profile.Sparse,
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "capacity-observed-stats-eval",
		FeatureNormalization:  FeatureNormalizationFamily,
		NormalizationFloor:    1,
		LocalCompetition:      local,
	})
	if err != nil {
		t.Fatal(err)
	}
	encoder, err := newProviderEncoder(p.cfg)
	if err != nil {
		t.Fatal(err)
	}
	prepared, err := p.preparedFeatures(item)
	if err != nil {
		t.Fatal(err)
	}
	signature, stats, err := encoder.EncodeWithStats(prepared)
	if err != nil {
		t.Fatal(err)
	}
	if stats.Local == nil || stats.Global != nil {
		t.Fatalf("expected localized stats only: %#v", stats)
	}
	return signature, stats
}

func TestObservedSelectionPressureAcrossCapacityProfiles(t *testing.T) {
	base := capacityBaseProfile()
	anchor, _, _ := capacityEvalItems()
	cases := []struct {
		id             string
		dimensions     uint16
		globalTouched  int
		globalSelected int
		textTouched    int
		textSelected   int
		graphSelected  int
		provSelected   int
		groupSelected  int
		mergedSelected int
	}{
		{"small", 2048, 495, 16, 433, 4, 4, 4, 4, 27},
		{"medium", 4096, 539, 32, 463, 8, 8, 8, 8, 52},
		{"large", 8192, 560, 64, 477, 16, 16, 16, 16, 80},
		{"oversized", 32768, 574, 256, 487, 64, 32, 32, 16, 256},
	}

	previousGlobalShare := float64(-1)
	for _, tc := range cases {
		t.Run(tc.id, func(t *testing.T) {
			profile, err := capacityprofile.ScaleDimensions(base, tc.id, tc.dimensions)
			if err != nil {
				t.Fatal(err)
			}
			signature, stats := capacityObservedStats(t, profile, anchor)
			local := stats.Local
			if local.GlobalResidual == nil {
				t.Fatal("missing global residual diagnostics")
			}
			global := *local.GlobalResidual
			if global.PositiveFeatures != 72 || global.ProjectionAttempts != 576 {
				t.Fatalf("global input cardinality changed: %#v", global)
			}
			if global.TouchedDimensions != tc.globalTouched || global.SelectedDimensions != tc.globalSelected {
				t.Fatalf("global stats=%#v want touched/selected=%d/%d",
					global, tc.globalTouched, tc.globalSelected)
			}

			textStats := local.Families["text"]
			graphStats := local.Families["graph"]
			provStats := local.Families["provenance"]
			groupStats := local.Families["grouping"]
			if textStats.TouchedDimensions != tc.textTouched || textStats.SelectedDimensions != tc.textSelected {
				t.Fatalf("text stats=%#v want touched/selected=%d/%d",
					textStats, tc.textTouched, tc.textSelected)
			}
			if graphStats.TouchedDimensions != 32 || graphStats.SelectedDimensions != tc.graphSelected {
				t.Fatalf("graph stats=%#v", graphStats)
			}
			if provStats.TouchedDimensions != 32 || provStats.SelectedDimensions != tc.provSelected {
				t.Fatalf("provenance stats=%#v", provStats)
			}
			if groupStats.TouchedDimensions != 16 || groupStats.SelectedDimensions != tc.groupSelected {
				t.Fatalf("grouping stats=%#v", groupStats)
			}
			if local.MergedSelectedDimensions != tc.mergedSelected ||
				len(signature.Active) != tc.mergedSelected {
				t.Fatalf("merged selected=%d signature=%d want %d",
					local.MergedSelectedDimensions, len(signature.Active), tc.mergedSelected)
			}

			globalShare := capacityprofile.ObservedWinnerShare(global)
			if previousGlobalShare >= 0 && globalShare <= previousGlobalShare {
				t.Fatalf("global observed winner share did not increase: previous=%v current=%v",
					previousGlobalShare, globalShare)
			}
			previousGlobalShare = globalShare
		})
	}
}

func TestLocalContributionBeyondResidualAcrossProfiles(t *testing.T) {
	base := capacityBaseProfile()
	anchor, _, _ := capacityEvalItems()
	cases := []struct {
		id          string
		dimensions  uint16
		incremental int
		textUnique  int
		graphUnique int
		provUnique  int
		groupUnique int
		merged      int
	}{
		{"small", 2048, 11, 4, 4, 3, 0, 27},
		{"medium", 4096, 20, 8, 6, 6, 0, 52},
		{"large", 8192, 16, 16, 0, 0, 0, 80},
		{"oversized", 32768, 0, 0, 0, 0, 0, 256},
	}

	for _, tc := range cases {
		t.Run(tc.id, func(t *testing.T) {
			profile, err := capacityprofile.ScaleDimensions(base, tc.id, tc.dimensions)
			if err != nil {
				t.Fatal(err)
			}
			_, stats := capacityObservedStats(t, profile, anchor)
			local := stats.Local
			if local == nil || local.GlobalResidual == nil {
				t.Fatalf("missing localized diagnostics: %#v", stats)
			}
			if local.LocalIncrementalDimensions != tc.incremental {
				t.Fatalf("local incremental=%d want %d",
					local.LocalIncrementalDimensions, tc.incremental)
			}
			if local.MergedSelectedDimensions != tc.merged {
				t.Fatalf("merged=%d want %d", local.MergedSelectedDimensions, tc.merged)
			}

			want := map[string]int{
				"text":       tc.textUnique,
				"graph":      tc.graphUnique,
				"provenance": tc.provUnique,
				"grouping":   tc.groupUnique,
			}
			for family, expected := range want {
				if got := local.FamilyUniqueBeyondResidual[family]; got != expected {
					t.Fatalf("%s unique beyond residual=%d want %d",
						family, got, expected)
				}
			}
		})
	}
}

func TestOversizedLocalCompetitionAddsNoDimensionsBeyondResidual(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	anchor, _, _ := capacityEvalItems()
	signature, stats := capacityObservedStats(t, oversized, anchor)
	local := stats.Local
	if local == nil || local.GlobalResidual == nil {
		t.Fatalf("missing localized diagnostics: %#v", stats)
	}
	if local.LocalIncrementalDimensions != 0 {
		t.Fatalf("oversized local incremental=%d want 0", local.LocalIncrementalDimensions)
	}
	if local.MergedSelectedDimensions != local.GlobalResidual.SelectedDimensions {
		t.Fatalf("merged=%d residual selected=%d",
			local.MergedSelectedDimensions, local.GlobalResidual.SelectedDimensions)
	}
	if len(signature.Active) != local.GlobalResidual.SelectedDimensions {
		t.Fatalf("signature=%d residual selected=%d",
			len(signature.Active), local.GlobalResidual.SelectedDimensions)
	}
	for family, unique := range local.FamilyUniqueBeyondResidual {
		if unique != 0 {
			t.Fatalf("%s contributes %d dimensions outside residual", family, unique)
		}
	}
}

func TestOversizedProfileExposesFamilyLocalSaturation(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	anchor, _, _ := capacityEvalItems()
	_, stats := capacityObservedStats(t, oversized, anchor)
	local := stats.Local
	if local == nil || local.GlobalResidual == nil {
		t.Fatalf("missing localized diagnostics: %#v", stats)
	}

	globalShare := capacityprofile.ObservedWinnerShare(*local.GlobalResidual)
	if globalShare < 0.44 || globalShare > 0.45 {
		t.Fatalf("unexpected global residual winner share: %v", globalShare)
	}
	for _, family := range []string{"graph", "provenance", "grouping"} {
		if share := capacityprofile.ObservedWinnerShare(local.Families[family]); share != 1 {
			t.Fatalf("%s local path must expose complete selection saturation, got %v", family, share)
		}
	}
	if textShare := capacityprofile.ObservedWinnerShare(local.Families["text"]); textShare >= 0.2 {
		t.Fatalf("text local path should remain selective in this fixture, got %v", textShare)
	}

	upperBoundProxy := capacityprofile.WinnerShareUpperBound(oversized, 72)
	if upperBoundProxy < 0.88 || upperBoundProxy > 0.90 {
		t.Fatalf("unexpected pre-collision proxy: %v", upperBoundProxy)
	}
	if globalShare >= upperBoundProxy {
		t.Fatalf("observed global share must remain below total-active upper-bound proxy: observed=%v proxy=%v",
			globalShare, upperBoundProxy)
	}
}

func TestObservedCollisionFallsWhileWinnerShareRises(t *testing.T) {
	base := capacityBaseProfile()
	anchor, _, _ := capacityEvalItems()
	var previousCollision, previousShare float64
	first := true
	for _, dimensions := range []uint16{2048, 4096, 8192, 32768} {
		profile, err := capacityprofile.ScaleDimensions(base, fmt.Sprintf("d%d", dimensions), dimensions)
		if err != nil {
			t.Fatal(err)
		}
		_, stats := capacityObservedStats(t, profile, anchor)
		global := *stats.Local.GlobalResidual
		collision := capacityprofile.ProjectionCollisionFraction(global)
		share := capacityprofile.ObservedWinnerShare(global)
		if !first {
			if collision >= previousCollision {
				t.Fatalf("collision fraction did not fall: previous=%v current=%v", previousCollision, collision)
			}
			if share <= previousShare {
				t.Fatalf("winner share did not rise: previous=%v current=%v", previousShare, share)
			}
		}
		first = false
		previousCollision = collision
		previousShare = share
	}
}

func TestStaticResidualCap64PreservesFirstThreeBaselineBudgets(t *testing.T) {
	base := capacityBaseProfile()
	for _, dimensions := range []uint16{2048, 4096, 8192} {
		profile, err := capacityprofile.ScaleDimensions(base, fmt.Sprintf("d%d", dimensions), dimensions)
		if err != nil {
			t.Fatal(err)
		}
		baseline, err := softLocalPolicyForProfile(profile)
		if err != nil {
			t.Fatal(err)
		}
		capped, err := softLocalCappedPolicyForProfile(profile, 64)
		if err != nil {
			t.Fatal(err)
		}
		if baseline.GlobalResidualActive != capped.GlobalResidualActive {
			t.Fatalf("dimensions=%d residual changed: baseline=%d capped=%d",
				dimensions, baseline.GlobalResidualActive, capped.GlobalResidualActive)
		}
		for _, family := range []string{"text", "graph", "provenance", "grouping"} {
			if baseline.FamilyActive[family] != capped.FamilyActive[family] {
				t.Fatalf("dimensions=%d family=%s local changed: baseline=%d capped=%d",
					dimensions, family, baseline.FamilyActive[family], capped.FamilyActive[family])
			}
		}
	}
}

func TestStaticResidualCapsRestoreOversizedFixtureOrdering(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}

	baselineDesired, baselineDistractor := capacitySimilarityPair(
		t,
		oversized,
		FeatureNormalizationFamily,
	)
	if baselineDesired >= baselineDistractor {
		t.Fatalf("baseline fixture must remain reversed: desired=%v distractor=%v",
			baselineDesired, baselineDistractor)
	}

	cases := []struct {
		cap            uint16
		wantDesired    float32
		wantDistractor float32
	}{
		{128, 0.5855263158, 0.3943082926},
		{64, 0.5855263158, 0.4072398535},
	}
	for _, tc := range cases {
		policy, err := softLocalCappedPolicyForProfile(oversized, tc.cap)
		if err != nil {
			t.Fatal(err)
		}
		desired, distractor := capacitySimilarityPairWithPolicy(
			t,
			oversized,
			FeatureNormalizationFamily,
			policy,
		)
		if desired <= distractor {
			t.Fatalf("cap=%d did not restore desired ordering: desired=%v distractor=%v",
				tc.cap, desired, distractor)
		}
		if diff := desired - tc.wantDesired; diff < -0.000001 || diff > 0.000001 {
			t.Fatalf("cap=%d desired=%v want approximately %v", tc.cap, desired, tc.wantDesired)
		}
		if diff := distractor - tc.wantDistractor; diff < -0.000001 || diff > 0.000001 {
			t.Fatalf("cap=%d distractor=%v want approximately %v",
				tc.cap, distractor, tc.wantDistractor)
		}
	}
}

func TestStaticResidualCapsRestoreLocalContributionAtOversized(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	anchor, _, _ := capacityEvalItems()

	cases := []struct {
		cap          uint16
		residual     int
		merged       int
		incremental  int
		textUnique   int
		graphUnique  int
		provUnique   int
		groupUnique  int
		unusedBudget int
	}{
		{128, 128, 152, 24, 24, 0, 0, 0, 128},
		{64, 64, 152, 88, 64, 12, 12, 0, 192},
	}
	for _, tc := range cases {
		policy, err := softLocalCappedPolicyForProfile(oversized, tc.cap)
		if err != nil {
			t.Fatal(err)
		}
		_, stats := capacityObservedStatsWithPolicy(t, oversized, anchor, policy)
		local := stats.Local
		if local == nil || local.GlobalResidual == nil {
			t.Fatalf("cap=%d missing localized diagnostics: %#v", tc.cap, stats)
		}
		if local.GlobalResidual.SelectedDimensions != tc.residual {
			t.Fatalf("cap=%d residual selected=%d want %d",
				tc.cap, local.GlobalResidual.SelectedDimensions, tc.residual)
		}
		if local.MergedSelectedDimensions != tc.merged ||
			local.LocalIncrementalDimensions != tc.incremental {
			t.Fatalf("cap=%d merged/incremental=%d/%d want %d/%d",
				tc.cap,
				local.MergedSelectedDimensions,
				local.LocalIncrementalDimensions,
				tc.merged,
				tc.incremental)
		}
		want := map[string]int{
			"text":       tc.textUnique,
			"graph":      tc.graphUnique,
			"provenance": tc.provUnique,
			"grouping":   tc.groupUnique,
		}
		for family, expected := range want {
			if got := local.FamilyUniqueBeyondResidual[family]; got != expected {
				t.Fatalf("cap=%d %s unique beyond residual=%d want %d",
					tc.cap, family, got, expected)
			}
		}
		reserved := 0
		for _, active := range policy.FamilyActive {
			reserved += int(active)
		}
		reserved += int(policy.GlobalResidualActive)
		if unused := int(oversized.Sparse.Active) - reserved; unused != tc.unusedBudget {
			t.Fatalf("cap=%d unused budget=%d want %d", tc.cap, unused, tc.unusedBudget)
		}
	}
}

func TestStaticResidualCapDoesNotChangeSparseProfile(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	before := oversized.Sparse
	if _, err := softLocalCappedPolicyForProfile(oversized, 64); err != nil {
		t.Fatal(err)
	}
	if oversized.Sparse != before {
		t.Fatalf("static residual policy mutated sparse profile: before=%#v after=%#v",
			before, oversized.Sparse)
	}
}

func TestStaticResidualScalingAcrossIndependentFixtures(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}

	type fixtureFactory func() (Item, Item, Item)
	fixtures := []struct {
		id             string
		items          fixtureFactory
		totalFeatures  int
		textFeatures   int
		graphFeatures  int
		provFeatures   int
		groupFeatures  int
		baselineMargin float32
		cap128Margin   float32
		cap64Margin    float32
		baselineInc    int
		cap128Inc      int
		cap64Inc       int
	}{
		{
			id: "control", items: capacityEvalItems,
			totalFeatures: 72, textFeatures: 61, graphFeatures: 4, provFeatures: 4, groupFeatures: 2,
			baselineMargin: -0.15625, cap128Margin: 0.19121802, cap64Margin: 0.17828646,
			baselineInc: 0, cap128Inc: 24, cap64Inc: 88,
		},
		{
			id: "structure-heavy", items: structureHeavyCapacityEvalItems,
			totalFeatures: 40, textFeatures: 5, graphFeatures: 16, provFeatures: 16, groupFeatures: 2,
			baselineMargin: 0.5373185, cap128Margin: 0.4398274, cap64Margin: 0.4378301,
			baselineInc: 0, cap128Inc: 65, cap64Inc: 128,
		},
		{
			id: "text-heavy", items: textHeavyCapacityEvalItems,
			totalFeatures: 119, textFeatures: 108, graphFeatures: 4, provFeatures: 4, groupFeatures: 2,
			baselineMargin: -0.33203125, cap128Margin: 0.08249881, cap64Margin: 0.06557022,
			baselineInc: 0, cap128Inc: 24, cap64Inc: 88,
		},
	}

	policyFor := func(t *testing.T, mode string) *LocalCompetitionPolicy {
		t.Helper()
		switch mode {
		case "baseline":
			policy, err := softLocalPolicyForProfile(oversized)
			if err != nil {
				t.Fatal(err)
			}
			return policy
		case "cap128":
			policy, err := softLocalCappedPolicyForProfile(oversized, 128)
			if err != nil {
				t.Fatal(err)
			}
			return policy
		case "cap64":
			policy, err := softLocalCappedPolicyForProfile(oversized, 64)
			if err != nil {
				t.Fatal(err)
			}
			return policy
		default:
			t.Fatalf("unknown policy mode: %s", mode)
			return nil
		}
	}

	for _, fixture := range fixtures {
		t.Run(fixture.id, func(t *testing.T) {
			anchor, desired, distractor := fixture.items()
			counts := map[string]int{}
			for _, feature := range featuresForItem(anchor) {
				counts[featureFamily(feature.Channel)]++
			}
			if total := len(featuresForItem(anchor)); total != fixture.totalFeatures {
				t.Fatalf("total features=%d want %d", total, fixture.totalFeatures)
			}
			if counts["text"] != fixture.textFeatures ||
				counts["graph"] != fixture.graphFeatures ||
				counts["provenance"] != fixture.provFeatures ||
				counts["grouping"] != fixture.groupFeatures ||
				counts["kind"] != 1 {
				t.Fatalf("unexpected family counts: %#v", counts)
			}

			for _, mode := range []string{"baseline", "cap128", "cap64"} {
				policy := policyFor(t, mode)
				desiredSimilarity, distractorSimilarity := capacitySimilarityForItemsWithPolicy(
					t,
					oversized,
					FeatureNormalizationFamily,
					policy,
					anchor,
					desired,
					distractor,
				)
				margin := desiredSimilarity - distractorSimilarity
				wantMargin := fixture.baselineMargin
				wantIncremental := fixture.baselineInc
				switch mode {
				case "cap128":
					wantMargin = fixture.cap128Margin
					wantIncremental = fixture.cap128Inc
				case "cap64":
					wantMargin = fixture.cap64Margin
					wantIncremental = fixture.cap64Inc
				}
				if diff := margin - wantMargin; diff < -0.00001 || diff > 0.00001 {
					t.Fatalf("%s margin=%v want approximately %v", mode, margin, wantMargin)
				}
				_, stats := capacityObservedStatsWithPolicy(t, oversized, anchor, policy)
				if stats.Local.LocalIncrementalDimensions != wantIncremental {
					t.Fatalf("%s local incremental=%d want %d",
						mode, stats.Local.LocalIncrementalDimensions, wantIncremental)
				}
			}

			switch fixture.id {
			case "control", "text-heavy":
				if fixture.baselineMargin >= 0 || fixture.cap128Margin <= 0 || fixture.cap64Margin <= 0 {
					t.Fatalf("fixture must expose residual-cap ordering recovery: %#v", fixture)
				}
			case "structure-heavy":
				if fixture.baselineMargin <= fixture.cap128Margin || fixture.baselineMargin <= fixture.cap64Margin {
					t.Fatalf("structure-heavy fixture must preserve baseline as strongest margin: %#v", fixture)
				}
			}
		})
	}
}

func TestCapacityProfilesPreserveOrderingAcrossFirstThreeProfiles(t *testing.T) {
	base := capacityBaseProfile()
	profiles := []capacityprofile.Profile{}
	for _, tc := range []struct {
		id         string
		dimensions uint16
	}{
		{"small", 2048},
		{"medium", 4096},
		{"large", 8192},
	} {
		profile, err := capacityprofile.ScaleDimensions(base, tc.id, tc.dimensions)
		if err != nil {
			t.Fatal(err)
		}
		profiles = append(profiles, profile)
	}

	for _, profile := range profiles {
		t.Run(profile.ID, func(t *testing.T) {
			desired, distractor := capacitySimilarityPair(t, profile, FeatureNormalizationFamily)
			if desired <= distractor {
				t.Fatalf("profile %s lost desired ordering: desired=%v distractor=%v", profile.ID, desired, distractor)
			}
		})
	}
}

func TestB1FamilyNormalizationImprovesMarginAcrossFirstThreeProfiles(t *testing.T) {
	base := capacityBaseProfile()
	for _, dimensions := range []uint16{2048, 4096, 8192} {
		profile, err := capacityprofile.ScaleDimensions(base, fmt.Sprintf("d%d", dimensions), dimensions)
		if err != nil {
			t.Fatal(err)
		}
		rawDesired, rawDistractor := capacitySimilarityPair(t, profile, FeatureNormalizationNone)
		normalizedDesired, normalizedDistractor := capacitySimilarityPair(t, profile, FeatureNormalizationFamily)

		rawMargin := rawDesired - rawDistractor
		normalizedMargin := normalizedDesired - normalizedDistractor
		if normalizedMargin <= rawMargin {
			t.Fatalf("dimensions=%d family normalization did not improve fixture margin: raw=%v normalized=%v",
				dimensions, rawMargin, normalizedMargin)
		}
	}
}

func TestActiveFractionAloneDoesNotPreventCompetitionSaturation(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	if capacityprofile.ActiveFraction(oversized) != capacityprofile.ActiveFraction(base) {
		t.Fatalf("fixture must preserve active fraction: base=%v oversized=%v",
			capacityprofile.ActiveFraction(base), capacityprofile.ActiveFraction(oversized))
	}

	anchor, _, _ := capacityEvalItems()
	positiveFeatures := len(featuresForItem(anchor))
	winnerShare := capacityprofile.WinnerShareUpperBound(oversized, positiveFeatures)
	if winnerShare < 0.8 {
		t.Fatalf("fixture must expose weak selection pressure; winner share upper-bound ratio=%v", winnerShare)
	}

	desired, distractor := capacitySimilarityPair(t, oversized, FeatureNormalizationFamily)
	if desired >= distractor {
		t.Fatalf("oversized same-fraction profile must expose saturation failure in this fixture: desired=%v distractor=%v", desired, distractor)
	}
}

func TestTinyProfileCannotRepresentSameB2CompetitionRatio(t *testing.T) {
	base := capacityBaseProfile()
	tiny, err := capacityprofile.ScaleDimensions(base, "tiny", 256)
	if err != nil {
		t.Fatal(err)
	}
	if tiny.Sparse.Active != 4 {
		t.Fatalf("tiny active=%d want 4", tiny.Sparse.Active)
	}
	if _, err := softLocalPolicyForProfile(tiny); err == nil {
		t.Fatal("tiny profile must fail instead of silently changing four-family half-local/half-global policy")
	}
}

func TestCrossProfileSignatureIdentityIsNotUsedAsQualityMetric(t *testing.T) {
	base := capacityBaseProfile()
	small, _ := capacityprofile.ScaleDimensions(base, "small", 2048)
	large, _ := capacityprofile.ScaleDimensions(base, "large", 8192)
	if small.Sparse.Dimensions == large.Sparse.Dimensions {
		t.Fatal("fixture requires different dimensions")
	}
	// No assertion compares sparse dimension IDs across profiles. The hash
	// modulo changes with Dimensions; profile quality is evaluated only through
	// within-profile candidate relationships.
}

func BenchmarkCapacityProfiles(b *testing.B) {
	base := capacityBaseProfile()
	for _, tc := range []struct {
		id         string
		dimensions uint16
	}{
		{"small", 2048},
		{"medium", 4096},
		{"large", 8192},
	} {
		profile, err := capacityprofile.ScaleDimensions(base, tc.id, tc.dimensions)
		if err != nil {
			b.Fatal(err)
		}
		local, err := softLocalPolicyForProfile(profile)
		if err != nil {
			b.Fatal(err)
		}
		p, err := New(Config{
			Sparse:                profile.Sparse,
			MinInternalSimilarity: 0,
			ProviderID:            "sei-sacs-go-eval",
			ImplementationVersion: "capacity-profile-eval",
			FeatureNormalization:  FeatureNormalizationFamily,
			NormalizationFloor:    1,
			LocalCompetition:      local,
		})
		if err != nil {
			b.Fatal(err)
		}
		encoder, err := newProviderEncoder(p.cfg)
		if err != nil {
			b.Fatal(err)
		}
		anchor, _, _ := capacityEvalItems()
		prepared, err := p.preparedFeatures(anchor)
		if err != nil {
			b.Fatal(err)
		}

		b.Run(tc.id, func(b *testing.B) {
			b.ReportAllocs()
			for i := 0; i < b.N; i++ {
				if _, err := encoder.Encode(prepared); err != nil {
					b.Fatal(err)
				}
			}
		})
	}
}
