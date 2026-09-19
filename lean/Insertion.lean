/-
  The deterministic core of the light-traffic expansion, proved in general.

  Section 2 of the manuscript rests on facts about a single marked configuration.  Writing `V` for
  the single-server workload at time zero and `S` for the work that would remain if every customer
  were served immediately by its own rate-one server, the first and load-bearing one is

      S <= V          the excess of the single server over parallel service is nonnegative

  and it is what makes the remainder in the expansion nonnegative.  `verify.py` checks it on a
  finite grid and says so in its own output ("finite-grid regression, not the general proof"):
  16,384 configurations built from seven ages and four mark values.  The theorem below is the
  general statement, for arbitrarily many arrivals with arbitrary nonnegative ages and marks.  It
  does not even need the ages to be increasing.

  Core Lean 4, no Mathlib.  Natural-number subtraction is truncated, so `x - y` means `(x - y)_+`,
  which is exactly the convention of `verify.py` (`max(mark - age, 0)`, and a running maximum
  started at zero).

      lean lean/Insertion.lean
-/

namespace RossInsertion

/-- One arrival: its age (time before zero) and its service mark. -/
abbrev Arrival := Nat × Nat

/-- Reich's recursion.  `run cfg T w` folds the configuration carrying the running total `T` of
    service marks and the running maximum `w` of `total - age`. -/
def run : List Arrival → Nat → Nat → Nat × Nat
  | [],           T, w => (T, w)
  | (a, m) :: xs, T, w => run xs (T + m) (max w (T + m - a))

/-- Total work that arrived. -/
def total (cfg : List Arrival) : Nat := (run cfg 0 0).1

/-- Single-server workload at time zero. -/
def workload (cfg : List Arrival) : Nat := (run cfg 0 0).2

/-- Work remaining under parallel service: each customer on its own rate-one server. -/
def shot : List Arrival → Nat
  | []           => 0
  | (a, m) :: xs => (m - a) + shot xs

/-- The running total is the head start plus the sum of the marks. -/
theorem run_fst (cfg : List Arrival) : ∀ T w, (run cfg T w).1 = T + (run cfg 0 0).1 := by
  induction cfg with
  | nil => intro T w; simp [run]
  | cons p xs ih =>
      obtain ⟨a, m⟩ := p
      intro T w
      simp only [run]
      rw [ih (T + m) (max w (T + m - a)), ih (0 + m) (max 0 (0 + m - a))]
      omega

/-- The carried maximum never decreases along the run. -/
theorem le_run_snd (cfg : List Arrival) : ∀ T w, w ≤ (run cfg T w).2 := by
  induction cfg with
  | nil => intro T w; simp [run]
  | cons p xs ih =>
      obtain ⟨a, m⟩ := p
      intro T w
      simp only [run]
      have h := ih (T + m) (max w (T + m - a))
      omega

/-- Raising the carried maximum raises the result. -/
theorem run_snd_mono (cfg : List Arrival) :
    ∀ T w₁ w₂, w₁ ≤ w₂ → (run cfg T w₁).2 ≤ (run cfg T w₂).2 := by
  induction cfg with
  | nil => intro T w₁ w₂ h; simpa [run] using h
  | cons p xs ih =>
      obtain ⟨a, m⟩ := p
      intro T w₁ w₂ h
      simp only [run]
      exact ih (T + m) _ _ (by omega)

/-- Parallel service never exceeds the work that arrived. -/
theorem shot_le_total (cfg : List Arrival) : shot cfg ≤ total cfg := by
  induction cfg with
  | nil => simp [shot, total, run]
  | cons p xs ih =>
      obtain ⟨a, m⟩ := p
      have hx : total ((a, m) :: xs) = m + total xs := by
        simp only [total, run]
        rw [run_fst xs (0 + m) (max 0 (0 + m - a))]
        simp
      simp only [shot, hx]
      omega

/-- The engine of the argument.  Along any run, either nothing is in parallel service at all, or
    the carried maximum ends up dominating the head start plus the whole parallel workload.

    The disjunction is what lets the induction go from the youngest arrival forwards: the last
    arrival still holding parallel work is the one whose prefix total absorbs every earlier
    residual, and until it appears the left branch carries the induction. -/
theorem shot_zero_or_le (ys : List Arrival) :
    ∀ T w, shot ys = 0 ∨ T + shot ys ≤ (run ys T w).2 := by
  induction ys with
  | nil => intro T w; left; simp [shot]
  | cons p xs ih =>
      obtain ⟨a, m⟩ := p
      intro T w
      rcases ih (T + m) (max w (T + m - a)) with h | h
      · -- nothing behind this arrival is still in service
        by_cases hma : m ≤ a
        · left; simp only [shot]; omega
        · right
          simp only [shot, run]
          have hb := le_run_snd xs (T + m) (max w (T + m - a))
          omega
      · -- something behind it is, and its prefix total already dominates
        right
        simp only [shot, run]
        omega

/-- **The excess over parallel service is nonnegative**, for every finite configuration.

    This is the general form of the assertion `v >= s` that `verify.py` samples on its grid. -/
theorem shot_le_workload (cfg : List Arrival) : shot cfg ≤ workload cfg := by
  rcases shot_zero_or_le cfg 0 0 with h | h
  · simp [workload, h]
  · simpa [workload] using h

/-- The workload itself is nonnegative, and dominated by the work that arrived. -/
theorem workload_le_total (cfg : List Arrival) : workload cfg ≤ total cfg := by
  have gen : ∀ (ys : List Arrival) T w, w ≤ T → (run ys T w).2 ≤ (run ys T w).1 := by
    intro ys
    induction ys with
    | nil => intro T w h; simpa [run] using h
    | cons p xs ih =>
        obtain ⟨a, m⟩ := p
        intro T w h
        simp only [run]
        exact ih (T + m) (max w (T + m - a)) (by omega)
  simpa [workload, total] using gen cfg 0 0 (Nat.le_refl 0)

end RossInsertion

-- Axiom audit: none of these may depend on `sorryAx`.
#print axioms RossInsertion.shot_le_workload
#print axioms RossInsertion.shot_le_total
#print axioms RossInsertion.workload_le_total
#print axioms RossInsertion.shot_zero_or_le
